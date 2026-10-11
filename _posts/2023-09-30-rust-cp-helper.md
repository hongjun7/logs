---
title: "Competitive Programming with Rust: Invariants, Complexity, and a Reliable Workflow"
tags: ["engineering", "rust", "algorithms"]
subtitle: "A practical path from input parsing and integer bounds to graph algorithms, ownership, and reproducible contest tooling."
last_modified_at: 2026-10-11
sources_checked_at: 2026-10-11
---

> **The idea in one minute.** Rust lets us express fast algorithms while the compiler checks many ownership and lifetime mistakes. Correctness still comes from a mathematical invariant, careful integer bounds, and testing. Start with a stable compiler, a small single-file template, and the judge's actual toolchain; add automation after that workflow works.

**Reading path.** Begin with the cost model and complete program. Then study ownership and the BFS proof. The last sections explain how to test and how optional contest tools fit into the workflow. Prerequisites are loops, arrays, and elementary graphs.

## 1. Choose the algorithm before the language

Let $$n$$ be the input size. A time complexity such as $$O(n\log n)$$ bounds growth up to constants for sufficiently large $$n$$; it does not promise a particular running time. An $$O(n)$$ program that allocates on every iteration can lose to an $$O(n\log n)$$ program at small sizes. Conversely, a constant-factor improvement cannot rescue an $$O(n^2)$$ algorithm when the judge expects near-linear work.

For $$n=200{,}000$$, a double loop performs about $$4\times10^{10}$$ iterations. Sorting involves an order of $$n\log_2 n\approx3.52\times10^6$$ comparison-scale operations. These are **operation estimates**, not measurements of Rust or a CPU. Use them to reject implausible approaches, then benchmark a representative implementation.

A problem's constraints are part of its specification. If we add $$n$$ values, each bounded by $$B$$ in absolute value, then

$$
\left\vert \sum_{i=1}^{n}a_i\right\vert \le nB.
$$

When $$n\le2\times10^5$$ and $$B\le10^9$$, the sum may reach $$2\times10^{14}$$. It fits in `i64` but not in `i32`. A signed $$b$$-bit integer represents $$[-2^{b-1},2^{b-1}-1]$$. Prove a bound on intermediate products as well as the final answer. If both operands are `i64`, casting the product afterward cannot repair overflow that already happened.

## 2. A small, complete starting program

The following program solves a deliberately simple task: read $$n$$ signed integers and print their sum. The input contract is whitespace-separated valid integers with $$n\le200{,}000$$ and $$\vert a_i\vert \le10^9$$.

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let mut sum: i64 = 0;
    for _ in 0..n {
        let x: i64 = it.next().unwrap().parse().unwrap();
        sum += x;
    }
    println!("{sum}");
}
```

This template uses $$O(L)$$ memory for an input string of $$L$$ bytes and $$O(L)$$ parsing work in the usual fixed-width integer model. It is appropriate for non-interactive problems. Interactive judges require streaming input and flushing output; reading to EOF would wait for an input stream that has not finished.

Compile locally with the judge's supported edition:

```sh
rustc --edition=2021 -O main.rs -o main
./main < input.txt
```

Edition 2021 is an example, not a statement that every judge uses it. Inspect the platform's compiler version and allowed crates. A stable toolchain is sufficient for standard algorithms; switch to nightly only for an explicit requirement of a particular dependency. Optimization flags do not establish correctness.

## 3. What safety does and does not guarantee

Safe Rust's ownership and borrowing rules prevent broad classes of memory misuse. They do not prevent a wrong recurrence, an out-of-bounds panic, a deadlock, or an arithmetic error. The standard Rust documentation describes debug overflow checks and release wrapping defaults; use explicit checked arithmetic when the proof requires detecting overflow. [Rust integer types and overflow](https://doc.rust-lang.org/book/ch03-02-data-types.html).

A `Vec<T>` owns its allocation. A shared borrow `&T` permits reading; a mutable borrow `&mut T` gives exclusive access for its lifetime. Algorithms often become easier to write when we store **indices** rather than references into a vector that may grow. Reallocation can move elements, and keeping a reference while pushing introduces an ownership conflict for a good reason.

For graph algorithms, use `Vec<Vec<usize>>` first. When memory pressure matters, a compressed sparse row representation stores all neighbors in one contiguous array plus $$n+1$$ offsets. Its storage is $$O(n+m)$$ for $$n$$ vertices and $$m$$ directed edges. Contiguity can improve locality, but measure it for the actual traversal.

## 4. BFS, with a proof rather than a slogan

For an unweighted graph $$G=(V,E)$$ and source $$s$$, breadth-first search computes the smallest number of edges from $$s$$ to every reachable vertex. Let `dist[v] = None` mean undiscovered. The queue contains discovered vertices awaiting expansion.

```rust
use std::collections::VecDeque;

fn bfs(graph: &[Vec<usize>], source: usize) -> Vec<Option<usize>> {
    let mut dist = vec![None; graph.len()];
    let mut queue = VecDeque::new();
    dist[source] = Some(0);
    queue.push_back(source);
    while let Some(v) = queue.pop_front() {
        let next = dist[v].unwrap() + 1;
        for &u in &graph[v] {
            if dist[u].is_none() {
                dist[u] = Some(next);
                queue.push_back(u);
            }
        }
    }
    dist
}
```

**Invariant.** Vertices leave the FIFO queue in nondecreasing distance order, and each assigned distance is a shortest-path length. Initially the source has distance zero. If $$v$$ is removed with shortest distance $$d$$, any undiscovered neighbor receives distance $$d+1$$. A shorter path to that neighbor would have a predecessor at distance at most $$d-1$$, which would already have been expanded and discovered it. This is a contradiction. Each vertex is enqueued once, and each stored edge is inspected once: time $$O(\vert V\vert +\vert E\vert )$$ and auxiliary memory $$O(\vert V\vert )$$.

BFS does not solve arbitrary weighted shortest paths. Dijkstra's method requires nonnegative weights; negative edges call for a different algorithm and negative cycles may make shortest-path distances undefined. A graph representation alone does not justify substituting one method for another.

## 5. Modular arithmetic and boundary cases

For integer modulus $$M\ge2$$, residue arithmetic computes in $$\mathbb Z/M\mathbb Z$$. The equivalence

$$
(a+b)\bmod M=((a\bmod M)+(b\bmod M))\bmod M
$$

is mathematical; a machine implementation must still hold the intermediate addition. Use a wider type or an overflow-safe construction. Division by $$a$$ means multiplication by an inverse, which exists exactly when $$\gcd(a,M)=1$$. Fermat's formula $$a^{M-2}\bmod M$$ additionally requires prime $$M$$ and $$a\not\equiv0\pmod M$$.

Signed `%` is a remainder operator. For a canonical nonnegative residue with positive modulus, `rem_euclid` communicates the intended behavior. Test $$0$$, $$M-1$$, $$M$$, negative inputs when allowed, and the largest intermediate value. For graph problems also test a single vertex, disconnected components, parallel edges, self-loops, and a chain long enough to expose recursive stack use.

## 6. Testing an algorithm against a small oracle

A strong test is to compare an optimized algorithm against a simple exhaustive solver on small random inputs. For shortest paths, enumerate or use a cubic all-pairs baseline on tiny graphs; for subset optimization, enumerate all $$2^n$$ subsets while $$n$$ is small. Save the random seed and the exact failing input. This distinguishes a reproducible counterexample from a lucky sample.

Tests complement the invariant proof. They are especially useful for boundaries, parsing, and indexing, while a proof explains why no unseen input in the stated domain breaks the algorithm. Run both debug and optimized binaries: the former exposes more runtime checks, and the latter matches the judge's execution mode more closely.

## 7. Optional contest tooling

The original workflow used [rust-competitive-helper](https://github.com/rust-competitive-helper/rust-competitive-helper), [Competitive Companion](https://github.com/jmerle/competitive-companion), and an example workspace. Those are project-specific conveniences, not language requirements. Read their current READMEs for installation, listener ports, supported judges, and toolchain requirements; pin a known revision before building a repeatable environment.

A robust workflow is: obtain statement and examples, make a problem directory, implement a single-file solution, run samples and the small oracle, compile with judge settings, and submit the actual source file. If a helper generates a Cargo workspace, verify that its dependencies and generated entry point also work as the judge's permitted submission format. Do not assume a local IDE run proves portability.

## References and current scope

- [The Rust Programming Language](https://doc.rust-lang.org/book/): ownership, borrowing, types, and error behavior.
- [Rust standard library](https://doc.rust-lang.org/std/): collections, I/O, numeric operations.
- [rust-competitive-helper](https://github.com/rust-competitive-helper/rust-competitive-helper) and [Competitive Companion](https://github.com/jmerle/competitive-companion): optional automation.

This revision replaces a tool-dependent setup with a judge-compatible baseline. No compiler performance comparison or contest-tool execution is claimed here.
