---
title: Handling owl:sameAs via Rewriting
tags: kg rewriting owl
subtitle: This article introduces an algorithm for rewriting in materialization-based OWL 2 RL systems, guaranteeing correctness, improving efficiency, and enabling effective parallelization, resulting in orders of magnitude reduction in reasoning times on practical datasets.
---


Let's consider the problems that the *owl:sameAs* property affects to reasoning.

The semantics of *owl:sameAs* can be captured explicitly using program $P_≈$, consisting of rules $(≈_1)-(≈_5)$, which axiomatises *owl:sameAs* as a congruence relation. We call each set of resources all of which are equal to each other an *owl:sameAs-clique*.

$≈_1 : ⟨ x_i, $ *owl:sameAs* $, x_i ⟩ $ ← $ ⟨ x_1, x_2, x_3 ⟩ $, for $1 ≤ i ≤ 3$

$ ≈_2 : ⟨ x^′_1, x_2, x_3 ⟩ $ ← $ ⟨ x_1, x_2, x_3 ⟩ $ ∧ $ ⟨ x_1, $ *owl:sameAs* $, x^′_1 ⟩ $

$ ≈_3 $ : $ ⟨ x_1, x_2^′, x_3 ⟩ $ ← $ ⟨ x_1, x_2, x_3 ⟩ $ ∧ $ ⟨ x_2, $ *owl:sameAs* $, x_2^′ ⟩ $

$ ≈_4 $ : $ ⟨ x_1, x_2, x_3^′ ⟩ $ ← $ ⟨ x_1, x_2, x_3 ⟩ $ ∧ $ ⟨ x_3, $ *owl:sameAs* $, x_3^′ ⟩ $

$ ≈_5 $ : *false* ← $ ⟨ x, $ *owl:differentFrom* $, x ⟩$

These rules can lead to the derivation of many equivalent triples, as we demonstrate using an example program $P_{ex}$ containing rules $(R)–(F3)$.

$R$ : $ ⟨ x, $ *owl:sameAs*$, $ *:USA*$ ⟩ ← ⟨ $*:Obama*$, $ *:presidentOf*$, x ⟩ $

$S$ : $ ⟨ x, $ *owl:sameAs*$, $ *:Obama*$ ⟩ ← ⟨ x, $ *:presidentOf*$, $ *:USA*$ ⟩ $

$F_1$ : $ ⟨ $*:USPresident*$, $ *:presidentOf*$, $ *:US*$ ⟩ $

$F_2$ : $ ⟨ $*:Obama*$, $ *:presidentOf*$, $ *:America*$ ⟩ $

$F_3$ : $ ⟨ $*:Obama*$, $ *:presidentOf*$, $ *:US*$ ⟩ $

On $P_{ex}$ U $P_{≈}$, rule $(R)$ derives that *:USA* is equal to *:US* and *:America*, and then rules $(≈_1)-(≈_4)$ derive an *owl:sameAs* triple for each of the 9 pairs involving *:USA*, *:America*, and *:US*.
The total number of derivations, however, is much higher. We get 66 derivations in total for the 9 *owl:sameAs* triples.
In fact, for each *owl:sameAs-clique* of size $n$, rules $(≈_1)–(≈_4)$ derive $n^2$ *owl:sameAs* triples via $2n^3+n^2+n$ derivations. Moreover, each triple $ ⟨ s, p, o ⟩ $ with terms in *owl:sameAs-cliques* of size $n_s, n_p, n_o$, respectively, is expanded to $n_s × n_p × n_o $ triples, each of which is derived $ n_s + n_p + n_o $ times. 
This duplication of facts and derivations is a major source of inefficiency.

To reduce these numbers, we can choose a representative resource for each *owl:sameAs-clique* and then rewrite all triples—that is, replace all resources with their representatives.

The materialisation of $P_{ex}$ then contains only the triple $ ⟨ $*:Obama*$, $ *:presidentOf*$, $ *:US*$ ⟩ $ and this makes the number of derivations of *owl:sameAs* triples drop from over 60 to just 6.

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-05-handling-owl-sameas-via-rewriting/fig1.png?raw=true" width="60%"> </p>

Since *owl:sameAs* triples can be derived continuously during materialisation, rewriting cannot be applied as preprocessing; moreover, to ensure that rewriting does not affect query answers.
Thus, we may need to continuously rewrite both triples and rules: rewriting only triples can be insufficient. For example, if we choose *:US* as the representative of *:USA*, *:US* and *:America*, then rule $(S)$ will not be applicable, and we will fail to derive that *:USPresident* is equal to *:Obama*. 

## Parallel Reasoning With Rewriting

The algorithm by [Motik et al. (2014)](https://www.cs.ox.ac.uk/dan.olteanu/papers/mnpho-aaai14.pdf) used in the [RDFox](https://www.oxfordsemantic.tech/rdfox) system implements a fact-at-a-time version of the seminaïve algorithm ([Abiteboul, Hull, and Vianu 1995](https://wiki.epfl.ch/provenance2011/documents/foundations+of+databases-abiteboul-1995.pdf)): it initialises the set of facts $T$ with the input data $E$, and then computes $P^∞(E)$ by repeatedly applying rules from $P$ to $T$ using $N$ threads until no new facts are derived.

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-05-handling-owl-sameas-via-rewriting/algo1.png?raw=true" width="80%"> </p>

To extend the original seminaive algorithm with rewriting, we allow each thread to perform three different actions.

- First, a thread can extract a rule $r$ from the queue $R$ of rewritten rules and apply $r$ to the set of all facts $T$, thus ensuring that changes to resources in rules are taken into account.
  <p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-05-handling-owl-sameas-via-rewriting/fig2_1.png?raw=true" width="40%"> </p>


- Second, a thread can rewrite outdated facts—that is, facts containing a resource that is not a representative of itself. To avoid iteration over all facts in $T$, the thread extracts a resource $c$ from the queue $C$ of unprocessed outdated resources, and uses indexes by [Motik et al. (2014)](https://www.cs.ox.ac.uk/dan.olteanu/papers/mnpho-aaai14.pdf) to identify each fact $F ∈ T$ containing $c$. The thread then removes each such $F$ from $T$, and it adds $ρ(F)$ to $T$.
  ($ρ$ is a mapping function that maps resources to their representatives)
  <p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-05-handling-owl-sameas-via-rewriting/fig2_2.png?raw=true" width="75%"> </p>


- Third, a thread can extract and process an unprocessed fact $F$ in $T$. The thread first checks whether $F$ is outdated $($i.e., whether $F ≠ ρ(F)$$)$; if so, the thread removes $F$ from $T$ and adds $ρ(F)$ to $T$. If $F$ is not outdated but is of the form $⟨ a, $*owl:sameAs*$, b ⟩$ with $a ≠ b$, the thread chooses a representative of the two resources, updates $ρ$, and adds the other resource to queue $C$. The thread derives a contradiction if $F$ is of the form $⟨ a, $*owl:differentFrom*$, a ⟩$. Otherwise, the thread processes $F$ by partially instantiating the rules in $P$ containing a body atom that matches $F$, and applying such rules to $T$ as described by [Motik et al. (2014)](https://www.cs.ox.ac.uk/dan.olteanu/papers/mnpho-aaai14.pdf).
  <p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-05-handling-owl-sameas-via-rewriting/fig2_3.png?raw=true" width="95%"> </p>

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-05-handling-owl-sameas-via-rewriting/algo2.png?raw=true" width="90%"> </p>

The process of rewriting rules in RDFox involves efficiently identifying rules matching a fact using an index, which may need updating when $ρ$ changes. However, due to the complexity of updating the index in parallel, this operation is performed serially. Specifically, when all threads are waiting (indicating that all facts have been processed), a single thread updates $P$ to $ρ(P)$, reindexes it, and inserts the updated rules into the queue $R$ for reevaluation. Despite being a parallelization bottleneck, experiments have shown that the time spent on this process is not significant for programs of moderate size.

Instead of physically removing facts from $T$, the approach involves marking them as outdated. During the matching of the body atoms of partially instantiated rules, marked facts are skipped. This entire process is lock-free, and the removal of all marked facts is performed in a postprocessing step.

Table 1 shows six steps of an application of the algorithm to the example program $P_{ex}$ on a single thread. Some resource names have been abbreviated for convenience, and $≈$ abbreviates *owl:sameAs*. The $⊲$ symbol identifies the last fact extracted from $T$. Facts are numbered for easier referencing, and their (re)derivation is indicated on the right: $R(n)$ or $S(n)$ means that the fact was obtained from fact $n$ and rule $R$ or $S$; moreover, we rewrite facts immediately after merging resources, so $W(n)$ identifies a rewritten version of fact $n$, and $M(n)$ means that a fact was marked outdated because fact $n$ caused $ρ$ to change.

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-05-handling-owl-sameas-via-rewriting/table1.png?raw=true" width="90%"> </p>

We start by extracting facts from $T$ and, in steps $1$ and $2$, we apply rule $R$ to facts $2$ and $3$ to derive facts $4$ and $5$, respectively. In step $3$, we extract fact $4$, merge *:America* into *:USA*, mark facts $2$ and $4$ as outdated, and add their rewriting, facts $6$ and $7$, to $T$. In step $4$ we merge *:USA* into *:US*, after which there are no further facts to process. Mapping $ρ$, however, has changed, so we update $P$ to contain rules $(R^′)$ and $(S^′)$ and add them to the queue $R$.

$R^′$ : $ ⟨ x, $ *owl:sameAs*$, $ *:US*$ ⟩ ← ⟨ $*:Obama*$, $ *:presidentOf*$, x ⟩ $

$S^′$ : $ ⟨ x, $ *owl:sameAs*$, $ *:Obama*$ ⟩ ← ⟨ x, $ *:presidentOf*$, $ *:US*$ ⟩ $

In step $5$ we evaluate the rules in queue $R$, which introduces facts $9$ and $10$. Finally, in step $6$, we rewrite *:USPresident* into *:Obama* and mark facts $1$ and $9$ as outdated. At this point the algorithm terminates, making only 6 derivations in total, instead of more than 60 derivations when *owl:sameAs* is axiomatised explicitly.


## SPARQL Queries on Rewritten Triples

Given a set of facts $T$ and mapping $ρ$, the expected answers to a SPARQL query $Q$ are those obtained by evaluating $Q$ in the expanded $T^ρ$. However, the question arises about how to evaluate $Q$ on the concise representation $T$, preserving the advantages of smaller joins, while still obtaining answers in $T^ρ$ only expanding necessary resources.

To illustrate a strategy, let's use the program $P_{ex}$ from above: Recall that, after we finish the materialisation of $P_{ex}$, we have $ρ(x) = $ *:US* for each $x ∈ $ { *:USA*, *:America*, *:US* } and $ρ(x) = $ *:Obama* for each $x ∈ $ { *:USPresident*, *:Obama* }.

- **$Q_1 :=$ SELECT $?x$ WHERE { $ ?x$ :presidentOf $?y $ }**

  On $T^ρ$, query $Q_1$ generates answers $\mu_1= $ { $?x → $ :Obama$ $ } and $\mu_2=$ {$ ?x → $ :USPresident }, each repeated 3 times for matches of $?y$ to *:USA*, *:US*, *:America*. 

  A simple evaluation of the normalized query $ρ(Q_1)$ on $T$, followed by a post-hoc expansion under $ρ$, produces only 1 occurrence of each $\mu_1$ and $\mu_2$, which is not the intended result. **This issue arises because the final expansion step doesn't consider the number of times each binding of** $?y$ **contributes to the result. To address this, we adjust the projection operator to output each projected answer as many times as there are resources in the projected** *owl:sameAsclique(s)***.**

  As a result, for $Q_1$, we match the triple pattern of $ρ(Q1)$ to $T$, obtaining one answer $ν_1$ = {$?x → $ :Obama $, ?y → $:US }. Next, we project $?y$ from $ν_1$ and get 3 occurrences of $µ_1$ since the *owl:sameAsclique* of *:US* has a size of 3. Finally, we expand each occurrence of $µ_1$ to $µ_2$, resulting in all 6 desired results.


- **$Q_2 :=$ SELECT $?y$ WHERE { $?x$ :presidentOf :US $.$ BIND ( STR ($?x$) AS $?y$) $ }**

  On $T^ρ$, query $Q_2$ produces answers $\tau_1=$ { $ ?y → $ "Obama" } and $\tau_2=$ {$ ?y → $ "USPresident" }; in contrast, on T, query $ρ (Q_2)$ yields only $\tau_1$, which does not expand into $\tau_2$ because the strings "Obama" and "USPresident" are not equal. Therefore **evaluation should expand answers before evaluating builtin functions**. 

  Thus, we answer $Q_2$ as follows: we match the triple pattern of $ρ (Q_2)$ to $T$ as usual, obtaining $k_1=$ { $?x → $ *:Obama* }; then we expand $k_1$ to $k_2=$ { $?x → $ *:USPresident* }; next, we evaluate the *BIND* expression and extend $k_1$ and $k_2$ with the respective values for $?y$; finally, we project $?x$ to obtain $tau_1$ and $tau_2$. Since we have already expanded $?x$, we must not repeat the projected answers further; instead, we output each projected answer only once to obtain the correct answer cardinalities.

## Evaluation

An extension to RDFox was implemented to handle *owl:sameAs* through either rewriting(REW) or axiomatisation(AX). A performance comparison of materialisation using these two approaches was conducted, with a specific focus on scalability concerning the number of threads. Furthermore, the study measured the influence of rewriting on the number of derivations and materialised triples.

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-05-handling-owl-sameas-via-rewriting/table2.png?raw=true" width="90%"> </p>

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-05-handling-owl-sameas-via-rewriting/table3.png?raw=true" width="90%"> </p>

The results confirm that rewriting can significantly reduce materialisation times.

## Reference
- [Motik, Boris, et al. "Parallel materialisation of datalog programs in centralised, main-memory RDF systems." Proceedings of the AAAI Conference on Artificial Intelligence. Vol. 28. No. 1. 2014.](https://www.cs.ox.ac.uk/dan.olteanu/papers/mnpho-aaai14.pdf)
- [Motik, Boris, et al. "Handling owl: sameAs via rewriting." Proceedings of the AAAI Conference on Artificial Intelligence. Vol. 29. No. 1. 2015.](https://ojs.aaai.org/index.php/AAAI/article/view/9187)