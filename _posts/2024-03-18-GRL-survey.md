---
lang: en
translation_key: 2024-03-18-GRL-survey
translation_url: /ko/2024/03/18/GRL-survey.html
title: "Graph Representation Learning"
tags: ["reinforcement-learning", "graphs", "graph-neural-networks"]
subtitle: "Graph features, sequential decisions, and the mathematics of policies and values."
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-11
---

Graph representations encode relational structure for prediction and decision-making. In reinforcement learning, node and graph features parameterize policies and value functions within a specified state, action, transition, and reward model.

## Graphs and decision processes
{: id="1-specify-the-graph-and-the-decision-problem"}

Let $$G=(V,E,X)$$ contain vertices $$V$$, edges $$E$$, and optional features $$X$$. In a knowledge graph, $$E\subseteq V\times\mathcal R\times V$$ uses relation labels $$\mathcal R$$; $$(h,r,t)$$ denotes one edge.

A discounted Markov decision process is

$$
\mathcal M=(\mathcal S,\mathcal A,P,r,\mu_0,\gamma),\qquad0\le\gamma<1.
$$

Here $$\mu_0$$ is the initial-state distribution, $$P(s'\mid s,a)$$ the transition kernel, and $$r(s,a)$$ the expected immediate reward. Bounded rewards give a finite objective:

$$
J(\pi)=\mathbb E_{s_0\sim\mu_0,\,a_t\sim\pi,\,s_{t+1}\sim P}
\left[\sum_{t=0}^{\infty}\gamma^t r(s_t,a_t)\right].
$$

A bounded finite-horizon episode can use $$\gamma=1$$. The graph may be fixed, action-dependent, or partially observed. An observation is a Markov state only if it retains the information needed for transitions.

## Knowledge-graph traversal
{: id="2-a-concrete-knowledge-graph-traversal"}

For query $$(v_0,r_q,?)$$, traversal starts at $$v_0$$ and selects outgoing relation–neighbor pairs. On a fixed graph, $$(v_t,v_0,r_q,t)$$ can specify a finite-horizon state; incomplete observations or no-revisit constraints require history. Feasible actions are

$$
\mathcal A(s_t)=\{(r,u):(v_t,r,u)\in E\}\cup\{\mathrm{stop}\}.
$$

Each move reaches $$u$$ and advances the clock. A terminal reward can be $$\mathbf1\{v_T=v_{\mathrm{target}}\}$$. An absent answer is unreachable without actions that extend the graph.

An action mask can encode topology:

$$
\pi_\theta(a\mid s)=
\frac{\exp z_\theta(s,a)}{\sum_{b\in\mathcal A(s)}\exp z_\theta(s,b)},
\qquad a\in\mathcal A(s).
$$

The mask assigns zero probability to invalid actions. A stop action keeps the feasible set nonempty; sampling, likelihoods, and training must share the mask.

## Message passing
{: id="3-graph-representations-for-policies-and-values"}

A message-passing layer updates a node representation using a permutation-invariant aggregation:

$$
\begin{aligned}
m_v^{(\ell)}&=\operatorname{AGG}\limits_{u\in\mathcal N(v)}
\phi_\ell(h_v^{(\ell)},h_u^{(\ell)},e_{uv}),\\
h_v^{(\ell+1)}&=\psi_\ell(h_v^{(\ell)},m_v^{(\ell)}).
\end{aligned}
$$

`AGG` can be sum, mean, or attention-weighted sum, invariant to neighbor order. Without global paths, $$L$$ local layers access at most an $$L$$-hop neighborhood. Oversmoothing and bottlenecks can erase distinctions as depth grows.

A policy scores actions from node, graph, and query embeddings; a value function can pool graph features. A combinatorial environment can choose a node, an edge, or a node pair, with different feasible sets and scoring costs. With $$n$$ nodes, actions selecting ordered node pairs have $$O(n^2)$$ candidates before constraints.

The objective $$\sum_{(u,v)\in E}\|h_u-h_v\|^2$$ admits collapse to $$h_v=c$$. Task losses, negative pairs, or variance constraints can prevent it. [PyTorch Geometric](https://github.com/pyg-team/pytorch_geometric) provides graph operations for such representations.

## Values and policy gradients
{: id="4-bellman-equations-and-policy-gradients"}

For a stationary policy,

$$
V^\pi(s)=\mathbb E_{a\sim\pi(\cdot\mid s)}
\left[r(s,a)+\gamma\mathbb E_{s'\sim P}V^\pi(s')\right].
$$

In a finite unconstrained discounted MDP, the optimal Bellman operator contracts the sup norm by $$\gamma$$ and has a unique fixed point. Neural approximation need not inherit this convergence.

For a finite trajectory and differentiable stochastic policy, the likelihood-ratio identity gives

$$
\nabla_\theta J
=\mathbb E\left[\sum_{t=0}^{T-1}
\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,G_t\right],
$$

The weighting in $$G_t$$ follows the objective: $$G_t=\sum_{u=t}^{T-1}r_u$$ for an undiscounted finite horizon; for $$J=\mathbb E\sum_u\gamma^u r_u$$, use $$G_t=\sum_{u=t}^{T-1}\gamma^u r_u$$.

An action-independent baseline $$b(s_t)$$ can reduce variance while preserving the expected gradient:

$$
\mathbb E_{a\sim\pi}[\nabla_\theta\log\pi(a\mid s)b(s)]
=b(s)\nabla_\theta\sum_a\pi(a\mid s)=0.
$$

This assumes fixed support or a fixed feasible action set and valid interchange of differentiation and expectation. A graph-dependent baseline can estimate state value. [Sutton and Barto](http://incompleteideas.net/book/the-book-2nd.html).

## Rewards and constraints
{: id="5-rewards-constraints-and-exploration"}

Sparse terminal rewards impede exploration. Under standard discounted-MDP assumptions, potential-based shaping adds

$$
F(s,a,s')=\gamma\Phi(s')-\Phi(s)
$$

whose trajectory sum telescopes. Correct terminal and boundedness conditions preserve optimal-policy rankings; arbitrary similarity rewards need not.

Hard masks exclude nonexistent edges and budget violations before learned ranking. An expected-cost bound such as $$\mathbb E_\pi\sum_t c_t\le B$$ instead requires a constrained-MDP formulation; a scalar penalty alone does not certify it.

## Applications
{: id="6-application-families"}

| Family | State and action | Main difficulty | Useful simple baseline |
| --- | --- | --- | --- |
| Knowledge-graph reasoning | Query plus current entity; choose an outgoing edge | Missing facts, sparse reward, path leakage | Bounded breadth-first search |
| Graph construction or attack | Current graph; add/remove an allowed edge | Large action space, validity constraints | Greedy local score |
| Routing and scheduling | Partial route or assignment; choose next feasible item | Delayed costs, distribution shift | Classical heuristic or solver |
| Active learning | Labeled/unlabeled graph; choose a node to label | Expensive observations, biased sampling | Random or uncertainty sampling |
| Recommendation | User history and item relations; choose a recommendation | Feedback loops, off-policy bias | Popularity and contextual-bandit baselines |

Sequential decisions matter when actions change future opportunities or information. Independent labeled choices may instead suit supervised learning or contextual bandits.

## Evaluation
{: id="7-evaluation-that-separates-learning-from-memorization"}

Edge, node, graph, relation, and time holdouts test different generalization. Propagation over unavailable edges leaks test information; temporal features and neighborhoods must precede prediction.

Useful comparisons match interaction budgets and reward definitions, report seed variation, runtime, invalid-action rates, and solution quality, and include random, greedy, search, and supervised baselines. Solver optima or valid bounds calibrate combinatorial results.

[Temporal Graph Benchmark](https://github.com/shenyangHuang/TGB) illustrates sensitivity to negative sampling and memorization. Its prediction scores measure a different objective from long-term control value.

## Bellman contraction
{: id="8-prove-the-bellman-contraction"}

For finite state and action spaces, define the operator on bounded value vectors:

$$
(\mathcal T V)(s)=\max_{a\in\mathcal A(s)}
\left[r(s,a)+\gamma\sum_{s'}P(s'\mid s,a)V(s')\right].
$$

For real vectors $$u,v$$ on a common finite index set, $$\vert \max_i u_i-\max_i v_i\vert \le\max_i\vert u_i-v_i\vert $$. Transition probabilities sum to one, giving

$$
\begin{aligned}
\vert \mathcal TV(s)-\mathcal TW(s)\vert
&\le\gamma\max_a\left\vert \sum_{s'}P(s'\mid s,a)(V(s')-W(s'))\right\vert \\
&\le\gamma\|V-W\|_\infty.
\end{aligned}
$$

Taking the state maximum yields $$\|\mathcal TV-\mathcal TW\|_\infty\le\gamma\|V-W\|_\infty$$. Since $$\gamma<1$$ and the space is complete, exact value iteration converges uniquely; after $$k$$ steps its error is at most $$\gamma^k$$ times the initial error.

A neural network restricts values to a parameterized function family. Projecting a Bellman update into that family need not preserve this contraction. Gradient descent adds optimization dynamics distinct from exact value iteration.

### Temporal difference and actor–critic
{: id="temporal-difference-and-policy-gradient-choices"}

A one-step sampled critic target is

$$
y_t=r_t+\gamma\mathbf1\{\text{nonterminal}\}\max_{a'\in\mathcal A(s_{t+1})}Q_{\bar\theta}(s_{t+1},a').
$$

A squared TD loss fits $$Q_\theta(s_t,a_t)$$ to the target. Terminal versus time-limit masking and next-state feasibility determine the bootstrap. A target network $$\bar\theta$$ and replay can stabilize training without guaranteeing convergence.

Actor–critic subtracts state value to estimate advantage. PPO uses the sampled ratio $$r_t(\theta)=\pi_\theta(a_t\mid s_t)/\pi_{\mathrm{old}}(a_t\mid s_t)$$ in a clipped surrogate:

$$
\mathcal L_{\mathrm{clip}}(\theta)=
\mathbb E_t\left[\min\left(r_t(\theta)\widehat A_t,
\operatorname{clip}(r_t(\theta),1-\epsilon,1+\epsilon)\widehat A_t\right)\right].
$$

The denominator comes from the sampling policy, with matching action semantics. Sampled clipping does not bound every state’s policy change. [PPO](https://arxiv.org/abs/1707.06347).

Entropy regularization adds $$\alpha H(\pi(\cdot\mid s))$$ with $$\alpha>0$$. For fixed action values at one state, maximize

$$
\sum_a\pi_a Q_a-\alpha\sum_a\pi_a\log\pi_a
\quad\text{subject to }\sum_a\pi_a=1.
$$

Lagrange differentiation gives $$\pi_a\propto\exp(Q_a/\alpha)$$ on feasible actions: entropy changes the preferred policy. [Soft Actor-Critic](https://arxiv.org/abs/1801.01290) develops this framework; discrete graph actions need a discrete formulation.

## Permutation symmetry
{: id="9-why-permutation-symmetry-matters"}

With arbitrary node IDs, a permutation matrix $$\Pi$$, adjacency $$A$$, and features $$X\in\mathbb R^{n\times d}$$ should satisfy node-level equivariance:

$$
f(\Pi A\Pi^\top,\Pi X)=\Pi f(A,X).
$$

Pooling should make graph-level output invariant, so renaming nodes preserves the decision problem.

A GCN-style layer uses $$\widetilde A=A+I$$, its degree matrix $$\widetilde D$$, and

$$
H'=\sigma(\widetilde D^{-1/2}\widetilde A\widetilde D^{-1/2}HW).
$$

Permutation transforms normalized adjacency into $$\Pi\widetilde D^{-1/2}\widetilde A\widetilde D^{-1/2}\Pi^\top$$. Multiplication and pointwise nonlinearity then give $$\Pi H'$$, proving layer equivariance. [Kipf and Welling](https://arxiv.org/abs/1609.02907). Directed, labeled, or heterogeneous edges require extensions.

Equivariance concerns renaming, not the ability to distinguish every structure. Local message passing can still map different structures to equal embeddings. Global budgets, path history, and selected sets therefore belong explicitly in the state when required.

Dense projection costs approximately $$O(nd_{\mathrm{in}}d_{\mathrm{out}})$$; sparse aggregation adds $$O(\vert E\vert d_{\mathrm{out}})$$. Ordered-pair action scoring can still cost $$O(n^2)$$.

## Max-Cut
{: id="10-a-complete-combinatorial-example-max-cut"}

Let an undirected graph have nonnegative edge weights $$w_{uv}$$. Assign every node a label $$z_v\in\{0,1\}$$ and maximize

$$
\mathrm{Cut}(z)=\sum_{\{u,v\}\in E}w_{uv}\mathbf1\{z_u\ne z_v\}.
$$

A sequential construction visits nodes in a fixed order. State records the graph, next node, and prior labels; each action labels that node. Count newly completed edges as reward:

$$
r_t=\sum_{u\text{ assigned earlier}}w_{uv_t}\mathbf1\{z_u\ne z_{v_t}\}.
$$

Each edge contributes once, making undiscounted return equal the final cut. This finite-horizon construction uses $$\gamma=1$$; discounting would favor early cut edges.

On the unit-weight four-cycle $$1-2-3-4-1$$, labels $$(0,1,0,1)$$ cut all four edges. Four is also the total edge weight and an upper bound, proving optimality. Larger unseen instances test whether amortized learned inference competes with solvers and heuristics.

Choosing node order enlarges the action space and requires masking assigned nodes. Terminal-only reward preserves the objective but complicates credit assignment: feedback arrives after all labels rather than at each newly completed edge. These choices define different environments for the same final combinatorial objective.

## Causal graphs and attacks
{: id="11-causal-discovery-attacks-and-multi-agent-graphs"}

A DAG search objective does not identify causality by observational fit alone. Markov-equivalent DAGs share conditional independences; stronger conclusions need assumptions, interventions, or restricted models.

For a weighted adjacency $$W$$, a useful differentiable acyclicity condition from [NOTEARS](https://arxiv.org/abs/1803.01422) is

$$
h(W)=\operatorname{tr}\big(\exp(W\odot W)\big)-n=0.
$$

For nonnegative $$B=W\odot W$$, $$\operatorname{tr}(B^k)$$ sums closed-walk weights. The expansion $$h(W)=\sum_{k\ge1}\operatorname{tr}(B^k)/k!$$ is positive for a nonzero directed cycle and zero for a DAG. This constrains structure, not causal identifiability; both RL search and continuous optimization still need a statistical objective.

A symmetric graph attack can impose $$\|A'-A\|_0\le2b$$ for at most $$b$$ undirected edits. Two counts both matrix entries; self-loop conventions alter it. Attacks maximize a victim’s loss within the budget. Attack success, validity, transfer to another victim, and defense performance measure different properties. A high reward against one frozen victim gives no guarantee about the others.

Graph agents may communicate locally while a centralized training critic sees global information unavailable to deployed actors. With $$K$$ actions each, the joint space has $$K^n$$ possibilities. Factorization reduces computation only under additional assumptions.

## References
{: id="references-and-current-scope"}

- [Reinforcement Learning on Graphs: A Survey](https://arxiv.org/abs/2204.06127).
- [MINERVA: Go for a Walk and Arrive at the Answer](https://arxiv.org/abs/1711.05851).
- [Multi-Hop Knowledge Graph Reasoning with Reward Shaping](https://arxiv.org/abs/1808.10568).
- [Sutton and Barto, Reinforcement Learning](http://incompleteideas.net/book/the-book-2nd.html).
- [PyTorch Geometric](https://github.com/pyg-team/pytorch_geometric) and [TGB](https://github.com/shenyangHuang/TGB).
