---
title: "Towards Better Evaluation for Dynamic Link Prediction"
tags: "link-prediction"
subtitle: This post provides novel evaluation strategies for dynamic link prediction, introducing new datasets, robust negative sampling methods, and the EdgeBank baseline for better model assessment.
---

In recent years, dynamic graph learning has gained significant attention, especially in tasks such as link prediction, where the goal is to predict future connections between nodes in a network. While existing methods have shown impressive results, particularly in static graphs, this identified several key limitations in the current evaluation process for dynamic graphs. To address these gaps, this post introduces new evaluation strategies, novel datasets, and the *EdgeBank* baseline, which together offer a more robust and realistic framework for advancing dynamic link prediction methods.

## Dynamic Link Prediction

Dynamic link prediction, a key task in dynamic graphs, aims to predict the probability of a future interaction between nodes, which is crucial for applications such as social networks, traffic forecasting, and recommendation systems.

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-09-18-TBEDLP/fig1.png?raw=true" width="75%"> </p>

Although recent methods like [JODIE](https://arxiv.org/abs/2006.10637), [TGN](https://arxiv.org/abs/1908.01207), and [CAWN](https://arxiv.org/abs/2101.05974) have made significant progress, their performance is nearly perfect in current evaluations, making it difficult to distinguish between them. This highlights the need for more stringent and robust evaluation procedures to better assess these methods.

## Limitations of Evaluation

There are several limitations in the current evaluation procedure for dynamic link prediction. This post proposes improvements and additions to tackle the issues.

#### Lack of domain diversity

Existing benchmark datasets are predominantly focused on social and interaction networks, which limits their applicability across other domains. Networks from different fields, such as biological, economic, or transportation systems, have distinct structural properties.

#### Easy negative edges

The edges used in the current evaluation are often too easy. In dynamic graphs, unobserved edges at previous timestamps are used as negative samples, but they are less likely to reoccur during testing. This leads to inflated performance metrics, as models are not being tested against more realistic, challenging negative edges.

This post proposes two new *Negative Sampling (NS) strategies*—***historical NS*** and ***inductive NS***—to sample more difficult negative edges that better match real-world dynamics.

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-09-18-TBEDLP/fig7.png?raw=true" width="75%"> </p>

#### Naive memorization works well

Current dynamic link prediction models tend to memorize the patterns of previously seen edges, leading to overly optimistic evaluations. To illustrate this, this post introduces [EdgeBank](https://github.com/fpour/DGB/blob/main/EdgeBank/link_pred/edge_bank_baseline.py), a simple, memorization-based baseline.

EdgeBank stores previously observed edges in memory and predicts them as positive during testing. Despite its simplicity, EdgeBank achieves surprisingly strong performance and, in some cases, outperforms state-of-the-art (SOTA) methods.

This raises questions about whether current methods are truly learning new patterns or simply memorizing past interactions.

## Dynamic Graph Dataset

Formally, we consider a (continuous time) dynamic graph as a timestamped edge stream including triples of *source*, *destination*, *timestamp*.

$$
G = { (s_1, d_1, t_1), (s_2, d_2, t_2), ... } (0 ≤ t_1 ≤ t_2 ≤ ... ≤ t_{split} ≤ ... ≤ T)
$$

For evaluation, we split the timeline at a point $ t_{split} $, separating the edges that appear before and after it.
Therefore, we have train and test set edges ($ E_{train} $ ∪ $ E_{test} $). In this regard, edges of a dynamic graph can be categorized as follows:

 - $ E_{train} $ \ $ E_{test} $ : Edges that are only seen during training.
 - $ E_{train} $ ∩ $ E_{test} $ : Edges that are seen during training and reappear during test phase(***transductive*** edges).
 - $ E_{test} $ \ $ E_{train} $ : Edges that are only seen during testing(***inductive*** edges).

## Temporal Edge Appearance(TEA) Plot

A TEA plot shows the proportion of repeated versus new edges at each timestamp in a dynamic graph.

In this context, $ E^t $ represents the set of edges at timestamp $ t $, and $ E^t_{seen} $ refers to the set of all edges from previous timestamps. This metric estimates the proportion of new positive edges that cannot be accurately predicted by a simple memorization method.

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-09-18-TBEDLP/fig2.png?raw=true" width="75%"> </p>

The grey bar represents repeated edges, while the red bar shows new edges. The average ratio of new edges is used to quantify these patterns.

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-09-18-TBEDLP/fig4.png?raw=true" width="75%"> </p>

## Temporal Edge Traffic(TEF) Plot

A TET plot displays the recurrence patterns of edges in dynamic networks over time. Edges are first sorted by their initial appearance and then by their most recent occurrence.

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-09-18-TBEDLP/fig3.png?raw=true" width="75%"> </p>

The edges are color-coded: green for edges in the training set only, red for inductive edges (test set only), and orange for transductive edges (present in both). Two indices are defined to quantify these patterns.

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-09-18-TBEDLP/fig5.png?raw=true" width="75%"> </p>

TET plots offer insights into how edges are used in training and testing DGNN methods. A memorization approach can effectively predict transductive edges (observed during training), especially when they appear consistently, resulting in a high recurrence index and low surprise index. If the edges appear intermittently, memorization may help but will be less reliable. For inductive edges (new, unseen edges in the test set), memorization is not useful, as these edges are entirely new, leading to a high surprise index.

## EdgeBank: a memorization baseline

The proposed approach, **EdgeBank**, is a memorization-based method designed to test whether storing past edges can serve as a competitive baseline for dynamic graph prediction. EdgeBank functions like a dictionary that records previously observed edges at each timestamp, requiring no parameters and having storage equal to the number of edges in the dataset. At test time, it predicts an edge as positive if it has been seen before, and negative otherwise, excelling at predicting frequently recurring edges.

EdgeBank makes incorrect predictions in two cases: (i) when encountering unseen (inductive) edges, and (ii) when edges from memory are not currently observed. However, due to the sparsity of graphs, EdgeBank performs well in scenarios with negative edges.

EdgeBank comes in two variants:
- $ EdgeBank_∞ $ stores all observed edges, but may falsely predict positive edges that rarely reoccur.
- $ EdgeBank_{tw} $ only retains edges from a recent fixed time window, focusing on short-term edge patterns.

Although EdgeBank is not meant to replace state-of-the-art models, it serves as a strong baseline to show how far memorization can go in dynamic graph prediction.

## Impact of Negative Sampling

The ranking of methods changes in the historical and inductive negative sampling.

EdgeBank shows competitive peformance, particularly in the standard setting, and even outperforms in some datasets.

Referring to the figure below, we can see a clear gap between the performance of the SOTA models and EdgeBank with the alternative negative sampling (i.e. historical and inductive negative sampling).

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2024-09-18-TBEDLP/fig6.png?raw=true" width="75%"> </p>

## Reference

- [[1] Poursafaei, Farimah, et al. &#34;Towards better evaluation for dynamic link prediction.&#34; Advances in Neural Information Processing Systems 35 (2022): 32928-32941.](https://proceedings.neurips.cc/paper_files/paper/2022/file/d49042a5d49818711c401d34172f9900-Supplemental-Datasets_and_Benchmarks.pdf)
- [[2] Temporal Graph Learning Reading Group: Towards Better Evaluation for Dynamic Link Prediction](https://www.youtube.com/watch?v=LvOEvGlVlUU/)
- [[3] E. Rossi, B. Chamberlain, F. Frasca, D. Eynard, F. Monti, and M. Bronstein. Temporal graph networks for deep learning on dynamic graphs. arXiv preprint arXiv:2006.10637, 2020.](https://arxiv.org/abs/2006.10637)
- [[4] S. Kumar, X. Zhang, and J. Leskovec. Predicting dynamic embedding trajectory in temporal interaction networks. In Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery &amp; Data Mining, 2019.](https://arxiv.org/abs/1908.01207)
- [[5] Y. Wang, Y. Chang, Y. Liu, J. Leskovec and P. Li. Inductive Representation Learning in Temporal Networks Via Causal Anonymous Walks. International Conference on Learning Representations (ICLR), 2021.](https://arxiv.org/abs/2101.05974)
