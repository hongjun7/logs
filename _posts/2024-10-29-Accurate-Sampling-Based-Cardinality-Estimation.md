---
lang: en
translation_key: 2024-10-29-Accurate-Sampling-Based-Cardinality-Estimation
translation_url: /ko/2024/10/29/Accurate-Sampling-Based-Cardinality-Estimation.html
title: "Sampling-Based Cardinality Estimation"
tags: ["databases", "cardinality", "probability"]
subtitle: "Inverse probabilities, query semantics, and finite-sample uncertainty."
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-11
---

Inverse-probability weighting estimates a query's answer count without enumerating every answer. The estimator samples outcomes and weights them by their probabilities. Its correctness depends on what those outcomes represent: derivations, projected answers, and distinct answers are different populations.

## Set and bag counts
{: id="1-define-exactly-what-is-counted"}

For query $$Q$$ on a fixed finite database $$I$$, binding $$\mu$$ has multiplicity $$m_Q(\mu)$$. Set cardinality is $$\vert \{\mu:m_Q(\mu)>0\}\vert $$; bag cardinality is

$$
N_Q=\sum_\mu m_Q(\mu).
$$

Projection and union separate these counts. Hu and Motik handle complex graph queries through compositional evaluation and weighted sampling, beyond a conjunctive random walk. The sampling construction must implement each operator's semantics. [Hu and Motik, TODS 2024](https://www.cs.ox.ac.uk/people/boris.motik/pubs/hm24-accurate-sampling.pdf).

## Inverse probabilities
{: id="2-inverse-probability-estimation"}

Draw $$a$$ from finite set $$A$$, knowing $$q(a)>0$$ for every $$a\in A$$. Define

$$
X=\frac1{q(a)}.
$$

Then

$$
\mathbb E[X]=\sum_{a\in A}q(a)\frac1{q(a)}=\vert A\vert .
$$

This with-replacement estimator is associated with Hansen–Hurwitz sampling. Horvitz–Thompson instead samples a subset $$S$$ and uses each element's inclusion probability $$\pi_a=\Pr(a\in S)$$:

$$
\widehat N_{\mathrm{HT}}=\sum_{a\in S}\frac1{\pi_a}.
$$

After $$n$$ independent replacement draws, $$\pi_a=1-(1-q(a))^n$$. Removing duplicates while keeping weights $$1/q(a)$$ generally introduces bias: inclusion and per-draw probabilities differ.

For a partition $$A=A_1\uplus\cdots\uplus A_k$$, choosing $$i$$ uniformly gives $$X=k\vert A_i\vert $$ with expectation $$\vert A\vert $$. Overlap would count answers repeatedly unless corrected.

## Random-walk joins
{: id="3-wanderjoin-and-failed-walks"}

For $$R(x,y)\Join S(y,z)$$, first sample a tuple uniformly from $$R$$, then a matching tuple uniformly from $$S$$ using its $$y$$. At degree $$d(y)>0$$, the path probability is

$$
q(r,s)=\frac1{\vert R\vert }\frac1{d(y)}.
$$

A successful binding gets weight $$X=\vert R\vert d(y)$$; a failed walk gets zero. Each successful path contributes one in expectation. Keeping failures preserves the unconditional expectation, whereas retrying until success changes the distribution and needs renormalization.

### Two starting tuples
{: id="a-small-exact-example"}

Suppose $$R$$ has two tuples, joining respectively one and three tuples in $$S$$. The four complete bindings give probability $$1/2$$ of $$X=2$$ and probability $$1/2$$ of $$X=6$$:

$$
\mathbb E[X]=4,\qquad\operatorname{Var}(X)=4.
$$

The mean of $$n$$ independent walks has variance $$4/n$$. This toy calculation does not bound every query's variance; rare high-degree paths can dominate the weights.

Longer walks multiply conditional probabilities. Closing an already bound cycle can be an existence test rather than another random selection. Multiple paths to one projected answer need separate accounting.

## DISTINCT and UNION
{: id="4-why-distinct-is-difficult"}

Consider

```sparql
PREFIX : <urn:example:>
SELECT DISTINCT ?x WHERE { ?x :knows ?y }
```

A person with 100 neighbors has 100 derivations but one distinct answer; one neighbor gives one derivation and the same distinct contribution. Unbiased derivation counts do not guarantee unbiased distinct-subject estimates.

Let $$W_x$$ contain derivations for answer $$x$$. Under path probabilities $$q(w)$$, answer $$x$$ has probability

$$
q_A(x)=\sum_{w\in W_x}q(w).
$$

Weight $$1/q_A(x)$$ counts distinct answers correctly when known and positive, but calculating the sum can itself require substantial query work. A later `set()` does not supply these probabilities.

Bag `UNION` adds multiplicities, $$m_{A\cup B}(x)=m_A(x)+m_B(x)$$, while distinct union obeys $$\vert A\cup B\vert =\vert A\vert +\vert B\vert -\vert A\cap B\vert $$. Branch probabilities and overlap matter; averaging branch counts does not compute their union.

## Filters and context
{: id="5-minus-filters-and-side-information"}

A rejected binding can retain zero contribution when probability accounting matches the process. Hidden retries instead change the accepted distribution.

SPARQL `MINUS` removes compatible partial mappings according to their shared variable domains, with special treatment of disjoint domains. It is not always ordinary difference over complete tuples. [SPARQL 1.1](https://www.w3.org/TR/sparql11-query/).

Sideways information passing evaluates a subquery under bindings obtained elsewhere. This can shrink the sampling population and change selection probabilities. Memoization keys must include every binding and semantic context affecting the result.

## Strong consistency
{: id="6-strong-consistency-is-an-asymptotic-statement"}

For independent, identically distributed (iid) $$X_1,X_2,\ldots$$ satisfying $$\mathbb E\vert X_1\vert <\infty$$ and $$\mathbb E X_1=N$$, the strong law gives

$$
\overline X_n=\frac1n\sum_{i=1}^{n}X_i
\xrightarrow[n\to\infty]{\mathrm{a.s.}}N.
$$

This is probability-one convergence as samples grow without bound, not a guarantee that a thousand samples suffice. A finite run can return zero, and severe skew can undermine a confidence interval.

Positive probabilities on a fixed finite sample space bound inverse weights and establish integrability. The bound may still be too large for useful finite-budget concentration. Updating probabilities from previous samples requires an adaptive argument rather than the unchanged iid proof.

## Uncertainty and stopping
{: id="7-variance-confidence-and-stopping"}

For iid draws with finite variance,

$$
s_n^2=\frac1{n-1}\sum_i(X_i-\overline X_n)^2,
\qquad\widehat{\operatorname{SE}}(\overline X_n)=\frac{s_n}{\sqrt n}.
$$

Normal approximation can work for large, well-behaved samples. It is fragile when almost all walks fail and rare weights dominate; all-zero observations and zero sample variance do not prove an empty answer.

Stopping when an ordinary fixed-sample interval first becomes narrow can invalidate nominal coverage. A justified sequential procedure or independent evaluation budget avoids treating that rule as fixed-sample inference. Support, failures, effective budget, and heavy tails affect interpretation.

Disagreement between plans estimating one subexpression can reflect variance, incorrect probabilities, or changed semantics. Cached estimates need their logical subexpression, context bindings, database revision, and seed.

## Planning cost
{: id="8-the-estimator-must-pay-for-itself"}

An optimizer may request hundreds of subquery estimates. Total latency is

$$
T_{\mathrm{total}}=T_{\mathrm{statistics}}+T_{\mathrm{planning}}+T_{\mathrm{execution}}.
$$

More accurate estimates help only when execution savings justify the extra planning work. Reuse, indexed restricted scans, pilot sampling, and order selection can reduce cost while retaining correct probability accounting.

Compared with synopses and simple sampling, q-error, false-zero rate, planning time, final query time, and worst regressions expose different tradeoffs. Query shape, answer count, and skew can separate a catastrophic minority from an acceptable average.

## Variance and proposal design
{: id="9-derive-the-variance-and-the-ideal-proposal"}

For finite answer set $$A$$ of size $$N$$ and positive probabilities $$q(a)$$,

$$
\mathbb E[X^2]=\sum_{a\in A}\frac1{q(a)},
\qquad
\operatorname{Var}(X)=\sum_{a\in A}\frac1{q(a)}-N^2.
$$

Cauchy–Schwarz on $$\sqrt{q(a)}$$ and $$1/\sqrt{q(a)}$$ gives

$$
N^2\le\left(\sum_aq(a)\right)\left(\sum_a\frac1{q(a)}\right).
$$

Equality holds at $$q(a)=1/N$$, where every draw returns $$X=N$$ and variance vanishes. Sampling answers uniformly and knowing $$1/N$$ can, however, cost as much as the query.

In the two-tuple example, sampling the starting tuple proportionally to join degree and then a neighbor uniformly gives all four paths equal probability and weight four. This requires computing the degrees and their total; the variance reduction has a construction cost.

With failure mass, successful paths have probabilities $$q(a)$$ and failure weight zero. The second moment remains $$\sum_a1/q(a)$$ but $$\sum_aq(a)\le1$$, so rare success can inflate variance. An answer with zero probability never enters the expectation, however many samples are taken.

## Finite error bounds
{: id="10-a-finite-bound-is-only-as-good-as-its-weight-bound"}

If successful probabilities are at least $$q_{\min}>0$$ and failures weigh zero, then $$0\le X\le M=1/q_{\min}$$. Independent draws satisfy Hoeffding's bound

$$
\Pr(\vert \overline X_n-N\vert \ge\epsilon)
\le2\exp\left(-\frac{2n\epsilon^2}{M^2}\right).
$$

An error-bound violation probability at most $$\delta$$ is ensured by

$$
n\ge\frac{M^2}{2\epsilon^2}\log\frac2\delta.
$$

This controls absolute error. Relative error via $$\epsilon=\eta N$$ requires the unknown $$N$$ or a lower bound. A huge finite $$M$$ can make the sufficient budget impractical; strong consistency alone supplies no useful latency guarantee.

An adaptive proposal $$q_t$$ based on past information can satisfy $$\mathbb E[X_t\mid\mathcal F_{t-1}]=N$$ with exact probability accounting and full support. This is a martingale property, not independence. Concentration and almost-sure convergence require an applicable martingale theorem with its moment or boundedness assumptions.

## Distinct-answer weights
{: id="11-distinct-answers-a-numerical-support-example"}

Person A has 100 neighbors and B has one. Uniform sampling of the 101 edges gives $$q_A(A)=100/101$$ and $$q_A(B)=1/101$$. The distinct-answer weights $$101/100$$ and $$101$$ have expectation

$$
\frac{100}{101}\frac{101}{100}+\frac1{101}101=2.
$$

Edge-path weight 101 instead has expectation 101, counting derivations. Deduplicating a finite batch measures observed subjects, at most two, with expectation depending on sample size. These are three different statistics.

For subset-based Horvitz–Thompson sampling, pairwise inclusion probabilities $$\pi_{ab}=\Pr(a,b\in S)$$ give

$$
\operatorname{Var}(\widehat N_{\mathrm{HT}})
=\sum_{a,b}\frac{\pi_{ab}-\pi_a\pi_b}{\pi_a\pi_b},
\qquad\pi_{aa}=\pi_a.
$$

Expanding the variance of $$\sum_a\mathbf1\{a\in S\}/\pi_a$$ yields this formula. Without-replacement inclusion indicators are dependent, so an independence assumption can misstate uncertainty despite an unbiased expectation.

A complex-query sampler therefore needs specified outcomes, derivation-to-answer mappings, failures, and probabilities. These foundations do not implement every operator in the 2024 paper; its guarantees require the corresponding construction and assumptions.

## References
{: id="references-and-current-scope"}

- [Hu and Motik, Accurate Sampling-Based Cardinality Estimation for Complex Graph Queries](https://www.cs.ox.ac.uk/people/boris.motik/pubs/hm24-accurate-sampling.pdf).
- [Wander Join, SIGMOD 2016](https://doi.org/10.1145/2882903.2915235).
- [G-CARE](https://github.com/yspark-dblab/gcare).
- [SPARQL 1.1 semantics](https://www.w3.org/TR/sparql11-query/).
