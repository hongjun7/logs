---
title: "Characteristic Sets: Accurate Cardinality Estimation for RDF Queries with Multiple Joins"
tags: kg query cardinality estimation
subtitle: This post introduces an algorithm for rewriting in materialization-based OWL 2 RL systems, guaranteeing correctness, improving efficiency, and enabling effective parallelization, resulting in orders of magnitude reduction in reasoning times on practical datasets.
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

Then we can compute the result cardinality of a star-join query by looking up the number of occurrences of the characteristic sets:

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
##### #1. Single Join Queries

For the data sets [Yago](https://yago-knowledge.org/) and [LibraryThing](https://cseweb.ucsd.edu/~jmcauley/datasets.html#social_data), queries of the form $(?S, p_1, ?O_1),(?S, p_2, ?O_2)$ were tested, where all possible combinations of p1, p2 were considered. This resulted in $1751$ queries for Yago and $19062990$ queries for LibraryThing.

<p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/table1.png?raw=true" width="75%"> </p>

<p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/table2.png?raw=true" width="75%"> </p>

##### #2. Complex Queries

To study cardinality estimation for more complex queries, queries with up to 6 joins and including additional object constraints were tested. The queries and the detailed results are included in the appendix.

<p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/table3.png?raw=true" width="75%"> </p>

<p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/table4.png?raw=true" width="75%"> </p>

##### #3. Other Data Sets

<p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/fig8.png?raw=true" width="75%"> </p>



In result, reducing the number of characteristic sets significantly improves efficiency without significantly compromising accuracy. Despite a reduction by more than a factor of 40, over 90% of estimates deviate by less than a factor of two. There is a minor issue with predicate combinations resulting in empty predictions, possibly addressed in the future by switching to a more conservative cardinality estimate when needed.

## Appendix

These are the concrete queries used in **Evaluation** and the individual cardinality estimates of all database systems in this section.

In some cases, a database system predicted a cardinality of less than one, which makes no sense for non-empty query results. When this happened, the estimates were rounded up to $1$.

##### #1. LibraryThing

```javascript
Q1: select ?s ?t ?y where { ?s <hasTitle> ?t. ?s <hasAuthor> ”Jane Austen”. ?s <inYear> ?y }
Q2: select ?s ?t where { ?s <hasTitle> ?t. ?s <hasAuthor> ”Jane Austen”. ?s <inYear> <2003> }
Q3: select ?s where { ?s <crime> ?b. ?s <romance> ?b2. ?s <poetry> ?b3. ?s <hasFavoriteAuthor> ”Neil Gaiman” }
Q4: select ?s where { ?s <crime> ?b. ?s <politics> ?b2. ?s <romance> ?b3. ?s <poetry> ?b4. ?s <cookbook> ?b5. ?s <ocean\ life> ?b6. ?s <new\ mexico> ?b7 }
Q5: select ?s ?t1 ?t2 where { ?s <inYear> <1975>. ?s <hasAuthor> ”T.S. Eliot”. ?s <hasTitle> ?t1. ?s <hasTitle> ?t2 }
Q6: select ?s where { ?s < thriller > ?b. ?s < politics > ?b2. ?s <conspiracy> ?b3. ?s <hasFavoriteAuthor> ?a }
Q7: select ?s where { ?s < thriller > ?b. ?s < politics > ?b2. ?s <conspiracy> ?b3. ?s <hasFavoriteAuthor> ”Robert B. Parker” }
Q8: select ?s where { ?s < thriller > ?b. ?s < politics > ?b2. ?s <conspiracy> ?b3. ?s <hasFavoriteAuthor> ”Noam Chomsky” }
Q9: select ?s where { ?s < politics > ?b1. ?s <society> ?b2. ?s <future> ?b3. ?s <democracy> ?b4. ?s <british> ?
b5. ?s <hasFavoriteAuthor> ”Aldous Huxley” }
Q10: select ?s where { ?s < politics > ?b1. ?s <society> ?b2. ?s <future> ?b3. ?s <democracy> ?b4. ?s <british> ?b5. ?s <hasFavoriteAuthor> ”Aldous Huxley”. ?s <hasFavoriteAuthor> ”George Orwell” }
```

The individual cardinality estimates for the following queries are shown below.

<p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/table5.png?raw=true" width="95%"> </p>

##### #2. Yago

```javascript
Q1: select ?s ?l ?n ?t where { ?s <bornInLocation> ?l. ?s <isCalled> ?n. ?s <type> ?t. }
Q2: select ?s ?n ?t where { ?s <bornInLocation> <Stockholm>. ?s <isCalled> ?n. ?s <type> ?t. }
Q3: select ?s ?c ?n ?w where { ?s <producedInCountry> ?c. ?s <isCalled> ?n. ?s <hasWebsite> ?w }
Q4: select ?s ?n ?w where { ?s <producedInCountry> <Spain>. ?s <isCalled> ?n. ?s <hasWebsite> ?w }
Q5: select ?s ?l ?n ?d ?t where { ?s <diedInLocation> ?l. ?s <isCalled> ?n. ?s <diedOnDate> ?d. ?s <type> ?t }
Q6: select ?s ?n ?d ?t where { ?s <diedInLocation> <Paris>. ?s <isCalled> ?n. ?s <diedOnDate> ?d. ?s <type> ?t }
Q7: select ?s ?n ?d where { ?s <diedInLocation> <Paris>. ?s <isCalled> ?n. ?s <diedOnDate> ?d. ?s <type> <wordnet person 100007846> }
Q8: select ?s ?l ?u ?c ?m where { ?s <hasOfficialLanguage> ?l. ?s <hasUTCOffset> ?u. ?s <hasCapital> ?c. ?s <hasCurrency> ?m }
Q9: select ?s ?l ?c ?m where { ?s <hasOfficialLanguage> ?l. ?s <hasUTCOffset> <1>. ?s <hasCapital> ?c. ?s <hasCurrency> ?m }
Q10: select ?s ?c ?m where { ?s <hasOfficialLanguage> <French language>. ?s <hasUTCOffset> <1>. ?s <hasCapital> ?c. ?s <hasCurrency> ?m }
```

The individual cardinality estimates for the following queries are shown below.

<p align="left"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-02-10-characteristic-sets/table6.png?raw=true" width="95%"> </p>

## Reference

- [T. Neumann and G. Moerkotte, "Characteristic sets: Accurate cardinality estimation for RDF queries with multiple joins," 2011 IEEE 27th International Conference on Data Engineering, Hannover, Germany, 2011, pp. 984-994, doi: 10.1109/ICDE.2011.5767868.](https://ieeexplore.ieee.org/document/5767868)
- [CS848-2018-slides/Characteristic-Sets-Pranjal](https://cs.uwaterloo.ca/~ssalihog/courses/cs848-2018-slides/Characteristic-Sets-Pranjal.pdf)