---
title: Notes on Common Components in Modern AI Systems
tags: ml
subtitle: This post introduces basic concepts of tokenization, decoding, prompting, tool-augmented agents, RAG, RLHF, VAEs, diffusion models, and LoRA—presented with standard objective functions and probabilistic notation.
---

Modern AI products are typically built by composing a small number of reusable modules: **(i) representations for inputs/outputs**, **(ii) probabilistic generation and control**, **(iii) mechanisms for grounding and alignment**, and **(iv) adaptation or generative modeling techniques**.

The sections below formalize the most frequently recurring modules with standard notation and objective functions.

## Tokenization

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770529991710.png?raw=true"> </p>

Let a raw text string be $ s \in \Sigma^{\ast} $, where $ \Sigma $ is the character set and $ \Sigma^{\ast} $ denotes the Kleene star (all finite strings over $ \Sigma $). A tokenizer defines a mapping:

$$
\begin{align*}
\tau: \Sigma^{\ast} \to \mathcal{V}^{\ast}
\end{align*}
$$

where $ \mathcal{V} $ is a finite vocabulary of tokens and $ \mathcal{V}^{\ast} $ is the set of finite token sequences. Each token is mapped to an integer ID via:

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

### Byte Pair Encoding(BPE) merges

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770529887128.png?raw=true"> </p>

Let $ \mathcal{C} $ be the multiset of token sequences over a corpus under the current vocabulary. Define adjacent-pair counts:

$$
\begin{align*}
c(a,b) = \#\{\text{occurrences of adjacent pair } (a,b) \text{ in } \mathcal{C}\}
\end{align*}
$$

At each step, select the most frequent pair:

$$
\begin{align*}
(a^{*}, b^{*}) = \arg\max_{(a,b)} c(a,b)
\end{align*}
$$

and merge $ \left( a^*, b^* \right) $ into a new token $ ab $.

## Decoding

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530055655.png?raw=true"> </p>

An autoregressive language model defines:

$$
\begin{align*}
p_\theta(x_{1:T}) = \prod_{t=1}^{T} p_\theta(x_t \mid x_{<t})
\end{align*}
$$

At time $ t $, the model outputs logits
$$
\begin{align*}
z_t \in \mathbb{R}^{|\mathcal{V}|}
\end{align*}
$$
and
$$
\begin{align*}
p_\theta(x_t = v \mid x_{<t}) = \mathrm{softmax}(z_t)_v = \frac{\exp(z_{t,v})}{\sum_{u\in\mathcal{V}} \exp(z_{t,u})}
\end{align*}
$$

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530258159.png?raw=true"> </p>

### Greedy

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530082015.png?raw=true"> </p>

$$
\begin{align*}
\hat{x}_t = \arg\max_{v\in\mathcal{V}} p_\theta(v \mid \hat{x}_{<t})
\end{align*}
$$

### Temperature

Given temperature $ \alpha > 0 $:

$$
\begin{align*}
p_\theta^\alpha(v \mid x_{<t}) \propto \exp(z_{t,v}/\alpha)
\end{align*}
$$

### Top-$p$

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530123687.png?raw=true"> </p>

Let tokens be sorted by probability $ p_1 \ge p_2 \ge \dots $. Define the smallest set $ S_p $ such that:

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

## Prompting

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530313143.png?raw=true"> </p>

Let $ c $ denote the prompt (instructions, constraints, examples, retrieved context). Generation is:

$$
\begin{align*}
p_\theta(y \mid c) = \prod_{t=1}^{|y|} p_\theta(y_t \mid y_{<t}, c)
\end{align*}
$$

### Few-shot

If $ c $ contains $ k $ demonstrations $ \{(x^{(i)}, y^{(i)})\}_{i=1}^{k} $, a latent-task view is:

$$
\begin{align*}
p(y \mid x, \mathcal{D}) = \int p(y \mid x, h)\,p(h \mid \mathcal{D})\,dh
\end{align*}
$$

### CoT (latent rationale)

Introduce latent reasoning variables $ r $:

$$
\begin{align*}
p(y \mid c) = \sum_{r} p(y \mid r, c)\,p(r \mid c)
\end{align*}
$$

## Agents

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530390060.png?raw=true"> </p>

Model agent interaction as a sequential decision process with:
- state $ s_t $ (dialogue, tool outputs, memory),
- action $ a_t \in \mathcal{A} $ (tool call, question, final answer),
- transition $ s_{t+1} \sim P(\cdot \mid s_t, a_t) $.

A policy $ \pi_\theta(a \mid s) $ selects actions. With a budget constraint:

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

## RAG

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530433335.png?raw=true"> </p>

Let a knowledge store be segmented into passages $ \{d_j\} $. A dense retriever scores relevance using embeddings:

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

## RLHF

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530478848.png?raw=true"> </p>

### Preferences

Given prompt $ x $ and responses $ y^{(1)}, y^{(2)} $, define reward $ R_\phi(x,y) $. The preference probability:

$$
\begin{align*}
P\big(y^{(1)} \succ y^{(2)} \mid x\big) = \sigma\big(R_\phi(x,y^{(1)}) - R_\phi(x,y^{(2)})\big)
\end{align*}
$$

Training loss:

$$
\begin{align*}
\mathcal{L}(\phi)= -\mathbb{E}\left[\log \sigma\big(R_\phi(x,y^+) - R_\phi(x,y^-)\big)\right]
\end{align*}
$$

### KL-regularized policy

Let $ \pi_\theta $ be the policy and $ \pi_{\mathrm{ref}} $ a reference policy:

$$
\begin{align*}
\max_{\theta}\; \mathbb{E}_{x,\, y \sim \pi_\theta(\cdot \mid x)}
\Big[
R_\phi(x,y) - \beta \,\mathrm{KL}\big(\pi_\theta(\cdot \mid x)\,\|\,\pi_{\mathrm{ref}}(\cdot \mid x)\big)
\Big]
\end{align*}
$$

## VAE

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770532121006.png?raw=true"> </p>

A VAE defines $ p_\theta(x \mid z)p(z) $ and an approximate posterior $ q_\phi(z \mid x) $.

The ELBO:

$$
\begin{align*}
\log p_\theta(x) \ge
\mathbb{E}_{q_\phi(z\mid x)}[\log p_\theta(x\mid z)] - \mathrm{KL}(q_\phi(z\mid x)\,\|\,p(z))
\end{align*}
$$

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770530630177.png?raw=true"> </p>

## Diffusion

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770532086687.png?raw=true"> </p>

Forward noising:

$$
\begin{align*}
q(x_t \mid x_{t-1}) = \mathcal{N}\big(\sqrt{1-\beta_t}\,x_{t-1}, \beta_t I\big)
\end{align*}
$$

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770531259618.png?raw=true"> </p>

Marginal:

$$
\begin{align*}
q(x_t \mid x_0) = \mathcal{N}\big(\sqrt{\bar{\alpha}_t}\,x_0, (1-\bar{\alpha}_t)I\big)
\end{align*}
$$

where $ \alpha_t = 1-\beta_t $ and $ \bar{\alpha}_t = \prod_{i=1}^{t} \alpha_i $.

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770531230164.png?raw=true"> </p>

Noise prediction (conditioning $ c $):

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

## LoRA

<p align="center"> <img src="https://github.com/hongjun7/logs/blob/main/_posts/image/2026-02-07-Core-Concepts-in-Modern-AI-Systems/1770531338665.png?raw=true"> </p>

For a linear layer $ W \in \mathbb{R}^{d_{\mathrm{out}}\times d_{\mathrm{in}}} $, LoRA constrains:

$$
\begin{align*}
\Delta W = B A
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

## Reference
- [[ByteByteAI and ByteByteGo] 9 AI Concepts Explained in 7 minutes: AI Agents, RAGs, Tokenization, RLHF, Diffusion, LoRA...](https://www.youtube.com/watch?v=nVnxG10D5W0)
- [[Medium] Decoding the Decoder: Top-k, Top-p, Temperature, Beam Search & Hallucinations in LLMs](https://medium.com/@ayushyajnik2/decoding-the-decoder-top-k-top-p-temperature-beam-search-hallucinations-in-llms-e54963eb3de7)