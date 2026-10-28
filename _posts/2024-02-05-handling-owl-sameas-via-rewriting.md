---
lang: en
translation_key: 2024-02-05-handling-owl-sameas-via-rewriting
translation_url: /ko/2024/02/05/handling-owl-sameas-via-rewriting.html
title: "Reasoning with owl:sameAs"
tags: ["knowledge-graphs", "logic", "owl"]
subtitle: "Equality closure through representatives, rule rewriting, and query expansion."
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-11
---

`owl:sameAs` identifies different names for one individual. Expanding every equivalent name into every fact can be expensive. Rewriting compresses this equality closure into representatives, while preserving rule consequences and the multiplicities of query answers.

## Representatives
{: id="1-names-individuals-and-equivalence-classes"}

An RDF graph contains triples $$(s,p,o)$$. Equality facts generate an equivalence relation $$a\sim b$$, whose reflexive, symmetric, and transitive closure defines

$$
[a]=\{b:b\sim a\}.
$$

A representative map $$\rho$$ satisfies

$$
a\sim b\iff\rho(a)=\rho(b),\qquad\rho(\rho(a))=\rho(a).
$$

The second condition is idempotence. Applying $$\rho$$ to each triple component and rule constant replaces equivalent names with one representative. If `:US`, `:USA`, and `:America` are equal, the store can retain `(:person, :livesIn, :US)` once.

The representative is a storage choice: the external vocabulary still contains every name. Quotienting changes which triples are stored, not which names the expanded graph exposes.

Unlike similarity, `owl:sameAs` permits substitution of equal individuals. Substitution in predicate positions depends on the selected RDF-based rules. The treatment here follows the rewriting paper and [OWL 2 RL/RDF](https://www.w3.org/TR/owl2-profiles/); syntax-sensitive RDF-term operations need separate handling. This is rule materialization with equality, not arbitrary OWL reasoning reduced to union–find.

## Expansion size
{: id="2-where-the-explosion-comes-from"}

A class of $$k$$ names yields $$k^2$$ ordered equality pairs, including self-pairs. If a triple's subject, predicate, and object classes have sizes $$k_s,k_p,k_o$$, substitution can yield up to

$$
k_s k_p k_o
$$

syntactic triples. Rule firings also depend on duplicate suppression, scheduling, and the rule set.

With `:alice` and `:a` in one class and the three country names in another, one normalized `livesIn` fact represents $$2\cdot1\cdot3=6$$ triples. The quotient stores that fact and class membership; its external answers can still contain all six combinations.

Path compression and union by rank give $$m$$ union/find operations on $$n$$ items amortized cost $$O(m\alpha(n))$$. This excludes fact rewriting, index updates, and rule reevaluation, which can dominate reasoning.

## Rewriting rules
{: id="3-why-preprocessing-is-insufficient"}

Rules can derive new equalities:

```text
sameAs(x, :USA) :- presidentOf(:person, x).
leader(x)      :- presidentOf(x, :USA).
```

`presidentOf(:person, :US)` derives `sameAs(:US, :USA)`. If `:US` becomes representative, the second rule's `:USA` must also become `:US`, either by rewriting or dynamic normalization. Otherwise fact rewriting hides a valid match.

New equalities enable matches that may derive further equalities. Normalization and materialization therefore advance together. One-time preprocessing suffices only when all required equivalences are already known and cannot change under the program.

## Correctness invariants
{: id="4-the-central-invariants"}

Let $$E$$ be the input facts and $$P$$ a finite, safe, function-free positive program with the selected equality rules. Its materialization is a least fixpoint. A compact engine maintains normalized facts $$T$$ and representatives $$\rho$$, with substitution expansion

$$
\operatorname{expand}_\rho(T)
=\{(s,p,o): (\rho(s),\rho(p),\rho(o))\in T\}.
$$

The engine must recover the relevant explicit-materialization consequences; equality facts and inconsistency handling also follow its chosen conventions.

A merge can leave old representatives in facts and constants simultaneously. Until the pending rewrites finish, matching must distinguish those stale versions from the live normalized view.

After a merge, live facts, rule constants, and matching indexes must eventually use current representatives. Changed rules must run against existing facts, and every newly enabled rule instance must eventually run. Soundness requires each normalized derivation to expand to an original consequence. Completeness follows by induction on explicit derivations, using represented premises, normalized constants, and fair reevaluation.

The finite domain bounds ground facts, and merges reduce the class count at most $$n-1$$ times. Fair finite rule processing therefore terminates. This argument does not establish race freedom for a concurrent implementation.

## Parallel evaluation
{: id="5-parallel-materialization"}

Motik et al. combine fact processing with queues for changed resources and rewritten rules. Outdated facts may be marked instead of removed, so matching must ignore them. Merges coordinate representatives, occurrence indexes, and pending work. These synchronization choices do not imply that all equality reasoners are lock-free. [Rewriting algorithm](https://ojs.aaai.org/index.php/AAAI/article/view/9187).

```text
take pending fact or equality update
normalize it with the current representative map
if it merges classes:
    enqueue affected facts and affected rule constants
otherwise:
    apply matching rules and enqueue new facts
repeat until all work, including rule reindexing, is complete
```

Termination requires both empty queues and no active worker or delayed update able to publish more work. Deletion is a separate problem: an existing class may have to split rather than merely undergo another union.

## SPARQL multiplicities
{: id="6-sparql-set-and-bag-semantics"}

Suppose a normalized `livesIn` fact has two subject names and three object names.

```sparql
PREFIX : <urn:example:>
SELECT ?s WHERE { ?s :livesIn ?country }
```

The expanded graph returns each subject three times: six rows. Projecting the normalized match before expanding only the subject returns two, losing the multiplicity of the hidden variable.

When each variable independently selects a class member, a normalized binding $$\nu$$ expands with multiplicity

$$
\prod_{x\in\operatorname{vars}(Q)}\vert [\nu(x)]\vert .
$$

Repeated variables, constants, filters, joins, and prior expansion constrain those choices. `SELECT DISTINCT ?s` instead returns the two distinct subjects.

Syntax-sensitive builtins need expansion before evaluation:

```sparql
PREFIX : <urn:example:>
SELECT ?label WHERE {
  ?s :livesIn :US .
  BIND(STR(?s) AS ?label)
}
```

`STR(:alice)` and `STR(:a)` differ even when the names denote one individual. Normalizing strings afterward cannot recover the lost lexical distinction. [SPARQL semantics](https://www.w3.org/TR/sparql11-query/).

## Inconsistency
{: id="7-inconsistency-and-practical-use"}

Equality closure can identify resources asserted different. An engine may report the contradiction rather than materialize classical explosion; its query behavior on inconsistent data needs a separate definition.

Rewriting is useful when substitution materially enlarges closure. Its effect is measured through normalized facts, expanded answer counts, wall time, memory, and update cost, including projection and filter behavior. A historical speedup need not persist on a graph with few equalities.

## Least fixpoint
{: id="8-a-least-fixpoint-view-of-positive-rules"}

On a finite ground universe, the inflationary immediate-consequence operator is

$$
T_P(S)=E\cup S\cup\{h\sigma:
(h\leftarrow b_1,\ldots,b_m)\in P,
\;b_i\sigma\in S\text{ for all }i\}.
$$

Here $$\sigma$$ substitutes domain terms for variables. Safety and the function-free finite domain keep grounding finite. Positivity gives monotonicity: when $$S\subseteq S'$$, every instance applicable in $$S$$ remains applicable in $$S'$$. From $$E$$, the chain $$S_{k+1}=T_P(S_k)$$ stabilizes at the least fixpoint containing $$E$$.

Rewriting stores a changing quotient of this process. Merging two constants can make a failed join succeed without inserting an ordinary fact. Rule and index reevaluation must therefore account for merges, not assume a fixed normalized program.

Semi-naive evaluation avoids repeated derivations by joining with newly added facts. Equality rewriting must also process changed classes and rule constants; an ordinary fact-insertion delta alone can miss consequences.

## Lexical identity
{: id="9-lexical-identity-and-semantic-equality-are-distinct"}

Equal names `:alice` and `:a` remain distinct RDF IRIs.

```sparql
PREFIX : <urn:example:>
SELECT ?x ?y WHERE {
  ?x :relatedTo ?y .
  FILTER(!sameTerm(?x, ?y))
}
```

An expanded self-relation can contain both equal-term and different-term pairs. Filtering the representative pair first discards valid different-term pairs. The engine must delay the filter, expand the relevant variables, or compute an equivalent symbolic result.

Repeated variables impose one assignment: `?x :relatedTo ?x` chooses one name for `?x`. For a two-member class with all expanded self-triples present, this gives two assignments, not four. Independent-choice products apply only after these constraints.

The Cartesian product for distinct variables is inappropriate when two positions contain the same variable. The query couples their choices even though storage uses one representative.

Lexical ordering, string conversion, and extensions inspecting term spelling follow [SPARQL's function definitions](https://www.w3.org/TR/sparql11-query/), not the reasoner's internal quotient.

## Deletion and provenance
{: id="10-deletion-demonstrates-why-provenance-matters"}

If the only asserted links are $$a=b$$ and $$b=c$$, all three names merge. Deleting $$a=b$$ should separate $$a$$ from $$\{b,c\}$$, unless another derivation proves equality.

Union–find cannot undo this by deleting one edge. Previously derived equalities are not independent surviving assertions. Deletion needs provenance, truth maintenance, or affected-closure recomputation, with costs determined by the workload.

A surviving equality needs a current assertion or derivation, not merely an appearance in the old closure. Recomputing the affected portion is one way to rebuild that distinction.

A small explicit materialization oracle can compare expanded triples and full query multisets after updates. Merges enabling constant-bearing rules, hidden projection multiplicities, and lexical filters reveal errors that fact counts alone miss. The discussion makes no new benchmark claim.

## References
{: id="references-and-current-scope"}

- [Motik et al., Handling owl:sameAs via rewriting, AAAI 2015](https://ojs.aaai.org/index.php/AAAI/article/view/9187).
- [Motik et al., Parallel materialisation, AAAI 2014](https://www.cs.ox.ac.uk/dan.olteanu/papers/mnpho-aaai14.pdf).
- [OWL 2 RL/RDF](https://www.w3.org/TR/owl2-profiles/) and [SPARQL 1.1](https://www.w3.org/TR/sparql11-query/).
