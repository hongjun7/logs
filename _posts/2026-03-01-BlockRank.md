---
lang: en
translation_key: 2026-03-01-BlockRank
translation_url: /ko/2026/03/01/BlockRank.html
title: "BlockRank"
tags: ["machine-learning", "retrieval", "attention"]
subtitle: "Sparse document attention and supervised ranking without autoregressive decoding."
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-11
---

BlockRank reranks candidate documents with sparse attention and a supervised attention readout. Documents read a shared prefix and themselves; final query tokens compare all candidates, allowing ranking without answer-token decoding.

## Candidate layout
{: id="1-reranking-a-shortlist"}

A first-stage retriever supplies $$D_q=(d_1,\ldots,d_N)$$. The ranker places instructions before the documents and a final query segment:

$$
P=I\;\Vert\;d_1\;\Vert\;\cdots\;\Vert\;d_N\;\Vert\;q.
$$

The prefix and final query play different roles. The prefix can already contain the question. Documents are then query-conditioned even though they cannot read the later query segment, whose tokens provide readout positions.

Stable identifiers distinguish candidates and connect scores to returned documents. First-stage recall bounds the end-to-end result: reranking cannot recover omitted documents. [Scalable In-context Ranking with Generative Models](https://arxiv.org/abs/2510.05396).

## Directional attention
{: id="2-attention-and-a-directional-mask"}

For one head with query and key matrices $$Q,K$$ and value matrix $$V$$,

$$
\operatorname{Attn}(Q,K,V;M)
=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}+M\right)V.
$$

Mask entries are zero for permitted pairs and $$-\infty$$ otherwise. Rows read columns; segments follow instruction–documents–query order.

The block mask is

$$
M=\begin{bmatrix}
C_I&-\infty&-\infty&\cdots&-\infty\\
0&C_{d_1}&-\infty&\cdots&-\infty\\
0&-\infty&C_{d_2}&\cdots&-\infty\\
\vdots&\vdots&\vdots&\ddots&\vdots\\
0&0&0&\cdots&C_q
\end{bmatrix},
$$

Diagonal blocks $$C$$ preserve within-segment causality; zero and $$-\infty$$ denote compatible whole blocks. Instructions read earlier instructions. Documents read the prefix and their own past. Final query tokens read the prefix, all documents, and their own past.

No document reads another document or the final query. This asymmetry determines the information flow.

## Complexity
{: id="3-deriving-the-scaling-claim"}

For prefix length $$p$$, final-query length $$q$$, and document lengths $$\ell_1,\ldots,\ell_N$$, total length is $$L=p+q+\sum_i\ell_i$$. Dense attention costs $$O(L^2)$$ token-pair work per layer, omitting feature dimensions.

The permitted pair count for the block construction is of order

$$
p^2+\sum_{i=1}^{N}(\ell_i^2+p\ell_i)
+q\left(p+q+\sum_{i=1}^{N}\ell_i\right).
$$

For bounded document length $$\ell$$ and fixed $$p,q$$, this becomes

$$
O\big(N\ell^2+Np\ell+Nq\ell+p^2+q^2+pq\big),
$$

This scales linearly in $$N$$ only under those bounds. An individual document still has quadratic self-attention cost in its length: doubling its length does not preserve linear cost.

With $$p=q=32$$, $$N=100$$, and $$\ell=128$$, dense attention has about $$(12{,}864)^2\approx165.48$$ million pairs versus $$2.46$$ million permitted pairs under a simplified full-block count. This does not predict a 67-fold speedup: projections, feed-forward layers, padding, kernels, memory access, and launches remain.

Savings require avoiding forbidden blocks with sparse or chunked kernels; masking an already computed dense matrix saves no pair computation.

## Position encoding
{: id="4-local-positions-and-candidate-order"}

BlockRank shares local document positions across blocks after the instruction positions and reserves a separate final-query region, reducing list-position bias.

Identifiers, truncation, padding, implementation, and numerical ties can still affect permutation invariance. A query-bearing prefix also makes document representations query-dependent, preventing a single cache for all queries.

## Attention supervision
{: id="5-turn-attention-into-a-supervised-ranking-signal"}

At layer $$\ell^*$$, query carrier tokens $$S$$ score document tokens. For carrier $$i$$ and document token $$j$$, normalize only over document tokens:

$$
z_{ij}=\frac{Q_iK_j^\top}{\sqrt{d_k}},\qquad
\alpha'_{ij}=\frac{e^{z_{ij}}}{\sum_{j'\in T_D}e^{z_{ij'}}}.
$$

Define document mass

$$
s_k=\sum_{i\in S}\sum_{j\in T_{d_k}}\alpha'_{ij}.
$$

Using a carrier mean instead changes the scale and effective loss temperature. Under this sum, $$\sum_k s_k=\vert S\vert $$. Mass ranks candidates without necessarily calibrating relevance probabilities.

For labeled positive document $$d^+$$, a contrastive loss is

$$
\mathcal L_{\mathrm{aux}}
=-\log\frac{\exp(s_+/\tau)}{\sum_k\exp(s_k/\tau)},
\qquad\tau>0.
$$

Training combines answer-token next-token prediction with this auxiliary loss:

$$
\mathcal L=\mathcal L_{\mathrm{NTP}}+\lambda\mathcal L_{\mathrm{aux}},\qquad\lambda\ge0.
$$

The auxiliary loss trains the readout to favor a labeled positive while next-token prediction trains the answer output. Supervision gives the attention readout its ranking role; arbitrary pretrained attention has no such guarantee. Token normalization and document aggregation can introduce length effects, so length distribution and truncation remain relevant.

## Direct readout
{: id="6-direct-inference-without-decoding"}

Inference stops at the chosen layer, computes masses, and returns $$\arg\max_k s_k$$ or a sorted list. It avoids autoregressive ranking tokens and can skip subsequent layers.

Every retained candidate still requires document processing and query-to-document attention. Early readout can remove later network and decoding work, not the cost of reading the shortlist. Corpus-scale retrieval therefore needs a first-stage index.

A full ordering of $$N$$ scores costs $$O(N\log N)$$; maximum selection costs $$O(N)$$. Linear model scoring and output sorting are separate costs.

## Reported performance
{: id="7-performance-evidence-and-its-boundary"}

The authors report $$4.7\times$$ faster inference on 100-document MSMARCO and about 500 documents, or 100K context tokens, within one second. These model-, hardware-, formatting-, and baseline-specific measurements were not reproduced here. [Experimental setup](https://arxiv.org/html/2510.05396v1).

Dense fine-tuning, unsupervised sparse attention, supervised attention readout, and autoregressive readout isolate different contributions. Matched candidates, lengths, models, training data, precision, hardware, and outputs support comparisons of nDCG/MRR, p50/p95 latency, peak memory, and first-stage recall.

Knowledge-graph blocks and mobile retrieval require new representations, kernels, and matched experiments; the reported text results do not establish those extensions.

## Decision scores
{: id="8-connections-to-decision-models"}

Like typed decision models, BlockRank extracts scores without prose generation. Its final query compares documents; a multi-question service may instead isolate questions over shared state. Similar outputs do not imply identical information flow.

Sparse attention specifies communication and compute. Calibration and downstream thresholds need their own training and evaluation.

## References
{: id="references-and-current-scope"}

- [Gupta et al., Scalable In-context Ranking with Generative Models](https://arxiv.org/abs/2510.05396).
- [Full HTML paper, including mask, loss, and complexity analysis](https://arxiv.org/html/2510.05396v1).
- [BEIR](https://github.com/beir-cellar/beir): retrieval evaluation.
