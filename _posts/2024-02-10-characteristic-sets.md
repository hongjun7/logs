---
lang: en
translation_key: 2024-02-10-characteristic-sets
translation_url: /ko/2024/02/10/characteristic-sets.html
title: "Characteristic Sets"
tags: ["knowledge-graphs", "databases", "cardinality"]
subtitle: "Predicate co-occurrence, exact star counts, and cardinality estimation."
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-11
---

A characteristic set records which predicates occur for a subject. This captures co-occurrence, such as books having both authors and titles. Complete counts answer restricted distinct-subject star queries exactly; multiplicities, constants, joins, and compression require more information.

## Cardinality and planning
{: id="1-why-an-optimizer-needs-cardinality"}

A planner uses cardinality to choose join order and operators. A filter reducing a million rows to ten can save substantial intermediate work when applied early.

RDF graphs are sets of triples, but SPARQL generally returns a multiset of solution mappings. Full bindings, projected rows, and distinct values have different counts; `SELECT DISTINCT` changes the target.

## Characteristic-set partitions
{: id="2-the-characteristic-set-partition"}

For a finite RDF graph $$R$$ with subjects $$U_R$$, define

$$
C(s)=\{p:\exists o\;(s,p,o)\in R\},\qquad
n_C=\vert \{s\in U_R:C(s)=C\}\vert .
$$

The subject groups indexed by $$C$$ form a disjoint partition. A star with predicate set $$P=\{p_1,\ldots,p_k\}$$ includes queries such as

```sparql
PREFIX : <urn:example:>
SELECT DISTINCT ?s WHERE {
  ?s :author ?a .
  ?s :title  ?t .
}
```

With fresh unrestricted object variables, no filters, and no other shared variables, a subject matches exactly when $$P\subseteq C(s)$$. Hence

$$
N_{\mathrm{distinct}}(P)=\sum_{C\supseteq P}n_C.
$$

Each required predicate must have an outgoing edge. Set containment states precisely that condition, and each subject belongs to one class, so the sum counts it once. Bounded objects, shared object variables, arbitrary joins, or merged classes do not retain this guarantee. [Neumann and Moerkotte, 2011](https://madoc.bib.uni-mannheim.de/29788/).

## Binding multiplicities
{: id="3-full-bindings-require-multiplicities"}

The outgoing multiplicity is

$$
m_p(s)=\vert \{o:(s,p,o)\in R\}\vert .
$$

For independent object variables without duplicate elimination, the full binding count is

$$
N_{\mathrm{bag}}(P)=\sum_{s:P\subseteq C(s)}\prod_{p\in P}m_p(s).
$$

Each variable selects an outgoing value independently; the product counts one subject's combinations. Projection without `DISTINCT` retains the resulting repeated rows.

A compact synopsis stores total occurrences $$o_{C,p}=\sum_{s:C(s)=C}m_p(s)$$ and mean multiplicities $$\bar m_{C,p}=o_{C,p}/n_C$$, giving

$$
\widehat N_{\mathrm{bag}}(P)=\sum_{C\supseteq P}n_C\prod_{p\in P}\bar m_{C,p}.
$$

This replaces an average of products with a product of averages, assuming away multiplicity correlations within a class.

Identical predicate presence does not imply identical outgoing counts. The synopsis preserves the former exactly while its mean-based approximation collapses the latter into one average per predicate.

### Correlation example
{: id="a-worked-counterexample"}

Two subjects with characteristic set `{author, title}` have multiplicities $$(1,1)$$ and $$(3,3)$$. Their true count is $$1\cdot1+3\cdot3=10$$. Both means equal $$2$$, yielding $$2\cdot2\cdot2=8$$. For a uniformly chosen subject in the class,

$$
\mathbb E[m_p m_q]
=\mathbb E[m_p]\mathbb E[m_q]+\operatorname{Cov}(m_p,m_q).
$$

The omitted contribution is $$n_C\operatorname{Cov}(m_p,m_q)$$. Reversing the pairs to $$(1,3)$$ and $$(3,1)$$ gives true count $$6$$ but estimate $$8$$, reversing the error's direction. Predicate-presence correlations therefore do not determine multiplicity correlations.

Repeated predicates with separate object variables introduce powers such as $$m_p(s)^2$$; a shared object variable instead imposes equality. Both differ from two independent predicates.

## Constants and shared variables
{: id="4-constants-and-shared-variables"}

`?s :author :Ada` requires Ada, not merely an author. The indicator

$$
b_{p,o}(s)=\mathbf1\{(s,p,o)\in R\}.
$$

supports exact distinct-subject counts through sums of indicator products. A global Ada frequency can miss correlations with classes, years, or other constants.

A probability such as $$\Pr(O=o\mid P=p)$$ needs a defined sampling universe and positive conditioning probability. Uniform triple sampling overrepresents high-degree subjects, so triple frequency is not automatically subject probability.

For `?s :author ?x . ?s :editor ?x`, separate multiplicities are insufficient; the answer count uses

$$
\sum_s \vert \operatorname{Authors}(s)\cap\operatorname{Editors}(s)\vert .
$$

This requires object-set overlap, beyond predicate co-occurrence.

## Compression
{: id="5-compression-changes-the-guarantee"}

With $$d$$ possible predicates, up to $$2^d$$ sets exist. Storage limits may force rare classes to merge. Counting `{author}` inside `{author, title}` creates false matches for a two-predicate star; splitting a true joint class into single-predicate summaries loses co-occurrence.

Neither error direction is inherently harmless. Overestimation can change join order, memory reservations, and operators; underestimation can select nested loops for large intermediates. Counts need an exact/merged/sampled/stale status. Adding a subject's first `title` edge or deleting its last moves the subject between classes; predicate totals alone cannot maintain the partition.

## Multi-star joins
{: id="6-join-estimation-beyond-one-star"}

For relational inputs $$R_1,\ldots,R_m$$ and join predicates $$e$$, an explicit independence approximation has the form

$$
\widehat N=\left(\prod_{i=1}^{m}\vert R_i\vert \right)
\left(\prod_{e}\widehat{\operatorname{sel}}(e)\right).
$$

Selectivities multiply. The formula assumes compatible sampling universes and independence, not correlated joins. A synopsis for a correlated predicate group replaces that group's factors; overlapping synopses risk counting a correlation or population twice.

Equivalent logical queries have the same true cardinality regardless of physical order. Reusing one logical-subexpression estimate avoids separate approximate calls disagreeing while physical plans are compared.

## Evaluation
{: id="7-evaluating-an-estimator-today"}

For positive actual and estimated counts,

$$
q\text{-error}=\max\left(\frac{\widehat N}{N},\frac{N}{\widehat N}\right).
$$

An estimate of $$80$$ for true count $$100$$ has q-error $$1.25$$. Zero needs an explicit policy: replacing it with one hides false-empty predictions. Useful measurements include empty-query detection, median/tail q-error, build/storage cost, estimate latency, and final query latency.

Complete and budgeted characteristic sets, sampling, and native statistics can be compared on the same snapshot, covering stars, cycles, constants, repeated predicates, skew, and update drift. [Complex-query sampling](https://www.cs.ox.ac.uk/people/boris.motik/pubs/hm24-accurate-sampling.pdf) addresses operators outside a simple star synopsis.

## Higher-order correlations
{: id="8-pairwise-independence-is-insufficient-for-a-three-predicate-star"}

For three multiplicities $$X,Y,Z$$ in one class, expansion around their means gives

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

Means and pairwise covariances omit the centered third-order term. Four equally weighted subjects with multiplicities $$(1,1,1),(1,2,2),(2,1,2),(2,2,1)$$ all have positive values and can share one characteristic set. Every pair is independent, with mean $$3/2$$ and zero covariance.

The exact count is $$1+4+4+4=13$$, while the product-of-means estimate is $$4(3/2)^3=13.5$$. The mean product $$13/4$$ differs from the product of means $$27/8$$ by $$-1/8$$. Pairwise independence therefore does not establish mutual independence; more marginal statistics need not recover the joint distribution.

## Equijoin estimates
{: id="9-derive-a-conventional-equijoin-estimate"}

Let $$f_R(v)$$ and $$f_S(v)$$ be the frequencies of join key $$v$$ in two relations. The true bag join size is

$$
N_{R\Join S}=\sum_v f_R(v)f_S(v).
$$

Under uniform keys in domains $$D_R,D_S$$ of sizes $$V_R,V_S$$, containment of the smaller domain gives $$\min(V_R,V_S)$$ common keys. Thus

$$
\widehat N=
\min(V_R,V_S)\frac{\vert R\vert }{V_R}\frac{\vert S\vert }{V_S}
=\frac{\vert R\vert \vert S\vert }{\max(V_R,V_S)}.
$$

The estimate requires uniformity and containment, not just distinct-value counts. Partial overlap changes the common-key factor; skew requires the frequency-product sum. Filters correlated with the key introduce further conditioning.

Two ten-row inputs with two equally frequent shared keys join to $$2\cdot5\cdot5=50$$ rows. If their frequencies become nine/one and one/nine, the join has $$9\cdot1+1\cdot9=18$$ rows. Both still have ten rows and two distinct keys, so the uniform estimate stays 50 and misses the skew.

## Maintenance
{: id="10-maintaining-and-selecting-a-synopsis"}

A complete build collects each subject's unique predicates and counts identical sets. Expected linear work assumes suitable hashing without repeated expensive canonicalization; sorting has different costs. Memory includes subject working state, keys, class counts, and multiplicity statistics.

Per-subject predicate counts distinguish another edge from the first or last edge. A second edge changes multiplicity only; removing the last changes the set and class. Class means must include moves and remaining multiplicities. Rebuilding provides an oracle for incremental maintenance on disposable data.

A budgeted synopsis can expose which distinct-star counts remain exact. This separates proof-backed zeros from sampled zeros or stale estimates. Lower q-error need not lower execution cost: a smaller error can cross an operator threshold in the wrong direction. Plan choices and latency remain part of evaluation; historical storage and benchmark figures are not universal RDF properties.

Exactness belongs to a query shape and the retained statistics, rather than to the characteristic-set label alone. Compression or added query constraints can change it.

## References
{: id="references-and-current-scope"}

- [Characteristic sets, ICDE 2011](https://madoc.bib.uni-mannheim.de/29788/).
- [SPARQL 1.1 semantics](https://www.w3.org/TR/sparql11-query/).
- [Accurate sampling, TODS 2024](https://www.cs.ox.ac.uk/people/boris.motik/pubs/hm24-accurate-sampling.pdf).
