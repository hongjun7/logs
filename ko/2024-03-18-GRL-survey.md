---
layout: article
lang: ko
translation_key: 2024-03-18-GRL-survey
date: 2024-03-18
permalink: /ko/2024/03/18/GRL-survey.html
original_url: /2024/03/18/GRL-survey.html
translated_at: 2026-10-29
title: "그래프 표현 학습"
tags: ["reinforcement-learning", "graphs", "graph-neural-networks"]
subtitle: "그래프 특징과 순차적 결정, 정책·가치 함수의 수학을 다룬다."
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-11
---

그래프 표현은 관계 구조를 예측과 의사결정에 사용할 특징으로 바꾼다. 강화학습에서는 노드·그래프 특징으로 정책과 가치 함수를 구성하고, 상태·행동·전이·보상으로 순차적 문제를 정의한다.

## 그래프와 의사결정 과정
{: id="1-그래프와-의사결정-문제를-명시한다"}

$$G=(V,E,X)$$는 정점 $$V$$, 간선 $$E$$, 선택적인 특징 $$X$$로 이루어진다. 지식 그래프의 $$E\subseteq V\times\mathcal R\times V$$는 관계 레이블 $$\mathcal R$$을 사용하며, $$(h,r,t)$$는 간선 하나를 나타낸다.

할인된 마르코프 의사결정 과정은 다음과 같다.

$$
\mathcal M=(\mathcal S,\mathcal A,P,r,\mu_0,\gamma),\qquad0\le\gamma<1.
$$

$$\mu_0$$는 초기 상태 분포, $$P(s'\mid s,a)$$는 전이 커널, $$r(s,a)$$는 즉시 보상의 기댓값이다. 보상이 유계이면 목적 함수가 유한하다.

$$
J(\pi)=\mathbb E_{s_0\sim\mu_0,\,a_t\sim\pi,\,s_{t+1}\sim P}
\left[\sum_{t=0}^{\infty}\gamma^t r(s_t,a_t)\right].
$$

길이가 제한된 에피소드는 $$\gamma=1$$을 사용할 수 있다. 그래프는 고정되거나 행동에 따라 바뀌거나 일부만 관측될 수 있다. 관측이 전이를 결정할 정보를 유지해야 마르코프 상태가 된다.

## 지식 그래프 탐색
{: id="2-구체적인-지식-그래프-탐색"}

질의 $$(v_0,r_q,?)$$에서 탐색은 $$v_0$$부터 시작해 밖으로 나가는 관계·이웃 쌍을 선택한다. 고정 그래프에서는 $$(v_t,v_0,r_q,t)$$로 유한 길이 상태를 정의할 수 있다. 부분 관측이나 재방문 금지 제약에는 이력이 필요하다. 가능한 행동은 다음과 같다.

$$
\mathcal A(s_t)=\{(r,u):(v_t,r,u)\in E\}\cup\{\mathrm{stop}\}.
$$

이동은 $$u$$에 도달하고 단계 수를 늘린다. 종료 보상으로 $$\mathbf1\{v_T=v_{\mathrm{target}}\}$$를 줄 수 있다. 그래프에 없는 정답에는 그래프를 확장하는 행동 없이는 도달할 수 없다.

행동 마스크로 위상 구조를 반영할 수 있다.

$$
\pi_\theta(a\mid s)=
\frac{\exp z_\theta(s,a)}{\sum_{b\in\mathcal A(s)}\exp z_\theta(s,b)},
\qquad a\in\mathcal A(s).
$$

마스크는 유효하지 않은 행동의 확률을 0으로 만든다. 정지 행동은 가능한 행동 집합이 비지 않게 하며, 샘플링·우도·학습에는 같은 마스크를 적용해야 한다.

## 메시지 전달
{: id="3-정책과-가치를-위한-그래프-표현"}

메시지 전달 층은 순열에 불변인 집계로 노드 표현을 갱신한다.

$$
\begin{aligned}
m_v^{(\ell)}&=\operatorname{AGG}\limits_{u\in\mathcal N(v)}
\phi_\ell(h_v^{(\ell)},h_u^{(\ell)},e_{uv}),\\
h_v^{(\ell+1)}&=\psi_\ell(h_v^{(\ell)},m_v^{(\ell)}).
\end{aligned}
$$

`AGG`는 이웃 순서에 불변인 합·평균·어텐션 가중합일 수 있다. 전역 경로가 없다면 지역 층 $$L$$개는 최대 $$L$$홉 이웃에 접근한다. 깊이가 늘면 과도한 평활화와 병목으로 구별에 필요한 정보가 사라질 수 있다.

정책은 노드·그래프·질의 임베딩으로 행동 점수를 매기고, 가치 함수는 그래프 특징을 풀링할 수 있다. 조합 환경의 행동은 노드 하나, 간선 하나, 노드 쌍 하나를 선택할 수 있으며 가능한 집합과 점수 계산 비용이 다르다. 노드가 $$n$$개일 때 순서가 있는 노드 쌍을 고르는 행동은 제약 적용 전 후보가 $$O(n^2)$$개다.

목적 함수 $$\sum_{(u,v)\in E}\|h_u-h_v\|^2$$는 $$h_v=c$$로 붕괴하는 해를 허용한다. 과제 손실, 음성 쌍, 분산 제약으로 이를 막을 수 있다. [PyTorch Geometric](https://github.com/pyg-team/pytorch_geometric)은 이런 표현을 위한 그래프 연산을 제공한다.

## 가치와 정책 기울기
{: id="4-벨만-방정식과-정책-기울기"}

정상 정책에 대해 다음이 성립한다.

$$
V^\pi(s)=\mathbb E_{a\sim\pi(\cdot\mid s)}
\left[r(s,a)+\gamma\mathbb E_{s'\sim P}V^\pi(s')\right].
$$

제약이 없는 유한 할인 MDP의 최적 벨만 연산자는 상한 노름을 $$\gamma$$배로 수축시키며 유일한 고정점을 갖는다. 신경망 근사가 이 수렴성을 이어받는 것은 아니다.

유한 궤적과 미분 가능한 확률적 정책에서는 우도비 항등식으로 다음을 얻는다.

$$
\nabla_\theta J
=\mathbb E\left[\sum_{t=0}^{T-1}
\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,G_t\right],
$$

$$G_t$$의 가중치는 목적 함수에 따른다. 할인하지 않는 유한 길이에서는 $$G_t=\sum_{u=t}^{T-1}r_u$$이고, $$J=\mathbb E\sum_u\gamma^u r_u$$에는 $$G_t=\sum_{u=t}^{T-1}\gamma^u r_u$$를 쓴다.

행동에 독립적인 기준값 $$b(s_t)$$는 기울기의 기댓값을 유지하면서 분산을 줄일 수 있다.

$$
\mathbb E_{a\sim\pi}[\nabla_\theta\log\pi(a\mid s)b(s)]
=b(s)\nabla_\theta\sum_a\pi(a\mid s)=0.
$$

지지집합이나 가능한 행동 집합이 고정되고 미분과 기댓값을 교환할 수 있다는 가정이 필요하다. 그래프에 의존하는 기준값으로 상태 가치를 추정할 수 있다. [Sutton과 Barto](http://incompleteideas.net/book/the-book-2nd.html).

## 보상과 제약
{: id="5-보상-제약-탐색"}

희소한 종료 보상은 탐색을 어렵게 한다. 표준 할인 MDP 가정에서 잠재함수 기반 보상 설계는 다음 항을 더한다.

$$
F(s,a,s')=\gamma\Phi(s')-\Phi(s)
$$

궤적 전체의 합은 중간 항이 상쇄되어 정리된다. 종료·유계 조건을 맞추면 최적 정책의 우열을 보존하지만, 임의의 유사도 보상에는 이 보장이 없다.

강한 마스크는 존재하지 않는 간선과 예산 위반을 먼저 제외하고 모델은 가능한 행동의 순위를 매긴다. $$\mathbb E_\pi\sum_t c_t\le B$$ 같은 기대 비용 상한에는 제약 MDP 정식화가 필요하며, 하나의 벌점 계수만으로 준수를 입증할 수는 없다.

## 응용
{: id="6-응용-분야"}

| 분야 | 상태와 행동 | 주요 어려움 | 유용한 단순 기준선 |
| --- | --- | --- | --- |
| 지식 그래프 추론 | 질의와 현재 개체; 밖으로 나가는 간선 선택 | 누락된 사실, 희소 보상, 경로를 통한 누출 | 깊이를 제한한 너비 우선 탐색 |
| 그래프 구성 또는 공격 | 현재 그래프; 허용된 간선 추가·제거 | 큰 행동 공간, 유효성 제약 | 탐욕적 지역 점수 |
| 경로 탐색과 일정 계획 | 부분 경로나 배정; 다음 가능한 항목 선택 | 지연된 비용, 분포 변화 | 고전적인 휴리스틱 또는 솔버 |
| 능동학습 | 레이블이 있는·없는 그래프; 레이블을 붙일 노드 선택 | 비싼 관측 비용, 편향된 샘플링 | 무작위 또는 불확실성 샘플링 |
| 추천 | 사용자 이력과 항목 관계; 추천 선택 | 피드백 루프, 오프폴리시 편향 | 인기도와 문맥적 밴딧 기준선 |

행동이 미래의 기회나 정보를 바꿀 때 순차적 결정이 중요하다. 서로 독립적이고 레이블이 있는 선택에는 지도학습이나 문맥적 밴딧이 적합할 수 있다.

## 평가
{: id="7-학습과-암기를-구분하는-평가"}

간선·노드·그래프·관계·시간을 분리하는 평가는 서로 다른 일반화를 측정한다. 이용할 수 없는 간선을 통한 전파는 테스트 정보를 누출한다. 시간 특징과 이웃은 예측보다 앞선 정보여야 한다.

비교에서는 상호작용 예산과 보상을 맞추고 시드 변동, 실행 시간, 유효하지 않은 행동 비율, 해의 품질을 측정한다. 무작위·탐욕적 선택·탐색·지도학습 기준선과 솔버 최적값이나 유효한 상하한이 비교 기준이 된다.

[Temporal Graph Benchmark](https://github.com/shenyangHuang/TGB)는 음성 샘플링과 암기에 대한 민감도를 보여 준다. 그 예측 점수는 장기 제어 가치와 다른 목적을 측정한다.

## 벨만 수축성
{: id="8-벨만-수축성을-증명한다"}

유한 상태·행동 공간의 유계 가치 벡터에 작용하는 연산자를 정의한다.

$$
(\mathcal T V)(s)=\max_{a\in\mathcal A(s)}
\left[r(s,a)+\gamma\sum_{s'}P(s'\mid s,a)V(s')\right].
$$

같은 유한 인덱스 집합의 실수 벡터 $$u,v$$에는 $$\vert \max_i u_i-\max_i v_i\vert \le\max_i\vert u_i-v_i\vert $$가 성립한다. 전이 확률의 합이 1이므로 다음을 얻는다.

$$
\begin{aligned}
\vert \mathcal TV(s)-\mathcal TW(s)\vert
&\le\gamma\max_a\left\vert \sum_{s'}P(s'\mid s,a)(V(s')-W(s'))\right\vert \\
&\le\gamma\|V-W\|_\infty.
\end{aligned}
$$

상태에 대해 최댓값을 취하면 $$\|\mathcal TV-\mathcal TW\|_\infty\le\gamma\|V-W\|_\infty$$이다. $$\gamma<1$$이고 공간이 완비이므로 정확한 가치 반복은 유일한 고정점으로 수렴한다. $$k$$단계 뒤 오차는 초기 오차의 $$\gamma^k$$배 이하다.

신경망은 가치를 매개변수화한 함수 집합으로 제한한다. 벨만 갱신을 이 집합으로 사영하면 수축성이 유지되지 않을 수 있다. 기울기 하강의 최적화 동역학도 정확한 가치 반복과 다르다.

### 시간차 학습과 액터–크리틱
{: id="시간차-학습과-정책-기울기의-선택"}

한 단계 표본을 사용하는 크리틱 목표는 다음과 같다.

$$
y_t=r_t+\gamma\mathbf1\{\text{nonterminal}\}\max_{a'\in\mathcal A(s_{t+1})}Q_{\bar\theta}(s_{t+1},a').
$$

제곱 TD 손실은 $$Q_\theta(s_t,a_t)$$를 목표에 맞춘다. 종료와 시간제한의 마스킹, 다음 상태의 실행 가능성이 부트스트랩을 결정한다. 목표 네트워크 $$\bar\theta$$와 재생은 학습을 안정화할 수 있지만 수렴을 보장하지는 않는다.

액터–크리틱은 상태 가치를 빼서 어드밴티지를 추정한다. PPO는 표본 우도비 $$r_t(\theta)=\pi_\theta(a_t\mid s_t)/\pi_{\mathrm{old}}(a_t\mid s_t)$$를 클리핑한 대리 목적 함수에 사용한다.

$$
\mathcal L_{\mathrm{clip}}(\theta)=
\mathbb E_t\left[\min\left(r_t(\theta)\widehat A_t,
\operatorname{clip}(r_t(\theta),1-\epsilon,1+\epsilon)\widehat A_t\right)\right].
$$

분모는 표본을 수집한 정책에서 가져오고 행동의 의미도 같아야 한다. 표본 클리핑은 모든 상태의 정책 변화에 상한을 주지는 않는다. [PPO](https://arxiv.org/abs/1707.06347).

엔트로피 정규화는 $$\alpha>0$$에 대해 $$\alpha H(\pi(\cdot\mid s))$$를 더한다. 한 상태의 행동 가치를 고정하면 다음을 최대화한다.

$$
\sum_a\pi_a Q_a-\alpha\sum_a\pi_a\log\pi_a
\quad\text{subject to }\sum_a\pi_a=1.
$$

라그랑주 미분으로 가능한 행동 위에서 $$\pi_a\propto\exp(Q_a/\alpha)$$를 얻는다. 엔트로피는 선호 정책을 바꾼다. [Soft Actor-Critic](https://arxiv.org/abs/1801.01290)은 이 체계를 전개하며, 그래프의 이산 행동에는 이산 정식화가 필요하다.

## 순열 대칭성
{: id="9-순열-대칭성이-중요한-이유"}

노드 ID가 임의일 때 순열 행렬 $$\Pi$$, 인접 행렬 $$A$$, 특징 $$X\in\mathbb R^{n\times d}$$는 노드 수준에서 다음 등변성을 만족해야 한다.

$$
f(\Pi A\Pi^\top,\Pi X)=\Pi f(A,X).
$$

풀링한 그래프 출력은 순열에 불변이어야 노드 이름을 바꾸어도 같은 의사결정 문제가 된다.

GCN 형태의 층은 $$\widetilde A=A+I$$, 그 차수 행렬 $$\widetilde D$$와 다음 식을 사용한다.

$$
H'=\sigma(\widetilde D^{-1/2}\widetilde A\widetilde D^{-1/2}HW).
$$

순열은 정규화 인접 행렬을 $$\Pi\widetilde D^{-1/2}\widetilde A\widetilde D^{-1/2}\Pi^\top$$로 바꾼다. 행렬 곱과 원소별 비선형 함수를 적용하면 $$\Pi H'$$를 얻으므로 층의 등변성이 성립한다. [Kipf와 Welling](https://arxiv.org/abs/1609.02907). 방향·레이블·이질성이 있는 간선에는 확장이 필요하다.

등변성은 이름을 바꾸는 성질이지 모든 구조의 구별 능력을 뜻하지 않는다. 지역 메시지 전달은 다른 구조에도 같은 임베딩을 줄 수 있다. 전역 예산, 경로 이력, 선택 집합이 필요하면 상태에 명시적으로 넣어야 한다.

밀집 투영은 대략 $$O(nd_{\mathrm{in}}d_{\mathrm{out}})$$, 희소 집계는 추가로 $$O(\vert E\vert d_{\mathrm{out}})$$가 든다. 순서가 있는 노드 쌍의 행동 점수 계산에는 여전히 $$O(n^2)$$가 들 수 있다.

## Max-Cut
{: id="10-완결된-조합-문제-예시-max-cut"}

무방향 그래프의 간선 가중치가 $$w_{uv}$$이고 음수가 아니라고 하자. 모든 노드에 레이블 $$z_v\in\{0,1\}$$을 부여하고 다음을 최대화한다.

$$
\mathrm{Cut}(z)=\sum_{\{u,v\}\in E}w_{uv}\mathbf1\{z_u\ne z_v\}.
$$

순차 구성은 고정된 순서로 노드를 방문한다. 상태에는 그래프·다음 노드·이전 레이블이 있고, 행동은 그 노드의 레이블을 정한다. 양 끝점의 배정이 막 끝난 간선을 보상으로 센다.

$$
r_t=\sum_{u\text{ assigned earlier}}w_{uv_t}\mathbf1\{z_u\ne z_{v_t}\}.
$$

간선마다 한 번씩 기여하므로 할인하지 않은 누적 보상은 최종 컷 값과 같다. 이 유한 길이 구성은 $$\gamma=1$$을 사용한다. 할인하면 일찍 잘린 간선을 선호하게 된다.

단위 가중치의 네 노드 사이클 $$1-2-3-4-1$$에 $$(0,1,0,1)$$을 배정하면 간선 네 개가 모두 잘린다. 전체 가중치 4가 상한이기도 하므로 최적이다. 더 큰 미관측 사례에서 학습 비용을 분담하는 추론을 솔버·휴리스틱과 비교할 수 있다.

노드 순서까지 선택하면 행동 공간이 커지고 배정한 노드를 마스킹해야 한다. 종료 보상만 쓰면 최종 목적은 같아도 새 간선을 완성할 때가 아닌 모든 배정 뒤에 피드백을 받으므로 기여도 배분이 어려워진다. 같은 최종 조합 목적에도 다른 환경을 정의하는 선택이다.

## 인과 그래프와 공격
{: id="11-인과-발견-공격-다중-에이전트-그래프"}

DAG 탐색에서 관측 데이터에 잘 맞는다는 사실만으로 인과성을 식별할 수는 없다. 마르코프 동치 DAG는 조건부 독립성을 공유한다. 더 강한 결론에는 가정·개입·제한된 모형이 필요하다.

가중 인접 행렬 $$W$$에 대해 [NOTEARS](https://arxiv.org/abs/1803.01422)가 제시한 미분 가능한 비순환성 조건은 다음과 같다.

$$
h(W)=\operatorname{tr}\big(\exp(W\odot W)\big)-n=0.
$$

음이 아닌 $$B=W\odot W$$에서 $$\operatorname{tr}(B^k)$$는 닫힌 보행 가중치의 합이다. 전개식 $$h(W)=\sum_{k\ge1}\operatorname{tr}(B^k)/k!$$는 0이 아닌 방향 사이클에서 양수이고 DAG에서 0이다. 인과 식별성이 아닌 구조 제약이므로 강화학습 탐색과 연속 최적화 모두 통계적 목적 함수가 필요하다.

대칭 그래프 공격은 최대 $$b$$개의 무방향 수정에 $$\|A'-A\|_0\le2b$$를 부과할 수 있다. 계수 2는 행렬의 두 원소를 세며 자기 루프 관례에 따라 달라진다. 공격은 예산 안에서 대상 모델의 손실을 최대화한다. 공격 성공, 유효성, 다른 대상에 대한 전이, 방어 성능은 서로 다른 속성이다. 하나의 고정 대상에서 높은 보상을 얻어도 나머지는 보장되지 않는다.

그래프 에이전트는 지역적으로 통신하면서 학습 시 중앙 크리틱만 전역 정보를 볼 수 있다. 배포된 액터에는 그 정보가 없을 수 있다. 행동이 각각 $$K$$개면 공동 공간은 $$K^n$$개이며, 분해로 계산을 줄이려면 추가 가정이 필요하다.

## 참고문헌
{: id="참고문헌과-적용-범위"}

- [Reinforcement Learning on Graphs: A Survey](https://arxiv.org/abs/2204.06127).
- [MINERVA: Go for a Walk and Arrive at the Answer](https://arxiv.org/abs/1711.05851).
- [Multi-Hop Knowledge Graph Reasoning with Reward Shaping](https://arxiv.org/abs/1808.10568).
- [Sutton과 Barto, Reinforcement Learning](http://incompleteideas.net/book/the-book-2nd.html).
- [PyTorch Geometric](https://github.com/pyg-team/pytorch_geometric)과 [TGB](https://github.com/shenyangHuang/TGB).
