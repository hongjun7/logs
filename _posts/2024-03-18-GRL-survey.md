---
title: "Reinforcement Learning on Graphs: States, Policies, and Evaluation"
tags: ["reinforcement-learning", "graphs", "graph-neural-networks"]
subtitle: "A unified mathematical view of graph decisions, from message passing and constrained actions to policy gradients, knowledge-graph traversal, and reliable evaluation."
last_modified_at: 2026-10-11
sources_checked_at: 2026-10-11
---

> **The idea in one minute.** A graph describes relationships; reinforcement learning describes sequential decisions. Combining them means defining a state, a feasible action set, transitions, and a reward, then using graph structure to represent or constrain the decision. A graph neural network is a possible policy component, not itself an RL algorithm.

**Reading path.** Read the MDP definition and traversal example before the policy-gradient section. Then compare the application families and evaluation protocol. Prerequisites are conditional probability, vectors, and basic graphs. This is a conceptual survey with worked derivations, not a claim that one graph policy wins every task.

## 1. Specify the graph and the decision problem

Let $$G=(V,E,X)$$ be a graph with vertex set $$V$$, edges $$E$$, and optional features $$X$$. A knowledge graph is a set of triples $$E\subseteq V\times\mathcal R\times V$$ indexed by relation labels $$\mathcal R$$; a single triple $$(h,r,t)$$ is an edge, not an entire graph.

A discounted Markov decision process is

$$
\mathcal M=(\mathcal S,\mathcal A,P,r,\mu_0,\gamma),\qquad0\le\gamma<1.
$$

Here $$\mu_0$$ is an initial-state distribution, $$P(s'\mid s,a)$$ a transition kernel, and $$r(s,a)$$ an expected immediate reward. For bounded rewards, the return objective is finite:

$$
J(\pi)=\mathbb E_{s_0\sim\mu_0,\,a_t\sim\pi,\,s_{t+1}\sim P}
\left[\sum_{t=0}^{\infty}\gamma^t r(s_t,a_t)\right].
$$

An episodic finite-horizon problem can instead use $$\gamma=1$$ with bounded horizon. A graph environment may have a fixed graph, a graph that changes after actions, or only a partial observation of the graph. If the observation omits information needed to determine transitions, the problem is partially observed; calling a node embedding a “state” does not make it Markov.

## 2. A concrete knowledge-graph traversal

For a query $$(v_0,r_q,?)$$, an agent starts at $$v_0$$ and selects outgoing relation–neighbor pairs. A finite-horizon state might be $$(v_t,v_0,r_q,t)$$ on a fixed graph; add history when constraints prohibit revisiting nodes or when observations are incomplete. The feasible actions are

$$
\mathcal A(s_t)=\{(r,u):(v_t,r,u)\in E\}\cup\{\mathrm{stop}\}.
$$

The transition moves to $$u$$ and increments the step count. A sparse terminal reward could be $$\mathbf1\{v_T=v_{\mathrm{target}}\}$$. If the graph does not contain the answer, no policy can reach it without additional actions. Distinguish path search from graph completion.

An action mask can encode topology:

$$
\pi_\theta(a\mid s)=
\frac{\exp z_\theta(s,a)}{\sum_{b\in\mathcal A(s)}\exp z_\theta(s,b)},
\qquad a\in\mathcal A(s).
$$

Invalid actions receive zero probability. Every denominator needs a nonempty feasible set, which is one reason to include a defined stop action. The mask must be used consistently during sampling, likelihood calculation, and training.

## 3. Graph representations for policies and values

A message-passing layer updates a node representation using a permutation-invariant aggregation:

$$
\begin{aligned}
m_v^{(\ell)}&=\operatorname{AGG}\limits_{u\in\mathcal N(v)}
\phi_\ell(h_v^{(\ell)},h_u^{(\ell)},e_{uv}),\\
h_v^{(\ell+1)}&=\psi_\ell(h_v^{(\ell)},m_v^{(\ell)}).
\end{aligned}
$$

`AGG` might be sum, mean, or an attention-weighted sum. Permuting neighbors should not change an aggregate over an unordered neighborhood. After $$L$$ local layers, a node depends on at most its $$L$$-hop neighborhood unless the architecture adds global paths. More layers do not automatically produce a useful global representation; oversmoothing and bottlenecks can remove distinctions.

A policy can score actions from node, graph, and query embeddings. A value function can use a graph-level pooled representation. These are architectural choices. In a combinatorial task with $$n$$ nodes, an action could choose one node, an edge, or a pair of nodes; the last case has $$O(n^2)$$ candidates before constraints.

A naive embedding objective $$\sum_{(u,v)\in E}\|h_u-h_v\|^2$$ admits the trivial solution $$h_v=c$$ for all nodes. To learn informative features, add a task loss, negative pairs, variance constraints, or another condition that avoids collapse. “Connected nodes should be close” is only part of a representation objective. [PyTorch Geometric](https://github.com/pyg-team/pytorch_geometric) supplies graph operations; it does not decide which RL problem is well posed.

## 4. Bellman equations and policy gradients

For a stationary policy,

$$
V^\pi(s)=\mathbb E_{a\sim\pi(\cdot\mid s)}
\left[r(s,a)+\gamma\mathbb E_{s'\sim P}V^\pi(s')\right].
$$

For an unconstrained finite discounted MDP, the optimal Bellman operator is a contraction in the sup norm with factor $$\gamma$$. This gives a unique optimal value fixpoint. It does not imply a nonlinear neural-network training algorithm converges to that fixpoint.

For a finite trajectory and differentiable stochastic policy, the likelihood-ratio identity gives

$$
\nabla_\theta J
=\mathbb E\left[\sum_{t=0}^{T-1}
\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,G_t\right],
$$

when $$G_t$$ includes the appropriate discount weighting for the chosen objective. With an undiscounted finite-horizon objective, $$G_t=\sum_{u=t}^{T-1}r_u$$. For $$J=\mathbb E\sum_u\gamma^u r_u$$, a directly corresponding form uses $$G_t=\sum_{u=t}^{T-1}\gamma^u r_u$$.

An action-independent baseline $$b(s_t)$$ can reduce variance without changing the expected gradient because

$$
\mathbb E_{a\sim\pi}[\nabla_\theta\log\pi(a\mid s)b(s)]
=b(s)\nabla_\theta\sum_a\pi(a\mid s)=0.
$$

This equality assumes fixed support or a well-defined fixed feasible action set for the state and the usual interchange conditions. A graph-dependent baseline may use a learned value estimate. [Sutton and Barto's RL text](http://incompleteideas.net/book/the-book-2nd.html) gives the foundational value and policy formulations.

## 5. Rewards, constraints, and exploration

Sparse terminal rewards make successful paths hard to discover. Reward shaping can add intermediate information, but an arbitrary shaped reward may change the optimal behavior. Under the standard discounted MDP conditions, a potential-based term

$$
F(s,a,s')=\gamma\Phi(s')-\Phi(s)
$$

telescopes over a trajectory and preserves optimal-policy rankings when terminal and boundedness conditions are handled correctly. A heuristic reward for “moving toward a similar node” does not automatically have this guarantee.

For constrained actions, distinguish hard feasibility from learned preference. The application can prohibit nonexistent edges or budget violations deterministically. A learned model then ranks feasible alternatives. For stochastic cost constraints, a problem such as $$\mathbb E_\pi\sum_t c_t\le B$$ calls for a constrained-MDP formulation; penalizing costs with one coefficient is not generally a certificate that the bound holds.

## 6. Application families

| Family | State and action | Main difficulty | Useful simple baseline |
| --- | --- | --- | --- |
| Knowledge-graph reasoning | Query plus current entity; choose an outgoing edge | Missing facts, sparse reward, path leakage | Bounded breadth-first search |
| Graph construction or attack | Current graph; add/remove an allowed edge | Large action space, validity constraints | Greedy local score |
| Routing and scheduling | Partial route or assignment; choose next feasible item | Delayed costs, distribution shift | Classical heuristic or solver |
| Active learning | Labeled/unlabeled graph; choose a node to label | Expensive observations, biased sampling | Random or uncertainty sampling |
| Recommendation | User history and item relations; choose a recommendation | Feedback loops, off-policy bias | Popularity and contextual-bandit baselines |

A sequential formulation is worthwhile when present actions change future opportunities or information. If choices do not affect future states and each has a direct label, supervised learning or a contextual bandit may be simpler. The original GRL survey provides a historical taxonomy; current implementations should be selected by the precise task and evaluation conditions, rather than by the word “graph.”

## 7. Evaluation that separates learning from memorization

Define the split before designing the policy. Holding out edges differs from holding out nodes, graphs, relations, or time periods. A graph encoder can leak test information if it propagates over edges that should not yet be visible. For temporal graphs, features and neighborhoods must be available at prediction time.

Report mean and variability across seeds, interaction budget, reward definition, wall time, invalid-action rate, and solution quality. Compare to random, greedy, graph-search, and supervised baselines. For finite combinatorial problems, a solver's exact optimum or valid lower/upper bounds can reveal whether a high reward actually means a good solution.

Temporal link-prediction benchmarks illustrate why negative sampling and memorization baselines matter. The [Temporal Graph Benchmark](https://github.com/shenyangHuang/TGB) is a current evaluation resource, but link prediction scores are not automatically measures of an RL policy's long-term value. Keep prediction and control evaluations separate.

## 8. Prove the Bellman contraction

For a finite state/action space, define the optimal operator on bounded value vectors by

$$
(\mathcal T V)(s)=\max_{a\in\mathcal A(s)}
\left[r(s,a)+\gamma\sum_{s'}P(s'\mid s,a)V(s')\right].
$$

For any real vectors $$u,v$$ over the same finite index set, $$\vert \max_i u_i-\max_i v_i\vert \le\max_i\vert u_i-v_i\vert $$. Apply this inequality, then the fact that transition probabilities sum to one:

$$
\begin{aligned}
\vert \mathcal TV(s)-\mathcal TW(s)\vert
&\le\gamma\max_a\left\vert \sum_{s'}P(s'\mid s,a)(V(s')-W(s'))\right\vert \\
&\le\gamma\|V-W\|_\infty.
\end{aligned}
$$

Taking the maximum over states gives $$\|\mathcal TV-\mathcal TW\|_\infty\le\gamma\|V-W\|_\infty$$. Because $$\gamma<1$$ and finite-dimensional bounded vectors form a complete normed space, value iteration converges to a unique fixed point. After $$k$$ exact iterations, its distance to that fixed point is at most $$\gamma^k$$ times the initial distance.

A graph neural network restricts values to a parameterized function family. A projected Bellman update need not preserve this sup-norm contraction, and gradient descent introduces its own optimization dynamics. This is why “the Bellman equation has a unique solution” and “my neural training converges” are distinct statements.

### Temporal difference and policy-gradient choices

A one-step sampled critic target is

$$
y_t=r_t+\gamma\mathbf1\{\text{nonterminal}\}\max_{a'\in\mathcal A(s_{t+1})}Q_{\bar\theta}(s_{t+1},a').
$$

A squared TD loss fits $$Q_\theta(s_t,a_t)$$ to this target. Terminal masking, the next-state action mask, and the distinction between a true terminal state and time-limit truncation all affect the target. A target network $$\bar\theta$$ and replay can stabilize practical training, but do not remove approximation error or supply a universal convergence theorem.

For an actor–critic, an advantage estimate subtracts a state value from a return or action value. PPO forms the sampled likelihood ratio $$r_t(\theta)=\pi_\theta(a_t\mid s_t)/\pi_{\mathrm{old}}(a_t\mid s_t)$$ and maximizes a clipped surrogate:

$$
\mathcal L_{\mathrm{clip}}(\theta)=
\mathbb E_t\left[\min\left(r_t(\theta)\widehat A_t,
\operatorname{clip}(r_t(\theta),1-\epsilon,1+\epsilon)\widehat A_t\right)\right].
$$

The old probability must come from the policy that collected the sample. Both probabilities must use the same feasible action semantics. Clipping a sampled ratio is not a hard bound on every state's policy change. [PPO](https://arxiv.org/abs/1707.06347).

An entropy-regularized objective adds $$\alpha H(\pi(\cdot\mid s))$$ to reward, with $$\alpha>0$$. At one state with fixed action values, maximize

$$
\sum_a\pi_a Q_a-\alpha\sum_a\pi_a\log\pi_a
\quad\text{subject to }\sum_a\pi_a=1.
$$

Lagrange differentiation gives $$\pi_a\propto\exp(Q_a/\alpha)$$ over feasible actions. Thus entropy changes the preferred policy: it is not just a numerical trick. [Soft Actor-Critic](https://arxiv.org/abs/1801.01290) develops a maximum-entropy actor–critic framework; graph-discrete actions require an appropriate discrete formulation rather than copying a continuous-action implementation unchanged.

## 9. Why permutation symmetry matters

Node IDs are often arbitrary. Let $$\Pi$$ be a permutation matrix, $$A$$ an adjacency matrix, and $$X\in\mathbb R^{n\times d}$$ node features. A node-level encoder should be equivariant:

$$
f(\Pi A\Pi^\top,\Pi X)=\Pi f(A,X).
$$

A graph-level readout should be invariant after pooling. Otherwise renaming nodes could change an action preference even though the graph problem has not changed.

A GCN-style layer uses $$\widetilde A=A+I$$, its degree matrix $$\widetilde D$$, and

$$
H'=\sigma(\widetilde D^{-1/2}\widetilde A\widetilde D^{-1/2}HW).
$$

Under permutation, degrees permute and the normalized adjacency becomes $$\Pi\widetilde D^{-1/2}\widetilde A\widetilde D^{-1/2}\Pi^\top$$. Matrix multiplication and a pointwise nonlinearity therefore produce $$\Pi H'$$. This proves equivariance for this layer. The definition follows [Kipf and Welling](https://arxiv.org/abs/1609.02907); directed, relation-labeled, or heterogeneous edges require a suitable extension.

Equivariance does not imply that every relevant structure is identifiable. Local message passing can assign equal embeddings to structurally different nodes or graphs. If a task needs a global budget, path history, or an already-selected set, include that information explicitly instead of expecting local embeddings to recover it.

For a dense feature projection, the cost is roughly $$O(nd_{\mathrm{in}}d_{\mathrm{out}})$$; sparse aggregation adds $$O(\vert E\vert d_{\mathrm{out}})$$ under a suitable representation. These bounds do not include pairwise action enumeration. A policy choosing an ordered pair of nodes can still require $$O(n^2)$$ scores even when the encoder is sparse.

## 10. A complete combinatorial example: Max-Cut

Let an undirected graph have nonnegative edge weights $$w_{uv}$$. Assign every node a label $$z_v\in\{0,1\}$$ and maximize

$$
\mathrm{Cut}(z)=\sum_{\{u,v\}\in E}w_{uv}\mathbf1\{z_u\ne z_v\}.
$$

A sequential environment can choose nodes in a fixed order. Its state contains the graph, the next node, and all previous assignments. An action chooses the next label. Give the incremental reward from edges whose second endpoint has just been assigned:

$$
r_t=\sum_{u\text{ assigned earlier}}w_{uv_t}\mathbf1\{z_u\ne z_{v_t}\}.
$$

Each undirected edge is counted once, so the undiscounted return equals the final cut value. Discounting this incremental reward would change the preference by favoring early cut edges; use $$\gamma=1$$ in this finite-horizon construction or state the changed objective.

For the four-cycle $$1-2-3-4-1$$ with unit weights, assigning $$(0,1,0,1)$$ cuts all four edges. The sum of all edge weights, four, is an upper bound on any cut, so this assignment is provably optimal. A learned policy solving this tiny instance is not impressive on its own; the question is whether amortized inference gives useful solutions on unseen larger instances relative to solvers and heuristics.

Choosing the next node as well as its label creates a larger action space and requires masking already assigned nodes. Using terminal-only reward preserves the same objective but makes credit assignment harder. These are alternative environment designs, not interchangeable implementations of one algorithm.

## 11. Causal discovery, attacks, and multi-agent graphs

Searching a directed acyclic graph can be a decision problem, but observational fit alone need not identify causal direction. Markov-equivalent DAGs can encode the same conditional independences; additional assumptions, interventions, or a restricted structural model are needed for stronger conclusions.

For a weighted adjacency $$W$$, a useful differentiable acyclicity condition from [NOTEARS](https://arxiv.org/abs/1803.01422) is

$$
h(W)=\operatorname{tr}\big(\exp(W\odot W)\big)-n=0.
$$

**Why it detects cycles.** The nonnegative matrix $$B=W\odot W$$ has $$\operatorname{tr}(B^k)$$ equal to a sum of nonnegative closed-walk weights. Expanding the matrix exponential yields $$h(W)=\sum_{k\ge1}\operatorname{tr}(B^k)/k!$$. A nonzero directed cycle makes one term positive; an acyclic graph has no such walks, so every term vanishes. This is a structural constraint, not a causal-identifiability theorem. RL can search graph structures using a score, while continuous optimization can use this constraint; both still need a defensible statistical objective.

A graph-attack problem restricts changes to a budget, for example $$\|A'-A\|_0\le2b$$ for at most $$b$$ undirected edge edits in a symmetric matrix. The factor two counts both matrix entries of an undirected edge; diagonal/self-loop conventions can change it. The attacker tries to increase a victim's loss under these constraints. Evaluate attack success, validity, transferred attacks, and defenses separately; high reward on one frozen victim does not establish a general attack.

In a multi-agent graph, local observations and policies may communicate along edges. A centralized training critic can use global information unavailable to a deployed actor; evaluation must preserve that distinction. If every agent has $$K$$ actions, a full joint action space has $$K^n$$ possibilities. Factorization and graph locality can reduce computation under additional assumptions, but do not make arbitrary coupled optimization independent.

The original survey's many application examples can be understood through these shared obligations: define a meaningful state, preserve feasibility, specify the objective, and evaluate at the correct information boundary. The taxonomy is useful; a long list of model names is not a substitute for those definitions.

## References and current scope

- [Reinforcement Learning on Graphs: A Survey](https://arxiv.org/abs/2204.06127).
- [MINERVA: Go for a Walk and Arrive at the Answer](https://arxiv.org/abs/1711.05851).
- [Multi-Hop Knowledge Graph Reasoning with Reward Shaping](https://arxiv.org/abs/1808.10568).
- [Sutton and Barto, Reinforcement Learning](http://incompleteideas.net/book/the-book-2nd.html).
- [PyTorch Geometric](https://github.com/pyg-team/pytorch_geometric) and [TGB](https://github.com/shenyangHuang/TGB).

The definitions and derivations are general. Application improvements require their own measured comparison; no historical survey is treated as proof of today's best method.
