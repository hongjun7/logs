---
lang: en
translation_key: 2026-02-15-Nested-Learning
translation_url: /ko/2026/02/15/Nested-Learning.html
title: "Nested Learning"
tags: ["machine-learning", "memory", "continual-learning"]
subtitle: "Associative memory, optimizer states, and coupled learning across timescales."
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-11
---

Nested Learning describes interacting learners with different context streams and update timescales. Fast associative states, optimizer traces, and slow weights provide distinct forms of memory; their update rules determine adaptation and retention.

## State and parameters
{: id="1-what-changes-when-a-model-learns"}

A supervised predictor $$f_\theta(x)$$ learns parameters from a loss. A stateful learner also maintains history-dependent $$z_t$$:

$$
\widehat y_t=f_\theta(x_t,z_t),\qquad
z_{t+1}=U_\psi(z_t,C_t).
$$

Update context $$C_t$$ can contain inputs, representations, targets, or internal learning signals. A required target $$y_t$$ must be available during that update.

The paper organizes nested or parallel optimization levels and introduces Hope as a proof of concept. The derivations below are generic examples, distinguished from Hope’s architecture. [Paper](https://arxiv.org/abs/2512.24695), [Google Research](https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/).

## Associative memory
{: id="2-associative-memory-as-a-regression-problem"}

Let keys $$k_i\in\mathbb R^{d_k}$$ map to values $$v_i\in\mathbb R^{d_v}$$. A linear memory $$M\in\mathbb R^{d_v\times d_k}$$ solves

$$
\mathcal L(M)=\frac12\sum_i\|Mk_i-v_i\|_2^2
+\frac\lambda2\|M\|_F^2,\qquad\lambda>0.
$$

With matrices $$K=[k_1,\ldots,k_n]$$ and $$V=[v_1,\ldots,v_n]$$, setting the gradient to zero gives

$$
M(KK^\top+\lambda I)=VK^\top,
\qquad
M^*=VK^\top(KK^\top+\lambda I)^{-1}.
$$

Positive $$\lambda$$ ensures invertibility. Without regularization, singular keys may require a pseudoinverse and allow nonunique optima.

For an unregularized one-observation online loss, a gradient step is

$$
M_{t+1}=M_t-\eta_t(M_tk_t-v_t)k_t^\top.
$$

The delta rule writes prediction error into memory; $$(M_tk_t-v_t)k_t^\top$$ has shape $$d_v\times d_k$$.

### Interference
{: id="interference-is-visible-in-the-algebra"}

After writing pair $$(k_t,v_t)$$, the output for an old key $$k'$$ changes by

$$
(M_{t+1}-M_t)k'
=-\eta_t(M_tk_t-v_t)(k_t^\top k').
$$

Orthogonal keys do not interfere in this update; correlated keys generally alter earlier readouts. Capacity, key geometry, regularization, gating, and consolidation determine retention.

For a fixed key of squared norm $$c>0$$, error follows $$e_{t+1}=(1-\eta c)e_t$$ and contracts when $$0<\eta c<2$$. This single-sample result does not establish nonlinear coupled stability.

## Attention and stored pairs
{: id="3-attention-as-a-different-memory-read"}

Given a query $$q\in\mathbb R^{d_k}$$, key vectors $$k_i$$, and values $$v_i$$,

$$
\alpha_i(q)=\frac{\exp(q^\top k_i/\sqrt{d_k})}
{\sum_j\exp(q^\top k_j/\sqrt{d_k})},
\qquad\widehat v(q)=\sum_i\alpha_i(q)v_i.
$$

Attention reads explicit key–value pairs, whose cache can change without gradient updates. Regression memory instead compresses associations into $$M$$. Their capacities, costs, and write mechanisms differ. Cache writes append or replace stored examples, whereas the regression rule changes the parameters used to answer every key.

A decoder KV cache is often request-local. Its update need not persist as fine-tuned weights across users; state lifetime and reset rules determine what survives.

## Optimizer memory
{: id="4-optimizers-already-carry-memory"}

For gradient $$g_t$$, normalized momentum maintains

$$
v_t=\beta v_{t-1}+(1-\beta)g_t,\qquad0\le\beta<1.
$$

With $$v_0=0$$, expansion gives

$$
v_t=(1-\beta)\sum_{i=1}^{t}\beta^{t-i}g_i.
$$

This exponentially weighted gradient history has half-life $$\log(1/2)/\log\beta$$ for $$0<\beta<1$$. Near-one decay retains longer history but responds more slowly.

Adam maintains coordinatewise first and second moments:

$$
\begin{aligned}
m_t&=\beta_1m_{t-1}+(1-\beta_1)g_t,\\
v_t&=\beta_2v_{t-1}+(1-\beta_2)(g_t\odot g_t),\\
\widehat m_t&=m_t/(1-\beta_1^t),\quad
\widehat v_t=v_t/(1-\beta_2^t),\\
\theta_{t+1}&=\theta_t-\eta_t\widehat m_t\oslash(\sqrt{\widehat v_t}+\epsilon).
\end{aligned}
$$

Division and square roots are coordinatewise; $$\epsilon>0$$ prevents zero division. These are standard [Adam](https://arxiv.org/abs/1412.6980) recurrences. Bias correction handles moment initialization under its assumptions, not arbitrary nonstationarity or convergence. Nested Learning interprets such states as memory.

## Nested objectives
{: id="5-nested-objectives-and-gradient-flow"}

A simple bilevel construction is

$$
\phi^*(\theta)=\arg\min_\phi\mathcal L_{\mathrm{inner}}(\phi;\theta),\qquad
\min_\theta\mathcal L_{\mathrm{outer}}(\theta,\phi^*(\theta)).
$$

For a unique smooth stationary inner solution with invertible Hessian in $$\phi$$, implicit differentiation gives

$$
\frac{d\phi^*}{d\theta}
=-\left(\nabla_{\phi\phi}^2\mathcal L_{\mathrm{inner}}\right)^{-1}
\nabla_{\phi\theta}^2\mathcal L_{\mathrm{inner}}.
$$

The outer gradient includes direct and adapted-state effects. Finite unrolling computes an alternative approximation; truncation and stopped gradients change the gradient approximation and computational cost.

This bilevel example does not require every Hope component to solve an inner optimum exactly during inference.

## Update frequencies
{: id="6-multiple-update-frequencies"}

For modules with states $$z_t^{(k)}$$, let $$u_k(t)\in\{0,1\}$$ indicate a scheduled update:

$$
z_{t+1}^{(k)}=
\begin{cases}
U_k(z_t^{(k)},C_t),&u_k(t)=1,\\
z_t^{(k)},&u_k(t)=0.
\end{cases}
$$

An empirical frequency over $$H$$ steps is

$$
f_k(H)=\frac1H\sum_{t=1}^{H}u_k(t).
$$

Frequency counts scheduled writes; learning rate controls an update’s step size. Frequent small writes can change less than rare large writes. Update magnitude and context horizon also determine effective timescales.

Hope combines the multi-rate Continuum Memory System with a self-modifying module. Gated sums, concatenation, and attention illustrate possible combinations, not a verified specification of its aggregation.

## Continual-learning metrics
{: id="7-continual-learning-evaluation"}

Let $$a_{t,i}$$ denote task-$$i$$ accuracy after task $$t$$. Final average accuracy is

$$
\mathrm{ACC}_T=\frac1T\sum_{i=1}^{T}a_{T,i}.
$$

One forgetting measure for $$T>1$$ is

$$
\mathrm F_T=\frac1{T-1}\sum_{i=1}^{T-1}
\left(\max_{i\le t<T}a_{t,i}-a_{T,i}\right).
$$

This signed measure becomes negative if old tasks improve; zero-clipping defines another metric. Keeping fast state can yield a different accuracy from evaluation after a reset. Transfer, adaptation latency, persistent-state size, and reset behavior expose retention–plasticity tradeoffs.

Language modeling, long-context recall, online adaptation, and continual supervised learning test different capabilities. Hope’s reported scales, data, and baselines do not establish universal elimination of forgetting.

## Controlled comparisons
{: id="8-designing-a-controlled-experiment"}

Frozen state, recurrence without online gradients, and online updates isolate different mechanisms. Matching parameters, update budgets, and inference compute makes update-rate comparisons meaningful across long streams, shifts, and revisited tasks.

Independent users or streams need separate resets unless persistence is intended. Training/evaluation state changes and implementation provenance distinguish an architectural replication from a community approximation.

## Gradient interference
{: id="9-forgetting-as-gradient-interference"}

Let task $$i$$ have risk $$R_i(\theta)=\mathbb E_{(x,y)\sim\mathcal D_i}[\ell(f_\theta(x),y)]$$. A gradient update on task $$t$$ is $$\theta'=\theta-\eta g_t$$ with $$g_t=\nabla R_t(\theta)$$. A first-order expansion gives

$$
R_i(\theta')-R_i(\theta)=-\eta\nabla R_i(\theta)^\top g_t+O(\eta^2).
$$

Opposing old/current gradients have negative inner product, raising old risk to first order. Curvature and step size bound that approximation. For an $$L_i$$-Lipschitz gradient,

$$
\left\vert R_i(\theta-\eta g_t)-R_i(\theta)+\eta\nabla R_i(\theta)^\top g_t\right\vert
\le\frac{L_i\eta^2}{2}\|g_t\|^2.
$$

In one dimension, for $$R_1(\theta)=\tfrac12(\theta-1)^2$$ and $$R_2(\theta)=\tfrac12(\theta+1)^2$$, the old optimum $$\theta=1$$ moves to $$\theta'=1-2\eta$$ after one new-task step, giving $$R_1(\theta')=2\eta^2$$. Separate fast states can reduce shared-weight pressure without removing incompatible objectives.

A regularized retention objective such as

$$
R_t(\theta)+\frac\lambda2\sum_jF_j(\theta_j-\theta_j^{\mathrm{old}})^2
$$

penalizes old-parameter changes using $$F_j\ge0$$. [Elastic Weight Consolidation](https://www.pnas.org/doi/10.1073/pnas.1611835114) approximates importance through Fisher information. Unlike a Hope definition, it is a comparison mechanism; replay, isolation, regularization, and consolidation have different storage/privacy costs.

## Differentiating through updates
{: id="10-differentiate-through-an-explicit-inner-update"}

Consider an explicit fast update:

$$
\phi_{t+1}=\phi_t-\eta\nabla_\phi\mathcal L_t(\phi_t;\theta).
$$

With column gradients, the prior-state Jacobian is

$$
J_t=I-\eta\nabla^2_{\phi\phi}\mathcal L_t.
$$

Let $$D_t=d\phi_t/d\theta$$. Chain differentiation gives

$$
D_{t+1}=J_tD_t-\eta\nabla^2_{\phi\theta}\mathcal L_t.
$$

The direct parameter derivative remains alongside the adapted-state contribution. The outer gradient adds $$D_T^\top\nabla_\phi\mathcal L_{\mathrm{outer}}$$. Products of $$J_t$$ shrink or amplify gradients; reset boundaries change which past adaptations affect the objective. A trainable learning rate or update network introduces additional derivative terms.

For a quadratic inner loss with positive-definite Hessian $$H$$ and fixed optimum, each eigenmode scales by $$1-\eta\lambda_j(H)$$. Stability requires $$0<\eta<2/\lambda_{\max}(H)$$. Curvature changes adaptation speed even at equal write frequency; a nonconvex network need not admit this global Hessian model.

## Schedules and coupled stability
{: id="11-wall-clock-timescales-and-coupled-stability"}

An exponential trace written every $$k$$ base steps with decay $$\beta\in(0,1)$$ retains weight proportional to $$\beta^m$$ after $$m$$ writes. Its base-step half-life is

$$
h_{\mathrm{base}}=k\frac{\log(1/2)}{\log\beta}.
$$

Equal long-run write counts can hide bursty versus uniform schedules. A module may perform many writes together or spread them through the interval, changing recency response and peak update latency even when empirical frequency agrees.

For the coupled linear system $$z_{t+1}=A_tz_t$$ with period $$k$$, boundaries obey $$z_{(m+1)k}=Pz_{mk}$$ with

$$
P=A_{k-1}\cdots A_1A_0.
$$

This finite-dimensional periodic system is asymptotically stable exactly when $$\rho(P)<1$$, where $$\rho$$ is the spectral radius. Individually stable modules need not give a stable product.

Under constant per-module read/write costs, an average compute model is

$$
\overline C=\sum_j C_{\mathrm{read},j}+\sum_j f_jC_{\mathrm{write},j}.
$$

This planning model omits synchronization, batching, and memory traffic. Coincident writes increase peak latency; average compute, tail latency, state size, reset lifetime, and available learning signals remain distinct measurements.

## Hope replication
{: id="12-what-a-hope-replication-must-establish"}

A replication requires the actual self-modifying module, Continuum Memory System wiring, objectives, context flows, and schedule. Generic recurrence and standard Adam illustrate mechanisms without reproducing those components.

Separate ablations of self-modification, frequency, capacity, and gradient-through-update distinguish nested structure from extra resources. Comparisons need matched parameter counts, training tokens, initialization, optimizers, context lengths, supervision, and reset policies.

The theoretical model organizes interacting learning levels; a particular implementation must demonstrate retention, adaptation, or efficiency on a defined stream.

## References
{: id="references-and-current-scope"}

- [Behrouz et al., Nested Learning](https://arxiv.org/abs/2512.24695).
- [Author-hosted full paper](https://abehrouz.github.io/files/NL.pdf).
- [Google Research overview](https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/).
- [Adam](https://arxiv.org/abs/1412.6980) and [Titans](https://arxiv.org/abs/2501.00663).
