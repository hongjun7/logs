---
title: Nested Learning
tags: ml
subtitle: This post introduces a new learning paradigm, Nested Learning (NL), which represents a model as a coherent set of nested, multi-level, and/or parallel optimization problems, each with its own context flow.
---

This post introduces Nested Learning as a paradigm for continual learning, drawing on a [Google Research blog post](https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/) and the accompanying [paper](https://abehrouz.github.io/files/NL.pdf).

[Continual learning](https://www.cs.uic.edu/~liub/lifelong-learning/continual-learning.pdf) studies models that learn from a non-stationary stream (tasks or distributions) while preserving previously acquired capabilities. A central failure mode is **catastrophic forgetting**: continuing gradient updates on new data often degrades performance on older tasks.

Let

$$
\{ \mathcal{D}_{t} \}_{t=1}^{T}
$$

be a sequence of data distributions and $ {f}_{θ} $ be a parametric model.

Let the per-task risk be

$$
\begin{align*}
R_t(θ) = \mathbb{E}_{(x,y)\sim \mathcal{D}_t}\big[\ell(f_θ(x),y)\big].
\end{align*}
$$

A naïve sequential learner updates $θ$ to reduce $R_t$ for the current $t$, but this can increase $R_i$ for earlier $i<t$.

## Nested Learning

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-15-Nested-Learning/fig1.png?raw=true"> </p>

Nested Learning (NL) reframes an ML system as a collection of **interacting optimization problems** (nested and/or parallel) organized by **update frequency** and driven by **context flow**, rather than as a single static “architecture + optimizer” split.

## Context Flow and Update Frequency

### Components and states

Let a learning system have internal components/states
$$
\begin{align*}
\mathcal{S} = \{ z^{(1)}, z^{(2)}, \dots, z^{(M)} \},
\end{align*}
$$
where each $z$ may represent parameters (e.g., weights), optimizer states (e.g., moments), memory buffers, or fast-adaptation variables.

### Context flow

Let $C_t$ denote the information available at step $t$. NL emphasizes that different components update using different **subsets** of context.

Let the context used by component $z$ at step $t$ be
$$
\begin{align*}
C_t^{(z)} \subseteq C_t.
\end{align*}
$$

Examples of context elements (non-exhaustive):
- input tokens / observations
- retrieved memory values
- gradients / losses
- internal activations or surprise signals

### Update indicators and empirical update frequency

Let $\Delta t$ be the base time unit (e.g., one token step at inference, or one gradient step at training).

Let the update indicator for component $z$ be
$$
\begin{align*}
u_z(t) =
\begin{cases}
1, & \text{if } z \text{ is updated at step } t \\
0, & \text{otherwise}.
\end{cases}
\end{align*}
$$

Let the empirical update frequency over horizon $H$ be
$$
\begin{align*}
f_z(H) = \frac{1}{H}\sum_{t=1}^{H} u_z(t).
\end{align*}
$$

NL uses frequency to induce a **level ordering**: components that update more frequently can be treated as “faster-level” mechanisms.

### NL as a multi-level optimization system

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-15-Nested-Learning/fig2.png?raw=true"> </p>

Let levels be indexed by $k \in \{1,\dots,K\}$, ordered from fast to slow.

Let $θ^{(k)}$ be the state(s) updated at level $k$, with objective(s) $L^{(k)}$ and context $C^{(k)}$.

A generic level objective is
$$
\begin{align*}
θ^{(k)} \leftarrow \arg\min_{θ^{(k)}} L^{(k)}\big(θ^{(k)}; C^{(k)}\big),
\end{align*}
$$
where $C^{(k)}$ may depend on faster states $θ^{(1)},\dots,θ^{(k-1)}$.

This abstraction captures “nested” or “parallel” optimization problems emphasized in NL.

## Associative Memory

This unifies attention, optimization state, and other learning modules.

### General key-value associative memory

Let

$$
\begin{align*}
K &= \{k_j\}_{j=1}^{n} \subset \mathbb{R}^{d_k}, \\
V &= \{v_j\}_{j=1}^{n} \subset \mathbb{R}^{d_v}, \\
q &\in \mathbb{R}^{d_k}.
\end{align*}
$$

Define similarity logits and normalized weights:

$$
\begin{align*}
s_j(q) &= \frac{\langle q, k_j\rangle}{\sqrt{d_k}}, \qquad j=1,\dots,n \\
\alpha_j(q) &= \frac{\exp(s_j(q))}{\sum_{i=1}^{n}\exp(s_i(q))}, \qquad j=1,\dots,n.
\end{align*}
$$

Define the readout:

$$
\begin{align*}
\hat{v}(q) = \sum_{j=1}^{n}\alpha_j(q)\, v_j.
\end{align*}
$$

### Attention as associative memory

Let $Q\in\mathbb{R}^{m\times d_k}$, $K\in\mathbb{R}^{n\times d_k}$, $V\in\mathbb{R}^{n\times d_v}$. Define scaled dot-product attention:

$$
\begin{align*}
\mathrm{Attn}(Q,K,V) = \mathrm{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V.
\end{align*}
$$

It explicitly states attention can be formalized as associative memory.

## Training and Optimizers as Memory

A central NL claim is that the “optimizer” is not merely an external procedure but can be treated as a **memory module** that compresses gradient history.

### Online learning notation

Let $\{(x_t,y_t)\}_{t\ge1}$ be a stream and $f_θ$ a model.

Define the per-step loss and gradient:

$$
\begin{align*}
\ell_t(θ) &= \ell\!\left(f_θ(x_t),y_t\right) \\
g_t &= \nabla_θ \ell_t(θ).
\end{align*}
$$

### SGD baseline

Let $\eta>0$ be a learning rate. Define SGD:

$$
\begin{align*}
θ_{t+1} = θ_t - \eta g_t.
\end{align*}
$$

### Momentum as an exponential-memory of gradients

Let $\beta\in[0,1)$ be the momentum coefficient and $v_t$ be the velocity (memory state).

Define momentum updates:

$$
\begin{align*}
v_{t+1} &= \beta v_t + (1-\beta) g_t \\
θ_{t+1} &= θ_t - \eta v_{t+1}.
\end{align*}
$$

**NL interpretation:** $v_t$ is a fast state that compresses gradient context; $θ_t$ changes using this memory trace.

### Adam as first/second-moment memories

Let $\beta_1,\beta_2\in[0,1)$, $\epsilon>0$, and let $m_t,s_t$ be first/second-moment states.

Define moments:

$$
\begin{align*}
m_t &= \beta_1 m_{t-1} + (1-\beta_1) g_t \\
s_t &= \beta_2 s_{t-1} + (1-\beta_2)\, (g_t \odot g_t).
\end{align*}
$$

Define bias corrections:

$$
\begin{align*}
\hat{m}_t &= \frac{m_t}{1-\beta_1^t} \\
\hat{s}_t &= \frac{s_t}{1-\beta_2^t}.
\end{align*}
$$

Define Adam update:

$$
\begin{align*}
θ_{t+1} = θ_t - \eta \frac{\hat{m}_t}{\sqrt{\hat{s}_t}+\epsilon}.
\end{align*}
$$

**NL interpretation**: These optimizer states act as compressed “associative memories” of the gradient stream; the paper further links Adam to an optimal associative memory view under an $\ell_2$-regression framing.

## Continuum Memory Systems (CMS)

Instead of a binary short-term vs long-term split, memory is a *spectrum* of modules with distinct update frequencies.

### Multi-rate memory modules

Let **memory modules** be

$$
\left\{M^{(k)}\right\}_{k=1}^{K}
$$

ordered by decreasing update frequency:

$$
\begin{align*}
f_{M^{(1)}} \ge f_{M^{(2)}} \ge \dots \ge f_{M^{(K)}}.
\end{align*}
$$

Let each module produce a representation $y_t^{(k)}$ from input $x_t$:
$$
\begin{align*}
y_t^{(k)} = M^{(k)}(x_t; \phi^{(k)}_t),
\end{align*}
$$
where $\phi^{(k)}_t$ is the internal state updated at that module’s frequency.

### Aggregation across the spectrum

Let $\mathrm{Agg}$ be an aggregation operator (e.g., concatenation + projection, gated sum, attention over modules). Define:
$$
\begin{align*}
y_t = \mathrm{Agg}\big(y_t^{(1)}, y_t^{(2)}, \dots, y_t^{(K)}\big).
\end{align*}
$$

It presents representative aggregation forms over modules indexed by frequency; the key structural property is explicit multi-frequency composition.

**Continual-learning intuition**
- fast modules absorb recent changes without forcing slow modules to drift;
- slow modules preserve stable information, reducing overwriting.

## Hope

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-15-Nested-Learning/fig3.png?raw=true"> </p>

It introduces **Hope** as a proof-of-concept architecture motivated by **Nested Learning (NL)**. Hope combines a **self-modifying learning module** (fast online adaptation) with a **Continuum Memory System (CMS)** (multi-rate memory blocks).

### Generic Hope-style template

Let $θ$ be **slow parameters** (consolidated mainly during training), $ϕ_t$ a **fast adaptation state** updated online, and 

$$
\mathcal{M}_{t}=\left\{M_{t}^{(k)}\right\}_{k=1}^{K}
$$

a **Continuum Memory Systems(CMS)**.

Let $\mathcal{U}_\psi$ be a (possibly learned) update rule with parameters $\psi$. Let $C_t$ denote the **context flow** available at step $t$ (e.g., $x_t$, hidden state $h_t$, memory readout, optional surprise/loss).

Define the prediction and loss:

$$
\begin{align*}
\hat{y}_t &= f(x_t; θ, \phi_t, \mathcal{M}_t), \\
\ell_t &= \ell(\hat{y}_t, y_t).
\end{align*}
$$

Define the fast state update (inference-time / online adaptation):

$$
\begin{align*}
\phi_{t+1} = \mathcal{U}_\psi(\phi_t, C_t).
\end{align*}
$$

A concrete gated form (example):

$$
\begin{align*}
g_t &= \sigma\!\left(W_g[\phi_t; C_t]\right), \\
\Delta_t &= W_\Delta[\phi_t; C_t], \\
\phi_{t+1} &= (1-g_t)\odot \phi_t + g_t \odot \Delta_t.
\end{align*}
$$

Define CMS reads and aggregation:

$$
\begin{align*}
m_t^{(k)} &= \mathrm{Read}^{(k)}(x_t; M_t^{(k)}), \\
m_t &= \mathrm{Agg}\big(m_t^{(1)},\dots,m_t^{(K)}\big).
\end{align*}
$$

Define frequency-controlled CMS writes using $u_k(t)\in\{0,1\}$:

$$
\begin{align*}
M_{t+1}^{(k)} =
\begin{cases}
\mathrm{Write}^{(k)}(M_t^{(k)}, x_t, h_t), & u_k(t)=1 \\
M_t^{(k)}, & u_k(t)=0.
\end{cases}
\end{align*}
$$

Define empirical update frequency over horizon $H$:
$$
\begin{align*}
f_k(H) = \frac{1}{H}\sum_{t=1}^{H} u_k(t),
\end{align*}
$$
typically arranged as a spectrum $f_1 \ge f_2 \ge \dots \ge f_K$.

Define slow learning (training-time consolidation):

$$
\begin{align*}
θ &\leftarrow θ - \eta_θ \nabla_θ \sum_{t=1}^{T}\ell_t, \\
\psi &\leftarrow \psi - \eta_\psi \nabla_\psi \sum_{t=1}^{T}\ell_t.
\end{align*}
$$

### NL interpretation

Let $\phi$ and high-frequency CMS modules be **fast-level learners**, and $θ$ (and low-frequency modules) be **slow-level learners**. Hope fits NL as a **multi-level nested learning** system: online adaptation happens via fast states/memory, while stable knowledge is consolidated into slower components.

## Experiments

The section describes an evaluation setup and main findings for testing **Hope** as the core architecture (“backbone”) of a language model.

* **Benchmarks / datasets:** Hope and other models are evaluated on standard **language modeling** datasets (Wikitext, LAMBADA) and multiple **common-sense reasoning** benchmarks (PIQA, HellaSwag, WinoGrande, ARC-Easy, ARC-Challenge, SIQA, BoolQ).

* **Baselines compared against:**

  1. **Hebbian/Delta-rule–style models:** RetNet, DeltaNet.
  2. **Modern matrix-valued recurrent models:** RWKV-7, Comba.
  3. **Attention-free deep memory modules** with different internal biases (dot-product, L2, Lp regression): TTT, Miras, DLA, Titans.
  4. **Transformers** and a **hybrid attention + linear RNN** model: Samba.

* **Training setup:** Models are trained from scratch at two scales—about **760M parameters (30B tokens)** and **1.3B parameters (100B tokens)**—using a data mixture of **FineWeb-Edu** and long-context documents, **32K vocabulary**, and **AdamW** with model-specific tuned learning rates (otherwise following a referenced default optimizer configuration).

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-15-Nested-Learning/fig4.png?raw=true"> </p>

* **Result:** **Hope achieves the best average performance** across both language modeling and common-sense reasoning benchmarks, beating all baselines. Additionally, when scaling up parameters, **Hope’s performance improves more than other attention-free models**.

## Appendix A: Equation Reference

### A.1 Attention (memory retrieval)
Let $K,V,q$ be keys, values, query. Define:

$$
\begin{align*}
s_j(q) &= \frac{\langle q, k_j\rangle}{\sqrt{d_k}} \\
\alpha_j(q) &= \frac{\exp(s_j(q))}{\sum_{i=1}^{n}\exp(s_i(q))} \\
\hat{v}(q) &= \sum_{j=1}^{n}\alpha_j(q)\, v_j.
\end{align*}
$$

### A.2 SGD / Momentum / Adam
Let

$$
g_t=\nabla_θ \ell_t(θ)
$$

Then,

$$
\begin{align*}
\text{SGD:}\quad θ_{t+1} &= θ_t - \eta g_t
\end{align*}
$$

$$
\begin{align*}
\text{Momentum:}\quad v_{t+1} &= \beta v_t + (1-\beta) g_t \\
θ_{t+1} &= θ_t - \eta v_{t+1}
\end{align*}
$$

$$
\begin{align*}
\text{Adam:}\quad m_t &= \beta_1 m_{t-1} + (1-\beta_1) g_t \\
s_t &= \beta_2 s_{t-1} + (1-\beta_2)(g_t\odot g_t) \\
\hat{m}_t &= \frac{m_t}{1-\beta_1^t},\quad \hat{s}_t = \frac{s_t}{1-\beta_2^t} \\
θ_{t+1} &= θ_t - \eta \frac{\hat{m}_t}{\sqrt{\hat{s}_t}+\epsilon}
\end{align*}
$$

### A.3 Continual learning metrics
Let $a_{t,i}$ be accuracy on task $i$ after training to $t$.

$$
\begin{align*}
\mathrm{ACC}_T &= \frac{1}{T}\sum_{i=1}^{T} a_{T,i} \\
\mathrm{F}_T &= \frac{1}{T-1}\sum_{i=1}^{T-1}\left(\max_{t<T} a_{t,i} - a_{T,i}\right)
\end{align*}
$$

### A.4 Update frequency
Let $u_z(t)\in\{0,1\}$ indicate whether component $z$ updates at time $t$.

$$
\begin{align*}
f_z(H) = \frac{1}{H}\sum_{t=1}^{H} u_z(t)
\end{align*}
$$

## References
- [Behrouz et al., *Nested Learning: The Illusion of Deep Learning Architecture* (NeurIPS 2025)](https://abehrouz.github.io/files/NL.pdf)  
- [Google Research Blog (2025-11-07), *Introducing Nested Learning: A new ML paradigm for continual learning*](https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/)

