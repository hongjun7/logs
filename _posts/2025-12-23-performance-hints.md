---
title: Performance Hints in C++
tags: engineering
subtitle: This post tidies up the core ideas for how to think about, estimate, measure, and ship performance improvements—mainly for single-binary software (not distributed systems or ML hardware tuning).
---

Most performance advice fails because it treats optimisation like a bag of tricks: reserve here, inline there, and hope for the best. In practice, high-impact performance work in C++ is usually about **removing systemic costs** that repeat millions of times: cache misses, allocations, unnecessary work, and contention.

[Jeff Dean and Sanjay Ghemawat’s “Performance Hints”](https://abseil.io/fast/hints.html) is essentially a guide to that mindset: not “optimise everything”, but **spot the critical 3% where small savings compound**, especially in library code and hot paths.

This post focuses on the ideas that consistently deliver outsized gains in real C++ systems—while keeping the code maintainable.

---

## Background

On modern CPUs, “speed” is rarely about raw arithmetic. It’s about **how often you stall** waiting for something:

* **Cache locality**: if your data isn’t already near the core, you’re paying to fetch it.
* **Branch prediction**: unpredictable branches cause pipeline flushes. In tight loops this is brutal.
* **Allocations**: the allocator isn’t just “a function call”—it scatters memory, increases cache footprint, and triggers extra initialisation/destruction work.
* **Locks**: uncontended locks are cheap-ish; contended locks are a performance cliff. Worse, they can make CPU utilisation look low even when the system is slow.

So the most valuable performance work tends to be:
**touch less memory, allocate less, branch less unpredictably, and synchronise less.**

---

## How to approach

A reliable workflow in C++ looks like this:

- **Classify the code**

  * Is this on a per-request path? per-element path? library code used everywhere?
    If yes, small costs matter.

- **Estimate before you engineer**

  * If an operation implies disk/network/locks/allocations, you probably don’t need a microscope to know it’s expensive.
  * Estimation stops you wasting time on micro-changes when the design is the issue.

- **Measure with the right lens**

  * CPU profile (pprof/perf) answers “where time is spent”.
  * Allocation profile answers “what causes churn”.
  * Lock contention profiling answers “where threads queue”.
  * Hardware counters can tell you “you’re cache-miss bound” even if CPU looks “busy”.

- **Prefer changes that reduce cost structurally**

  * Fast paths, data layout, bulk operations, reducing allocations, and sharding locks tend to beat instruction-level tweaks.

---

## Ideas

### 1. Allocations

Allocations cost you in three ways:

1. allocator overhead (and possible contention),
2. repeated initialisation/destruction,
3. memory scattering → more cache misses later.

In a hot loop, even “small” allocations are poison.

##### (A) Reserve once, then push

```cpp
std::vector<Foo> out;
out.reserve(n);                 // one allocation
for (...) out.push_back(makeFoo());
```

**Common mistake:** using `resize(n)` when construction is expensive. `resize` constructs `n` elements, which can double work if you later overwrite.

##### (B) Reuse temporaries across iterations

```cpp
std::string buf;
buf.reserve(4096);

for (const auto& item : items) {
  buf.clear();                  // keep capacity
  buildInto(buf, item);
  consume(buf);
}
```

This is especially important for `std::string`, `std::vector`, protobuf objects, JSON buffers, etc.

##### (C) Avoid node-based containers on hot paths

Node containers (`std::map`, `std::unordered_map` often too) allocate per element and chase pointers. Many workloads are faster with **contiguous storage**:

* If you can keep keys sorted: `std::vector<pair<K,V>> + binary_search`
* If you need hashing: consider flatter hash tables (Abseil’s `flat_hash_map` is a classic example in Google’s world)

Even if you stick to STL: if your map is small or you can batch operations, you can often redesign to a vector-based structure.

---

### 2. Cache miss

CPU cores are absurdly fast when they have data in L1/L2. They’re painfully slow when they must fetch from main memory. So you win by ensuring hot code touches **fewer cache lines**.

##### (A) Separate hot fields from cold fields

If your hot loop only needs a few fields, don’t place bulky/cold fields right next to them.

```cpp
struct User {
  uint64_t id;
  uint32_t flags;
  uint32_t quota;

  // cold: rarely needed in hot path
  std::string display_name;
  std::string bio;
};
```

If cold data is large and rarely touched, put it behind indirection:

```cpp
struct UserCold { std::string display_name, bio; };

struct User {
  uint64_t id;
  uint32_t flags, quota;
  std::unique_ptr<UserCold> cold; // only when needed
};
```

##### (B) Prefer indices over pointers for graph-like structures

Pointers are 64-bit and lead to random memory access. Indices often keep you in contiguous arrays:

```cpp
struct Edge { uint32_t to; };      // index into nodes[]
std::vector<Node> nodes;
std::vector<Edge> edges;
```

This often improves locality and reduces memory footprint at once.

##### (C) Choose “flat” representations

If you can turn “many small objects” into “one big array”, you often get a step-change improvement.

A classic example: avoid `vector<unique_ptr<T>>` if `vector<T>` works.

---

### 3. Avoid work you don’t need

The best optimisation is not doing the thing at all. And this is where you can gain a lot **without** turning the code into assembly.

##### (A) Make the common case cheap with a simple flag

This pattern is extremely common in Dean/Ghemawat’s examples: skip a loop if you can prove it’s unnecessary.

```cpp
struct Stats {
  std::array<double, 16> errors{};
  bool any_error = false;

  void set_error(int i, double v) {
    errors[i] = v;
    any_error = true;
  }

  void merge_from(const Stats& other) {
    if (!other.any_error) return;     // cheap common case
    for (int i = 0; i < 16; ++i) errors[i] += other.errors[i];
    any_error = true;
  }
};
```

This is “boringly readable” and often huge in practice.

##### (B) Move expensive checks to module boundaries

Instead of validating the same invariants repeatedly inside inner loops, validate input once when it enters the module.

---

### 4. API choices

Some of the best performance wins come from enabling callers to avoid copies and per-call overhead, especially for libraries.

##### (A) Use view types for read-only params

```cpp
void parse(std::string_view s);  // avoids copies, accepts string/substr/etc.
```

For arrays:

```cpp
void process(std::span<const int> xs); // C++20
```

This keeps APIs flexible *and* fast.

##### (B) Bulk operations to amortise overhead

If callers call your API in a loop, you may be forcing repeated locks, repeated lookups, repeated boundary costs.

Instead of:

```cpp
Value lookup(Key k);
```

Provide:

```cpp
void lookup_many(std::span<const Key> keys,
                 std::span<Value> out);
```

Even if callers don’t adopt it immediately, you can sometimes **use bulk internally** and cache results.

---

### 5. Concurrency

A contended lock doesn’t just “cost some nanoseconds”. It serialises progress and can destroy throughput. It can also make CPU profiles misleading (threads are blocked, not burning CPU).

##### (A) Keep critical sections tiny

Don’t do expensive work while holding a lock.

```cpp
auto v = build_value(k);           // do this outside
{
  std::lock_guard lk(mu);
  cache.emplace(k, std::move(v));  // short lock
}
```

##### (B) Shard a hot mutex

A simple sharding scheme often gives a clean 2x-ish throughput jump under concurrency:

```cpp
static constexpr size_t kShards = 16;

struct Shard { std::mutex mu; std::unordered_map<int,int> m; };
std::array<Shard, kShards> shards;

Shard& shard_for(int k) {
  return shards[std::hash<int>{}(k) % kShards];
}
```

**Key caution:** shard selection must not create skew (e.g., bad hash bits).

---

## Conclusion

If you only remember one practical sequence for C++ performance work:

1. **Stop allocating in hot paths** (reserve, reuse, avoid node containers).
2. **Flatten data** (contiguous storage, indices not pointers, hot/cold separation).
3. **Add fast paths** for common cases (simple flags, early returns).
4. **Make APIs cheap** (views, spans, bulk ops).
5. **Fix contention** (short critical sections, sharding).
