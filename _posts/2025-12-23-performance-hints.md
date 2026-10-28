---
lang: en
translation_key: 2025-12-23-performance-hints
translation_url: /ko/2025/12/23/performance-hints.html
title: "Performance Hints"
tags: ["engineering", "performance", "cpp"]
subtitle: "Bottlenecks, memory traffic, allocation, and concurrency in C++ performance work."
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-11
---

Performance work connects a measured bottleneck to an application metric. Allocation, memory traffic, redundant work, and contention often matter more than shorter expressions. The models below develop several ideas from Dean and Ghemawat's [Performance Hints](https://abseil.io/fast/hints.html); their numerical examples are assumed workloads, not machine measurements.

<div id="3-a-reproducible-measurement-protocol"></div>

## Metrics and measurement
{: id="1-decide-which-metric-matters"}

Latency, throughput, CPU time, peak memory, allocations, and energy can move in opposite directions. Batching trades waiting for throughput; caching trades memory and invalidation work for computation. A representative benchmark therefore specifies input distributions, hot/cold states, threads, hardware, compiler, flags, and required behavior.

Equivalent builds must consume their outputs so the compiler cannot discard the work. Warm and cold runs are separate; initialization belongs in the timing when users pay for it. Repeated times $$T_i$$ describe a distribution, not just its minimum. Alternating or randomizing trials reduces drift; paired differences $$D_i=T_i^{\mathrm{candidate}}-T_i^{\mathrm{baseline}}$$ remove shared conditions but not necessarily autocorrelation. CPU/allocation profiles and hardware counters locate candidate costs, not proof that one source line caused them. Results need the binary, input, host, repetitions, aggregation, and uncertainty.

## Amdahl's law
{: id="2-amdahls-law-limits-local-wins"}

If a component occupies fraction $$f$$ of baseline time and becomes $$s$$ times faster,

$$
S=\frac1{(1-f)+f/s}.
$$

Normalizing baseline time to one leaves $$1-f$$ unchanged and reduces the component to $$f/s$$. This assumes unchanged workload, interactions, and other costs. With $$f=0.2$$ and $$s=5$$, total speedup is $$1/(0.8+0.04)\approx1.19$$, rather than $$5$$; removing the component entirely permits at most $$1/(1-f)=1.25$$. Cross-component effects, such as fewer cache misses after removing allocations, require a new end-to-end measurement.

## Memory traffic
{: id="4-memory-traffic-and-locality"}

For $$F$$ operations and $$B$$ transferred bytes, processing-rate bound $$P$$ and bandwidth bound $$W$$ imply

$$
T\ge\max\left(\frac{F}{P},\frac{B}{W}\right),
$$

because $$F\le PT$$ and $$B\le WT$$. Dependency stalls, caches, and contention can increase time. Substituting measured effective rates makes this an estimate rather than a guaranteed bound. A hypothetical scan of $$B=1$$ GB at $$W=50$$ GB/s takes $$20$$ ms in the bandwidth term; changing arithmetic cannot reduce that term.

A dense scan of $$n$$ contiguous records, stride $$r$$ bytes, and cache lines of $$L$$ bytes touches roughly $$\lceil nr/L\rceil$$ lines. Structure-of-arrays can save traffic when only selected fields are read; joint field access, SIMD, prefetching, and layout overhead determine the result. Contiguous indices can reduce pointer indirection and width, but bounds, handle lifetimes, and relocation remain API contracts.

## Allocation and lifetime
{: id="5-allocation-and-object-construction"}

`reserve(n)` allocates capacity without constructing $$n$$ elements; `resize(n)` changes size and constructs elements.

```cpp
std::vector<Result> out;
out.reserve(items.size());
for (const auto& item : items) {
    out.push_back(compute(item));
}
```

Geometric growth gives amortized constant reallocation work per append, with possible latency spikes. Repeated `reserve(size()+1)` can instead cause quadratic copying. Reusing capacity avoids allocations:

```cpp
std::string buffer;
for (const auto& item : items) {
    buffer.clear();
    encode_into(item, buffer);
    consume(buffer);
}
```

Here `consume` must not retain a view across the next mutation. Non-owning `std::string_view`, vector references, and iterators remain subject to lifetime and invalidation rules ([C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)).

## Caches and fast paths
{: id="6-fast-paths-caching-and-avoiding-work"}

Skipping work requires a maintained invariant: a stale “nothing pending” flag can lose results. For cache hit rate $$h$$, hit cost $$c_h$$, and miss/recomputation cost $$c_m$$,

$$
\mathbb E[C]=hc_h+(1-h)c_m.
$$

excludes invalidation and memory effects. Hashing, keys, eviction, storage, and dependency revisions add costs; omitting an output-affecting input from the key permits stale answers. Precomputation pays only with sufficient reuse. Sorted-vector lookup takes $$O(\log n)$$ comparisons; hashing has expected $$O(1)$$ lookup under hashing/load assumptions. Locality, footprint, and adversarial inputs still distinguish them.

## Concurrency and queues
{: id="7-concurrency-and-queueing"}

Independent work must outweigh synchronization and scheduling costs. False sharing places independently modified variables on one cache line; padding may reduce contention while increasing footprint. For stable systems with consistent averages, Little's law is

$$
L=\lambda W
$$

where $$L$$ is average work in the system, $$\lambda$$ the arrival rate, and $$W$$ mean residence time. It does not identify the delay's cause. The idealized M/M/1 model assumes Poisson arrivals, exponential service, and $$\lambda<\mu$$, giving mean residence time $$1/(\mu-\lambda)$$. This illustrates saturation sensitivity, not production tail latency.

Batching adds waiting while amortizing overhead. Offered load and p50/p95/p99, with adequate samples, expose effects that closed-loop request/response benchmarks can hide.

<div id="9-a-practical-decision-record"></div>

## API costs
{: id="8-api-choices-and-correctness-costs"}

Bulk operations reduce repeated parsing, validation, and synchronization but change cancellation, partial failure, and ownership. Shared buffers have validity periods; moving an object is not universally free. A valid optimization preserves results, ordering, error behavior, lifetimes, and concurrent-access rules, including small inputs and infrequent paths. Its decision record connects the bottleneck, profile, measured gain, uncertainty, and maintenance cost; microbenchmark ratios do not establish application speedup. Compiler/profiler versions and local hardware rates belong to that evidence.

## References
{: id="references"}

- [Dean and Ghemawat, Performance Hints](https://abseil.io/fast/hints.html).
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines).
- [Google Benchmark](https://github.com/google/benchmark).
- [Abseil performance notes](https://abseil.io/fast/).
