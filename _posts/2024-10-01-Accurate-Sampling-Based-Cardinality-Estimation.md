---
title: "(WIP) Accurate Sampling-Based Cardinality Estimation for Complex Graph Queries"
tags: query cardinality estimation
subtitle: This post provides a novel, strongly consistent method for accurately and efficiently estimating the cardinality of complex graph queries.
---
Accurate cardinality estimation (i.e., predicting the number of answers to a query) is a vital aspect of database systems, particularly in graph databases where queries often involve numerous joins and self-joins.

Recent studies identified that a sampling method based on the [WanderJoin algorithm](https://dl.acm.org/doi/pdf/10.1145/2882903.2915235) is highly effective in estimating cardinality for graph queries. However, this method has limitations, especially in handling complex queries and performing efficiently on large datasets.

This post explores a novel approach inspired by WanderJoin that can effectively handle complex graph queries and improve performance.

## Challenges in Cardinality Estimation	

Graph databases pose challenges due to their complexity:

- Queries often involve multiple joins and self-joins.
- Data distributions can be skewed, leading to inaccurate or zero estimates.
- Cardinality estimation needs to account for complex graph operations like union, projection, and duplicate elimination. Here is the syntax and the semantics of the SPARQL.
  <p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-10-01-Accurate-Sampling-Based-Cardinality-Estimation/tab1.png?raw=true" width="100%"> </p>

Existing methods struggle with such complexities and may produce slow or inaccurate results on larger datasets.

## The WanderJoin Algorithm

WanderJoin randomly selects facts from the database instance for each atom (query component) but ensures that these selections are not independent.

For example, let $ Q = AND(R(x, y), S(y, z), T(z, x)) $ be the example query.

When evaluating $ Q $, it first selects a fact from relation $R$, then matches facts from $S$ that join correctly with $R$, and finally matches $T$ to complete a valid query answer.

The order in which atoms are sampled critically determines the accuracy of the estimates produced by WanderJoin.

The advantage is its flexibility, as it doesn't need predefined schemas, making it ideal for unpredictable graph database queries.

[Li et al.](https://dl.acm.org/doi/pdf/10.1145/3284551) emphasize the need for an optimal atom order to improve cardinality estimates, proposing trial runs with all reasonable orders and selecting the least costly one for further trials. [Park et al.](https://personal.ntu.edu.sg/assourav/papers/SIGMOD-20-GCARE.pdf) integrate this into G-CARE as the **WJ** method, which averages 30 estimation attempts to find the final result. Orders are tested in a round-robin fashion, and the best one, based on variance, is used for the remaining runs.

The **WJ** method handles only conjunction queries, while [Li et al.](https://dl.acm.org/doi/pdf/10.1145/3284551)'s approach supports **aggregate** queries but not **distinct** queries or nested operators.


## Cardinality Estimation Methods Used in the G-CARE Framework

The G-CARE framework's cardinality estimation algorithms, as described by [Park et al.](https://personal.ntu.edu.sg/assourav/papers/SIGMOD-20-GCARE.pdf), are classified into two categories: **synopsis-based** and **sampling-based** methods.

#### Synopsis-based methods:

- Bounded Sketch (BS) : Divides relations into partitions, recording constants and max degree for each, and uses bounding formulas to estimate cardinality based on query structure.
- Characteristic Sets (C-Set) : Summarizes star-shaped structures in the database and estimates cardinality by decomposing queries into subqueries and combining results using independence assumptions.
- SumRDF : Merges graph vertices to summarize the graph and uses possible worlds semantics to estimate query cardinality with certainty bounds.

#### Sampling-based methods:

- $ J_{SUB} $ : Samples a fact matching the first query atom, evaluates the rest with this atom bound, similar to CS2 but samples for each estimate.
- Correlated Sampling (CS) : Uses hashing to create a database synopsis instead of sampling data.
- $ I_{MPR} $ : Adapts random walks to estimate the number of graphlets in a visible subgraph, tailored for graph matching and directed labelled graphs.

## Strongly Consistent Cardinality Estimator for Complex Queries

## Reference

- [Hu, Pan, and Boris Motik. &#34;Accurate Sampling-Based Cardinality Estimation for Complex Graph Queries.&#34; ACM Transactions on Database Systems 49.3 (2024): 1-46.](https://dl.acm.org/doi/pdf/10.1145/3689209)
- [Li, Feifei, et al. &#34;Wander join: Online aggregation via random walks.&#34; Proceedings of the 2016 International Conference on Management of Data. 2016.](https://dl.acm.org/doi/pdf/10.1145/2882903.2915235)
- [F. Li, B. Wu, K. Yi, and Z. Zhao. 2019. Wander join and XDB: Online aggregation via random walks. ACM Trans. Datab. Syst. 44, 1 (2019), 2:1–2:41.](https://dl.acm.org/doi/pdf/10.1145/3284551)
- [Y. Park, S. Ko, S. S. Bhowmick, K. Kim, K. Hong, and W.-S. Han. 2020. G-CARE: A framework for performance benchmarking of cardinality estimation techniques for subgraph matching. In Proceedings of the 41st ACM SIGMOD International Conference on Management of Data (SIGMOD’20). ACM Press, 1099–1114.](https://personal.ntu.edu.sg/assourav/papers/SIGMOD-20-GCARE.pdf)