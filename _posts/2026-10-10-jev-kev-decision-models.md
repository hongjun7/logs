---
title: "Jev and Kev: Decision Models, Calibrated Probabilities, and Open-Source Deployment"
tags: ["machine-learning", "decision-models", "calibration", "open-source", "engineering"]
subtitle: "From categorical probability and decision theory to Jev\u2019s typed API, Kev\u2019s pointer head, benchmarks with stated measurement conditions, and a reproducible local workflow."
last_modified_at: 2026-10-11
sources_checked_at: 2026-10-11
---

> **The idea in one minute.** Jev answers questions about supplied information with a finite probability distribution rather than a generated paragraph. Kev provides an open implementation of this decision-model pattern. A routing system can use the distribution to choose an action or request review. The difficult part is establishing what the probabilities mean on your data, how errors cost money or time, and whether the measurements transfer to your deployment.

**Reading path.** Sections 1–4 introduce the API and probability language. Sections 5–7 develop calibration and decision theory. Sections 8–10 explain the open implementation and reported measurements. Sections 11–13 give a local workflow, training design, and alternatives. You need elementary algebra first; the later sections introduce vectors, expectation, and logarithms as they become necessary.

**Date and evidence.** Published October 10, 2026; references checked October 11. To make the dated open-source examples reproducible, Kev is pinned to [`fc4a17e`](https://github.com/jaredpalmer/kev/tree/fc4a17e194bca35a48c57211392ec49ea54a94ac), a revision available by the end of October 10 in Korea. API documentation is a live reference and can change. Reported benchmarks below belong to their authors; this article does not claim to have run Jev or Kev inference.

## 1. What problem does a decision model solve?

Suppose a support ticket says: “I was charged twice. Please refund the duplicate charge.” We might ask which team should handle it, whether urgent review is needed, and how severe the problem is. These are bounded decisions. A paragraph can explain a judgment, but production code ultimately needs a label, a numerical score, or a yes/no value.

Let $$x$$ denote the supplied **state**, $$q$$ the question and instructions, and $$C=(c_1,\ldots,c_K)$$ the candidate descriptions. A conditional classifier returns

$$
p_\theta(y=k\mid x,q,C),\qquad p_k\ge0,\qquad\sum_{k=1}^{K}p_k=1.
$$

Here $$\theta$$ denotes learned parameters. The output is a point in the probability simplex $$\Delta^{K-1}$$. If an ordinary generative language model produces $$M$$ tokens, its sequence likelihood factorizes as

$$
p_\theta(t_{1:M}\mid x)=\prod_{j=1}^{M}p_\theta(t_j\mid x,t_{1:j-1}).
$$

A decision model targets the finite decision directly. This removes the need to generate a long answer and parse it. It still processes input tokens, forms contextual representations, and computes output scores. “No generated explanation” does not imply zero inference work or a proof that the decision is correct.

[TypeSafe's introduction](https://docs.typesafe.ai/introduction) presents Jev as its hosted System One model. Its release material calls the training approach **Reinforcement Learning for Calibrated Decisions (RLCD)**. The complete training data, weights, architecture, and reproducible original recipe are not publicly established by these documents. A community implementation of a similar interface is evidence about that implementation, rather than proof of Jev's internal computation. See [the official introduction article](https://typesafe.ai/blog/introducing-system-one-models-and-jev).

## 2. Three primitives: Choice, Noul, and Score

| Primitive | Mathematical output | Suitable question | Main interpretation risk |
|---|---|---|---|
| Choice | Distribution on $$K$$ unordered options | Which team: billing, shipping, or account access? | The true answer may be outside the option set |
| Noul | Probability $$p$$ of “yes” | Does this ticket mention a duplicate charge? | A threshold is a policy choice |
| Score | Distribution on ordered levels and its mean index | Low, normal, or high urgency? | Ordered labels do not imply equally spaced real-world severity |

For Choice, the selected option usually maximizes probability:

$$
\widehat y=\operatorname*{arg\,max}_{k}p_k.
$$

For Noul, interpret the two outcomes as $$(1-p,p)$$. A $$0.5$$ threshold minimizes symmetric binary misclassification loss **if** $$p$$ is the true posterior. Different costs give a different threshold, derived below.

For Score, number $$K$$ ordered levels $$0,\ldots,K-1$$. The returned mean is

$$
\overline s=\sum_{i=0}^{K-1}i\,p_i.
$$

For $$(p_0,p_1,p_2)=(0,0.57,0.43)$$, this gives $$1.43$$. It is not a fourth label between levels 1 and 2. It is the mean of a distribution under the chosen numerical encoding. Replacing the encoding $$(0,1,2)$$ with $$(0,1,10)$$ changes the mean; ordinal information alone cannot justify the original spacing. Keep the full distribution when real costs are nonlinear. The [Choice](https://docs.typesafe.ai/primitives/choice), [Noul](https://docs.typesafe.ai/primitives/noul), and [Score](https://docs.typesafe.ai/primitives/score) documentation define the request and response fields.

A request may ask several questions about one state. Questions are evaluated without reading one another's answers. This computational separation does **not** imply that their target labels are statistically independent. Duplicate billing and customer frustration can be correlated even when their model branches cannot communicate.

## 3. Why an option probability is conditional

If we remove “billing” from the candidate set, a classifier must distribute its mass among the remaining choices. A high resulting maximum can be a confident wrong answer. In particular,

$$
p(y=k\mid x,q,C)\ne p(y=k\mid x,q,C')
$$

in general when $$C\ne C'$$. Adding a “none of these / insufficient evidence” option can represent an important missing outcome, but does not guarantee that the model recognizes every unfamiliar input.

Make candidate descriptions operational. “Billing” could mean invoices, payments, duplicate charges, and refunds; specify how mixed tickets should be routed. Decide whether the task is single-label or multi-label. If both billing and shipping are true, a single Choice forces one winner. Separate Nouls can model individual properties, although their marginal probabilities do not specify a joint distribution.

For example, if $$\Pr(A)=0.8$$ and $$\Pr(B)=0.7$$, their intersection satisfies the Fréchet bounds

$$
0.5=\max(0,0.8+0.7-1)\le \Pr(A\cap B)\le\min(0.8,0.7)=0.7.
$$

The value $$0.56$$ follows only from an additional independence assumption. Multiplying independent *model calls* is not a justification for that assumption.

## 4. Confidence is a summary of the distribution

TypeSafe's [confidence specification](https://docs.typesafe.ai/confidence) defines the following statistics. For Choice, let $$K$$ be the number of options, with at least two options:

$$
c_{\mathrm{choice}}=\frac{p_{\max}-1/K}{1-1/K}.
$$

It maps a uniform distribution to 0 and a point mass to 1. For $$(0.6,0.3,0.1)$$, it is $$0.4$$. It is **not** an estimated probability of correctness. Noul returns $$p$$ directly; the analogous optional summary is $$\vert 2p-1\vert $$.

For Score, take a mode $$m=\arg\max_i p_i$$ and define

$$
\begin{aligned}
D_K&=\frac1K\sum_{i=0}^{K-1}\left\vert i-\frac{K-1}{2}\right\vert ,\\
c_{\mathrm{score}}&=\max\left(0,1-\frac{\sum_i p_i\vert i-m\vert }{D_K}\right).
\end{aligned}
$$

Use the implementation's tie convention for the mode. At $$K=3$$, $$D_K=2/3$$; $$(0,0.57,0.43)$$ has $$c_{\mathrm{score}}=0.355$$. The mean is still $$1.43$$.

For Choice, the threshold conversion is an algebraic consequence:

$$
c_{\mathrm{choice}}\ge t
\quad\Longleftrightarrow\quad
p_{\max}\ge\frac1K+t\left(1-\frac1K\right).
$$

Thus $$t=0.9$$ at $$K=3$$ requires $$p_{\max}\ge0.933\overline3$$. A confidence value cannot be substituted for $$p_{\max}$$ in a cost formula. Also, $$D_K=K/4$$ for even $$K$$, and $$D_K=(K^2-1)/(4K)$$ for odd $$K$$: both follow by pairing distances around the midpoint. The denominator is positive for $$K\ge2$$; the single-option case requires a separate convention.

<div class="probability-explorer" data-probability-explorer>
  <h3>Try a three-option distribution</h3>
  <p>Change nonnegative weights. The example normalizes them into probabilities; it does not call a model. Use Choice for unordered labels, or Score for levels 0, 1, 2.</p>
  <div class="probability-controls">
    <label>Option / level 0 <input type="range" min="0" max="100" value="60" data-weight="0"></label>
    <label>Option / level 1 <input type="range" min="0" max="100" value="30" data-weight="1"></label>
    <label>Option / level 2 <input type="range" min="0" max="100" value="10" data-weight="2"></label>
  </div>
  <div class="probability-bars" aria-hidden="true"><span data-bar="0"></span><span data-bar="1"></span><span data-bar="2"></span></div>
  <p class="probability-result" aria-live="polite" data-result>Loading the probability example…</p>
  <noscript><p>Initial values: probabilities (0.600, 0.300, 0.100), Choice confidence 0.400, mean level 0.500, Score confidence 0.250. Enable JavaScript to adjust the weights.</p></noscript>
</div>

## 5. Accuracy, calibration, and proper scoring rules

A model can be accurate and poorly calibrated. Suppose it predicts a top probability of $$0.95$$ for 1,000 comparable tickets but is right on only 800. Its accuracy on those tickets is $$0.8$$, while its probability estimates are too concentrated.

Let $$Y$$ be the true class and $$P$$ the random predicted vector. **Top-label calibration** asks that, for probability values with support,

$$
\Pr(Y=\widehat Y\mid P_{\max}=s)=s.
$$

Classwise calibration asks $$\Pr(Y=k\mid P_k=s)=s$$ for every class $$k$$. Full-vector calibration asks $$\Pr(Y=k\mid P)=P_k$$ almost surely; this is stronger than each marginal classwise condition. In continuous settings these are statements about conditional expectations, rather than ratios of counts in an exact singleton bin. Empirical bins approximate them.

Accuracy discards every probability except the winning label. The multiclass negative log-likelihood and Brier score retain the distribution:

$$
\mathrm{NLL}=-\frac1n\sum_{j=1}^{n}\log p_{j,y_j},
\qquad
\mathrm{Brier}=\frac1n\sum_{j=1}^{n}\sum_{k=1}^{K}
\left(p_{j,k}-\mathbf1\{y_j=k\}\right)^2.
$$

NLL is unbounded when the model assigns arbitrarily small mass to the correct label. This **full multiclass** Brier convention lies in $$[0,2]$$. Binary Brier is sometimes reported using only the positive probability, in $$[0,1]$$; the full two-component score is twice that value. Always record the convention before comparing numbers.

To see why both are proper, fix an input with true conditional vector $$q$$ and prediction $$p$$. Then

$$
\mathbb E_{Y\sim q}[-\log p_Y]=H(q)+D_{\mathrm{KL}}(q\Vert p),
$$

and

$$
\mathbb E_{Y\sim q}\left[\sum_k(p_k-\mathbf1\{Y=k\})^2\right]
=\|p-q\|_2^2+1-\|q\|_2^2.
$$

The second identity follows by expanding the square and using $$\mathbb E[\mathbf1\{Y=k\}]=q_k$$. Both expectations are minimized at $$p=q$$. This is a population result under the stated distribution, not a promise that minimizing a finite training loss calibrates an unfamiliar domain.

### Why rewarding the winning label is insufficient

A simple bandit-style reward illustrates the difference. Suppose an action label $$A$$ is sampled from $$p$$ independently of the unknown label $$Y\sim q$$, conditional on the input. With reward $$\mathbf1\{A=Y\}$$,

$$
\mathbb E[R]=\sum_k p_kq_k.
$$

This is linear in $$p$$ and is maximized by putting all mass on a class with maximal $$q_k$$. At $$q=(0.6,0.4)$$, the deterministic $$p=(1,0)$$ earns expected reward $$0.6$$, whereas $$p=q$$ earns $$0.52$$. Maximizing this reward identifies a good discrete action but does not recover calibrated probabilities.

By contrast, rewarding the whole distribution with negative Brier score has expected reward

$$
\mathbb E[R(p,Y)]=-\|p-q\|_2^2-1+\|q\|_2^2,
$$

uniquely maximized at $$p=q$$. The distinction explains why a training objective for probabilistic decisions must care about more than whether the most likely label wins. It is an illustrative objective comparison, **not a disclosure of Jev's RLCD reward or training algorithm**. Supervised cross-entropy is already a proper objective; reinforcement learning is one possible optimization framework, not a prerequisite for producing calibrated distributions.

A binned expected calibration error is

$$
\mathrm{ECE}=\sum_{b=1}^{B}\frac{\vert I_b\vert }{n}
\left\vert \mathrm{acc}(I_b)-\mathrm{conf}(I_b)\right\vert .
$$

For a top-label ECE, `conf` means mean **top probability**, not the API's rescaled confidence. Results depend on binning and sample size; different errors can cancel within a bin. Report a reliability diagram, NLL, Brier, and class or workload slices alongside ECE.

### Temperature scaling

Given logits $$z_1,\ldots,z_K$$, temperature $$\tau>0$$ gives

$$
p_k^{(\tau)}=\frac{\exp(z_k/\tau)}{\sum_{i=1}^{K}\exp(z_i/\tau)}.
$$

Fit $$\tau$$ by minimizing NLL on a held-out calibration split. Increasing $$\tau$$ softens the distribution; decreasing it sharpens it. A positive temperature preserves the argmax **within each example**, so it cannot fix classification errors. In multiclass problems it can change the ordering of maximum probabilities **across different examples**, because the entire logit vector participates in normalization. Do not assume every selective-coverage curve is invariant.

[Guo et al., On Calibration of Modern Neural Networks](https://proceedings.mlr.press/v70/guo17a.html) studies temperature scaling. The fitted temperature is specific to a model and calibration distribution. Refitting after a domain change requires new labeled evidence; a shipped temperature is a starting point.

## 6. Derive the action from its loss

Let $$L(a,y)$$ be the cost of action $$a$$ when the truth is $$y$$. Under a calibrated posterior, the Bayes action minimizes conditional expected loss:

$$
a^*(x)=\operatorname*{arg\,min}_a\sum_y L(a,y)p(y\mid x).
$$

For a binary decision, let a false positive cost $$C_{\mathrm{FP}}>0$$ and a false negative cost $$C_{\mathrm{FN}}>0$$, with correct decisions costing zero. Acting positive has risk $$C_{\mathrm{FP}}(1-p)$$; acting negative has risk $$C_{\mathrm{FN}}p$$. Hence

$$
\text{choose positive iff}\quad
p\ge\frac{C_{\mathrm{FP}}}{C_{\mathrm{FP}}+C_{\mathrm{FN}}}.
$$

If $$C_{\mathrm{FP}}=9$$ and $$C_{\mathrm{FN}}=1$$, the threshold is $$0.9$$. If missing an urgent ticket costs nine times more than reviewing a normal one, interchange the costs and the threshold becomes $$0.1$$. Neither follows from a universal confidence cutoff.

For multiclass routing, suppose every wrong route costs $$C_w$$ and every correct route costs zero. The risk of the best automatic route is $$C_w(1-p_{\max})$$. If a **perfect** reviewer costs $$C_r$$ per case, choose automatic routing when

$$
p_{\max}\ge1-\frac{C_r}{C_w}.
$$

With $$C_w=10$$ and $$C_r=1$$, the probability threshold is $$0.9$$, which corresponds to Choice confidence $$0.85$$ at $$K=3$$. Real reviewers are not perfect: add their residual error cost and waiting cost before making the comparison. If wrong routes have different consequences, use the full loss matrix rather than its uniform-cost simplification.

For ordered scores, squared-error loss is minimized by the conditional mean; absolute-error loss is minimized by a conditional median. To derive the first result, expand

$$
\mathbb E[(a-Y)^2\mid x]=(a-\mathbb E[Y\mid x])^2+\operatorname{Var}(Y\mid x).
$$

The variance term does not depend on $$a$$. This explains the mathematical usefulness of the mean score while exposing the assumption that numeric level distances carry the intended meaning.

## 7. Measure coverage and residual risk

For an acceptance rule $$A_t=\mathbf1\{s(x)\ge t\}$$, define

$$
\mathrm{coverage}(t)=\Pr(A_t=1),
\qquad
\mathrm{risk}(t)=\Pr(\widehat Y\ne Y\mid A_t=1).
$$

Risk is undefined when no cases are accepted. The useful deployment question is often “what fraction can we automate while keeping accepted-case error below $$\epsilon$$?” Plot risk against coverage on untouched evaluation data, and report accepted counts. High overall accuracy can hide substantial risk in one language or a new routing category.

For a fixed threshold and $$n_a$$ independent, identically distributed accepted test cases with binary error indicators, Hoeffding's bound gives

$$
\Pr(R>\widehat R+\eta)\le e^{-2n_a\eta^2},
\qquad
\eta=\sqrt{\frac{\log(1/\delta)}{2n_a}}.
$$

This supplies a one-sided upper bound at confidence $$1-\delta$$, subject to the independence and sampling assumptions. If no errors occur, the exact binomial one-sided upper limit is

$$
R_{\mathrm{upper}}=1-\delta^{1/n_a}.
$$

At $$\delta=0.05$$ and $$n_a=100$$, it is approximately $$0.0295$$. Zero observed errors do not establish zero risk. The familiar “three over $$n$$” approximation follows from $$-\log(0.05)\approx3$$.

Choose thresholds on development data; then estimate final risk once on a separate test set. Searching many thresholds on that same test set invalidates the naive fixed-threshold guarantee. Customer-level clustering, temporal drift, and repeated near-duplicate tickets also weaken an iid argument; split by the unit that will change in production and report that unit.

## 8. What the open Kev implementation actually computes

[Kev's pinned source](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/kev/model.py) makes its architecture inspectable. It encodes the state, question, candidate descriptions, and a decision marker. Let $$h_d\in\mathbb R^d$$ be the decision representation and $$h_i\in\mathbb R^d$$ an option representation. Its learned pointer head applies affine projections

$$
\begin{aligned}
u&=W_qh_d+b_q,\\
v_i&=W_kh_i+b_k,\\
z_i&=\frac{v_i^\top u}{\sqrt{d_p}}.
\end{aligned}
$$

then a temperature-scaled softmax. Here $$d_p$$ is the projection dimension, not the number of options. This produces an option-index distribution; it is not a fixed vocabulary-generation head. Candidate descriptions can therefore change between requests.

The head's projection work is $$O((K+1)dd_p)$$ and dot-product work is $$O(Kd_p)$$. Those bounds exclude the backbone, which normally dominates. Choosing fewer options does not remove the state-encoding cost.

### Shared state and separate branches

For a pure attention backbone, a conceptual block-causal layout allows question branches to read a common state prefix but blocks access to sibling questions. With state length $$S$$, branch lengths $$Q_1,\ldots,Q_m$$, allowed attention-pair work has the form

$$
O\left(S^2+\sum_{j=1}^{m}(SQ_j+Q_j^2)\right)
$$

under an implementation that exploits the mask. A dense masked kernel may still compute disallowed pairs; a mask alone is not a speedup proof. In the open source, packed pure-attention inputs also have a token-length guard.

Current Kev-0.8B, 4B, and 9B use Qwen3.5 base models with LoRA adapters and a pointer head. Their hybrid attention/recurrent layers cannot simply honor the same packed attention mask. The code chooses separate causal rows, can reuse a shared prefix, and clones recurrent state for independent continuations. It also sanitizes reserved marker spellings in caller text. These are concrete implementation details; they do not establish universal immunity to semantic prompt injection.

Kev-27B uses a post-trained Qwen3.8 base and full-weight fine-tuning. It differs in base, size, and training configuration, so a comparison with smaller Kev models is not a controlled ablation of parameter count alone. The [pinned README and model cards](https://github.com/jaredpalmer/kev/tree/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards) document the released recipes.

### Compare with a language-model label baseline

A next-token baseline can restrict a generative model to single-token label IDs and normalize their logits. This is a useful comparator, not automatically a calibrated decision model. For multi-token label strings $$\ell_k$$, compute their full conditional sequence log-likelihoods, including an appropriate boundary convention:

$$
a_k=\log p_\theta(\ell_k\mid x,q),
\qquad
\widetilde p_k=\frac{e^{a_k}}{\sum_i e^{a_i}}.
$$

This is a conditional distribution over the selected strings, not necessarily over semantic classes: length, spelling, tokenization, and synonymous realizations matter. [LLM-as-Jev](https://arxiv.org/abs/2610.02076) studies training language models for direct probabilistic decisions. Its results support investigating this baseline; they do not identify Jev's proprietary architecture.

## 9. Read performance tables without changing their meaning

The following values are **Kev-maintainer measurements** for `transfer-v4` (656 questions in each development/test panel), taken from the pinned model cards. The cards describe evaluation sources and policy rules absent from Kev training. Development data selects checkpoints; test data is reported separately.

| Model | New-source accuracy, dev | New-source accuracy, test | Full Brier, dev | Full Brier, test |
|---|---:|---:|---:|---:|
| Kev-0.8B | 0.648 | 0.697 | 0.430 | 0.397 |
| Kev-4B | 0.817 | 0.838 | 0.243 | 0.224 |
| Kev-9B v2 | 0.820 | 0.852 | 0.262 | 0.199 |
| Kev-27B v2 | 0.851 | 0.889 | 0.218 | 0.154 |
| Jev | 0.857 | Not reported | 0.211 | Not reported |

Sources: [0.8B card](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-0.8b.md), [4B card](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-4b.md), [9B card](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-9b.md), and [27B card](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-27b.md). **Source discrepancy:** the overview README at the same revision lists different Brier values, for example 0.269 / 0.242 for 4B. This table follows the detailed model cards; the discrepancy is not independently resolved by rerunning their evaluation.

The valid same-split comparison is Kev-27B development accuracy $$0.851$$ versus Jev $$0.857$$, a difference of $$0.006$$ or **0.6 percentage points**. Comparing Kev's $$0.889$$ test accuracy with Jev's $$0.857$$ development accuracy would change the question. Jev's training data is unknown; contamination is not ruled out for either model by this table. Sample sizes, dependence, paired predictions, and evaluation design determine statistical significance; rounded aggregate scores alone cannot establish it.

Kev's validated context is 8,192 tokens for 0.8B, 4B, and 9B, and 65,536 for 27B. This means the documentation's CUAD accuracy criterion remained within three percentage points of the same model's 8k result at the stated lower confidence bound. It is narrower than a guarantee on arbitrary documents. A server accepting 65k tokens does not prove that every checkpoint retains its short-context accuracy there.

### Latency and throughput have different denominators

| Model / GPU | Short input, new / same state, ms | About 2,200 tokens, new / same state, ms | Requests/s, 64 clients |
|---|---:|---:|---:|
| Kev-0.8B / L4 | 22.7 / 16.1 | 108.6 / 32.3 | 62.8 |
| Kev-4B / L40S | 41.5 / 27.7 | 145.2 / 43.0 | 51.4 |
| Kev-4B / H100 | 18.1 / 12.9 | 89.4 / 22.5 | 100.8 |
| Kev-9B v1 / H100 | 24.0 / 16.6 | 88.5 / 26.4 | 79.5 |

Sources: the [0.8B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-0.8b.md), [4B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-4b.md), and [9B serving sections](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-9b.md). The 9B latency was measured on **v1**, whose architecture/adapter shape matches v2; it is not a fresh v2 timing result. Short requests contain six questions; long requests contain five. Latencies are medians of 20 server-side measurements and exclude network time. “Same state” allows prefix reuse; it is not a cold-start measurement. Throughput uses concurrent short-input requests with new states. Its reciprocal is not the median latency of one request under another load.

For comparison, an open-loop production latency study should specify model revision, dtype/quantization, hardware, state and branch token distributions, cache hits, batch size, concurrency, arrival process, warm-up, and p50/p95/p99. End-to-end cost includes input preparation, transport, queueing, inference, and policy execution. GPU cost per decision is

$$
\frac{\text{GPU price per hour}}{3600\times\text{sustained decisions per second}},
$$

only if the throughput and utilization assumptions actually hold. Idle capacity, replicas, downloads, and operations add costs.

### Jev latency and hosted cost

The [official release article](https://typesafe.ai/blog/introducing-system-one-models-and-jev), checked October 11, reports end-to-end response times of 70–500 ms and input pricing of USD 0.042 per million tokens, with output tokens uncharged. These are vendor-reported figures and published pricing, not a universal latency guarantee or a matched measurement against the GPU table above. Its headline speed/cost ratios arise from particular workflow comparisons and should not be applied to every workload.

For a billed input count $$N_{\mathrm{in}}$$ under that tariff, the token charge is

$$
\mathrm{charge}_{\mathrm{USD}}=0.042\,N_{\mathrm{in}}/10^6.
$$

Count the complete billable request under the API rules, rather than just the state text. Recheck current pricing, token accounting, rate limits, regional/network latency, and version availability before a cost estimate.

### What independent Jev results establish

[Evaluating and Benchmarking Jev](https://arxiv.org/html/2609.37647v1) reports Jev 1.13.0 on 37 datasets, 346,009 requests, and an API cost below USD 10 for that study. It reports strong results on several standard classification tasks and broad multilingual coverage. Those are results for particular datasets, prompts, versions, and thresholds. Public benchmark success is not evidence that the training distribution excluded them, nor a guarantee for private tickets. Evaluate on your own held-out cases before choosing an automation policy.

## 10. Common applications and their failure modes

| Application | Suitable construction | What to test beyond accuracy |
|---|---|---|
| Request or tool routing | Choice with explicit mutually exclusive routes | Unknown routes, mixed intent, action-specific costs |
| Content-policy triage | Separate Nouls per operational rule | False negatives, adversarial text, policy revision |
| Retrieval filtering | Noul for evidence relevance or ordered Score | Recall before filtering, long documents, cited evidence |
| Workflow prioritization | Score with observable level descriptions | Ordinal loss, ranking stability, queue waiting cost |
| Agent stopping | Noul for a precisely defined completion condition | Missing evidence, premature stops, loop behavior |
| Local/private processing | Open weights with controlled serving | Data retention, logs, hardware, quality on the target language |

A decision model can decide **which** tool is appropriate; a generative or deterministic component may still need to construct arguments. Do not turn a routing probability into permission to perform an action. Authentication, argument validation, and workflow rules are separate application responsibilities. Treat model output as an input to the policy whose loss you derived.

## 11. A reproducible local Kev workflow

These commands follow the pinned project's interface. They are an installation example, not a claim of execution on the reader's hardware. Use Python 3.12 or 3.13 and [uv](https://docs.astral.sh/uv/). The PyPI package named `kev` is a different project; install this model implementation from its repository.

```sh
git clone https://github.com/jaredpalmer/kev.git
cd kev
git checkout fc4a17e194bca35a48c57211392ec49ea54a94ac
uv sync --extra serve
uv run --extra serve python -m kev.serve \
  --run jaredpalmer/kev-4b@v1.0 --port 8009
```

Pin both serving code and model weights; the release's `v1.0` Hub tag identifies the checkpoint family. For archival reproduction, record the resolved full Hub commit and file hashes too. The first start downloads the base model and adapter. Select an explicit supported device when silent CPU fallback would invalidate a latency comparison.

A request uses a common state and a map of questions:

```python
import json
import urllib.request

request_body = {
    "state": "I see two charges for order 4411. Please refund one.",
    "model": "kev-latest",
    "questions": {
        "team": {
            "type": "choice",
            "instructions": "Select the primary team for this ticket.",
            "criteria": {
                "billing": "Payments, duplicate charges, invoices and refunds",
                "shipping": "Delivery status, delays and lost packages",
                "access": "Login and account access",
                "other": "None of these teams or insufficient evidence",
            },
        },
        "duplicate_charge": {
            "type": "noul",
            "instructions": "Does the ticket report a duplicate charge?",
        },
        "urgency": {
            "type": "score",
            "instructions": "Rate urgency using the described evidence.",
            "criteria": [
                "Routine: no stated deadline or ongoing loss",
                "Time-sensitive: stated near-term deadline",
                "Immediate: ongoing loss or access-critical deadline today",
            ],
        },
    },
}
request = urllib.request.Request(
    "http://127.0.0.1:8009/v1/systemone",
    data=json.dumps(request_body).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(request, timeout=60) as response:
    result = json.load(response)
answer = result["answers"]["team"]
print(answer["choice"], answer["probabilities"], answer["confidence"])
```

The request includes four options, so its confidence conversion uses $$K=4$$, not the earlier three-option example. No numerical response is invented here. A locally hosted endpoint and a hosted Jev endpoint have different model selectors, authentication, limits, and privacy arrangements; consult the [current API](https://docs.typesafe.ai/api) when switching. API compatibility does not make two models' probability values interchangeable.

Persist the model and code revision, prompt/criteria version, raw distribution, latency scope, acceptance decision, and eventual label. If input text is sensitive, design logging and retention before collecting it. A cache key must cover all inputs that affect the output, including question text, option order, model, temperature, and state.

## 12. Fine-tuning without contaminating the evaluation

Begin with an operational label specification and independently labeled examples. If annotators disagree, measure that disagreement: some uncertainty comes from the task definition rather than model capacity. Preserve real deployment frequencies for a representative test set, or explicitly reweight a deliberately balanced one.

Partition by customer, document, or time as appropriate:

1. **Training:** update the adapter/head or full model.
2. **Development:** select checkpoints and task design.
3. **Calibration:** fit temperature and choose risk thresholds.
4. **Test:** report the final pipeline once.

A small dataset may require cross-validation or nested cross-fitting to use labels efficiently, but it still needs a clear distinction between fitting and evaluation. Synthetic examples are training material; a synthetic test generated by the same recipe does not establish accuracy on real user input.

For labeled candidate index $$y_j$$, the usual categorical loss is

$$
\mathcal L_{\mathrm{CE}}(\theta)=-\frac1n\sum_j
\log p_\theta(y_j\mid x_j,q_j,C_j).
$$

In LoRA, a frozen weight matrix can be augmented by $$\Delta W=(\alpha/r)BA$$, with $$A\in\mathbb R^{r\times d_{\mathrm{in}}}$$ and $$B\in\mathbb R^{d_{\mathrm{out}}\times r}$$. Trainable parameters for that update are $$r(d_{\mathrm{in}}+d_{\mathrm{out}})$$ instead of $$d_{\mathrm{in}}d_{\mathrm{out}}$$. That counts adapter parameters, not total GPU memory: backbone weights, activations, gradients, and optimizer states still matter. Kev-27B's full-weight recipe is a different memory regime.

Start from a released compatible checkpoint when adapting its decision behavior; starting only from the raw backbone also discards the learned decision head and adapter. The pinned [training instructions](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/README.md#by-hand) specify JSONL labels and `--init_from`. Measure both the new domain and a retained general set, because an improvement in one domain can coincide with forgetting elsewhere.

Recalibrate the final checkpoint, then evaluate coverage at the chosen risk budget. A useful release record includes frozen examples, label definitions, revisions, loss convention, calibration method, threshold, subgroup counts, and latency conditions. Improving training loss alone is insufficient.

## 13. Open-source projects with related goals

Similar names conceal different implementations. Check the exact repository, base model, model revision, license, and output semantics before treating a project as interchangeable with Kev or Jev.

| Project | Inspectable mechanism or focus | When to investigate it |
|---|---|---|
| [jaredpalmer/kev](https://github.com/jaredpalmer/kev) | Decoder-backbone option pointer head; Choice/Noul/Score server; released temperatures | Self-hosting the typed decision interface and adapting it to domain labels |
| [nico-martin/open-jev](https://github.com/nico-martin/open-jev) | Browser-oriented TypeScript and ONNX/Transformers.js with WebGPU or WASM | Local browser inference; check checkpoint and context support |
| [kalufinnle/laya-decision-model](https://github.com/kalufinnle/laya-decision-model) | Multilingual encoder-based decision model family | Multilingual routing with an encoder inference stack |
| [fastino-ai/GLiNER2](https://github.com/fastino-ai/GLiNER2) | Schema-guided extraction and classification; Decide checkpoint family | Joint labels/entities when a pure router is insufficient |
| [kotoba-lang/typed-decisions](https://github.com/kotoba-lang/typed-decisions) | Open typed-decision implementations across multiple backbones | Comparing architecture and training choices under a common task design |
| [ZimmyGao/openjev-rlcd](https://github.com/ZimmyGao/openjev-rlcd) | An independent open training recipe related to RLCD | Studying reproducible decision-model training rather than assuming a recovered proprietary recipe |

The browser `open-jev` project's listed older Kev checkpoints are not the same as the pinned Kev 1.0 Qwen3.5/3.8 family above. Its ONNX paths and encoder paths also have their own context and hardware constraints. A small encoder, a hybrid decoder, and a large post-trained decoder can differ in tokenizer, supported languages, sequence length, and probability calibration; parameter count alone does not rank their usefulness.

For a fair comparison, freeze the same examples and label definitions, tune each candidate on the same allowed development/calibration data, and compare accuracy, proper scores, accepted-case risk, coverage, and end-to-end resource use. Include a rules baseline, a conventional supervised classifier when labels are fixed, and a restricted-label language model. Select the simplest candidate that meets the measured requirements.

## References and reproducibility limits

- [TypeSafe introduction](https://docs.typesafe.ai/introduction), [API](https://docs.typesafe.ai/api), [Choice](https://docs.typesafe.ai/primitives/choice), [Noul](https://docs.typesafe.ai/primitives/noul), [Score](https://docs.typesafe.ai/primitives/score), and [confidence specification](https://docs.typesafe.ai/confidence).
- [Kev, pinned source and release documentation](https://github.com/jaredpalmer/kev/tree/fc4a17e194bca35a48c57211392ec49ea54a94ac), including `kev/model.py` and model cards.
- [Guo et al., On Calibration of Modern Neural Networks](https://proceedings.mlr.press/v70/guo17a.html).
- [Evaluating and Benchmarking Jev, version 1](https://arxiv.org/html/2609.37647v1).
- [LLM-as-Jev](https://arxiv.org/abs/2610.02076) and [independent open RLCD work](https://arxiv.org/abs/2609.38850).

The probability and loss derivations above state their assumptions explicitly. Actual calibration, domain accuracy, and hardware performance require measurements on the selected model and workload. Public claims and reproducible source code supply starting evidence; neither substitutes for that final evaluation.
