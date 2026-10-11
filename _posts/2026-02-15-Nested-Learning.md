---
title: "Nested Learning: Memory, Optimization, and Multiple Timescales"
tags: ["machine-learning", "memory", "continual-learning"]
subtitle: "Understand Nested Learning through explicit state updates, associative memory, optimizer traces, and the distinction between a general mathematical model and the Hope architecture."
last_modified_at: 2026-10-11
sources_checked_at: 2026-10-11
---

> **The idea in one minute.** Nested Learning views a model and its learning process as interacting systems that update on different context streams and timescales. An optimizer's moment estimates, a fast associative memory, and slow model weights can all be stateful learners. This perspective helps design continual adaptation, but multiple timescales alone do not prove that forgetting disappears.

**Reading path.** Start with state versus parameters, derive a linear memory update, and then examine momentum and Adam. The later sections describe a generic multi-rate construction and explain how it relates to the paper's Hope model. Prerequisites are gradients, matrices, and supervised loss functions.

## 1. What changes when a model learns?

A conventional supervised model predicts $$f_\theta(x)$$ and updates parameters using a loss. A stateful learner additionally carries $$z_t$$, which changes with its input history:

$$
\widehat y_t=f_\theta(x_t,z_t),\qquad
z_{t+1}=U_\psi(z_t,C_t).
$$

$$C_t$$ is the context available for that update. It may include an input, a representation, a target, or an internally generated learning signal. If an update requires a target $$y_t$$, that target must actually be available; ordinary inference does not magically provide ground truth.

The Nested Learning paper organizes architecture and optimization through nested or parallel optimization levels and their context flows. It motivates a continuum of update frequencies and introduces Hope as a proof of concept. The equations in the following explanatory sections are **generic mathematical examples**, not undocumented equations of Hope. [Paper](https://arxiv.org/abs/2512.24695) and [Google Research explanation](https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/).

## 2. Associative memory as a regression problem

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

Positive $$\lambda$$ makes the inverse well defined. Without regularization, singular keys may require a pseudoinverse and the optimum need not be unique.

For an unregularized one-observation online loss, a gradient step is

$$
M_{t+1}=M_t-\eta_t(M_tk_t-v_t)k_t^\top.
$$

This delta-rule update writes the prediction error into memory. It is dimensionally consistent: $$(M_tk_t-v_t)k_t^\top$$ has shape $$d_v\times d_k$$.

### Interference is visible in the algebra

After writing pair $$(k_t,v_t)$$, the output for an old key $$k'$$ changes by

$$
(M_{t+1}-M_t)k'
=-\eta_t(M_tk_t-v_t)(k_t^\top k').
$$

Orthogonal keys give zero interference for this particular update; correlated keys generally change one another's readout. Fast writing alone therefore does not guarantee retention. Capacity, key geometry, regularization, gating, and consolidation all affect memory behavior.

For a fixed key with squared norm $$c>0$$, the one-sample error evolves as $$e_{t+1}=(1-\eta c)e_t$$. Contraction requires $$0<\eta c<2$$. This elementary stability condition is not a convergence theorem for a nonlinear multi-module architecture, but it illustrates why update scales matter.

## 3. Attention as a different memory read

Given a query $$q\in\mathbb R^{d_k}$$, key vectors $$k_i$$, and values $$v_i$$,

$$
\alpha_i(q)=\frac{\exp(q^\top k_i/\sqrt{d_k})}
{\sum_j\exp(q^\top k_j/\sqrt{d_k})},
\qquad\widehat v(q)=\sum_i\alpha_i(q)v_i.
$$

This is a weighted read over explicitly stored key–value pairs. Updating the cache appends or replaces stored data; it need not update trainable weights by a gradient. A regression memory compresses associations into parameters such as $$M$$. Both can be discussed as memory, but their capacity, computational cost, and update mechanism differ.

A decoder's KV cache is often local to a request. Calling it “learning” in a broad computational sense does not imply persistent model fine-tuning across users. Always state the lifetime and reset policy of a fast state.

## 4. Optimizers already carry memory

For gradient $$g_t$$, normalized momentum maintains

$$
v_t=\beta v_{t-1}+(1-\beta)g_t,\qquad0\le\beta<1.
$$

With $$v_0=0$$, expansion gives

$$
v_t=(1-\beta)\sum_{i=1}^{t}\beta^{t-i}g_i.
$$

It is an exponentially weighted history of gradients. The half-life in update steps is $$\log(1/2)/\log\beta$$ for $$0<\beta<1$$. A coefficient near one stores a longer trace; it also responds more slowly to new directions.

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

The division and square root are coordinatewise; $$\epsilon>0$$ avoids division by zero. Bias correction addresses initialization of moment traces under its conventional assumptions. It does not fix every nonstationary bias or guarantee convergence for arbitrary objectives. Nested Learning's optimizer-as-memory viewpoint is an interpretation of these states; the equations above are the standard Adam recurrence. [Adam](https://arxiv.org/abs/1412.6980).

## 5. Nested objectives and gradient flow

A simple bilevel construction is

$$
\phi^*(\theta)=\arg\min_\phi\mathcal L_{\mathrm{inner}}(\phi;\theta),\qquad
\min_\theta\mathcal L_{\mathrm{outer}}(\theta,\phi^*(\theta)).
$$

If the inner solution is unique and smooth, its gradient is zero, and the inner Hessian in $$\phi$$ is invertible, implicit differentiation gives

$$
\frac{d\phi^*}{d\theta}
=-\left(\nabla_{\phi\phi}^2\mathcal L_{\mathrm{inner}}\right)^{-1}
\nabla_{\phi\theta}^2\mathcal L_{\mathrm{inner}}.
$$

The outer gradient includes both a direct effect and the effect through the adapted state. Unrolling a finite number of update steps is a different computational route. Truncating that unroll or stopping gradients changes the optimized approximation. These choices determine training cost and behavior; a box labeled “fast learner” is not enough to specify them.

This generic bilevel example explains one type of nesting. It does not assert that every component of the published architecture solves its inner problem exactly at inference.

## 6. Multiple update frequencies

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

Frequency is not the same as learning rate. A module updated every step with a tiny step size may change less than a rarely updated module with a large step. Context horizon and update magnitude also shape its effective timescale.

The paper's Continuum Memory System uses this broad idea of multiple rates, and Hope combines it with a self-modifying learning module. A gated sum, concatenation, or attention over generic module outputs is a possible explanatory construction; it should not be described as the exact published aggregation unless checked against the paper's specification.

## 7. Continual-learning evaluation

Let $$a_{t,i}$$ be accuracy on task $$i$$ after learning through task $$t$$. Average final accuracy is

$$
\mathrm{ACC}_T=\frac1T\sum_{i=1}^{T}a_{T,i}.
$$

One forgetting measure for $$T>1$$ is

$$
\mathrm F_T=\frac1{T-1}\sum_{i=1}^{T-1}
\left(\max_{i\le t<T}a_{t,i}-a_{T,i}\right).
$$

This signed definition can be negative if a task improves later; clipping at zero gives a different metric. State the convention. Also measure forward transfer, backward transfer, adaptation latency, persistent state size, and reset behavior. A model may trade retention for plasticity, or perform well with fast state retained but poorly after reset.

Language modeling, long-context recall, online adaptation, and continual supervised learning are related but different evaluations. The original Hope experiments support claims within their model scales, data, and baselines. They do not establish that a new paradigm universally eliminates catastrophic forgetting or supersedes every Transformer.

## 8. Designing a controlled experiment

Start with a single fast memory and a clear learning signal. Compare frozen state, recurrent state without online gradients, and actual online updates. Then vary update rates while matching parameter count, total update budget, and inference compute. Test long task sequences, abrupt shifts, and the return to an old task.

Reset state between independent users or test streams unless persistence is part of the contract. Record which weights and states change during training and during evaluation. The newest available implementation can be useful, but a community reproduction is not automatically an official implementation of every paper component.

## 9. Forgetting as gradient interference

Let task $$i$$ have risk $$R_i(\theta)=\mathbb E_{(x,y)\sim\mathcal D_i}[\ell(f_\theta(x),y)]$$. A gradient update on task $$t$$ is $$\theta'=\theta-\eta g_t$$ with $$g_t=\nabla R_t(\theta)$$. A first-order expansion gives

$$
R_i(\theta')-R_i(\theta)=-\eta\nabla R_i(\theta)^\top g_t+O(\eta^2).
$$

If the old-task and current-task gradients point against one another, their inner product is negative and the first-order effect increases old-task risk. The full conclusion depends on curvature and step size. Under an $$L_i$$-Lipschitz gradient,

$$
\left\vert R_i(\theta-\eta g_t)-R_i(\theta)+\eta\nabla R_i(\theta)^\top g_t\right\vert
\le\frac{L_i\eta^2}{2}\|g_t\|^2.
$$

This bound quantifies when the first-order term dominates. In a one-dimensional toy model, $$R_1(\theta)=\tfrac12(\theta-1)^2$$ and $$R_2(\theta)=\tfrac12(\theta+1)^2$$ have different minimizers. At the old optimum $$\theta=1$$, one step toward the new task gives $$\theta'=1-2\eta$$ and old risk $$R_1(\theta')=2\eta^2$$. Separate fast states may reduce pressure on shared weights, but no architecture can assume that incompatible tasks disappear.

A regularized retention objective such as

$$
R_t(\theta)+\frac\lambda2\sum_jF_j(\theta_j-\theta_j^{\mathrm{old}})^2
$$

penalizes changes to old parameters with weights $$F_j\ge0$$. [Elastic Weight Consolidation](https://www.pnas.org/doi/10.1073/pnas.1611835114) uses an importance approximation related to the Fisher information. This is an alternative retention mechanism to compare, not an equation defining Hope. Replay, parameter isolation, regularization, and state consolidation impose different storage and privacy costs.

## 10. Differentiate through an explicit inner update

To make a fast learner concrete, let

$$
\phi_{t+1}=\phi_t-\eta\nabla_\phi\mathcal L_t(\phi_t;\theta).
$$

With column gradients, its derivative with respect to its prior fast state is

$$
J_t=I-\eta\nabla^2_{\phi\phi}\mathcal L_t.
$$

Let $$D_t=d\phi_t/d\theta$$. Chain differentiation gives

$$
D_{t+1}=J_tD_t-\eta\nabla^2_{\phi\theta}\mathcal L_t.
$$

The outer loss therefore includes the indirect term $$D_T^\top\nabla_\phi\mathcal L_{\mathrm{outer}}$$ in addition to its direct parameter derivative. Products of successive $$J_t$$ can shrink or amplify gradients; stopping the gradient at a state reset changes which effects are learned. A trainable learning-rate or update network introduces additional derivative terms.

For a quadratic inner loss with positive-definite Hessian $$H$$ and a fixed optimum, plain gradient descent contracts each eigenmode by $$1-\eta\lambda_j(H)$$. Stability requires $$0<\eta<2/\lambda_{\max}(H)$$. Different curvatures cause different adaptation speeds even at the same update frequency. This exact quadratic result explains a mechanism; a nonconvex network need not obey one global positive-definite Hessian.

## 11. Wall-clock timescales and coupled stability

For a simple exponential trace updated once every $$k$$ base steps with decay $$\beta\in(0,1)$$, a contribution's weight after $$m$$ updates is proportional to $$\beta^m$$. Its half-life in base steps is

$$
h_{\mathrm{base}}=k\frac{\log(1/2)}{\log\beta}.
$$

A frequency number by itself loses schedule information. Two modules can have the same number of writes in a long interval while one performs them in bursts and another spreads them uniformly. Their recency response and peak update latency can differ.

For a coupled linear approximation $$z_{t+1}=A_tz_t$$ with a schedule of period $$k$$, the state at period boundaries follows $$z_{(m+1)k}=Pz_{mk}$$, where

$$
P=A_{k-1}\cdots A_1A_0.
$$

Asymptotic stability of this finite-dimensional periodic linear system is equivalent to $$\rho(P)<1$$, with $$\rho$$ the spectral radius. Testing each module independently does not establish stability of their coupled product. This observation cautions against claiming that slow modules are automatically stable merely because they update less often.

Under constant per-module read/write costs, an average compute model is

$$
\overline C=\sum_j C_{\mathrm{read},j}+\sum_j f_jC_{\mathrm{write},j}.
$$

It ignores synchronization, batching, and memory traffic, so it is a planning model. Peak latency can be much larger when several slow writes coincide. Measure average compute, tail latency, and persistent-state size separately. Report the reset lifetime of every state and whether targets or self-supervised signals are available at each write.

## 12. What a Hope replication must establish

A faithful replication needs the paper's actual self-modifying module, Continuum Memory System wiring, objectives, context flows, and update schedule. A generic gated recurrent update is useful for teaching state dynamics but does not establish that wiring. Likewise, a standard Adam recurrence explains optimizer memory without reproducing a newly proposed optimizer.

Compare language modeling, recall, and continual adaptation as separate tasks. Specify parameter count, training tokens, initialization, optimizer, context length, state-reset policy, and all available supervision. Ablate self-modification, update frequency, memory capacity, and gradient-through-update separately where possible. A gain at a fixed model scale can result from more compute or more state; match those resources before attributing it to nested structure.

The central theoretical contribution to understand is the representation of interacting learning levels. The practical claim to evaluate is whether a particular realization improves retention, adaptation, or efficiency under a defined stream. Keeping those two statements separate makes the framework testable.

## References and current scope

- [Behrouz et al., Nested Learning](https://arxiv.org/abs/2512.24695).
- [Author-hosted full paper](https://abehrouz.github.io/files/NL.pdf).
- [Google Research overview](https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/).
- [Adam](https://arxiv.org/abs/1412.6980) and [Titans](https://arxiv.org/abs/2501.00663).

The revision separates exact standard recurrences, explanatory constructions, and the authors' empirical claims. This distinction makes the theory usable without presenting an illustrative model as a verified architecture.
