---
lang: en
translation_key: 2024-09-18-Towards-Better-Evaluation-for-Dynamic-Link-Prediction
translation_url: /ko/2024/09/18/Towards-Better-Evaluation-for-Dynamic-Link-Prediction.html
title: "Dynamic Link Prediction"
tags: ["graphs", "evaluation", "temporal-graphs"]
subtitle: "Temporal state, negative sampling, and ranking evaluation."
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-11
---

Dynamic link prediction estimates future interactions or ranks their endpoints from a time-ordered history. The observation window, candidate set, and negative sampler define the task; easy negatives can make edge memorization look like prediction.

## Events and targets
{: id="1-events-are-not-a-static-edge-set"}

A temporal graph contains events

$$
\mathcal E=\{(u_i,v_i,t_i,x_i)\}_{i=1}^{m},\qquad t_1\le\cdots\le t_m,
$$

Here $$x_i$$ contains optional event attributes. Repeated $$(u,v)$$ pairs at different times are distinct; a static edge set loses that recurrence.

At time $$t$$, history $$\mathcal H_{<t}$$ supports targets such as

$$
\Pr\big((u,v)\text{ interacts in }[t,t+\Delta)\mid\mathcal H_{<t}\big).
$$

Alternatively, a source and event time define a destination-ranking task. Event probabilities need a horizon $$\Delta$$ and candidate-pair distribution; conditional rankings need not be calibrated probabilities.

## Chronological state
{: id="2-chronological-splits-and-causal-features"}

Training, validation, and test occupy ordered intervals. At $$t$$, embeddings, neighborhoods, normalization, and learned preprocessing can use only permitted earlier information.

Frozen-history evaluation keeps its pre-test history unchanged throughout the test period. Online replay predicts each test event before adding it to history. These protocols model different deployments and produce different EdgeBank and neural scores.

When events are simultaneous, their order within a stored file does not make one available before the other. They form a timestamp batch: predict all from strictly earlier history, then update together. Within-batch updates otherwise expose unavailable information.

## New pairs and nodes
{: id="3-new-edges-and-new-nodes-are-different"}

For endpoint-pair sets $$E_{\mathrm{train}}$$ and $$E_{\mathrm{test}}$$,

$$
E_{\mathrm{test}}\cap E_{\mathrm{train}}
$$

contains recurring pairs; $$E_{\mathrm{test}}\setminus E_{\mathrm{train}}$$ contains new pairs, possibly between familiar nodes.

Node sets $$V_{\mathrm{train}}$$ and $$V_{\mathrm{test}}$$ define another split: an edge touching $$V_{\mathrm{test}}\setminus V_{\mathrm{train}}$$ tests new-node generalization. A benchmark’s “inductive negative sampling” follows its own protocol definition.

For timestamp pairs $$E_t$$ and previous pairs $$E_{<t}=\bigcup_{s<t}E_s$$, the new-pair fraction is

$$
\nu_t=\frac{\vert E_t\setminus E_{<t}\vert }{\vert E_t\vert },\qquad \vert E_t\vert >0.
$$

This denominator counts unique timestamp pairs rather than the number of event records. Weighting repeated events instead defines a different appearance fraction.

## Negative sampling
{: id="4-what-negative-sampling-really-changes"}

An unobserved candidate is not necessarily impossible or permanently absent. Missing and delayed observations can become false negatives under a different target definition.

Random destinations are often easy negatives in sparse graphs. Historical negatives use previously seen pairs absent from the current positive batch; other protocols use pairs absent from training. These choices alter model rankings and memorization advantages. [Poursafaei et al., 2022](https://proceedings.neurips.cc/paper_files/paper/2022/hash/d49042a5d49818711c401d34172f9900-Abstract-Datasets_and_Benchmarks.html).

Binary scores fit the sampled distribution. If sampling changes only the class prior, preserving class-conditional feature distributions, posterior odds obey

$$
\frac{p_{\mathrm{deploy}}(1\mid x)}{1-p_{\mathrm{deploy}}(1\mid x)}
=
\frac{p_{\mathrm{sample}}(1\mid x)}{1-p_{\mathrm{sample}}(1\mid x)}
\frac{\pi_{\mathrm{deploy}}/(1-\pi_{\mathrm{deploy}})}{\pi_{\mathrm{sample}}/(1-\pi_{\mathrm{sample}})}.
$$

Hard negatives can change those conditional distributions, invalidating prior-only correction to deployment probabilities.

## EdgeBank
{: id="5-edgebank-as-a-transparent-baseline"}

Infinite-memory EdgeBank scores prior membership:

$$
s_t(u,v)=\mathbf1\{(u,v)\in E_{<t}\}.
$$

A windowed version keeps $$[t-w,t)$$, selecting $$w$$ on validation data. Hash membership takes expected $$O(1)$$ time and $$O(\vert E_{<t}\vert )$$ storage for unique pairs, not events.

This one-bit rule separates recurring positives from unseen negatives without fitting any parameters. Historical negatives challenge that separation, making EdgeBank a probe of sampler difficulty.

Online replay follows this order:

```text
for each timestamp batch:
    score positives and fixed negatives from earlier history
    record metrics
    add the current positive batch to history, if the protocol permits updates
```

Scoring after adding the current positive would leak its label.

## Ranking metrics
{: id="6-ranking-metrics-and-candidate-sets"}

For positive score $$s^+$$ and $$K$$ negative scores $$s_j^-$$, pessimistic rank is

$$
r=1+\sum_{j=1}^{K}\mathbf1\{s_j^-\ge s^+\}.
$$

Without ties this is the usual rank; optimistic rank counts only strictly higher negatives, while pessimistic and average conventions treat ties differently. Across $$n$$ events,

$$
\mathrm{MRR}=\frac1n\sum_i\frac1{r_i},\qquad
\mathrm{Hits@}k=\frac1n\sum_i\mathbf1\{r_i\le k\}.
$$

Increasing candidate count or difficulty can lower both metrics for an unchanged scorer. MRR with one negative and MRR with hundreds describe different tests.

AUROC measures pairwise ordering; average precision also depends strongly on prevalence. Sampler, candidate count, class ratio, ties, and aggregation define the result. Source-macro averaging weights sources equally; event-micro averaging weights their event counts. Skewed activity therefore changes their interpretation.

## Benchmark protocols
{: id="7-modern-benchmark-practice"}

[Temporal Graph Benchmark](https://arxiv.org/abs/2307.01026) supplies dataset-specific negatives and evaluators in its [repository](https://github.com/shenyangHuang/TGB). Preserving them enables leaderboard comparisons; deployment-specific variants form separate evaluations.

Dataset revisions, event order, negative-file checksums, configurations, seeds, resets, and validation selection determine reproducibility. Matched histories support EdgeBank, static, and temporal comparisons, with new-pair, recurring-pair, and new-node slices where sufficiently populated.

Replay throughput, online latency, and memory complement prediction quality. A recurrent-state advantage may exceed a constrained device’s resources.

## Failure modes
{: id="8-common-failure-cases"}

Full-graph embeddings can leak across a time split. Simultaneous positives are invalid negatives. High AUC need not imply calibrated probabilities, and one interaction network does not establish cross-process generalization.

## References
{: id="references"}

- [Towards Better Evaluation for Dynamic Link Prediction, NeurIPS 2022](https://proceedings.neurips.cc/paper_files/paper/2022/hash/d49042a5d49818711c401d34172f9900-Abstract-Datasets_and_Benchmarks.html).
- [DGB and EdgeBank implementation](https://github.com/fpour/DGB).
- [TGB paper](https://arxiv.org/abs/2307.01026) and [code](https://github.com/shenyangHuang/TGB).
- [Temporal Graph Networks](https://arxiv.org/abs/2006.10637), [JODIE](https://arxiv.org/abs/1908.01207), and [CAWN](https://arxiv.org/abs/2101.05974).
