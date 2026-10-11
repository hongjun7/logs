---
title: "Sampling-Based Cardinality Estimation: Unbiasedness, Consistency, and Complex Queries"
tags: ["databases", "cardinality", "probability"]
subtitle: "Derive inverse-probability estimates for joins, explain why DISTINCT changes the sample space, and separate asymptotic convergence from finite-budget accuracy."
last_modified_at: 2026-10-11
sources_checked_at: 2026-10-11
---

> **The idea in one minute.** A sampler does not need to enumerate every query answer. It can sample answers or derivations, track the probability of each outcome, and use inverse-probability weighting to estimate the total. The hard part is matching the sample space to the query's semantics, especially for projection, UNION, DISTINCT, and MINUS.

**Reading path.** Start with the unbiasedness proof and small join example. Then read the distinction between answers and derivations. The last sections discuss strong consistency, uncertainty, and query-planning cost. Prerequisites are expectation, variance, and relational joins.

## 1. Define exactly what is counted

Let $$Q$$ be a query on a fixed finite database $$I$$. Its answer can be a set of bindings or a bag whose binding $$\mu$$ has multiplicity $$m_Q(\mu)$$. Set cardinality is $$\vert \{\mu:m_Q(\mu)>0\}\vert $$; bag cardinality is

$$
N_Q=\sum_\mu m_Q(\mu).
$$

These differ after projection or unions. Query syntax is not enough; a sampling estimator must implement the corresponding semantics. The Hu–Motik work addresses complex graph queries through compositional evaluation and carefully weighted sampling, going beyond a simple conjunctive random walk. [Hu and Motik, TODS 2024](https://www.cs.ox.ac.uk/people/boris.motik/pubs/hm24-accurate-sampling.pdf).

## 2. Inverse-probability estimation

Suppose a single draw samples $$a$$ from finite set $$A$$ with known probability $$q(a)>0$$ for every $$a\in A$$. Define

$$
X=\frac1{q(a)}.
$$

Then

$$
\mathbb E[X]=\sum_{a\in A}q(a)\frac1{q(a)}=\vert A\vert .
$$

This is a with-replacement inverse-probability estimator, commonly associated with Hansen–Hurwitz sampling. Horvitz–Thompson instead samples a subset $$S$$ and weights each included element by its **inclusion probability** $$\pi_a=\Pr(a\in S)$$:

$$
\widehat N_{\mathrm{HT}}=\sum_{a\in S}\frac1{\pi_a}.
$$

Draw probabilities and inclusion probabilities are different quantities. For $$n$$ independent draws with replacement, $$\pi_a=1-(1-q(a))^n$$. Deduplicating sampled draws and continuing to weight by $$1/q(a)$$ would generally be biased.

A partition version is equally instructive. If $$A=A_1\uplus\cdots\uplus A_k$$ and we choose $$i$$ uniformly, $$X=k\vert A_i\vert $$ has expectation $$\vert A\vert $$. The disjointness is essential; overlapping subsets count some answers multiple times unless corrected.

## 3. WanderJoin and failed walks

Consider $$R(x,y)\Join S(y,z)$$. First choose a tuple from $$R$$ uniformly. Then choose uniformly among tuples in $$S$$ matching its $$y$$. If a first-stage tuple has degree $$d(y)>0$$, the path probability is

$$
q(r,s)=\frac1{\vert R\vert }\frac1{d(y)}.
$$

For one successful complete binding, use $$X=\vert R\vert d(y)$$. A walk with no match returns zero. Successful paths contribute one unit in expectation; failed paths contribute none. Keeping failures as zero-weight outcomes preserves the unconditional expectation. Retrying until success and treating accepted walks as original draws changes the distribution and requires renormalization.

### A small exact example

Let $$R$$ have two tuples. The first joins one tuple in $$S$$; the second joins three. There are four complete join bindings. With probability $$1/2$$ we get $$X=2$$, and with probability $$1/2$$ we get $$X=6$$:

$$
\mathbb E[X]=4,\qquad\operatorname{Var}(X)=4.
$$

The sample mean of $$n$$ independent walks has variance $$4/n$$. This is a full calculation for a toy database, not a claim about the variance of every graph query. A rare high-degree path can produce enormous weights and make finite-sample estimates unstable.

For a longer walk, multiply the conditional selection probabilities at every step. Closing an already bound cycle may be a Boolean existence test rather than a fresh random choice. Multiple derivations of the same projected binding require further care.

## 4. Why DISTINCT is difficult

Consider

```sparql
PREFIX : <urn:example:>
SELECT DISTINCT ?x WHERE { ?x :knows ?y }
```

A person with 100 neighbors has 100 derivations but contributes one distinct answer. A person with one neighbor has one derivation and also contributes one. An unbiased estimator of derivations is not an unbiased estimator of distinct subjects.

Let $$W_x$$ be the derivations mapping to answer $$x$$. If a draw over derivations has probabilities $$q(w)$$, the probability of answer $$x$$ is

$$
q_A(x)=\sum_{w\in W_x}q(w).
$$

Weighting a sampled answer by $$1/q_A(x)$$ would count distinct answers correctly when those probabilities are known and positive. But computing that sum may itself require difficult query work. This explains the need for more sophisticated query-aware sampling constructions rather than an after-the-fact `set()` on sampled bindings.

For bag `UNION`, multiplicities add: $$m_{A\cup B}(x)=m_A(x)+m_B(x)$$. For distinct union, set cardinality obeys $$\vert A\cup B\vert =\vert A\vert +\vert B\vert -\vert A\cap B\vert $$. Branch sampling must account for overlap and branch probabilities. It is not enough to average branch cardinalities and call the result a union size.

## 5. MINUS, filters, and side information

Filters may reject a sampled binding. If rejected outcomes remain in the sampling process with zero contribution and the probability calculation matches the process, unbiasedness can be retained. If rejection causes hidden retries, the accepted distribution changes.

SPARQL `MINUS` is not ordinary set difference over fully materialized tuples in all cases. Compatibility of partial solution mappings and their shared variable domains determines removal. A query estimator must reproduce those conditions, including the special treatment of disjoint variable domains. [SPARQL 1.1](https://www.w3.org/TR/sparql11-query/).

Sideways information passing means evaluating a subquery under bindings already produced elsewhere. It can shrink the eligible sampling population substantially. Any changed restriction also changes the probability of selecting an outcome. Memoization is valid only when its key includes every binding and semantic context affecting the result.

## 6. Strong consistency is an asymptotic statement

For independent identically distributed $$X_1,X_2,\ldots$$ with $$\mathbb E\vert X_1\vert <\infty$$ and $$\mathbb E X_1=N$$, the strong law gives

$$
\overline X_n=\frac1n\sum_{i=1}^{n}X_i
\xrightarrow[n\to\infty]{\mathrm{a.s.}}N.
$$

This means convergence with probability one as the sample count grows without bound. It does **not** mean a thousand samples are enough, a finite run cannot return zero, or a confidence interval is automatically reliable under severe skew.

For a fixed finite sample space with strictly positive selection probabilities, inverse-probability weights are bounded, so the integrability condition holds. That theoretical bound can still be too large to give useful finite-budget concentration. Adaptive samplers need their own conditions; iid arguments do not transfer unchanged when probabilities are updated using prior samples.

## 7. Variance, confidence, and stopping

For iid draws with finite variance, estimate

$$
s_n^2=\frac1{n-1}\sum_i(X_i-\overline X_n)^2,
\qquad\widehat{\operatorname{SE}}(\overline X_n)=\frac{s_n}{\sqrt n}.
$$

A normal-approximation interval may be useful at large sample sizes with a well-behaved distribution, but it is fragile when nearly all walks fail and rare huge weights dominate. An observed variance of zero after all-zero samples is not proof that the true count is zero.

Repeatedly stopping when an ordinary fixed-sample interval first looks narrow can invalidate its nominal coverage. Use a justified sequential procedure or reserve an independent evaluation budget. Report sampler support, failures, effective budget, and heavy-tail diagnostics rather than only a point estimate.

When two plans for the same subexpression give estimates, disagreement can indicate variance, probability-accounting mistakes, or different semantics. Store the logical subexpression, context bindings, database revision, and random seed with cached results.

## 8. The estimator must pay for itself

An optimizer can request hundreds of subquery estimates. Total latency is

$$
T_{\mathrm{total}}=T_{\mathrm{statistics}}+T_{\mathrm{planning}}+T_{\mathrm{execution}}.
$$

More accurate estimates are beneficial only when the execution gain justifies the added planning cost for the workload. Estimate reuse, indexed restricted scans, pilot sampling, and order selection can reduce the budget. All are engineering choices whose correctness still depends on probability accounting.

Compare q-error distributions, false-zero rates, planning time, final query time, and worst regressions against both synopsis methods and simple sampling. Stratify results by query shape, cardinality, and skew. Averages alone can hide a small group of catastrophic plans.

## 9. Derive the variance and the ideal proposal

For a finite answer set $$A$$ of size $$N$$ with positive draw probabilities $$q(a)$$, the inverse-probability variable has

$$
\mathbb E[X^2]=\sum_{a\in A}\frac1{q(a)},
\qquad
\operatorname{Var}(X)=\sum_{a\in A}\frac1{q(a)}-N^2.
$$

Cauchy–Schwarz applied to vectors $$\sqrt{q(a)}$$ and $$1/\sqrt{q(a)}$$ gives

$$
N^2\le\left(\sum_aq(a)\right)\left(\sum_a\frac1{q(a)}\right).
$$

Equality occurs at uniform $$q(a)=1/N$$, when $$X=N$$ on every draw and variance is zero. The apparent ideal hides the hard part: sampling uniformly from query answers and knowing $$1/N$$ can require work comparable to the query itself.

For the two-first-tuple join example, selecting an initial tuple proportionally to its join degree and then uniformly selecting a neighbor makes all four complete paths equally likely. The inverse probability becomes four on every draw. This is exact after degrees and their total have been computed; it is not a free way to discover that total. A good proposal balances the cost of constructing sampling information against the reduction in variance.

If failed walks absorb probability mass, denote successful path probabilities by $$q(a)$$ and keep failure weight zero. The second-moment formula remains $$\sum_a1/q(a)$$, but $$\sum_aq(a)\le1$$. Rare success can make variance enormous. If any valid answer has probability zero, the expectation omits it; no number of samples can repair missing support.

## 10. A finite bound is only as good as its weight bound

Suppose every successful probability is at least $$q_{\min}>0$$, and failures have weight zero. Then $$0\le X\le M=1/q_{\min}$$. For independent draws, Hoeffding's inequality gives

$$
\Pr(\vert \overline X_n-N\vert \ge\epsilon)
\le2\exp\left(-\frac{2n\epsilon^2}{M^2}\right).
$$

A sufficient budget for failure probability at most $$\delta$$ is

$$
n\ge\frac{M^2}{2\epsilon^2}\log\frac2\delta.
$$

This controls **absolute** error. Setting $$\epsilon=\eta N$$ for relative error requires knowing or lower-bounding the unknown $$N$$. A mathematically finite $$M$$ may be huge, making the sufficient bound unusable in practice. Report the observed weight distribution and the worst-case support bound rather than equating strong consistency with a useful latency budget.

An adaptive proposal $$q_t$$ chosen from past information can still satisfy $$\mathbb E[X_t\mid\mathcal F_{t-1}]=N$$ when probability accounting is exact and every answer remains supported. This conditional identity is a martingale property, not independence. Concentration or almost-sure convergence needs an applicable martingale theorem and its moment/boundedness assumptions; it cannot be justified by copying the iid proof.

## 11. Distinct answers: a numerical support example

Suppose person A has 100 neighbors and person B has one. Sampling uniformly from the 101 edges gives answer probabilities $$q_A(A)=100/101$$ and $$q_A(B)=1/101$$. Correct distinct-answer weights are $$101/100$$ and $$101$$. Their expected value is

$$
\frac{100}{101}\frac{101}{100}+\frac1{101}101=2.
$$

By contrast, using the edge-path weight 101 gives expectation 101, the number of derivations. Merely retaining distinct values in a finite sampled batch gives a third statistic: the number of subjects observed, which is at most two and has a sample-size-dependent expectation. These three calculations count different populations.

For a subset-based Horvitz–Thompson estimator, variance also depends on pairwise inclusion probabilities $$\pi_{ab}=\Pr(a,b\in S)$$:

$$
\operatorname{Var}(\widehat N_{\mathrm{HT}})
=\sum_{a,b}\frac{\pi_{ab}-\pi_a\pi_b}{\pi_a\pi_b},
\qquad\pi_{aa}=\pi_a.
$$

Derive it by expanding the variance of $$\sum_a\mathbf1\{a\in S\}/\pi_a$$. Sampling without replacement introduces dependence between inclusion indicators. Treating them as independent generally misstates uncertainty even though the estimator's expectation is correct.

These distinctions explain why a complex query sampler must specify its elementary outcomes, derivation-to-answer map, failed branches, and all relevant probabilities. The probabilistic proof is part of the operator's implementation contract.

## References and current scope

- [Hu and Motik, Accurate Sampling-Based Cardinality Estimation for Complex Graph Queries](https://www.cs.ox.ac.uk/people/boris.motik/pubs/hm24-accurate-sampling.pdf).
- [Wander Join, SIGMOD 2016](https://doi.org/10.1145/2882903.2915235).
- [G-CARE benchmark](https://github.com/yspark-dblab/gcare).
- [SPARQL 1.1 query semantics](https://www.w3.org/TR/sparql11-query/).

The derivations above explain the foundation; they are not a substitute implementation of every operator in the 2024 paper. An estimator inherits that paper's guarantees only after its sampling construction and assumptions are faithfully implemented.
