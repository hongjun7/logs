---
title: Scalable In-context Ranking with Generative Models
tags: ml, retrieval, llm
subtitle: This post analyzes BlockRank, a scalable in-context ranking (ICR) method that adapts LLM attention structure to enable efficient large-scale retrieval and ranking.
---

Large language models (LLMs) can perform retrieval implicitly: given a query and a set of candidate documents in context, the model identifies relevant items through next-token likelihoods. This paradigm, **in-context ranking (ICR)**, treats ranking as conditional generation over a structured prompt rather than explicit embedding similarity. While cross-document attention enables strong effectiveness, scalability is limited by quadratic attention cost in context length.

## In-Context Ranking

Let a query be (q) and candidates be

$$
\mathcal{D} = {d_1, d_2, \dots, d_N}.
$$

ICR constructs a prompt

$$
P = \text{Instruction} ,\Vert, q ,\Vert, d_1 ,\Vert, \dots ,\Vert, d_N,
$$

and relevance emerges from next-token probabilities. As candidate count grows, attention cost scales as

$$
\mathcal{O}(|P|^2),
$$

making large-scale ranking impractical.

## BlockRank

**BlockRank** observes that ranking-tuned LLMs develop structured sparsity in attention: document tokens attend primarily within their own block, while query→document attention correlates with relevance. This implies that ranking signal resides in query-mediated interactions, and document–document attention can be removed without losing relevance information.

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-03-01-BlockRank/1772439547697.png?raw=true"> </p>

Segment the prompt into blocks

$$
P = {B_{\text{inst}}, B_q, B_{d_1}, \dots, B_{d_N}}.
$$

BlockRank enforces that document tokens attend only to their own block and instruction

$$
B_{d_i} \cup B_{\text{inst}},
$$

while query tokens attend globally. The attention matrix becomes block-sparse:

$$
A =
\begin{bmatrix}
A_{\text{inst}} & A_{\text{inst},q} & 0 & \dots & 0 \\
A_{q,\text{inst}} & A_q & A_{q,d_1} & \dots & A_{q,d_N} \\
0 & A_{d_1,q} & A_{d_1} & 0 & 0 \\
\vdots & \vdots & 0 & \ddots & 0 \\
0 & A_{d_N,q} & 0 & 0 & A_{d_N}
\end{bmatrix}.
$$

This removes document–document interactions and reduces complexity from quadratic in total tokens to linear in document count:

$$
\mathcal{O}(N^2) \rightarrow \mathcal{O}(N).
$$

To align attention with relevance, BlockRank supervises mid-layer attention. Let (a_{q \to d_i}) be attention from selected query tokens to document block (d_i). For a positive document (d^+) and negatives (d^-), the auxiliary contrastive loss is

$$
L_{\text{aux}} = -\log
\frac{\exp(a_{q \to d^+}/\tau)}
{\sum_{j} \exp(a_{q \to d_j}/\tau)}.
$$

Training minimizes

$$
L(\theta) = L_{\text{NTP}}(\theta) + \lambda L_{\text{aux}}(\theta).
$$

Because attention now encodes relevance, inference can rank directly without autoregressive decoding:

$$
\text{score}(d_i) = a_{q \to d_i}.
$$

This yields linear-time ranking over hundreds of candidates while preserving ICR effectiveness.

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-03-01-BlockRank/1772439632920.png?raw=true"> </p>

Experiments on BEIR, MSMarco, and Natural Questions show that structured attention maintains accuracy comparable to full fine-tuning while providing several-fold latency reduction and linear scaling with document count. Ablations confirm that both components are necessary: removing block sparsity harms scalability, while removing attention supervision weakens ranking signal. Thus ranking in ICR emerges from optimized internal attention rather than generation.

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-03-01-BlockRank/1772439698286.png?raw=true"> </p>

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-03-01-BlockRank/1772439706704.png?raw=true"> </p>

Conceptually, BlockRank identifies the minimal attention substructure required for retrieval: query-mediated block interactions. Classical dual encoders approximate relevance via vector similarity; generative ICR uses dense cross-attention; BlockRank constrains attention to structured sparse retrieval paths. This connects neural attention sparsity with symbolic retrieval constraints: both restrict candidate interactions while preserving relevance flow.

For graph-based or on-device retrieval settings, BlockRank provides a compatible abstraction. Knowledge-graph queries naturally form block contexts (entities, relations, subgraphs), federated retrieval resembles multi-document ICR, and sparse attention parallels constrained traversal. Attention-based scoring therefore acts as a neural analogue of structured query evaluation.

## References

* [Gupta, Nilesh, et al. "Scalable In-context Ranking with Generative Models." arXiv preprint arXiv:2510.05396 (2025).](https://arxiv.org/abs/2510.05396)
* [Emergent Mind: In-Context Ranking (ICR)](https://www.emergentmind.com/topics/in-context-ranking-icr)
