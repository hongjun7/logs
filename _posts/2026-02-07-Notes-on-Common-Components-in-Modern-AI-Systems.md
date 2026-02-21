---
title: Common ML Concepts Explained Simply
tags: ml
subtitle: This post introduces basic concepts of tokenization, decoding, prompting, tool-augmented agents, RAG, RLHF, VAEs, diffusion models, and LoRA—presented with standard objective functions and probabilistic notation.
---

Modern AI products are typically built by composing a small number of reusable modules:

1. **Representations for inputs/outputs** (how text/images become model inputs and how outputs are represented)
2. **Probabilistic generation and control** (how models sample or search for good outputs)
3. **Grounding and alignment** (how models stay faithful to sources and human intent)
4. **Adaptation and generative modeling** (how we efficiently fine-tune or build generative models)

The sections below describe the most frequently recurring modules using standard notation and objective functions.

## Tokenization

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770529991710.png?raw=true">
</p>

Language models do not directly process raw text characters. Instead, text is converted into a **sequence of tokens**, and each token is represented by an integer **token ID**.

Let a raw text string be $s \in \Sigma^\ast$, where $\Sigma$ is the character set and $\Sigma^\ast$ denotes all finite strings over $\Sigma$.

A tokenizer defines a mapping:

$$
\begin{align*}
\tau: Σ^{\ast} \to \mathcal{V}^{\ast}
\end{align*}
$$

where $\mathcal{V}$ is a finite vocabulary of tokens and $\mathcal{V}^{\ast}$ is the set of finite token sequences.

Each token is mapped to an integer ID via:

$$
\begin{align*}
\iota: \mathcal{V} \to \{1,2,\dots,|\mathcal{V}|\}
\end{align*}
$$

Thus, the model receives a sequence of IDs:

$$
\begin{align*}
x_{1:T} = (\iota(\tau(s)_1), \dots, \iota(\tau(s)_T))
\end{align*}
$$

**Practical intuition**
- Tokenization trades off **sequence length** (efficiency) vs. **coverage** (ability to represent arbitrary text).
- Common patterns (frequent words/subwords) often become single tokens; rare words are composed from smaller pieces.

### Byte Pair Encoding (BPE) merges

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770529887128.png?raw=true">
</p>

BPE starts with a basic vocabulary (often characters/bytes) and then repeatedly merges the most frequent **adjacent token pair** in a corpus, creating new tokens.

Let $\mathcal{C}$ be the multiset of token sequences over a corpus under the current vocabulary. Define adjacent-pair counts:

$$
\begin{align*}
c(a,b) = \#\{\text{occurrences of adjacent pair } (a,b) \text{ in } \mathcal{C}\}
\end{align*}
$$

At each step, select the most frequent pair:

$$
\begin{align*}
(a^\ast, b^\ast) = \arg\max_{(a,b)} c(a,b)
\end{align*}
$$

and merge $\left(a^\ast, b^\ast\right)$ into a new token $ab$.

**Practical intuition**
- Merging frequent pairs reduces sequence length.
- Over time, frequent words may become single tokens, while rare words remain multi-token.

## Decoding

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530055655.png?raw=true">
</p>

An autoregressive language model defines a probability distribution over sequences:

$$
\begin{align*}
p_\theta(x_{1:T}) = \prod_{t=1}^{T} p_\theta(x_t \mid x_{<t})
\end{align*}
$$

At time $t$, the model outputs logits:

$$
\begin{align*}
z_t \in \mathbb{R}^{|\mathcal{V}|}
\end{align*}
$$

and converts them to probabilities with softmax:

$$
\begin{align*}
p_\theta(x_t = v \mid x_{<t}) = \mathrm{softmax}(z_t)_v
= \frac{\exp(z_{t,v})}{\sum_{u\in\mathcal{V}} \exp(z_{t,u})}
\end{align*}
$$

**Decoding** is the method used to choose the next token from this distribution (deterministically or by sampling).

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530258159.png?raw=true">
</p>

### Greedy

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530082015.png?raw=true">
</p>

Greedy decoding always picks the most likely token:

$$
\begin{align*}
\hat{x}_t = \arg\max_{v\in\mathcal{V}} p_\theta(v \mid \hat{x}_{<t})
\end{align*}
$$

**Intuition**
- Fast and deterministic.
- Can be brittle: once it makes a locally “best” choice, it cannot recover.

### Temperature

Given temperature $\alpha > 0$, rescale logits before softmax:

$$
\begin{align*}
p_\theta^\alpha(v \mid x_{<t}) \propto \exp(z_{t,v}/\alpha)
\end{align*}
$$

**Intuition**
- $\alpha < 1$: sharper distribution (more conservative).
- $\alpha > 1$: flatter distribution (more diverse/random).

### Top-$p$ (nucleus)

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530123687.png?raw=true">
</p>

Let tokens be sorted by probability $p_1 \ge p_2 \ge \dots$. Define the smallest set $S_p$ such that:

$$
\begin{align*}
\sum_{v\in S_p} p(v \mid x_{<t}) \ge p
\end{align*}
$$

Sample from the renormalized distribution:

$$
\begin{align*}
\tilde{p}(v \mid x_{<t}) =
\begin{cases}
\frac{p(v \mid x_{<t})}{\sum_{u\in S_p} p(u \mid x_{<t})}, & v\in S_p \\
0, & \text{otherwise}
\end{cases}
\end{align*}
$$

**Intuition**
- Keep only the minimal set of tokens that accounts for probability mass $p$.
- The “candidate set size” adapts automatically depending on model confidence.

## Prompting

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530313143.png?raw=true">
</p>

A prompt $c$ includes instructions, constraints, examples, and possibly retrieved context. Generation is conditioned on $c$:

$$
\begin{align*}
p_\theta(y \mid c) = \prod_{t=1}^{|y|} p_\theta(y_t \mid y_{<t}, c)
\end{align*}
$$

### Few-shot

If $c$ contains $k$ demonstrations $\{(x^{(i)}, y^{(i)})\}_{i=1}^{k}$, you can interpret the prompt as providing evidence about an (implicit) latent task variable $h$:

$$
\begin{align*}
p(y \mid x, \mathcal{D}) = \int p(y \mid x, h)\,p(h \mid \mathcal{D})\,dh
\end{align*}
$$

**Intuition**
- The examples define the task “on the fly” without updating weights.

### CoT (latent rationale)

Introduce latent reasoning variables $r$:

$$
\begin{align*}
p(y \mid c) = \sum_{r} p(y \mid r, c)\,p(r \mid c)
\end{align*}
$$

**Intuition**
- The model may internally form intermediate reasoning $r$ and then produce $y$.
- This is a probabilistic way to express “reasoning as an unobserved intermediate.”

## Agents

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530390060.png?raw=true">
</p>

Tool-augmented agents can be modeled as a sequential decision process:

- state $s_t$ (dialogue, tool outputs, memory),
- action $a_t \in \mathcal{A}$ (tool call, clarification question, final answer),
- transition $s_{t+1} \sim P(\cdot \mid s_t, a_t)$.

A policy $\pi_\theta(a \mid s)$ selects actions. With a budget constraint:

$$
\begin{align*}
\sum_{t=1}^{T} \mathrm{cost}(a_t) \le B
\end{align*}
$$

A generic control objective is:

$$
\begin{align*}
\max_{\pi_\theta}\; \mathbb{E}\left[\sum_{t=1}^{T} \gamma^{t-1} r_t\right]
\end{align*}
$$

**Intuition**
- “Actions” include thinking steps like calling tools, retrieving evidence, or asking follow-ups.
- The reward can represent correctness, task completion, user satisfaction, etc.

## RAG

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530433335.png?raw=true">
</p>

Let a knowledge store be segmented into passages $\{d_j\}$. A dense retriever scores relevance using embeddings:

$$
\begin{align*}
s(q, d_j) = \langle f(q), g(d_j)\rangle
\end{align*}
$$

Top-$K$ retrieval:

$$
\begin{align*}
D_K(q) = \operatorname{TopK}_j \; s(q, d_j)
\end{align*}
$$

Generation with retrieved evidence:

$$
\begin{align*}
p_\theta(y \mid q) \approx p_\theta(y \mid q, D_K(q))
\end{align*}
$$

Latent-variable view:

$$
\begin{align*}
p(y \mid q) = \sum_{D} p(y \mid q, D)\,p(D \mid q)
\end{align*}
$$

**Intuition**
- Retrieval chooses evidence; generation conditions on that evidence.
- This reduces hallucination if retrieval quality is high and the prompt enforces citation/faithfulness.

## RLHF

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530478848.png?raw=true">
</p>

RLHF aligns model behavior with human preferences, typically in two parts:
1) learn a reward model from preference comparisons, then  
2) optimize the policy while staying close to a reference model.

### Preferences

Given prompt $x$ and responses $y^{(1)}, y^{(2)}$, define reward $R_\phi(x,y)$. The preference probability:

$$
\begin{align*}
P\big(y^{(1)} \succ y^{(2)} \mid x\big) =
Σ\big(R_\phi(x,y^{(1)}) - R_\phi(x,y^{(2)})\big)
\end{align*}
$$

Training loss:

$$
\begin{align*}
\mathcal{L}(\phi)= -\mathbb{E}\left[\log Σ\big(R_\phi(x,y^+) - R_\phi(x,y^-)\big)\right]
\end{align*}
$$

### KL-regularized policy

Let $\pi_\theta$ be the policy and $\pi_{\mathrm{ref}}$ a reference policy:

$$
\begin{align*}
\max_{\theta}\; \mathbb{E}_{x,\, y \sim \pi_\theta(\cdot \mid x)}
\Big[
R_\phi(x,y) - \beta \,\mathrm{KL}\big(\pi_\theta(\cdot \mid x)\,\|\,\pi_{\mathrm{ref}}(\cdot \mid x)\big)
\Big]
\end{align*}
$$

**Intuition**
- Reward encourages preferred outputs.
- KL discourages drifting too far (stability + prevents reward hacking).

## VAE

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770532121006.png?raw=true">
</p>

A VAE defines a latent-variable generative model $p_\theta(x \mid z)p(z)$ and an approximate posterior $q_\phi(z \mid x)$.

The ELBO:

$$
\begin{align*}
\log p_\theta(x) \ge
\mathbb{E}_{q_\phi(z\mid x)}[\log p_\theta(x\mid z)] -
\mathrm{KL}(q_\phi(z\mid x)\,\|\,p(z))
\end{align*}
$$

**Intuition**
- Reconstruction term: make $z$ informative for reproducing $x$.
- KL term: regularize latents so sampling from $p(z)$ produces valid $x$.

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530630177.png?raw=true">
</p>

## Diffusion

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770532086687.png?raw=true">
</p>

Diffusion models define a forward noising process and learn to reverse it.

Forward noising:

$$
\begin{align*}
q(x_t \mid x_{t-1}) = \mathcal{N}\big(\sqrt{1-\beta_t}\,x_{t-1}, \beta_t I\big)
\end{align*}
$$

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770531259618.png?raw=true">
</p>

Marginal:

$$
\begin{align*}
q(x_t \mid x_0) = \mathcal{N}\big(\sqrt{\bar{\alpha}_t}\,x_0, (1-\bar{\alpha}_t)I\big)
\end{align*}
$$

where $\alpha_t = 1-\beta_t$ and $\bar{\alpha}_t = \prod_{i=1}^{t} \alpha_i$.

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770531230164.png?raw=true">
</p>

Noise prediction (conditioning $c$):

$$
\begin{align*}
\mathcal{L}(\theta)=
\mathbb{E}_{t, x_0, \varepsilon}
\left[\left\|\varepsilon - \varepsilon_\theta(x_t, t, c)\right\|^2\right]
\end{align*}
$$

with:

$$
\begin{align*}
x_t = \sqrt{\bar{\alpha}_t}\,x_0 + \sqrt{1-\bar{\alpha}_t}\,\varepsilon,
\quad
\varepsilon \sim \mathcal{N}(0,I)
\end{align*}
$$

**Intuition**
- Train a model to predict the noise added at step $t$.
- Sampling iteratively removes noise to generate a clean sample.

## LoRA

<p align="center">
  <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770531338665.png?raw=true">
</p>

For a linear layer $W \in \mathbb{R}^{d_{\mathrm{out}}\times d_{\mathrm{in}}}$, LoRA constrains the update to be low-rank:

$$
\begin{align*}
\Delta W = BA
\end{align*}
$$

where:

$$
\begin{align*}
A \in \mathbb{R}^{r \times d_{\mathrm{in}}},
\quad
B \in \mathbb{R}^{d_{\mathrm{out}} \times r},
\quad
r \ll \min(d_{\mathrm{in}}, d_{\mathrm{out}})
\end{align*}
$$

Effective weights:

$$
\begin{align*}
W' = W + \Delta W = W + BA
\end{align*}
$$

Parameter count reduction:

$$
\begin{align*}
d_{\mathrm{out}}d_{\mathrm{in}}
\;\;\to\;\;
r(d_{\mathrm{in}}+d_{\mathrm{out}})
\end{align*}
$$

**Intuition**
- Fine-tuning updates often lie in a low-dimensional subspace.
- LoRA reduces trainable parameters and storage while preserving performance.

## Reference
- [[1] [ByteByteAI and ByteByteGo] 9 AI Concepts Explained in 7 minutes: AI Agents, RAGs, Tokenization, RLHF, Diffusion, LoRA...](https://www.youtube.com/watch?v=nVnxG10D5W0)
- [[2] [Medium] Decoding the Decoder: Top-k, Top-p, Temperature, Beam Search & Hallucinations in LLMs](https://medium.com/@ayushyajnik2/decoding-the-decoder-top-k-top-p-temperature-beam-search-hallucinations-in-llms-e54963eb3de7)
