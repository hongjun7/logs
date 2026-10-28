---
lang: en
translation_key: 2024-09-18-Towards-Better-Evaluation-for-Dynamic-Link-Prediction
translation_url: /ko/2024/09/18/Towards-Better-Evaluation-for-Dynamic-Link-Prediction.html
title: "Dynamic Link Prediction: Time, Negative Samples, and Honest Evaluation"
tags: ["graphs", "evaluation", "temporal-graphs"]
subtitle: "Why temporal prediction can look solved under easy negatives, how EdgeBank exposes memorization, and how modern temporal benchmarks define a reproducible protocol."
last_modified_at: 2026-10-11
sources_checked_at: 2026-10-11
---

> **The idea in one minute.** Predicting a future interaction is meaningful only relative to a time horizon and a candidate set. Easy random negatives can reward remembering old edges rather than identifying the next interaction. Chronological splits, difficult but valid negatives, and a simple EdgeBank baseline reveal how much a model actually learns.

**Reading path.** Begin with the prediction target and chronological state. Then inspect how negative sampling changes the measured problem. The ranking formulas and current benchmark resources follow. Prerequisites are graphs, sets, and binary classification.

## 1. Events are not a static edge set

A temporal graph contains events

$$
\mathcal E=\{(u_i,v_i,t_i,x_i)\}_{i=1}^{m},\qquad t_1\le\cdots\le t_m,
$$

with optional event attributes $$x_i$$. Repeated $$(u,v)$$ pairs at different times remain distinct events. A static edge set would collapse them and lose the recurrence pattern.

At prediction time $$t$$, the available history is $$\mathcal H_{<t}$$. One possible target is

$$
\Pr\big((u,v)\text{ interacts in }[t,t+\Delta)\mid\mathcal H_{<t}\big).
$$

Another is ranking the observed destination among candidates for a given source and event time. These are different tasks. The first requires a defined horizon $$\Delta$$ and a distribution over candidate pairs; the second is a conditional ranking test and need not yield calibrated real-world event probabilities.

## 2. Chronological splits and causal features

Use ordered intervals for training, validation, and test. A model at time $$t$$ must not see later events through an embedding, graph neighborhood, normalization statistic, or preprocessing step. Fit learned preprocessing only on permitted training information.

During evaluation, distinguish two protocols: a frozen-history setting that never updates from test events, and online replay that predicts each test event before adding it to history. Both can be reasonable for different deployment scenarios. They yield different EdgeBank and neural-model performance, so state the choice.

Events sharing a timestamp require a policy. If they represent simultaneous observations, predicting one after updating with another at the same time can introduce artificial information. Predict a timestamp batch using the history strictly before that timestamp, then update with the batch.

## 3. New edges and new nodes are different

Let $$E_{\mathrm{train}}$$ and $$E_{\mathrm{test}}$$ denote sets of endpoint pairs appearing in each period. Then

$$
E_{\mathrm{test}}\cap E_{\mathrm{train}}
$$

contains recurring pairs, while $$E_{\mathrm{test}}\setminus E_{\mathrm{train}}$$ contains new pairs. A new pair can connect two familiar nodes. It is therefore not automatically a new-node inductive example.

Separately define node sets $$V_{\mathrm{train}}$$ and $$V_{\mathrm{test}}$$. A test edge touching $$V_{\mathrm{test}}\setminus V_{\mathrm{train}}$$ tests a different generalization problem. “Inductive negative sampling” in a named benchmark is a protocol label; read its definition rather than infer it from the word inductive.

For a timestamp edge set $$E_t$$, define prior pairs $$E_{<t}=\bigcup_{s<t}E_s$$. A simple new-pair fraction is

$$
\nu_t=\frac{\vert E_t\setminus E_{<t}\vert }{\vert E_t\vert },\qquad \vert E_t\vert >0.
$$

This counts unique pairs at a timestamp, not event multiplicities. A stream with repeated events can have a different event-weighted fraction. State the denominator when using temporal edge-appearance plots.

## 4. What negative sampling really changes

Positive events are observed interactions. Negative candidates often mean “not observed at this evaluation time,” not “impossible” and not “will never occur.” Missing observations and delayed interactions can produce false negatives relative to another target definition.

Randomly selecting an arbitrary destination can create extremely easy negatives, particularly in a sparse graph. Historical negatives instead emphasize pairs seen previously but absent from the current positive batch. Other protocols emphasize pairs absent from training. The 2022 evaluation paper studies how these choices change rankings and exposes the strength of memorization. [Poursafaei et al.](https://proceedings.neurips.cc/paper_files/paper/2022/hash/d49042a5d49818711c401d34172f9900-Abstract-Datasets_and_Benchmarks.html).

For a sampled binary dataset, a score estimates the positive class under the **sampled distribution**. If sampling only changes the class prior while leaving class-conditional feature distributions unchanged, prior correction obeys

$$
\frac{p_{\mathrm{deploy}}(1\mid x)}{1-p_{\mathrm{deploy}}(1\mid x)}
=
\frac{p_{\mathrm{sample}}(1\mid x)}{1-p_{\mathrm{sample}}(1\mid x)}
\frac{\pi_{\mathrm{deploy}}/(1-\pi_{\mathrm{deploy}})}{\pi_{\mathrm{sample}}/(1-\pi_{\mathrm{sample}})}.
$$

This assumption often fails when hard negatives change the conditional distribution itself. In that case, a simple prior correction cannot turn sampled classifier outputs into deployment probabilities.

## 5. EdgeBank as a transparent baseline

An infinite-memory EdgeBank assigns

$$
s_t(u,v)=\mathbf1\{(u,v)\in E_{<t}\}.
$$

A sliding-window version restricts memory to a recent interval $$[t-w,t)$$. The window $$w$$ is a hyperparameter chosen on validation data. A hash set supports expected $$O(1)$$ membership checks and uses $$O(\vert E_{<t}\vert )$$ storage for unique pairs; that is not necessarily the number of events.

On recurring positives and mostly never-seen random negatives, this one-bit baseline can score well without learning. Historical negatives intentionally challenge it with previously seen pairs that are not current positives. This makes EdgeBank an informative probe of the evaluation distribution rather than a universal replacement for temporal models.

A minimal replay rule is:

```text
for each timestamp batch:
    score positives and fixed negatives from earlier history
    record metrics
    add the current positive batch to history, if the protocol permits updates
```

The order matters. Adding the current positive edge before scoring it turns a baseline into a label leak.

## 6. Ranking metrics and candidate sets

For one positive candidate with score $$s^+$$ and $$K$$ negatives $$s_j^-$$, a pessimistic rank is

$$
r=1+\sum_{j=1}^{K}\mathbf1\{s_j^-\ge s^+\}.
$$

With no ties this is the usual rank. With ties, optimistic, pessimistic, or averaged ranks differ; use the benchmark's evaluator. Over $$n$$ events,

$$
\mathrm{MRR}=\frac1n\sum_i\frac1{r_i},\qquad
\mathrm{Hits@}k=\frac1n\sum_i\mathbf1\{r_i\le k\}.
$$

Increasing the number or difficulty of candidates can lower these metrics for the same score function. Never compare MRR from one negative per positive against MRR from hundreds as though they describe the same task.

AUROC measures pairwise score ordering under sampled positives and negatives. Average precision additionally depends strongly on prevalence and ranking. Report the sampler, candidate count, class ratio, tie treatment, and aggregation unit along with any metric. Macro-averaging over sources and event-weighted micro-averaging answer different questions when activity is skewed.

## 7. Modern benchmark practice

The [Temporal Graph Benchmark paper](https://arxiv.org/abs/2307.01026) and [TGB repository](https://github.com/shenyangHuang/TGB) provide a broader evaluation framework. Use the dataset's prescribed negative samples and evaluator when reporting leaderboard-compatible results, then add a deployment-relevant evaluation with an explicitly different label.

A reproducible experiment records dataset revision, event ordering, negative-file checksum, model configuration, seeds, state-reset policy, and validation selection. Compare EdgeBank, static feature baselines, and temporal methods at matched observation histories. Evaluate new pairs, recurring pairs, and new nodes separately when sample sizes support those slices.

Test time and memory as well: a large recurrent memory may retain an advantage unavailable on a constrained device. Model quality, replay throughput, and online latency are separate measurements.

## 8. Common failure cases

A time split does not prevent leakage if embeddings were trained on the full graph. A hard negative is not valid if it is a simultaneous positive excluded by mistake. A high AUC does not imply calibrated interaction probabilities. A model's strong result on one interaction network does not establish generalization to another event process.

The goal is a clearly defined forecasting or ranking problem, with information available at the correct time. Once that contract is fixed, results become interpretable and comparisons become useful.

## References

- [Towards Better Evaluation for Dynamic Link Prediction, NeurIPS 2022](https://proceedings.neurips.cc/paper_files/paper/2022/hash/d49042a5d49818711c401d34172f9900-Abstract-Datasets_and_Benchmarks.html).
- [DGB and EdgeBank implementation](https://github.com/fpour/DGB).
- [TGB paper](https://arxiv.org/abs/2307.01026) and [code](https://github.com/shenyangHuang/TGB).
- [Temporal Graph Networks](https://arxiv.org/abs/2006.10637), [JODIE](https://arxiv.org/abs/1908.01207), and [CAWN](https://arxiv.org/abs/2101.05974).
