---
layout: article
lang: ko
translation_key: 2026-02-15-Nested-Learning
date: 2026-02-15
permalink: /ko/2026/02/15/Nested-Learning.html
original_url: /2026/02/15/Nested-Learning.html
translated_at: 2026-10-29
title: "Nested Learning"
tags: ["machine-learning", "memory", "continual-learning"]
subtitle: "연관 기억과 최적화기 상태, 여러 시간 척도의 결합 학습을 다룬다."
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-11
---

Nested Learning은 서로 다른 문맥과 시간 척도에서 갱신하는 학습기들의 상호작용을 설명한다. 빠른 연관 상태, 최적화기 이력, 느린 가중치는 서로 다른 기억이며, 갱신 규칙이 적응과 보존을 결정한다.

## 상태와 매개변수
{: id="1-모델이-학습할-때-무엇이-바뀌는가"}

지도학습 예측기 $$f_\theta(x)$$는 손실로 매개변수를 학습한다. 상태를 가진 학습기는 이력에 의존하는 $$z_t$$도 유지한다.

$$
\widehat y_t=f_\theta(x_t,z_t),\qquad
z_{t+1}=U_\psi(z_t,C_t).
$$

갱신 문맥 $$C_t$$에는 입력·표현·정답·내부 학습 신호가 들어갈 수 있다. 정답 $$y_t$$가 필요한 갱신이라면 그 시점에 정답을 이용할 수 있어야 한다.

논문은 중첩·병렬 최적화 수준을 정리하고 구현 사례로 Hope를 제시한다. 아래 유도는 Hope 아키텍처와 구분한 일반 예시다. [논문](https://arxiv.org/abs/2512.24695), [Google Research](https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/).

## 연관 기억
{: id="2-회귀-문제로-보는-연관-기억"}

키 $$k_i\in\mathbb R^{d_k}$$가 값 $$v_i\in\mathbb R^{d_v}$$에 대응한다고 하자. 선형 기억 $$M\in\mathbb R^{d_v\times d_k}$$는 다음 문제를 푼다.

$$
\mathcal L(M)=\frac12\sum_i\|Mk_i-v_i\|_2^2
+\frac\lambda2\|M\|_F^2,\qquad\lambda>0.
$$

행렬을 $$K=[k_1,\ldots,k_n]$$와 $$V=[v_1,\ldots,v_n]$$로 두고 기울기를 0으로 놓으면 다음을 얻는다.

$$
M(KK^\top+\lambda I)=VK^\top,
\qquad
M^*=VK^\top(KK^\top+\lambda I)^{-1}.
$$

양수 $$\lambda$$가 가역성을 보장한다. 정규화가 없으면 특이한 키 행렬에 의사역행렬이 필요하고 최적해가 여럿일 수 있다.

정규화하지 않은 단일 관측 온라인 손실에 대해 한 번 기울기 갱신을 하면 다음과 같다.

$$
M_{t+1}=M_t-\eta_t(M_tk_t-v_t)k_t^\top.
$$

델타 규칙은 예측 오차를 기억에 쓴다. $$(M_tk_t-v_t)k_t^\top$$의 크기는 $$d_v\times d_k$$다.

### 간섭
{: id="간섭은-수식에서-드러난다"}

쌍 $$(k_t,v_t)$$를 기록하면 과거의 키 $$k'$$에 대한 출력은 다음만큼 바뀐다.

$$
(M_{t+1}-M_t)k'
=-\eta_t(M_tk_t-v_t)(k_t^\top k').
$$

이 갱신에서 직교 키는 간섭하지 않고 상관된 키는 이전 읽기 결과를 바꿀 수 있다. 용량, 키의 기하, 정규화, 게이팅, 통합이 기억 보존을 결정한다.

제곱 노름이 $$c>0$$인 고정 키의 오차는 $$e_{t+1}=(1-\eta c)e_t$$이며, $$0<\eta c<2$$에서 수축한다. 단일 표본의 결과로 비선형 결합 시스템의 안정성을 입증할 수는 없다.

## 어텐션과 저장된 쌍
{: id="3-다른-기억-읽기-방식으로서의-어텐션"}

질의 $$q\in\mathbb R^{d_k}$$, 키 벡터 $$k_i$$, 값 $$v_i$$가 주어졌을 때 다음과 같다.

$$
\alpha_i(q)=\frac{\exp(q^\top k_i/\sqrt{d_k})}
{\sum_j\exp(q^\top k_j/\sqrt{d_k})},
\qquad\widehat v(q)=\sum_i\alpha_i(q)v_i.
$$

어텐션은 명시적인 키·값 쌍을 읽으며 캐시는 기울기 갱신 없이 바뀔 수 있다. 회귀 기억은 연관 관계를 $$M$$에 압축한다. 용량·비용·기록 방식이 다르다. 캐시는 저장 예시를 추가·교체하지만 회귀 규칙은 모든 키에 답할 때 사용하는 매개변수를 바꾼다.

디코더 KV 캐시는 대개 요청 안에서만 유지된다. 그 갱신이 사용자 사이에 미세조정 가중치로 남는 것은 아니다. 상태 수명과 초기화 규칙이 무엇을 보존할지 정한다.

## 최적화기의 기억
{: id="4-최적화기도-이미-기억을-유지한다"}

기울기 $$g_t$$에 대해 정규화된 모멘텀은 다음 상태를 유지한다.

$$
v_t=\beta v_{t-1}+(1-\beta)g_t,\qquad0\le\beta<1.
$$

$$v_0=0$$으로 두고 전개하면 다음과 같다.

$$
v_t=(1-\beta)\sum_{i=1}^{t}\beta^{t-i}g_i.
$$

지수 가중 기울기 이력의 반감기는 $$0<\beta<1$$에서 $$\log(1/2)/\log\beta$$다. 감쇠 계수가 1에 가까우면 긴 이력을 유지하지만 반응은 느려진다.

Adam은 좌표별 1차·2차 모멘트를 유지한다.

$$
\begin{aligned}
m_t&=\beta_1m_{t-1}+(1-\beta_1)g_t,\\
v_t&=\beta_2v_{t-1}+(1-\beta_2)(g_t\odot g_t),\\
\widehat m_t&=m_t/(1-\beta_1^t),\quad
\widehat v_t=v_t/(1-\beta_2^t),\\
\theta_{t+1}&=\theta_t-\eta_t\widehat m_t\oslash(\sqrt{\widehat v_t}+\epsilon).
\end{aligned}
$$

나눗셈·제곱근은 좌표별 연산이고 $$\epsilon>0$$은 0 나눗셈을 막는다. 이는 표준 [Adam](https://arxiv.org/abs/1412.6980) 점화식이다. 편향 보정은 가정 아래 모멘트 초기화를 다룰 뿐 임의의 비정상성이나 수렴을 해결하지 않는다. Nested Learning은 이 상태를 기억으로 해석한다.

## 중첩 목적 함수
{: id="5-중첩된-목적-함수와-기울기-흐름"}

간단한 이중 수준 구성은 다음과 같다.

$$
\phi^*(\theta)=\arg\min_\phi\mathcal L_{\mathrm{inner}}(\phi;\theta),\qquad
\min_\theta\mathcal L_{\mathrm{outer}}(\theta,\phi^*(\theta)).
$$

내부 해가 유일하고 매끄러운 정지점이며 $$\phi$$의 헤시안이 가역이면 음함수 미분으로 다음을 얻는다.

$$
\frac{d\phi^*}{d\theta}
=-\left(\nabla_{\phi\phi}^2\mathcal L_{\mathrm{inner}}\right)^{-1}
\nabla_{\phi\theta}^2\mathcal L_{\mathrm{inner}}.
$$

외부 기울기는 직접 효과와 적응 상태의 효과를 포함한다. 유한 단계 전개는 다른 근사를 계산하며, 전개를 자르거나 기울기를 막으면 기울기 근사와 계산 비용이 달라진다.

이 이중 수준 예시가 Hope의 모든 구성 요소에 추론 중 정확한 내부 최적화를 요구하는 것은 아니다.

## 갱신 빈도
{: id="6-여러-갱신-빈도"}

상태 $$z_t^{(k)}$$를 가진 모듈에서 $$u_k(t)\in\{0,1\}$$가 예정된 갱신 여부를 나타낸다고 하자.

$$
z_{t+1}^{(k)}=
\begin{cases}
U_k(z_t^{(k)},C_t),&u_k(t)=1,\\
z_t^{(k)},&u_k(t)=0.
\end{cases}
$$

$$H$$단계에서 관측한 빈도는 다음과 같다.

$$
f_k(H)=\frac1H\sum_{t=1}^{H}u_k(t).
$$

빈도는 예정된 기록 횟수를 세고 학습률은 한 갱신의 보폭을 정한다. 잦은 작은 갱신이 드문 큰 갱신보다 덜 바꿀 수 있다. 갱신 크기와 문맥 범위도 실질적인 시간 척도를 정한다.

Hope는 여러 속도의 Continuum Memory System과 자기 수정 모듈을 결합한다. 게이트 합·이어 붙이기·어텐션은 가능한 결합의 예시이지 검증한 구현 명세가 아니다.

## 지속 학습 지표
{: id="7-지속-학습의-평가"}

$$a_{t,i}$$는 과제 $$t$$까지 학습한 뒤 과제 $$i$$의 정확도다. 최종 평균은 다음과 같다.

$$
\mathrm{ACC}_T=\frac1T\sum_{i=1}^{T}a_{T,i}.
$$

$$T>1$$일 때 망각을 측정하는 한 가지 정의는 다음과 같다.

$$
\mathrm F_T=\frac1{T-1}\sum_{i=1}^{T-1}
\left(\max_{i\le t<T}a_{t,i}-a_{T,i}\right).
$$

이 부호 있는 지표는 이전 과제 성능이 좋아지면 음수가 된다. 0에서 잘라내면 다른 지표다. 빠른 상태를 유지한 평가와 초기화 후의 정확도도 다를 수 있다. 전이, 적응 지연, 영속 상태 크기, 초기화 동작으로 보존과 가소성의 상충관계를 볼 수 있다.

언어 모델링, 긴 문맥 회상, 온라인 적응, 지속 지도학습은 다른 능력을 시험한다. Hope의 보고된 규모·데이터·기준선으로 망각의 보편적 제거를 입증할 수는 없다.

## 통제된 비교
{: id="8-통제된-실험을-설계한다"}

고정 상태, 온라인 기울기 없는 순환 상태, 온라인 갱신은 다른 작동 원리를 분리한다. 매개변수·갱신 예산·추론 계산량을 맞추면 긴 스트림, 변화, 이전 과제 복귀에서 갱신 속도를 비교할 수 있다.

상태 유지가 목적이 아니라면 독립 사용자·스트림 사이에 초기화가 필요하다. 학습·평가 중 상태 변화와 구현 출처를 기록해야 아키텍처 재현과 커뮤니티 근사를 구분할 수 있다.

## 기울기 간섭
{: id="9-기울기-간섭으로-보는-망각"}

과제 $$i$$의 위험을 $$R_i(\theta)=\mathbb E_{(x,y)\sim\mathcal D_i}[\ell(f_\theta(x),y)]$$라고 하자. 과제 $$t$$의 기울기 갱신은 $$\theta'=\theta-\eta g_t$$이고 $$g_t=\nabla R_t(\theta)$$이다. 1차 전개는 다음과 같다.

$$
R_i(\theta')-R_i(\theta)=-\eta\nabla R_i(\theta)^\top g_t+O(\eta^2).
$$

이전·현재 기울기의 내적이 음수이면 1차 효과는 이전 위험을 높인다. 곡률과 보폭이 이 근사의 오차를 제한한다. 기울기가 $$L_i$$-Lipschitz이면 다음과 같다.

$$
\left\vert R_i(\theta-\eta g_t)-R_i(\theta)+\eta\nabla R_i(\theta)^\top g_t\right\vert
\le\frac{L_i\eta^2}{2}\|g_t\|^2.
$$

1차원에서 $$R_1(\theta)=\tfrac12(\theta-1)^2$$, $$R_2(\theta)=\tfrac12(\theta+1)^2$$에서 이전 최적점 $$\theta=1$$은 새 과제를 향한 한 단계 뒤 $$\theta'=1-2\eta$$가 되어 $$R_1(\theta')=2\eta^2$$를 얻는다. 빠른 상태를 나누면 공유 가중치의 부담은 줄어도 양립하지 않는 목적이 사라지지는 않는다.

다음과 같이 보존을 위한 정규화 목적 함수를 둘 수 있다.

$$
R_t(\theta)+\frac\lambda2\sum_jF_j(\theta_j-\theta_j^{\mathrm{old}})^2
$$

이 목적 함수는 $$F_j\ge0$$로 이전 매개변수 변화에 벌점을 준다. [Elastic Weight Consolidation](https://www.pnas.org/doi/10.1073/pnas.1611835114)은 피셔 정보로 중요도를 근사한다. Hope의 정의가 아닌 비교 수단이며, 재생·분리·정규화·통합에는 다른 저장·개인정보 비용이 따른다.

## 갱신을 통과하는 미분
{: id="10-명시적인-내부-갱신을-통과해-미분한다"}

명시적인 빠른 갱신을 생각하자.

$$
\phi_{t+1}=\phi_t-\eta\nabla_\phi\mathcal L_t(\phi_t;\theta).
$$

기울기를 열벡터로 쓰면 이전 상태의 야코비안은 다음과 같다.

$$
J_t=I-\eta\nabla^2_{\phi\phi}\mathcal L_t.
$$

$$D_t=d\phi_t/d\theta$$로 두고 연쇄법칙으로 미분하면 다음을 얻는다.

$$
D_{t+1}=J_tD_t-\eta\nabla^2_{\phi\theta}\mathcal L_t.
$$

직접적인 매개변수 미분과 적응 상태의 기여를 함께 계산한다. 외부 기울기에는 $$D_T^\top\nabla_\phi\mathcal L_{\mathrm{outer}}$$가 더해진다. $$J_t$$의 곱은 기울기를 줄이거나 키운다. 초기화 경계는 어떤 과거 적응이 목적 함수에 영향을 주는지 바꾼다. 학습 가능한 학습률이나 갱신 네트워크에는 추가 미분 항이 생긴다.

양의 정부호 헤시안 $$H$$와 고정 최적점이 있는 이차 손실은 고유 모드마다 $$1-\eta\lambda_j(H)$$배로 변한다. 안정성에는 $$0<\eta<2/\lambda_{\max}(H)$$가 필요하다. 빈도가 같아도 곡률에 따라 적응 속도가 다르며, 비볼록 네트워크는 이 전역 헤시안 모형을 따르지 않을 수 있다.

## 갱신 일정과 결합 안정성
{: id="11-실제-시간의-척도와-결합된-안정성"}

기본 단계 $$k$$번마다 감쇠 $$\beta\in(0,1)$$로 기록하는 지수 이력은 $$m$$번 기록 뒤 $$\beta^m$$에 비례하는 가중치를 유지한다. 기본 단계 단위의 반감기는 다음과 같다.

$$
h_{\mathrm{base}}=k\frac{\log(1/2)}{\log\beta}.
$$

장기 기록 횟수가 같아도 일정을 알 수는 없다. 한 번에 몰아 쓰거나 구간 전체에 고르게 기록하면 경험적 빈도는 같더라도 최근 정보에 대한 반응과 최대 갱신 지연이 달라진다.

결합 선형계 $$z_{t+1}=A_tz_t$$의 주기가 $$k$$이면 경계 상태는 $$z_{(m+1)k}=Pz_{mk}$$를 따르며 다음과 같다.

$$
P=A_{k-1}\cdots A_1A_0.
$$

이 유한 차원 주기계의 점근적 안정성은 스펙트럴 반지름 $$\rho$$에 대해 $$\rho(P)<1$$일 때, 그리고 그때만 성립한다. 모듈이 각각 안정해도 그 곱이 안정하다는 보장은 없다.

모듈별 읽기·쓰기 비용이 일정할 때 평균 계산량 모형은 다음과 같다.

$$
\overline C=\sum_j C_{\mathrm{read},j}+\sum_j f_jC_{\mathrm{write},j}.
$$

계획용 모형이므로 동기화·배치·메모리 전송을 제외한다. 쓰기가 겹치면 최대 지연이 커진다. 평균 계산량, 꼬리 지연, 상태 크기·수명, 학습 신호의 가용성은 별도 측정량이다.

## Hope 재현
{: id="12-hope-재현에서-입증해야-할-것"}

재현에는 실제 자기 수정 모듈, Continuum Memory System 연결, 목적, 문맥 흐름, 일정이 필요하다. 일반 순환식과 표준 Adam은 작동 원리를 설명하지만 해당 구성 요소를 재현하지는 않는다.

자기 수정·빈도·용량·갱신 미분을 따로 바꾸면 중첩 구조와 추가 자원의 효과를 분리할 수 있다. 매개변수, 학습 토큰, 초기화, 최적화기, 문맥 길이, 지도 정보, 초기화 규칙을 맞춰 비교한다.

이론 모형은 상호작용하는 학습 수준을 정리한다. 특정 구현의 보존·적응·효율은 정해진 스트림에서 입증해야 한다.

## 참고문헌
{: id="참고문헌과-적용-범위"}

- [Behrouz 외, Nested Learning](https://arxiv.org/abs/2512.24695).
- [저자가 제공하는 논문 전문](https://abehrouz.github.io/files/NL.pdf).
- [Google Research 개요](https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/).
- [Adam](https://arxiv.org/abs/1412.6980)과 [Titans](https://arxiv.org/abs/2501.00663).
