---
lang: en
translation_key: 2023-09-30-rust-cp-helper
translation_url: /ko/2023/09/30/rust-cp-helper.html
title: "Rust CP Helper"
tags: ["engineering", "rust", "algorithms"]
subtitle: "Algorithms, ownership, and a reproducible Rust contest workflow."
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-11
---

Rust's compiler catches many ownership and lifetime errors; algorithmic correctness still rests on invariants and numeric bounds. A small single-file solution, tested against the judge's toolchain, provides a reliable baseline before adding contest automation.

## Complexity and integer bounds
{: id="1-choose-the-algorithm-before-the-language"}

For input size $$n$$, $$O(n\log n)$$ bounds growth up to constants for sufficiently large $$n$$, not elapsed time. Repeated allocation can make an $$O(n)$$ implementation slower than an $$O(n\log n)$$ one on small inputs. Constant-factor tuning cannot make an $$O(n^2)$$ algorithm near-linear.

At $$n=200{,}000$$, a double loop performs roughly $$4\times10^{10}$$ iterations; sorting takes on the order of $$n\log_2 n\approx3.52\times10^6$$ comparison-scale operations. These are operation estimates, not Rust or CPU measurements.

Summing $$n$$ values bounded in absolute value by $$B$$ gives

$$
\left\vert \sum_{i=1}^{n}a_i\right\vert \le nB.
$$

With $$n\le2\times10^5$$ and $$B\le10^9$$, the sum can reach $$2\times10^{14}$$: within `i64`, beyond `i32`. A signed $$b$$-bit integer represents $$[-2^{b-1},2^{b-1}-1]$$. Intermediate products need bounds too: multiplying two `i64` operands and casting afterward cannot undo overflow.

## A single-file solution
{: id="2-a-small-complete-starting-program"}

This program reads $$n$$ signed integers and prints their sum. Input consists of valid whitespace-separated integers satisfying $$n\le200{,}000$$ and $$\vert a_i\vert \le10^9$$.

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

The input string occupies $$O(L)$$ memory for $$L$$ bytes, with $$O(L)$$ parsing work under the usual fixed-width integer model. Reading to EOF suits non-interactive problems; interactive judges need streaming input and output flushing.

An example compilation is

```sh
rustc --edition=2021 -O main.rs -o main
./main < input.txt
```

Edition 2021 is illustrative; the edition, compiler version, and crates must follow the judge's requirements. Stable Rust suffices for standard algorithms; a dependency may explicitly require nightly. Optimization changes execution, not the correctness argument.

## Ownership and graph storage
{: id="3-what-safety-does-and-does-not-guarantee"}

Safe Rust prevents broad classes of memory misuse, but a wrong recurrence, bounds panic, deadlock, or arithmetic error remains possible. Debug overflow checks and release wrapping defaults differ; explicit checked arithmetic detects overflow when required. [Rust integer overflow](https://doc.rust-lang.org/book/ch03-02-data-types.html).

A `Vec<T>` owns its allocation; `&T` allows shared reading and `&mut T` grants exclusive access for its lifetime. Storing indices avoids holding references across vector growth: reallocation can move elements, explaining the borrowing conflict when pushing while a reference remains live.

`Vec<Vec<usize>>` is a straightforward adjacency list. Compressed sparse row storage instead uses one contiguous neighbor array and $$n+1$$ offsets, occupying $$O(n+m)$$ for $$n$$ vertices and $$m$$ directed edges. Its locality benefit depends on the traversal.

## Breadth-first search
{: id="4-bfs-with-a-proof-rather-than-a-slogan"}

For an unweighted graph $$G=(V,E)$$ and source $$s$$, BFS finds the minimum edge count from $$s$$ to each reachable vertex. `dist[v] = None` marks an undiscovered vertex; the FIFO queue holds discovered vertices awaiting expansion.

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

Vertices leave the queue in nondecreasing distance order. The source starts at zero. When $$v$$ leaves with shortest distance $$d$$, an undiscovered neighbor receives $$d+1$$. A shorter path would have a predecessor at distance at most $$d-1$$, already expanded, contradicting the neighbor's undiscovered state. Each vertex enters once and each stored edge is inspected once, giving time $$O(\vert V\vert +\vert E\vert )$$ and auxiliary space $$O(\vert V\vert )$$.

Weighted paths require different assumptions: Dijkstra needs nonnegative weights, while negative edges need another algorithm and negative cycles can leave shortest distances undefined.

## Modular arithmetic
{: id="5-modular-arithmetic-and-boundary-cases"}

For integer modulus $$M\ge2$$, arithmetic in $$\mathbb Z/M\mathbb Z$$ satisfies

$$
(a+b)\bmod M=((a\bmod M)+(b\bmod M))\bmod M
$$

The implementation must still hold the intermediate sum, using a wider type or overflow-safe calculation. Division by $$a$$ uses an inverse, existing exactly when $$\gcd(a,M)=1$$. Fermat's formula $$a^{M-2}\bmod M$$ additionally requires prime $$M$$ and $$a\not\equiv0\pmod M$$.

Signed `%` returns a remainder; `rem_euclid` yields a canonical nonnegative residue for positive modulus. Boundary cases include $$0$$, $$M-1$$, $$M$$, permitted negative inputs, and the largest intermediate value.

## Small oracles
{: id="6-testing-an-algorithm-against-a-small-oracle"}

An exhaustive solver makes an effective reference for small random inputs. Tiny shortest-path cases allow enumeration or a cubic all-pairs solver; subset optimization allows all $$2^n$$ subsets for small $$n$$. Saving the seed and failing input makes counterexamples reproducible.

Tests cover parsing, indexing, and boundaries; the invariant covers the stated domain. Debug and optimized binaries exercise different checks and execution modes. Graph cases include isolated vertices, disconnected components, parallel edges, self-loops, and long chains that expose recursive stack use.

## Contest tools
{: id="7-optional-contest-tooling"}

The original workspace used [rust-competitive-helper](https://github.com/rust-competitive-helper/rust-competitive-helper) and [Competitive Companion](https://github.com/jmerle/competitive-companion). Their installation, ports, judge support, and toolchain requirements belong to their current READMEs; pinned revisions make the setup reproducible.

The underlying workflow remains a problem directory, single-file implementation, samples and oracle tests, judge-compatible compilation, and source submission. A generated Cargo workspace must also fit the judge's dependency and entry-point restrictions. Local IDE success alone does not establish portability. No compiler benchmark or execution of these helpers is reported here.

## References
{: id="references-and-current-scope"}

- [The Rust Programming Language](https://doc.rust-lang.org/book/): ownership, borrowing, types, and errors.
- [Rust standard library](https://doc.rust-lang.org/std/): collections, I/O, and numeric operations.
- [rust-competitive-helper](https://github.com/rust-competitive-helper/rust-competitive-helper) and [Competitive Companion](https://github.com/jmerle/competitive-companion).
