---
lang: en
translation_key: 2024-02-10-characteristic-sets
translation_url: /ko/2024/02/10/characteristic-sets.html
title: "Characteristic Sets: When RDF Cardinality Is Exact, and When It Is Estimated"
tags: ["knowledge-graphs", "databases", "cardinality"]
subtitle: "Derive star-query counts from predicate co-occurrence, then expose the multiplicity, correlation, and compression assumptions behind the estimator."
last_modified_at: 2026-10-11
sources_checked_at: 2026-10-11
---

> **The idea in one minute.** A characteristic set records which predicates occur for a subject. It preserves correlations such as “books usually have both an author and a title.” For a restricted distinct-subject star query, complete characteristic-set counts give an exact answer count. Bag multiplicities, constants, and compressed summaries require additional information or assumptions.

**Reading path.** Follow the exact counting formula first, then the two-subject counterexample. The later sections connect synopsis design to join planning and explain how to evaluate an estimator. Prerequisites are sets, averages, and the idea of a database join.

## 1. Why an optimizer needs cardinality

A query planner chooses join order and physical operators. Intermediate result size can matter more than final result size. If a filter reduces a million rows to ten, applying it early may save substantial work; an incorrect estimate can choose the opposite order.

Cardinality is the number of solutions under specified semantics. RDF graphs are sets of triples, but SPARQL evaluation generally produces a **multiset of solution mappings**. `SELECT DISTINCT` changes that output. Always identify whether the count concerns full bindings, projected rows, or distinct values.

## 2. The characteristic-set partition

Let $$R$$ be a finite RDF graph and $$U_R$$ its subjects. Define

$$
C(s)=\{p:\exists o\;(s,p,o)\in R\},\qquad
n_C=\vert \{s\in U_R:C(s)=C\}\vert .
$$

The sets of subjects indexed by $$C$$ form a disjoint partition. Consider a star query with predicates $$P=\{p_1,\ldots,p_k\}$$:

```sparql
PREFIX : <urn:example:>
SELECT DISTINCT ?s WHERE {
  ?s :author ?a .
  ?s :title  ?t .
}
```

Assume every object variable is fresh and unrestricted, with no filters or extra shared variables. A subject matches precisely when $$P\subseteq C(s)$$. Therefore

$$
N_{\mathrm{distinct}}(P)=\sum_{C\supseteq P}n_C.
$$

**Proof.** The query requires at least one outgoing edge for every requested predicate. That condition is exactly set containment. Count each matching subject once in its unique partition class. The sum has neither missing subjects nor double counting.

This is the main useful exactness result. It does not extend unchanged to bounded objects, shared object variables, arbitrary joins, or summaries that merged distinct characteristic sets. [Neumann and Moerkotte, 2011](https://madoc.bib.uni-mannheim.de/29788/).

## 3. Full bindings require multiplicities

Let

$$
m_p(s)=\vert \{o:(s,p,o)\in R\}\vert .
$$

For the same star with independent object variables and no duplicate elimination, the number of full bindings is

$$
N_{\mathrm{bag}}(P)=\sum_{s:P\subseteq C(s)}\prod_{p\in P}m_p(s).
$$

Each object variable independently chooses one value from that subject's outgoing edges. The product counts combinations for a subject; the sum combines subjects. Projection may keep repeated rows, so removing object variables without `DISTINCT` does not remove their multiplicity.

Store total predicate occurrences $$o_{C,p}=\sum_{s:C(s)=C}m_p(s)$$ and mean multiplicity $$\bar m_{C,p}=o_{C,p}/n_C$$. A compact estimator is

$$
\widehat N_{\mathrm{bag}}(P)=\sum_{C\supseteq P}n_C\prod_{p\in P}\bar m_{C,p}.
$$

It replaces an average of products by a product of averages. That is an assumption about multiplicity correlation within each class.

### A worked counterexample

Two subjects share characteristic set `{author, title}`. Their multiplicities are $$(1,1)$$ and $$(3,3)$$. The true count is $$1\cdot1+3\cdot3=10$$. Both mean multiplicities are $$2$$, so the estimator gives $$2\cdot2\cdot2=8$$.

For two predicates, write expectation over a uniformly chosen subject in the class:

$$
\mathbb E[m_p m_q]
=\mathbb E[m_p]\mathbb E[m_q]+\operatorname{Cov}(m_p,m_q).
$$

The missing cardinality contribution is $$n_C\operatorname{Cov}(m_p,m_q)$$. With pairs $$(1,3)$$ and $$(3,1)$$, the true count is $$6$$ and the same mean-based estimate is $$8$$: negative covariance reverses the error. Characteristic sets capture **predicate presence** correlations, not automatically all multiplicity correlations.

Repeated predicates with different object variables introduce powers, such as $$m_p(s)^2$$. Reusing the same object variable instead introduces equality constraints. Neither case should silently use an ordinary two-predicate independence formula.

## 4. Constants and shared variables

For `?s :author :Ada`, predicate presence only says an author exists. It does not say Ada is one of the authors. Define

$$
b_{p,o}(s)=\mathbf1\{(s,p,o)\in R\}.
$$

An exact distinct-subject count for bounded predicates is a sum of products of these indicators. Storing only a global frequency for Ada can miss correlations with a subject class, publication year, or another constant.

A formula such as $$\Pr(O=o\mid P=p)$$ is meaningful when the conditioning event has positive probability and the sampling universe is defined, for example a uniformly selected triple. But converting a triple-level frequency into a subject-level query probability requires care: high-degree subjects occur more often in the triple distribution.

For a join `?s :author ?x . ?s :editor ?x`, counting separate author and editor multiplicities is insufficient. We need the intersection of object sets for each subject:

$$
\sum_s \vert \operatorname{Authors}(s)\cap\operatorname{Editors}(s)\vert .
$$

This example cleanly separates a predicate co-occurrence synopsis from a complete query answer counter.

## 5. Compression changes the guarantee

With $$d$$ possible predicates, as many as $$2^d$$ sets exist in principle. A real dataset often uses far fewer, but a strict storage budget may still require merging rare sets. If a subject with `{author}` is counted inside `{author, title}`, a query requiring both properties can count it incorrectly. If a true `{author, title}` class is split into separate single-predicate summaries, its co-occurrence can be lost.

There is no universal rule that overestimation is harmless. It can change join order, memory reservations, and operator choice. Underestimation can also be damaging when it selects nested loops for a large intermediate. The relevant objective is execution cost under the workload, not a preference for one error direction in isolation.

An implementation should retain metadata saying whether counts are exact, merged, sampled, or stale. Incremental updates can change a subject's entire characteristic set: adding its first `title` edge moves it to another partition; deleting its last such edge moves it back. Updating only predicate totals would leave the synopsis inconsistent.

## 6. Join estimation beyond one star

Under an explicit independence approximation for relational inputs $$R_1,\ldots,R_m$$ and join predicates $$e$$, the common form is

$$
\widehat N=\left(\prod_{i=1}^{m}\vert R_i\vert \right)
\left(\prod_{e}\widehat{\operatorname{sel}}(e)\right).
$$

Selectivities are multiplied, not summed. This expression assumes compatible sampling universes and independence; it is not a theorem for correlated joins. A synopsis covering a group of correlated predicates replaces the corresponding factors as a group. Overlapping synopses must be combined carefully to avoid counting the same correlation or base population twice.

Equivalent logical queries have the same true cardinality regardless of physical join order. A consistent planner should reuse one logical-subexpression estimate when comparing physical plans, although approximate estimation procedures can otherwise return different values on separate calls.

## 7. Evaluating an estimator today

For positive true and estimated counts, define

$$
q\text{-error}=\max\left(\frac{\widehat N}{N},\frac{N}{\widehat N}\right).
$$

A count of $$80$$ versus true count $$100$$ has q-error $$1.25$$. Zero counts require a separately stated policy; silently replacing all zeroes with one hides false emptiness predictions. Report empty-query detection, median and tail q-error, synopsis build time, storage, estimate latency, and downstream query latency.

Compare a complete characteristic-set baseline, a budgeted version, a sampling estimator, and the system's native statistics on the same data snapshot. Include stars, cycles, bounded objects, repeated predicates, skew, and update drift. The 2024 complex-query sampling work provides a complementary direction for operators that a simple star synopsis cannot model. [Hu and Motik, 2024](https://www.cs.ox.ac.uk/people/boris.motik/pubs/hm24-accurate-sampling.pdf).

## 8. Pairwise independence is insufficient for a three-predicate star

For three multiplicities $$X,Y,Z$$ in a characteristic-set class, expanding around their means gives

$$
\begin{aligned}
\mathbb E[XYZ]
={}&\mu_X\mu_Y\mu_Z
+\mu_X\operatorname{Cov}(Y,Z)
+\mu_Y\operatorname{Cov}(X,Z)\\
&+\mu_Z\operatorname{Cov}(X,Y)
+\mathbb E[(X-\mu_X)(Y-\mu_Y)(Z-\mu_Z)].
\end{aligned}
$$

A synopsis of only means and pairwise covariances can still miss the final centered third-order term. For a concrete RDF multiplicity construction, consider four equally weighted subjects with tuples $$(1,1,1),(1,2,2),(2,1,2),(2,2,1)$$. Every multiplicity is positive, so the subjects can all share the same three-predicate characteristic set. Each pair is independent, with mean $$3/2$$ and covariance zero.

The exact number of full star bindings is $$1+4+4+4=13$$. A product-of-means estimate gives $$4(3/2)^3=13.5$$. The mean product is $$13/4$$, while the product of means is $$27/8$$; the centered third-order term is $$-1/8$$. Thus eliminating every pairwise covariance does not establish mutual independence. This matters as stars grow: collecting more marginal statistics does not automatically recover their joint distribution.

## 9. Derive a conventional equijoin estimate

For two relations joining on one variable, let $$f_R(v)$$ and $$f_S(v)$$ be the multiplicities of key $$v$$. The true bag join size is

$$
N_{R\Join S}=\sum_v f_R(v)f_S(v).
$$

Suppose keys are uniform within domains $$D_R,D_S$$ of sizes $$V_R,V_S$$. If the smaller domain is contained in the larger, there are $$\min(V_R,V_S)$$ common keys. Hence

$$
\widehat N=
\min(V_R,V_S)\frac{\vert R\vert }{V_R}\frac{\vert S\vert }{V_S}
=\frac{\vert R\vert \vert S\vert }{\max(V_R,V_S)}.
$$

This familiar estimate follows from **uniformity and containment**, not merely from knowing distinct-value counts. With incomplete domain overlap, replace the common-key factor by the actual overlap size; with skew, use the frequency-product sum. Correlation between joined keys and filters creates another conditioning problem.

For example, if both inputs have ten rows over two equally frequent common keys, the join has $$2\cdot5\cdot5=50$$ rows. If one input instead has nine occurrences of the first key and one of the second, while the other has the reverse, the join has $$9\cdot1+1\cdot9=18$$ rows. Both inputs still have ten rows and two distinct keys, so the uniform estimate remains 50. The failure is invisible to those marginal counts.

## 10. Maintaining and selecting a synopsis

A complete characteristic-set build can scan triples to collect each subject's unique predicate set, then count identical sets. Expected linear work in triple count assumes appropriate hashing and a representation that avoids repeated expensive canonicalization; sorting-based implementations have different costs. Memory includes subject-to-set working state, keys, class counts, and any multiplicity statistics, not just the final number of characteristic sets.

For dynamic data, maintain a per-subject count for each predicate. Adding a second edge for an already present predicate changes multiplicity but not predicate presence. Deleting the last edge removes that predicate from the set and moves the subject to a different class. Class means must reflect both the move and remaining multiplicities. A periodic rebuild supplies a useful oracle for checking incremental maintenance on disposable data.

A budgeted summary should expose which queries retain exact distinct-star counts and which use merged or estimated information. An optimizer can then distinguish a proof-backed zero from a sampled zero or a stale approximation. Downstream cost need not vary monotonically with q-error: an estimate with a smaller numerical error can cross an operator-choice threshold in the wrong direction. Evaluate plan choices and query latency as well as the statistical metric.

## References and current scope

- [Characteristic sets, ICDE 2011](https://madoc.bib.uni-mannheim.de/29788/).
- [SPARQL 1.1 query semantics](https://www.w3.org/TR/sparql11-query/).
- [Accurate sampling for complex graph queries, TODS 2024](https://www.cs.ox.ac.uk/people/boris.motik/pubs/hm24-accurate-sampling.pdf).

The exact formula is now separated from every approximation. Historical storage and benchmark figures are not treated as universal properties of RDF data.
