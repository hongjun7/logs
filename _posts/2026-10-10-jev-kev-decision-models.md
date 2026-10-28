---
lang: en
translation_key: 2026-10-10-jev-kev-decision-models
translation_url: /ko/2026/10/10/jev-kev-decision-models.html
title: "Jev and Kev"
tags: ["machine-learning", "decision-models", "calibration", "open-source", "engineering"]
subtitle: "Probability outputs, calibration, decision losses, and the open Kev implementation."
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-11
---

Jev returns probability distributions over bounded decisions rather than generated explanations. Kev implements a similar interface with open weights. Their usefulness depends on calibrated probabilities, operational labels, and the loss attached to each action.

## Decision distributions
{: id="1-what-problem-does-a-decision-model-solve"}

A ticket about a duplicate charge might need a team label, urgency score, or yes/no decision. For supplied state $$x$$, instructions $$q$$, and candidate descriptions $$C=(c_1,\ldots,c_K)$$, a classifier returns

$$
p_\theta(y=k\mid x,q,C),\qquad p_k\ge0,\qquad\sum_{k=1}^{K}p_k=1.
$$

Learned parameters $$\theta$$ map the input to the simplex $$\Delta^{K-1}$$. A generative model producing $$M$$ tokens instead factorizes

$$
p_\theta(t_{1:M}\mid x)=\prod_{j=1}^{M}p_\theta(t_j\mid x,t_{1:j-1}).
$$

Direct decisions avoid answer generation and parsing, but still require input processing and scoring; they do not establish correctness. [TypeSafe](https://docs.typesafe.ai/introduction) presents Jev as a hosted System One model trained with Reinforcement Learning for Calibrated Decisions (RLCD). Its [release article](https://typesafe.ai/blog/introducing-system-one-models-and-jev) does not establish a complete public training set, architecture, weights, or reproducible original recipe. Community implementations do not reveal those internals.

<div id="3-why-an-option-probability-is-conditional"></div>

## Outputs
{: id="2-three-primitives-choice-noul-and-score"}

| Primitive | Output | Interpretation |
|---|---|---|
| Choice | Distribution over $$K$$ unordered options | The correct class may be absent |
| Noul | Probability $$p$$ of “yes” | The action threshold depends on loss |
| Score | Distribution over ordered levels and mean index | Ordering alone does not establish equal severity intervals |

Choice usually selects

$$
\widehat y=\operatorname*{arg\,max}_{k}p_k.
$$

Noul represents $$(1-p,p)$$. Threshold $$0.5$$ minimizes symmetric binary misclassification loss only if $$p$$ is the true posterior. For $$K$$ ordered Score levels $$0,\ldots,K-1$$,

$$
\overline s=\sum_{i=0}^{K-1}i\,p_i.
$$

Thus $$(p_0,p_1,p_2)=(0,0.57,0.43)$$ gives $$1.43$$, a mean under the encoding rather than another label. Replacing $$(0,1,2)$$ with $$(0,1,10)$$ changes it. Nonlinear costs require the full distribution ([Choice](https://docs.typesafe.ai/primitives/choice), [Noul](https://docs.typesafe.ai/primitives/noul), [Score](https://docs.typesafe.ai/primitives/score)).

Removing “billing” forces mass onto the remaining options, possibly yielding a high-confidence error. In general,

$$
p(y=k\mid x,q,C)\ne p(y=k\mid x,q,C')
$$

when $$C\ne C'$$. An “insufficient evidence” option represents a missing outcome without guaranteeing unfamiliar-input detection. Operational descriptions must resolve mixed intents: single Choice selects one winner, whereas separate Nouls describe marginal properties.

Questions do not read one another's answers, but their labels can remain statistically dependent. If $$\Pr(A)=0.8$$ and $$\Pr(B)=0.7$$, Fréchet bounds give

$$
0.5=\max(0,0.8+0.7-1)\le \Pr(A\cap B)\le\min(0.8,0.7)=0.7.
$$

The product $$0.56$$ needs label independence; separate model calls do not supply it.

## Confidence
{: id="4-confidence-is-a-summary-of-the-distribution"}

The [API specification](https://docs.typesafe.ai/confidence) rescales the maximum Choice probability for $$K$$ options, at least two:

$$
c_{\mathrm{choice}}=\frac{p_{\max}-1/K}{1-1/K}.
$$

Uniform distributions map to 0 and point masses to 1; $$(0.6,0.3,0.1)$$ gives $$0.4$$. This is not correctness probability. Noul returns $$p$$; an analogous optional summary is $$\vert 2p-1\vert $$. For Score, a mode $$m=\arg\max_i p_i$$ gives

$$
\begin{aligned}
D_K&=\frac1K\sum_{i=0}^{K-1}\left\vert i-\frac{K-1}{2}\right\vert ,\\
c_{\mathrm{score}}&=\max\left(0,1-\frac{\sum_i p_i\vert i-m\vert }{D_K}\right).
\end{aligned}
$$

with implementation-specific tie handling. At $$K=3$$, $$D_K=2/3$$, so $$(0,0.57,0.43)$$ gives $$c_{\mathrm{score}}=0.355$$ while retaining mean $$1.43$$. Algebraically,

$$
c_{\mathrm{choice}}\ge t
\quad\Longleftrightarrow\quad
p_{\max}\ge\frac1K+t\left(1-\frac1K\right).
$$

Hence $$t=0.9$$ at $$K=3$$ requires $$p_{\max}\ge0.933\overline3$$; confidence cannot replace $$p_{\max}$$ in a loss formula. Pairing midpoint distances gives $$D_K=K/4$$ for even $$K$$ and $$D_K=(K^2-1)/(4K)$$ for odd $$K$$. The denominator is positive for $$K\ge2$$; one option needs a separate convention.

<div class="probability-explorer" data-probability-explorer>
  <h3>Three-option distribution</h3>
  <p>Nonnegative weights become probabilities without a model call. Choice treats labels as unordered; Score uses levels 0, 1, 2.</p>
  <div class="probability-controls">
    <label>Option / level 0 <input type="range" min="0" max="100" value="60" data-weight="0"></label>
    <label>Option / level 1 <input type="range" min="0" max="100" value="30" data-weight="1"></label>
    <label>Option / level 2 <input type="range" min="0" max="100" value="10" data-weight="2"></label>
  </div>
  <div class="probability-bars" aria-hidden="true"><span data-bar="0"></span><span data-bar="1"></span><span data-bar="2"></span></div>
  <p class="probability-result" aria-live="polite" data-result>Loading the probability example…</p>
  <noscript><p>Initial values: probabilities (0.600, 0.300, 0.100), Choice confidence 0.400, mean level 0.500, Score confidence 0.250. Enable JavaScript to adjust the weights.</p></noscript>
</div>

## Calibration
{: id="5-accuracy-calibration-and-proper-scoring-rules"}

A model assigning $$0.95$$ to 1,000 comparable tickets but answering only 800 correctly has accuracy $$0.8$$ and overconcentrated probabilities. With true class $$Y$$ and random prediction vector $$P$$, top-label calibration requires

$$
\Pr(Y=\widehat Y\mid P_{\max}=s)=s.
$$

on supported probability values. Classwise calibration requires $$\Pr(Y=k\mid P_k=s)=s$$ for each $$k$$; full-vector calibration requires $$\Pr(Y=k\mid P)=P_k$$ almost surely and is stronger. These are conditional-expectation statements; finite bins approximate them rather than defining exact continuous-value frequencies.

Negative log-likelihood and Brier score retain probabilities discarded by accuracy:

$$
\mathrm{NLL}=-\frac1n\sum_{j=1}^{n}\log p_{j,y_j},
\qquad
\mathrm{Brier}=\frac1n\sum_{j=1}^{n}\sum_{k=1}^{K}
\left(p_{j,k}-\mathbf1\{y_j=k\}\right)^2.
$$

NLL is unbounded near zero probability for the true label. Full multiclass Brier lies in $$[0,2]$$; the positive-component binary convention lies in $$[0,1]$$ and is half the two-component score. For true vector $$q$$ and prediction $$p$$,

$$
\mathbb E_{Y\sim q}[-\log p_Y]=H(q)+D_{\mathrm{KL}}(q\Vert p),
$$

and

$$
\mathbb E_{Y\sim q}\left[\sum_k(p_k-\mathbf1\{Y=k\})^2\right]
=\|p-q\|_2^2+1-\|q\|_2^2.
$$

Expanding the square with $$\mathbb E[\mathbf1\{Y=k\}]=q_k$$ shows both are minimized at $$p=q$$. This population property does not guarantee calibration from finite training or under domain shift.

### Proper rewards
{: id="why-rewarding-the-winning-label-is-insufficient"}

Conditional on an input, independently sample action $$A$$ from $$p$$ and truth $$Y\sim q$$. Correct-label reward $$\mathbf1\{A=Y\}$$ has expectation

$$
\mathbb E[R]=\sum_k p_kq_k.
$$

Linear dependence on $$p$$ favors a point mass at maximal $$q_k$$: with $$q=(0.6,0.4)$$, $$p=(1,0)$$ earns $$0.6$$ while $$p=q$$ earns $$0.52$$. Negative Brier reward instead gives

$$
\mathbb E[R(p,Y)]=-\|p-q\|_2^2-1+\|q\|_2^2,
$$

uniquely maximized at $$p=q$$. These illustrate objectives, not Jev's undisclosed RLCD reward. Supervised cross-entropy is already proper; reinforcement learning is not required for calibration.

Binned expected calibration error is

$$
\mathrm{ECE}=\sum_{b=1}^{B}\frac{\vert I_b\vert }{n}
\left\vert \mathrm{acc}(I_b)-\mathrm{conf}(I_b)\right\vert .
$$

where top-label `conf` is mean top probability, not rescaled API confidence. Binning and sample size affect ECE, and within-bin errors can cancel; reliability diagrams, proper scores, and workload slices expose different errors.

### Temperature
{: id="temperature-scaling"}

Logits $$z_1,\ldots,z_K$$ and temperature $$\tau>0$$ define

$$
p_k^{(\tau)}=\frac{\exp(z_k/\tau)}{\sum_{i=1}^{K}\exp(z_i/\tau)}.
$$

Fitting $$\tau$$ minimizes held-out calibration NLL; increasing $$\tau$$ softens predictions and decreasing it sharpens them. Positive temperature preserves each example's argmax, not the ordering of maxima across examples, so classification errors persist while multiclass risk/coverage curves may change. The fitted value depends on model and distribution ([Guo et al.](https://proceedings.mlr.press/v70/guo17a.html)); a changed domain needs new labeled calibration evidence.

## Loss and actions
{: id="6-derive-the-action-from-its-loss"}

For loss $$L(a,y)$$ of action $$a$$ under truth $$y$$, the Bayes action under a calibrated posterior is

$$
a^*(x)=\operatorname*{arg\,min}_a\sum_y L(a,y)p(y\mid x).
$$

With false-positive cost $$C_{\mathrm{FP}}>0$$, false-negative cost $$C_{\mathrm{FN}}>0$$, and zero correct-decision cost, the risks are $$C_{\mathrm{FP}}(1-p)$$ and $$C_{\mathrm{FN}}p$$:

$$
\text{choose positive iff}\quad
p\ge\frac{C_{\mathrm{FP}}}{C_{\mathrm{FP}}+C_{\mathrm{FN}}}.
$$

Costs $$C_{\mathrm{FP}}=9$$ and $$C_{\mathrm{FN}}=1$$ yield threshold $$0.9$$. Reversing them for expensive missed urgency yields $$0.1$$; neither is a universal confidence cutoff.

For uniformly wrong-route cost $$C_w$$, the best automatic risk is $$C_w(1-p_{\max})$$. A perfect reviewer costing $$C_r$$ makes automation preferable when

$$
p_{\max}\ge1-\frac{C_r}{C_w}.
$$

With $$C_w=10$$ and $$C_r=1$$, threshold $$0.9$$ equals Choice confidence $$0.85$$ at $$K=3$$. Real review adds residual errors and waiting; nonuniform consequences require the full loss matrix.

For ordered scores, squared loss selects the conditional mean because

$$
\mathbb E[(a-Y)^2\mid x]=(a-\mathbb E[Y\mid x])^2+\operatorname{Var}(Y\mid x).
$$

has a variance term independent of $$a$$. Absolute loss selects a conditional median. Both interpretations require meaningful numerical level distances.

## Coverage
{: id="7-measure-coverage-and-residual-risk"}

For acceptance rule $$A_t=\mathbf1\{s(x)\ge t\}$$,

$$
\mathrm{coverage}(t)=\Pr(A_t=1),
\qquad
\mathrm{risk}(t)=\Pr(\widehat Y\ne Y\mid A_t=1).
$$

Risk is undefined at zero acceptance. Error below $$\epsilon$$ must be assessed with accepted counts and language/category slices, not overall accuracy alone. At a fixed threshold with $$n_a$$ independent, identically distributed (iid) accepted test cases and binary errors, Hoeffding gives

$$
\Pr(R>\widehat R+\eta)\le e^{-2n_a\eta^2},
\qquad
\eta=\sqrt{\frac{\log(1/\delta)}{2n_a}}.
$$

a one-sided bound at confidence $$1-\delta$$. Zero errors give exact binomial upper limit

$$
R_{\mathrm{upper}}=1-\delta^{1/n_a}.
$$

At $$\delta=0.05$$ and $$n_a=100$$, the limit is $$0.0295$$, not zero. “Three over $$n$$” uses $$-\log(0.05)\approx3$$. Threshold search belongs on development data; reusing the test set invalidates this fixed-threshold guarantee. Customer clusters, temporal drift, and duplicates also weaken iid assumptions.

## Kev
{: id="8-what-the-open-kev-implementation-actually-computes"}

Kev is pinned to [`fc4a17e`](https://github.com/jaredpalmer/kev/tree/fc4a17e194bca35a48c57211392ec49ea54a94ac), available by October 10, 2026 in Korea. Its [pointer head](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/kev/model.py) projects decision representation $$h_d\in\mathbb R^d$$ and option representation $$h_i\in\mathbb R^d$$:

$$
\begin{aligned}
u&=W_qh_d+b_q,\\
v_i&=W_kh_i+b_k,\\
z_i&=\frac{v_i^\top u}{\sqrt{d_p}}.
\end{aligned}
$$

Temperature-scaled softmax yields option-index probabilities. Projection dimension $$d_p$$ is not the option count; descriptions can change between requests. Projection work $$O((K+1)dd_p)$$ and dot-product work $$O(Kd_p)$$ exclude the usually dominant backbone.

### Shared state
{: id="shared-state-and-separate-branches"}

A conceptual pure-attention block-causal mask lets each question read state length $$S$$ but not sibling branches $$Q_1,\ldots,Q_m$$. A mask-exploiting implementation has allowed-pair work

$$
O\left(S^2+\sum_{j=1}^{m}(SQ_j+Q_j^2)\right)
$$

Dense masking may still compute blocked pairs; the mask alone proves no speedup. Packed pure-attention inputs also have a token-length guard.

The pinned 0.8B/4B/9B models use Qwen3.5, LoRA, and a pointer head. Hybrid attention/recurrent layers instead use separate causal rows, shared-prefix reuse, and cloned recurrent states. Reserved-marker sanitization does not guarantee protection from semantic prompt injection. The 27B model uses post-trained Qwen3.8 and full-weight tuning; base, size, and recipe all change, preventing a parameter-count-only ablation ([model cards](https://github.com/jaredpalmer/kev/tree/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards)).

### Label likelihoods
{: id="compare-with-a-language-model-label-baseline"}

A generative baseline can normalize logits for single-token labels. Multi-token strings $$\ell_k$$ require complete conditional likelihoods and a boundary convention:

$$
a_k=\log p_\theta(\ell_k\mid x,q),
\qquad
\widetilde p_k=\frac{e^{a_k}}{\sum_i e^{a_i}}.
$$

This distributes mass over strings, not necessarily semantic classes; length, tokenization, spelling, and synonyms matter. [LLM-as-Jev](https://arxiv.org/abs/2610.02076) studies direct probabilistic decisions without identifying Jev's proprietary architecture.

## Measurements
{: id="9-read-performance-tables-without-changing-their-meaning"}

The pinned cards report maintainer measurements for `transfer-v4`, with 656 questions per development/test panel. They describe sources and policies absent from Kev training; development selects checkpoints. These are reported results, not local inference measurements.

| Model | New-source accuracy, dev | New-source accuracy, test | Full Brier, dev | Full Brier, test |
|---|---:|---:|---:|---:|
| Kev-0.8B | 0.648 | 0.697 | 0.430 | 0.397 |
| Kev-4B | 0.817 | 0.838 | 0.243 | 0.224 |
| Kev-9B v2 | 0.820 | 0.852 | 0.262 | 0.199 |
| Kev-27B v2 | 0.851 | 0.889 | 0.218 | 0.154 |
| Jev | 0.857 | Not reported | 0.211 | Not reported |

Sources: [0.8B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-0.8b.md), [4B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-4b.md), [9B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-9b.md), [27B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-27b.md). The same-revision overview instead lists, for example, 4B Brier 0.269 / 0.242. This table follows the detailed cards; no independent rerun resolves that discrepancy.

The same-split comparison is Kev-27B dev $$0.851$$ versus Jev $$0.857$$: $$0.006$$, or 0.6 percentage points. Kev test $$0.889$$ versus Jev dev $$0.857$$ mixes splits. Unknown Jev training data and these aggregate scores exclude neither contamination nor dependence; statistical significance needs evaluation design, sample sizes, and paired predictions.

Validated contexts are 8,192 tokens for 0.8B/4B/9B and 65,536 for 27B: the stated lower-confidence-bound CUAD criterion stays within three percentage points of each model's 8k result. Accepted server input length does not guarantee arbitrary-document accuracy.

### Serving
{: id="latency-and-throughput-have-different-denominators"}

| Model / GPU | Short input, new / same state, ms | About 2,200 tokens, new / same state, ms | Requests/s, 64 clients |
|---|---:|---:|---:|
| Kev-0.8B / L4 | 22.7 / 16.1 | 108.6 / 32.3 | 62.8 |
| Kev-4B / L40S | 41.5 / 27.7 | 145.2 / 43.0 | 51.4 |
| Kev-4B / H100 | 18.1 / 12.9 | 89.4 / 22.5 | 100.8 |
| Kev-9B v1 / H100 | 24.0 / 16.6 | 88.5 / 26.4 | 79.5 |

The [0.8B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-0.8b.md), [4B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-4b.md), and [9B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-9b.md) cards use 20 server-side measurements' medians, excluding network time; short/long requests contain six/five questions. The 9B timings are v1, not fresh v2 measurements, though architecture/adapter shape matches. Same-state requests reuse prefixes; throughput uses concurrent short requests with new states. Reciprocal throughput is not single-request median latency under another load.

An open-loop comparison needs revisions, dtype/quantization, hardware, state/branch lengths, cache hits, batching, concurrency, arrivals, warm-up, and p50/p95/p99. GPU cost per decision is

$$
\frac{\text{GPU price per hour}}{3600\times\text{sustained decisions per second}},
$$

only at the assumed sustained throughput/utilization. End-to-end cost adds preparation, transport, queues, policy execution, idle capacity, replicas, downloads, and operations.

<div id="what-independent-jev-results-establish"></div>

### Hosted Jev
{: id="jev-latency-and-hosted-cost"}

The [release article](https://typesafe.ai/blog/introducing-system-one-models-and-jev), checked October 11, reports 70–500 ms end-to-end and USD 0.042/million input tokens, with free outputs. These vendor figures are not guarantees or a matched comparison with the GPU table. For billed input $$N_{\mathrm{in}}$$,

$$
\mathrm{charge}_{\mathrm{USD}}=0.042\,N_{\mathrm{in}}/10^6.
$$

The complete billable request, rate limits, versions, and regional/network conditions determine a current estimate; headline workflow ratios do not generalize.

[Evaluating and Benchmarking Jev](https://arxiv.org/html/2609.37647v1) reports version 1.13.0 on 37 datasets, 346,009 requests, and API cost below USD 10, with strong classification and multilingual results. Dataset, prompt, version, and threshold conditions limit transfer to private tickets; public success does not establish exclusion from training.

## Applications
{: id="10-common-applications-and-their-failure-modes"}

| Task | Construction | Main failure cases |
|---|---|---|
| Routing | Choice with exclusive routes | Unknown routes, mixed intent, unequal costs |
| Policy triage | Noul per rule | False negatives, adversarial text, revisions |
| Retrieval filtering | Relevance Noul or ordered Score | Recall loss, long documents, unsupported evidence |
| Prioritization | Score with observable levels | Ordinal loss, unstable ranking, waiting |
| Agent stopping | Noul for explicit completion | Missing evidence, early stops, loops |
| Private processing | Controlled open-weight serving | Retention, logs, hardware, target-language quality |

Selecting a tool does not construct its arguments or authorize execution. Authentication, argument validation, and workflow rules remain application responsibilities.

## Local inference
{: id="11-a-reproducible-local-kev-workflow"}

The pinned interface uses Python 3.12/3.13 and [uv](https://docs.astral.sh/uv/); PyPI's `kev` is unrelated. This installation example is not a hardware execution result:

```sh
git clone https://github.com/jaredpalmer/kev.git
cd kev
git checkout fc4a17e194bca35a48c57211392ec49ea54a94ac
uv sync --extra serve
uv run --extra serve python -m kev.serve \
  --run jaredpalmer/kev-4b@v1.0 --port 8009
```

The Hub `v1.0` tag identifies a checkpoint family; archival reproduction also needs its resolved commit and hashes. First startup downloads the base and adapter. Explicit device selection avoids silent CPU fallback in GPU comparisons. A state with several questions is submitted as follows:

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

Four options mean $$K=4$$ for confidence conversion. Local Kev and hosted Jev differ in model selectors, authentication, limits, and privacy ([API](https://docs.typesafe.ai/api)); compatible schemas do not make probabilities interchangeable. Reproducible records retain revisions, criteria, raw probabilities, timing scope, acceptance, and eventual labels. Sensitive input needs a retention policy; cache keys need every output-affecting input, including state, question, option order, model, and temperature.

## Fine-tuning
{: id="12-fine-tuning-without-contaminating-the-evaluation"}

Operational labels and independent annotation distinguish task ambiguity from model error. Representative test frequencies, or explicit reweighting, matter. Training updates weights; development selects checkpoints; calibration fits temperature/thresholds; a separate test evaluates the final pipeline. Grouping by customer, document, or time prevents leakage. Cross-validation can economize labels without collapsing fitting and evaluation; same-recipe synthetic tests do not establish real-input accuracy.

For target index $$y_j$$,

$$
\mathcal L_{\mathrm{CE}}(\theta)=-\frac1n\sum_j
\log p_\theta(y_j\mid x_j,q_j,C_j).
$$

LoRA adds $$\Delta W=(\alpha/r)BA$$ with $$A\in\mathbb R^{r\times d_{\mathrm{in}}}$$ and $$B\in\mathbb R^{d_{\mathrm{out}}\times r}$$, training $$r(d_{\mathrm{in}}+d_{\mathrm{out}})$$ parameters instead of $$d_{\mathrm{in}}d_{\mathrm{out}}$$. Backbone weights, activations, gradients, and optimizer state still consume memory; 27B full-weight tuning is different. A compatible released checkpoint retains the learned head/adapter discarded by raw-backbone initialization ([training instructions](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/README.md#by-hand), JSONL and `--init_from`). Final calibration and risk/coverage evaluation need both domain and retained general data to expose forgetting, with frozen labels, revisions, score conventions, thresholds, subgroup counts, and latency conditions.

## Related models
{: id="13-open-source-projects-with-related-goals"}

| Project | Mechanism / scope |
|---|---|
| [kev](https://github.com/jaredpalmer/kev) | Decoder option-pointer head and typed server |
| [open-jev](https://github.com/nico-martin/open-jev) | Browser TypeScript, ONNX/Transformers.js, WebGPU/WASM |
| [laya-decision-model](https://github.com/kalufinnle/laya-decision-model) | Multilingual encoder family |
| [GLiNER2](https://github.com/fastino-ai/GLiNER2) | Schema-guided extraction/classification and Decide checkpoints |
| [typed-decisions](https://github.com/kotoba-lang/typed-decisions) | Typed decisions across backbones |
| [openjev-rlcd](https://github.com/ZimmyGao/openjev-rlcd) | Independent open RLCD-related recipe |

Browser `open-jev` lists older Kev checkpoints, distinct from the pinned Qwen3.5/3.8 family; its ONNX/encoder paths have separate context/hardware limits. Base model, tokenizer, language, context, license, revision, and calibration matter beyond parameter count. Matched examples and tuning budgets allow comparison of accuracy, proper scores, accepted risk, coverage, and total resources against rules, fixed-label classifiers, and restricted-label language models.

## References
{: id="references-and-reproducibility-limits"}

- [TypeSafe](https://docs.typesafe.ai/introduction), [API](https://docs.typesafe.ai/api), [Choice](https://docs.typesafe.ai/primitives/choice), [Noul](https://docs.typesafe.ai/primitives/noul), [Score](https://docs.typesafe.ai/primitives/score), [confidence](https://docs.typesafe.ai/confidence).
- [Pinned Kev source and release documentation](https://github.com/jaredpalmer/kev/tree/fc4a17e194bca35a48c57211392ec49ea54a94ac).
- [Guo et al., calibration](https://proceedings.mlr.press/v70/guo17a.html).
- [Evaluating and Benchmarking Jev, v1](https://arxiv.org/html/2609.37647v1).
- [LLM-as-Jev](https://arxiv.org/abs/2610.02076), [independent RLCD work](https://arxiv.org/abs/2609.38850).
