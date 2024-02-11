---
title: "Characteristic Sets: Accurate Cardinality Estimation for RDF Queries with Multiple Joins"
tags: kg query cardinality estimation
subtitle: This article introduces an algorithm for rewriting in materialization-based OWL 2 RL systems, guaranteeing correctness, improving efficiency, and enabling effective parallelization, resulting in orders of magnitude reduction in reasoning times on practical datasets.
---

### Plain characteristic sets

While RDF is used usually without a fixed schema, some kind of latent soft schema in the data frequently occurs: *Book*s tend to have *author*s and *title*s, etc. Although we might not be able to clearly classify an entity as "book" (due to the lack of schema information), we observe that we can *characterize* an entity by its emitting edges. For each entity $s$ occuring in an RDF data set $R$, we define its ***charateristic set $S_C(s)$*** and a ***set of charateristic sets $S_C(R)$*** as follows:

$$ S_C(s) := \lbrace p|∃o : (s,p,o) ∈ R \rbrace $$

A charateristic set $S_C(s)$ is a set that encompasses all properties associated with a specific subject $s$ in the RDF graph $R$. It collects all properties $p$ related to the subject $s$.

$$ S_C(R) := \lbrace S_C(s)|∃p,o : (s,p,o) ∈ R \rbrace $$

A set of charateristic sets $S_C(R)$ is a set that includes property sets $S_C(s)$ for each subject $s$ found in the RDF graph $R$.

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/fig1.png?raw=true" width="100%"> </p>

The key idea of using characteristic sets for selectivity estimation is to compute (and count) the characteristic sets for the data and calculate the characteristic set of the query. Subsequently, we find (and count) those characteristic sets of the data that are supersets of the characteristic set of the query.

Let us illustrate this with an example. Assume that $R$ is the set of data triples, $S_C(R)$ the set of characteristic sets, and

$$ count(S) = | \lbrace s|S_C(s)=S \rbrace | $$ 

Then we can be compute the result cardinality of a star-join query by looking up the number of occurrences of the characteristic sets:

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/fig2.png?raw=true" width="80%"> </p>

The cardinality computation is exact. This kind of computation works for an arbitrary number of joins, correlated or not, and requires only knowledge about the characteristic sets and their frequency. Memory space is typically no issue either. For example, **the characteristic sets for the 57 GB UniProt data set consume less than 64 KB**.

This observation makes characteristic sets attractive for RDF star join cardinality computations. However, this simple and exact computation is only possible due to the keyword $distinct$: in the general case, we have to take into account that the joins can produce duplicate bindings for $?e$ (due to different bindings of $?a$ and $?b$).

### Occurrence annotations

For the above-mentioned reason, we annotate each predicate in a characteristic set with the number of occurrences of this predicate in entities belonging to the characteristic set.

Formally, the different annotations of a characteristic set $S = ${ $p_1, p_2, ... $ } derived from a triple set $R$ can computed as follows:

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/fig3.png?raw=true" width="75%"> </p>

Note that in the implementation we compute and annotate the complete set $S_C$ with only two group-by operators. Thus, its calculation is not expensive.

Consider the query from above without the distinct clause, and assume that all entities in the RDF data set belong to the following hypothetical annotated characteristic set:

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/fig4.png?raw=true" width="55%"> </p>

The first column tells us that with a $distinct$ clause, we get $1000$ results. That is, there are $1000$ unique entities $s$ that occur in triples of the form $(s, author, ?x)$ and in triples of the form $(s, author, ?y)$. The second column says that there are $2300$ $author$ triples with entities from this characteristic set, i.e., each entity has $2.3$ $author$ triples on average. Accordingly, the third column says that each entity has $1.01$ $title$ triples on average. We therefore predict that without the $distinct$ clause, the result cardinality is $1000 × 2.3 × 1.01 = 2323$.

In contrast to the case with $distinct$, this computation is no longer exact in general: we average over the whole characteristic set and, therefore, introduce some error. However, entities belonging to the same characteristic set tend to be very similar in this respect. Thus, using the count for multiplicity estimations leads to very accurate predictions.

### Queries with bounded objects

Let's define *conditional selectivity*:

$$ sel(?o=o_1|?p=p_1)= \frac{sel(?o=o_1∧?p=p_1)}{sel(?p=p_1)} $$

The simple selectivity of $sel(?o=o_1)$ would ignore the correlation between predicate and object. However, even using the *conditional selectivities* is sometimes not accurate enough.

- A given object value might be more frequent within a certain characteristic set than within in the whole data set due to correlations.

- *Conditional selectivity* still assumes independence between object values, which in practice is frequently not true.

Instead of storing only the multiplicity, we also store the number of distinct object values. This increases space consumption by about 30%, but gives very useful bounds.

Putting everything together, the complete algorithm for star join cardinality estimation is shown below.

<p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/fig5.png?raw=true" width="75%"> </p>

### Handling diverse sets

The number of characteristic sets in a data can be very large. To manage this complexity, the system keeps only the most frequent $10,000$ characteristic sets. The remaining sets are then merged with the most frequent ones, ensuring efficient and streamlined data representation.

<p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/fig6.png?raw=true" width="75%"> </p>

When merging characteristic sets, we have two choices:

- We can merge directly a characteristic set S1 into a superset $S2 (S1 ⊆ S2)$ by adding the counts.

- We can split a characteristic set $S$ into two parts $S_1$, $S_2$ that can then be merged individually.

As a set is defined as following:

$$
\{ (predicate_0, count_0), (predicate_1, count_1), ... , distinct \}
$$


Assume we have 4 annotated characteristic sets:

$$
\begin{aligned}
S_1 &= \{ (author, 120), 100 \}\\
S_2 &= \{ (title, 230), 200 \}\\
S_3 &= \{ (author, 120), 100 \}\\
S_4 &= \{ (author, 30), (author, 20), 20 \}
\end{aligned}
$$

Now, we want to eliminate $S_4$.

The first alternative would be to merge $S_3$ into $S_4$,  producing the new set
$$
S_3 = \{(author, 2330),(title, 1021),(year, 1000), 1020\}
$$

This potentially leads to an overestimation of results, as we now predict too many entities for queries asking for {author, title, year}.

Or we could split $S_4$ into {$author$} and {$title$}, and update $S_1$ into {$(author, 150, 120)$} and {$(title, 250, 220)$}. This has the advantage of being accurate for the individual predicates, but potentially leads to underestimations for queries asking for both predicates. Which of the two alternatives is better depends on the data and the queries.

Overestimation is prefered as it usually derives only a small error and is often less dangerous for the resulting execution plan.

### Principles for cardinality estimator

##### #1. Calculate cardinality estimate once per equivalent query plans
- Cardinality is independent of the plan structure.
- It should not change by changing the ordering of operators.

##### #2. Use maximum amount of consistent correlation information
-  A typical query graph has a lot of joins, we can have consistent information for only a few portions of the graph.
- Characteristic sets are used to estimate to the maximum portion of the graph, before starting to use join estimates.

##### #3. Assume independence if no correlation information is available
- If no consistent information is available, we assume independence to calculate estimates using general join stats.
- Error is relatively low, since independence is being assumed very **“late”** in cost estimation.

### Estimation Algorithm

Given a join graph $Q = (V, E)$, we can directly estimate the result cardinality using the independence assumption:

$$
card(Q) = \prod_{R ∈ V}{|R|} \sum_{p ∈ E}{sel(p)}
$$

To overcome the limitation of the independence assumption in data queries, we aim to leverage correlated information. The strategy involves using statistical synopses to cover the query graph and estimate different parts of the query. By marking covered sections in the graph, we replace several factors in the product formula with synopses estimates, simplifying the process without reconstructing individual factors. For instance, in cases of correlated joins, where join order is unknown, we focus on replacing groups of factors to estimate result cardinality. If the entire graph cannot be covered, independence is assumed, and the remaining factors are multiplied.

<p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/fig7.png?raw=true" width="75%"> </p>

### Evaluation

<p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/table1.png?raw=true" width="75%"> </p>

<p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/table2.png?raw=true" width="75%"> </p>

<p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/table3.png?raw=true" width="75%"> </p>

<p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/table4.png?raw=true" width="75%"> </p>


## Reference

- [T. Neumann and G. Moerkotte, "Characteristic sets: Accurate cardinality estimation for RDF queries with multiple joins," 2011 IEEE 27th International Conference on Data Engineering, Hannover, Germany, 2011, pp. 984-994, doi: 10.1109/ICDE.2011.5767868.](https://ieeexplore.ieee.org/document/5767868)
- [CS848-2018-slides/Characteristic-Sets-Pranjal](https://cs.uwaterloo.ca/~ssalihog/courses/cs848-2018-slides/Characteristic-Sets-Pranjal.pdf)