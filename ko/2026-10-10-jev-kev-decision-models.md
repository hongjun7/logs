---
layout: article
lang: ko
date: 2026-10-10
translation_key: 2026-10-10-jev-kev-decision-models
permalink: /ko/2026/10/10/jev-kev-decision-models.html
original_url: /2026/10/10/jev-kev-decision-models.html
title: "Jev와 Kev"
tags: ["machine-learning", "decision-models", "calibration", "open-source", "engineering"]
subtitle: "확률 출력, 확률 보정, 의사결정 손실, 공개 Kev 구현."
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-11
translated_at: 2026-10-29
---

Jev는 설명을 생성하는 대신 범위가 정해진 의사결정에 확률분포를 반환한다. Kev는 비슷한 인터페이스를 공개 가중치로 구현한다. 유용성은 확률 보정, 업무에 맞는 레이블, 각 행동에 부여한 손실에 달려 있다.

## 의사결정 분포
{: id="1-의사결정-모델은-어떤-문제를-해결하는가"}

중복 청구 문의에는 담당 팀 레이블, 긴급도 점수, 참·거짓 판단이 필요할 수 있다. 주어진 상태 $$x$$, 지시문 $$q$$, 선택지 설명 $$C=(c_1,\ldots,c_K)$$에 대해 분류기는 다음을 반환한다.

$$
p_\theta(y=k\mid x,q,C),\qquad p_k\ge0,\qquad\sum_{k=1}^{K}p_k=1.
$$

학습된 매개변수 $$\theta$$는 입력을 확률 단체 $$\Delta^{K-1}$$로 보낸다. 반면 $$M$$개 토큰을 생성하는 모델은 다음과 같이 분해한다.

$$
p_\theta(t_{1:M}\mid x)=\prod_{j=1}^{M}p_\theta(t_j\mid x,t_{1:j-1}).
$$

직접 판단하면 답변 생성과 파싱을 피하지만 입력 처리와 점수 계산은 필요하며, 정답이 보장되는 것도 아니다. [TypeSafe](https://docs.typesafe.ai/introduction)는 Jev를 보정된 의사결정을 위한 강화학습(Reinforcement Learning for Calibrated Decisions, RLCD)으로 학습한 호스팅형 System One 모델로 소개한다. [출시 글](https://typesafe.ai/blog/introducing-system-one-models-and-jev)만으로 전체 학습 데이터, 아키텍처, 가중치, 재현 가능한 원래 학습법의 공개를 확인할 수는 없다. 커뮤니티 구현이 그 내부를 밝혀 주지는 않는다.

<div id="3-선택지-확률이-조건부인-이유"></div>

## 출력
{: id="2-세-가지-기본-연산-choice-noul-score"}

| 기본 연산 | 출력 | 해석 |
|---|---|---|
| Choice | 순서 없는 선택지 $$K$$개의 분포 | 정답 클래스가 빠질 수 있다 |
| Noul | “예”의 확률 $$p$$ | 행동 임계값은 손실에 달려 있다 |
| Score | 순서 있는 수준의 분포와 평균 인덱스 | 순서만으로 심각도의 같은 간격을 보장하지 않는다 |

Choice는 보통 다음을 선택한다.

$$
\widehat y=\operatorname*{arg\,max}_{k}p_k.
$$

Noul은 $$(1-p,p)$$을 나타낸다. $$p$$가 참 사후확률일 때만 임계값 $$0.5$$가 대칭 이진 오분류 손실을 최소화한다. 순서 있는 Score 수준 $$K$$개를 $$0,\ldots,K-1$$로 두면 다음과 같다.

$$
\overline s=\sum_{i=0}^{K-1}i\,p_i.
$$

따라서 $$(p_0,p_1,p_2)=(0,0.57,0.43)$$은 $$1.43$$을 준다. 별도의 레이블이 아니라 주어진 부호화에서의 평균이다. $$(0,1,2)$$를 $$(0,1,10)$$으로 바꾸면 평균도 바뀐다. 비용이 비선형이면 전체 분포가 필요하다([Choice](https://docs.typesafe.ai/primitives/choice), [Noul](https://docs.typesafe.ai/primitives/noul), [Score](https://docs.typesafe.ai/primitives/score)).

“결제”를 빼면 남은 선택지에 확률 질량이 몰려 높은 신뢰도의 오답이 나올 수 있다. $$C\ne C'$$이면 일반적으로 다음과 같다.

$$
p(y=k\mid x,q,C)\ne p(y=k\mid x,q,C')
$$

“근거 부족” 선택지는 누락된 결과를 표현하지만 낯선 입력의 탐지를 보장하지는 않는다. 업무 설명은 복합 의도를 처리할 규칙을 정해야 한다. 단일 Choice는 승자 하나를 고르고, 별도 Noul은 각 속성의 주변확률을 나타낸다.

질문들이 서로의 답을 읽지 않아도 레이블은 통계적으로 의존할 수 있다. $$\Pr(A)=0.8$$, $$\Pr(B)=0.7$$이면 프레셰 경계는 다음과 같다.

$$
0.5=\max(0,0.8+0.7-1)\le \Pr(A\cap B)\le\min(0.8,0.7)=0.7.
$$

곱 $$0.56$$에는 레이블의 독립성이 필요하다. 별도의 모델 호출만으로는 충족되지 않는다.

## 신뢰도
{: id="4-신뢰도는-분포를-요약한-통계량이다"}

[API 명세](https://docs.typesafe.ai/confidence)는 적어도 두 개인 선택지 $$K$$개에 대해 Choice의 최대 확률을 다시 조정한다.

$$
c_{\mathrm{choice}}=\frac{p_{\max}-1/K}{1-1/K}.
$$

균등분포는 0, 점질량은 1이 되며 $$(0.6,0.3,0.1)$$는 $$0.4$$를 준다. 정답 확률은 아니다. Noul은 $$p$$를 반환하고, 같은 취지의 선택적 요약값은 $$\vert 2p-1\vert $$다. Score의 최빈값 $$m=\arg\max_i p_i$$에 대해 다음과 같다.

$$
\begin{aligned}
D_K&=\frac1K\sum_{i=0}^{K-1}\left\vert i-\frac{K-1}{2}\right\vert ,\\
c_{\mathrm{score}}&=\max\left(0,1-\frac{\sum_i p_i\vert i-m\vert }{D_K}\right).
\end{aligned}
$$

동률 처리는 구현에 따른다. $$K=3$$이면 $$D_K=2/3$$이므로 $$(0,0.57,0.43)$$의 신뢰도는 $$c_{\mathrm{score}}=0.355$$이며 평균은 $$1.43$$다. 대수적으로 다음이 성립한다.

$$
c_{\mathrm{choice}}\ge t
\quad\Longleftrightarrow\quad
p_{\max}\ge\frac1K+t\left(1-\frac1K\right).
$$

따라서 $$K=3$$에서 $$t=0.9$$이면 $$p_{\max}\ge0.933\overline3$$이어야 한다. 손실 공식의 $$p_{\max}$$를 신뢰도로 대체할 수 없다. 중점 양쪽의 거리를 짝지으면 짝수 $$K$$에서 $$D_K=K/4$$, 홀수 $$K$$에서 $$D_K=(K^2-1)/(4K)$$다. 분모는 $$K\ge2$$에서 양수이며, 선택지가 하나이면 별도 규칙이 필요하다.

<div class="probability-explorer" data-probability-explorer>
  <h3>세 선택지 분포</h3>
  <p>음수가 아닌 가중치를 모델 호출 없이 확률로 바꾼다. Choice는 순서 없는 레이블, Score는 수준 0, 1, 2를 사용한다.</p>
  <div class="probability-controls">
    <label>선택지 / 수준 0 <input type="range" min="0" max="100" value="60" data-weight="0"></label>
    <label>선택지 / 수준 1 <input type="range" min="0" max="100" value="30" data-weight="1"></label>
    <label>선택지 / 수준 2 <input type="range" min="0" max="100" value="10" data-weight="2"></label>
  </div>
  <div class="probability-bars" aria-hidden="true"><span data-bar="0"></span><span data-bar="1"></span><span data-bar="2"></span></div>
  <p class="probability-result" aria-live="polite" data-result>확률 예제를 불러오는 중…</p>
  <noscript><p>초깃값: 확률 (0.600, 0.300, 0.100), Choice 신뢰도 0.400, 평균 수준 0.500, Score 신뢰도 0.250. JavaScript를 활성화하면 가중치를 조절할 수 있다.</p></noscript>
</div>

## 확률 보정
{: id="5-정확도-확률-보정-적정-점수-규칙"}

비슷한 문의 1,000개에 $$0.95$$를 부여하고 800개만 맞힌 모델의 정확도는 $$0.8$$이며 확률은 지나치게 집중되어 있다. 정답 클래스 $$Y$$와 무작위 예측 벡터 $$P$$에서 최상위 레이블 보정은 지지집합의 확률값에 대해 다음을 요구한다.

$$
\Pr(Y=\widehat Y\mid P_{\max}=s)=s.
$$

클래스별 보정은 각 $$k$$에 대해 $$\Pr(Y=k\mid P_k=s)=s$$를 요구한다. 전체 벡터 보정은 $$\Pr(Y=k\mid P)=P_k$$가 거의 확실하게 성립할 것을 요구하며 더 강하다. 조건부 기댓값에 관한 조건이며, 유한한 구간은 이를 근사할 뿐 연속값의 정확한 빈도를 정의하지 않는다.

음의 로그우도와 Brier 점수는 정확도가 버리는 확률을 보존한다.

$$
\mathrm{NLL}=-\frac1n\sum_{j=1}^{n}\log p_{j,y_j},
\qquad
\mathrm{Brier}=\frac1n\sum_{j=1}^{n}\sum_{k=1}^{K}
\left(p_{j,k}-\mathbf1\{y_j=k\}\right)^2.
$$

정답 확률이 0에 가까워지면 NLL에는 상한이 없다. 전체 다중 클래스 Brier는 $$[0,2]$$, 양성 성분만 쓰는 이진 정의는 $$[0,1]$$에 속하며 후자는 두 성분 점수의 절반이다. 참 벡터 $$q$$와 예측 $$p$$에 대해 다음과 같다.

$$
\mathbb E_{Y\sim q}[-\log p_Y]=H(q)+D_{\mathrm{KL}}(q\Vert p),
$$

또 다음이 성립한다.

$$
\mathbb E_{Y\sim q}\left[\sum_k(p_k-\mathbf1\{Y=k\})^2\right]
=\|p-q\|_2^2+1-\|q\|_2^2.
$$

제곱을 전개하고 $$\mathbb E[\mathbf1\{Y=k\}]=q_k$$를 적용하면 두 값 모두 $$p=q$$에서 최소다. 이 모집단 성질은 유한한 학습이나 영역 변화에서의 보정을 보장하지 않는다.

### 적정 보상
{: id="승리한-레이블에-보상하는-것만으로-부족한-이유"}

입력이 주어졌을 때 행동 $$A$$를 $$p$$에서, 정답 $$Y\sim q$$를 그와 독립적으로 뽑는다. 정답 레이블 보상 $$\mathbf1\{A=Y\}$$의 기댓값은 다음과 같다.

$$
\mathbb E[R]=\sum_k p_kq_k.
$$

$$p$$에 대해 선형이므로 $$q_k$$가 최대인 점질량을 선호한다. $$q=(0.6,0.4)$$일 때 $$p=(1,0)$$의 기대 보상은 $$0.6$$이고, $$p=q$$의 기대 보상은 $$0.52$$다. 반면 음의 Brier 보상은 다음을 준다.

$$
\mathbb E[R(p,Y)]=-\|p-q\|_2^2-1+\|q\|_2^2,
$$

$$p=q$$에서 유일하게 최대다. 목적함수의 예시이며 Jev의 비공개 RLCD 보상이 아니다. 지도학습 교차 엔트로피도 이미 적정하므로 강화학습은 확률 보정의 필수 조건이 아니다.

구간별 기대 보정 오차는 다음과 같다.

$$
\mathrm{ECE}=\sum_{b=1}^{B}\frac{\vert I_b\vert }{n}
\left\vert \mathrm{acc}(I_b)-\mathrm{conf}(I_b)\right\vert .
$$

최상위 레이블의 `conf`는 재조정한 API 신뢰도가 아니라 평균 최대 확률이다. 구간과 표본 수가 ECE에 영향을 주고 구간 안의 오차는 상쇄될 수 있다. 신뢰도 도표, 적정 점수, 작업별 분석은 서로 다른 오류를 드러낸다.

### 온도
{: id="온도-조정"}

로짓 $$z_1,\ldots,z_K$$와 온도 $$\tau>0$$는 다음 분포를 정의한다.

$$
p_k^{(\tau)}=\frac{\exp(z_k/\tau)}{\sum_{i=1}^{K}\exp(z_i/\tau)}.
$$

$$\tau$$를 적합할 때는 보류한 보정 데이터의 NLL을 최소화한다. $$\tau$$를 높이면 분포가 완만해지고 낮추면 뾰족해진다. 양의 온도는 예제별 최댓값 인덱스를 보존하지만 예제 사이의 최대 확률 순서는 보존하지 않는다. 분류 오류는 남아도 다중 클래스의 위험·커버리지 곡선은 달라질 수 있다. 적합한 값은 모델과 분포에 종속되며([Guo 외](https://proceedings.mlr.press/v70/guo17a.html)), 영역이 바뀌면 새로운 레이블이 있는 보정 근거가 필요하다.

## 손실과 행동
{: id="6-손실로부터-행동을-유도하기"}

정답 $$y$$에서 행동 $$a$$의 손실이 $$L(a,y)$$이면, 보정된 사후확률 아래의 베이즈 행동은 다음과 같다.

$$
a^*(x)=\operatorname*{arg\,min}_a\sum_y L(a,y)p(y\mid x).
$$

거짓 양성 비용 $$C_{\mathrm{FP}}>0$$, 거짓 음성 비용 $$C_{\mathrm{FN}}>0$$, 정답 비용 0에서 각 위험은 $$C_{\mathrm{FP}}(1-p)$$와 $$C_{\mathrm{FN}}p$$다.

$$
\text{choose positive iff}\quad
p\ge\frac{C_{\mathrm{FP}}}{C_{\mathrm{FP}}+C_{\mathrm{FN}}}.
$$

$$C_{\mathrm{FP}}=9$$, $$C_{\mathrm{FN}}=1$$이면 임계값은 $$0.9$$다. 긴급 문의를 놓치는 비용이 더 높아 두 비용을 뒤집으면 $$0.1$$가 된다. 어느 쪽도 보편적인 신뢰도 기준은 아니다.

모든 오배정의 비용이 $$C_w$$이면 최선의 자동 배정 위험은 $$C_w(1-p_{\max})$$다. 완벽한 검토자의 비용이 $$C_r$$일 때 다음 조건에서 자동화가 유리하다.

$$
p_{\max}\ge1-\frac{C_r}{C_w}.
$$

$$C_w=10$$, $$C_r=1$$이면 확률 임계값 $$0.9$$은 $$K=3$$의 Choice 신뢰도 $$0.85$$과 같다. 실제 검토에는 잔여 오류와 대기가 추가된다. 결과별 비용이 다르면 전체 손실 행렬이 필요하다.

순서 있는 점수의 제곱 손실은 조건부 평균을 선택한다.

$$
\mathbb E[(a-Y)^2\mid x]=(a-\mathbb E[Y\mid x])^2+\operatorname{Var}(Y\mid x).
$$

분산 항이 $$a$$와 무관하기 때문이다. 절대 손실은 조건부 중앙값을 선택한다. 두 해석 모두 수치로 표현한 수준 간 거리가 의미 있어야 한다.

## 커버리지
{: id="7-커버리지와-잔여-위험-측정하기"}

수용 규칙 $$A_t=\mathbf1\{s(x)\ge t\}$$에 대해 다음과 같다.

$$
\mathrm{coverage}(t)=\Pr(A_t=1),
\qquad
\mathrm{risk}(t)=\Pr(\widehat Y\ne Y\mid A_t=1).
$$

수용이 없으면 위험은 정의되지 않는다. 오류가 $$\epsilon$$보다 작은지는 전체 정확도만이 아니라 수용 수와 언어·범주별 결과로 평가해야 한다. 임계값이 고정되어 있고 수용한 테스트 $$n_a$$개가 독립·동일분포(iid)이며 오류가 이진이면 회프딩 경계는 다음과 같다.

$$
\Pr(R>\widehat R+\eta)\le e^{-2n_a\eta^2},
\qquad
\eta=\sqrt{\frac{\log(1/\delta)}{2n_a}}.
$$

신뢰수준 $$1-\delta$$의 단측 경계다. 오류가 0건이면 정확한 이항 단측 상한은 다음과 같다.

$$
R_{\mathrm{upper}}=1-\delta^{1/n_a}.
$$

$$\delta=0.05$$, $$n_a=100$$에서 상한은 0이 아니라 $$0.0295$$다. “$$n$$분의 3”은 $$-\log(0.05)\approx3$$를 사용한다. 임계값은 개발 데이터에서 탐색해야 한다. 테스트 집합을 재사용하면 이 고정 임계값 보장이 무효가 된다. 고객 군집, 시간에 따른 변화, 중복도 iid 가정을 약화시킨다.

## Kev
{: id="8-공개-kev-구현이-실제로-계산하는-것"}

Kev는 한국 시간 2026년 10월 10일까지 공개된 [`fc4a17e`](https://github.com/jaredpalmer/kev/tree/fc4a17e194bca35a48c57211392ec49ea54a94ac)에 고정했다. [포인터 헤드](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/kev/model.py)는 의사결정 표현 $$h_d\in\mathbb R^d$$와 선택지 표현 $$h_i\in\mathbb R^d$$를 사영한다.

$$
\begin{aligned}
u&=W_qh_d+b_q,\\
v_i&=W_kh_i+b_k,\\
z_i&=\frac{v_i^\top u}{\sqrt{d_p}}.
\end{aligned}
$$

온도로 조정한 소프트맥스가 선택지 인덱스 확률을 만든다. 사영 차원 $$d_p$$는 선택지 수가 아니며 설명은 요청마다 바꿀 수 있다. 사영 작업 $$O((K+1)dd_p)$$와 내적 작업 $$O(Kd_p)$$에는 보통 지배적인 비용인 백본이 빠져 있다.

### 공유 상태
{: id="공유-상태와-분리된-분기"}

개념적인 순수 어텐션 블록 인과 마스크는 각 질문이 길이 $$S$$의 상태를 읽되 형제 분기 $$Q_1,\ldots,Q_m$$는 읽지 못하게 한다. 마스크를 활용하는 구현의 허용된 쌍 작업량은 다음과 같다.

$$
O\left(S^2+\sum_{j=1}^{m}(SQ_j+Q_j^2)\right)
$$

밀집 마스킹은 차단한 쌍까지 계산할 수 있어 마스크만으로 속도 향상이 입증되지는 않는다. 패킹한 순수 어텐션 입력에는 토큰 길이 제한 검사도 있다.

고정한 0.8B/4B/9B 모델은 Qwen3.5, LoRA, 포인터 헤드를 사용한다. 어텐션·순환 혼합 계층은 대신 별도의 인과적 행, 공유 접두사 재사용, 복제한 순환 상태를 쓴다. 예약 마커 정제가 의미를 이용한 프롬프트 주입을 막는다는 보장은 아니다. 27B는 사후학습된 Qwen3.8과 전체 가중치 조정을 쓴다. 기본 모델, 크기, 학습법이 모두 달라 매개변수 수만의 절제 실험이 되지 않는다([모델 카드](https://github.com/jaredpalmer/kev/tree/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards)).

### 레이블 우도
{: id="언어-모델의-레이블-기준선과-비교하기"}

생성형 기준선은 단일 토큰 레이블의 로짓을 정규화할 수 있다. 여러 토큰의 문자열 $$\ell_k$$에는 완전한 조건부 우도와 경계 규칙이 필요하다.

$$
a_k=\log p_\theta(\ell_k\mid x,q),
\qquad
\widetilde p_k=\frac{e^{a_k}}{\sum_i e^{a_i}}.
$$

의미상 클래스가 아니라 문자열에 질량을 부여한다. 길이, 토큰화, 철자, 동의어가 영향을 준다. [LLM-as-Jev](https://arxiv.org/abs/2610.02076)는 Jev의 비공개 아키텍처를 밝히지 않으면서 확률적 판단을 직접 내리는 방법을 연구한다.

## 측정 결과
{: id="9-성능표의-의미를-바꾸지-않고-읽기"}

고정한 카드는 개발·테스트 패널마다 질문 656개인 `transfer-v4`의 유지보수자 측정값을 보고한다. Kev 학습에 없던 출처와 정책을 사용했다고 설명하며 개발 데이터로 체크포인트를 선택한다. 보고된 결과이며 이 글에서 추론을 직접 측정한 값은 아니다.

| 모델 | 새 출처 정확도, 개발 | 새 출처 정확도, 테스트 | 전체 Brier, 개발 | 전체 Brier, 테스트 |
|---|---:|---:|---:|---:|
| Kev-0.8B | 0.648 | 0.697 | 0.430 | 0.397 |
| Kev-4B | 0.817 | 0.838 | 0.243 | 0.224 |
| Kev-9B v2 | 0.820 | 0.852 | 0.262 | 0.199 |
| Kev-27B v2 | 0.851 | 0.889 | 0.218 | 0.154 |
| Jev | 0.857 | 보고되지 않음 | 0.211 | 보고되지 않음 |

출처: [0.8B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-0.8b.md), [4B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-4b.md), [9B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-9b.md), [27B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-27b.md). 같은 리비전의 개요에는 예를 들어 4B Brier가 0.269 / 0.242로 나온다. 표는 상세 카드를 따르며 독립적인 재실행으로 불일치를 해소한 것은 아니다.

같은 분할의 비교는 Kev-27B 개발 $$0.851$$와 Jev $$0.857$$다. 차이는 $$0.006$$, 즉 0.6퍼센트포인트다. Kev 테스트 $$0.889$$와 Jev 개발 $$0.857$$는 서로 다른 분할이다. 알려지지 않은 Jev 학습 데이터와 이 집계값으로 오염이나 의존성을 배제할 수 없다. 통계적 유의성에는 평가 설계, 표본 수, 짝지은 예측이 필요하다.

검증한 문맥은 0.8B/4B/9B에서 8,192토큰, 27B에서 65,536토큰이다. 명시한 신뢰하한의 CUAD 기준이 각 모델의 8k 결과와 3퍼센트포인트 이내를 유지한다는 뜻이다. 서버가 입력 길이를 받아들인다고 임의 문서의 정확도가 보장되지는 않는다.

### 서빙
{: id="지연시간과-처리량은-분모가-다르다"}

| 모델 / GPU | 짧은 입력, 새 상태 / 같은 상태, ms | 약 2,200토큰, 새 상태 / 같은 상태, ms | 초당 요청 수, 클라이언트 64개 |
|---|---:|---:|---:|
| Kev-0.8B / L4 | 22.7 / 16.1 | 108.6 / 32.3 | 62.8 |
| Kev-4B / L40S | 41.5 / 27.7 | 145.2 / 43.0 | 51.4 |
| Kev-4B / H100 | 18.1 / 12.9 | 89.4 / 22.5 | 100.8 |
| Kev-9B v1 / H100 | 24.0 / 16.6 | 88.5 / 26.4 | 79.5 |

[0.8B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-0.8b.md), [4B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-4b.md), [9B](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/docs/model-cards/kev-9b.md) 카드는 서버 측 측정 20회의 중앙값을 사용하며 네트워크 시간은 제외한다. 짧은 요청과 긴 요청의 질문 수는 각각 여섯 개와 다섯 개다. 9B는 아키텍처·어댑터 형태가 같더라도 v2를 새로 측정한 것이 아니라 v1 측정값이다. 같은 상태는 접두사를 재사용하며, 처리량은 새 상태의 짧은 요청을 동시에 실행해 구한다. 처리량의 역수는 다른 부하에서 요청 하나의 지연시간 중앙값이 아니다.

개루프 비교에는 리비전, dtype·양자화, 하드웨어, 상태·분기 길이, 캐시 적중, 배치, 동시성, 도착 과정, 워밍업, p50/p95/p99가 필요하다. 판단당 GPU 비용은 다음과 같다.

$$
\frac{\text{GPU price per hour}}{3600\times\text{sustained decisions per second}},
$$

가정한 지속 처리량·가동률에서만 성립한다. 전체 비용에는 준비, 전송, 대기열, 정책 실행, 유휴 용량, 복제본, 다운로드, 운영도 포함된다.

<div id="독립적인-jev-결과가-보여-주는-범위"></div>

### 호스팅형 Jev
{: id="jev의-지연시간과-호스팅-비용"}

10월 11일 확인한 [출시 글](https://typesafe.ai/blog/introducing-system-one-models-and-jev)은 전체 응답시간 70–500ms, 입력 100만 토큰당 미화 0.042달러, 출력 무료를 보고한다. 공급자 수치이며 보장이나 GPU 표와 조건을 맞춘 비교가 아니다. 과금 입력 $$N_{\mathrm{in}}$$에 대해 다음과 같다.

$$
\mathrm{charge}_{\mathrm{USD}}=0.042\,N_{\mathrm{in}}/10^6.
$$

과금 대상인 요청 전체, 호출 제한, 버전, 지역·네트워크 조건이 현재 비용 추정을 결정한다. 대표 문구의 작업 흐름 비율을 일반화할 수는 없다.

[Evaluating and Benchmarking Jev](https://arxiv.org/html/2609.37647v1)는 버전 1.13.0을 데이터셋 37개, 요청 346,009건, API 비용 미화 10달러 미만으로 평가했으며 높은 분류·다국어 성능을 보고한다. 데이터셋, 프롬프트, 버전, 임계값 조건은 비공개 문의로의 적용을 제한한다. 공개 평가에서의 성공으로 학습 데이터에서 제외되었다고 확인할 수는 없다.

## 활용
{: id="10-일반적인-활용과-실패-양상"}

| 작업 | 구성 | 주요 실패 양상 |
|---|---|---|
| 라우팅 | 상호배타적 경로의 Choice | 미지 경로, 복합 의도, 불균등 비용 |
| 정책 분류 | 규칙별 Noul | 거짓 음성, 적대적 텍스트, 개정 |
| 검색 필터링 | 관련성 Noul 또는 순서형 Score | 재현율 손실, 긴 문서, 뒷받침 없는 근거 |
| 우선순위 | 관찰 가능한 수준의 Score | 순서형 손실, 순위 불안정, 대기 |
| 에이전트 중단 | 명시적 완료 조건의 Noul | 근거 누락, 조기 중단, 반복 |
| 비공개 처리 | 통제된 공개 가중치 서빙 | 보존, 로그, 하드웨어, 목표 언어 품질 |

도구 선택이 인자를 구성하거나 실행을 허가하는 것은 아니다. 인증, 인자 검증, 작업 흐름 규칙은 애플리케이션의 책임이다.

## 로컬 추론
{: id="11-재현-가능한-로컬-kev-실행-절차"}

고정한 인터페이스는 Python 3.12/3.13과 [uv](https://docs.astral.sh/uv/)를 쓴다. PyPI의 `kev`는 별개 프로젝트다. 다음 설치 예시는 하드웨어 실행 결과가 아니다.

```sh
git clone https://github.com/jaredpalmer/kev.git
cd kev
git checkout fc4a17e194bca35a48c57211392ec49ea54a94ac
uv sync --extra serve
uv run --extra serve python -m kev.serve \
  --run jaredpalmer/kev-4b@v1.0 --port 8009
```

Hub 태그 `v1.0`은 체크포인트 계열을 식별한다. 장기 재현에는 실제 커밋과 해시도 필요하다. 첫 실행은 기본 모델과 어댑터를 내려받는다. GPU 비교에서는 장치를 명시해야 알리지 않은 CPU 대체를 피할 수 있다. 한 상태와 여러 질문을 다음과 같이 제출한다.

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

선택지가 네 개이므로 신뢰도 변환에는 $$K=4$$를 쓴다. 로컬 Kev와 호스팅형 Jev는 모델 선택자, 인증, 제한, 개인정보 처리가 다르다([API](https://docs.typesafe.ai/api)). 스키마가 호환되어도 확률을 서로 바꿔 쓸 수는 없다. 재현 기록에는 리비전, 기준, 원시 확률, 측정 범위, 수용 여부, 나중에 확인한 레이블이 남아야 한다. 민감한 입력에는 보존 정책이 필요하고, 캐시 키에는 상태, 질문, 선택지 순서, 모델, 온도를 비롯한 모든 출력 영향 입력이 필요하다.

## 미세조정
{: id="12-평가를-오염시키지-않는-미세조정"}

업무 레이블과 독립적인 정답 부여는 작업의 모호함과 모델 오류를 구분한다. 대표성 있는 테스트 빈도나 명시적인 재가중이 중요하다. 학습은 가중치를 갱신하고, 개발은 체크포인트를 고르며, 보정은 온도·임계값을 적합하고, 별도 테스트는 최종 파이프라인을 평가한다. 고객·문서·시간별 분리는 누출을 막는다. 교차검증은 적합과 평가를 합치지 않고 레이블을 아낄 수 있다. 같은 생성법의 합성 테스트가 실제 입력 정확도를 입증하지는 않는다.

정답 인덱스 $$y_j$$에 대해 다음과 같다.

$$
\mathcal L_{\mathrm{CE}}(\theta)=-\frac1n\sum_j
\log p_\theta(y_j\mid x_j,q_j,C_j).
$$

LoRA는 $$A\in\mathbb R^{r\times d_{\mathrm{in}}}$$, $$B\in\mathbb R^{d_{\mathrm{out}}\times r}$$로 $$\Delta W=(\alpha/r)BA$$를 더해 $$d_{\mathrm{in}}d_{\mathrm{out}}$$ 대신 $$r(d_{\mathrm{in}}+d_{\mathrm{out}})$$개 매개변수를 학습한다. 백본 가중치, 활성값, 기울기, 최적화기 상태는 여전히 메모리를 쓰며, 27B의 전체 가중치 학습은 다른 조건이다. 호환되는 공개 체크포인트는 원래 백본 초기화가 버리는 학습된 헤드·어댑터를 유지한다([학습 지침](https://github.com/jaredpalmer/kev/blob/fc4a17e194bca35a48c57211392ec49ea54a94ac/README.md#by-hand), JSONL과 `--init_from`). 최종 보정과 위험·커버리지 평가는 망각을 드러내도록 새 영역과 보존한 일반 데이터를 모두 사용해야 한다. 레이블, 리비전, 점수 정의, 임계값, 하위 집단 수, 지연시간 조건도 고정해 남겨야 한다.

## 관련 모델
{: id="13-비슷한-목표를-가진-오픈소스-프로젝트"}

| 프로젝트 | 구조·범위 |
|---|---|
| [kev](https://github.com/jaredpalmer/kev) | 디코더 선택지 포인터 헤드와 타입 기반 서버 |
| [open-jev](https://github.com/nico-martin/open-jev) | 브라우저 TypeScript, ONNX/Transformers.js, WebGPU/WASM |
| [laya-decision-model](https://github.com/kalufinnle/laya-decision-model) | 다국어 인코더 계열 |
| [GLiNER2](https://github.com/fastino-ai/GLiNER2) | 스키마 기반 추출·분류와 Decide 체크포인트 |
| [typed-decisions](https://github.com/kotoba-lang/typed-decisions) | 여러 백본의 타입 기반 의사결정 |
| [openjev-rlcd](https://github.com/ZimmyGao/openjev-rlcd) | 독립적인 공개 RLCD 관련 학습법 |

브라우저 `open-jev`에 나열된 이전 Kev 체크포인트는 고정한 Qwen3.5/3.8 계열과 다르다. ONNX·인코더 경로에는 별도의 문맥·하드웨어 한계가 있다. 매개변수 수 외에 기본 모델, 토크나이저, 언어, 문맥, 라이선스, 리비전, 보정도 중요하다. 예제와 조정 예산을 맞추면 규칙, 고정 레이블 분류기, 레이블을 제한한 언어 모델을 상대로 정확도, 적정 점수, 수용 위험, 커버리지, 전체 자원을 비교할 수 있다.

## 참고문헌
{: id="참고-자료와-재현성의-한계"}

- [TypeSafe](https://docs.typesafe.ai/introduction), [API](https://docs.typesafe.ai/api), [Choice](https://docs.typesafe.ai/primitives/choice), [Noul](https://docs.typesafe.ai/primitives/noul), [Score](https://docs.typesafe.ai/primitives/score), [신뢰도](https://docs.typesafe.ai/confidence).
- [고정한 Kev 소스와 출시 문서](https://github.com/jaredpalmer/kev/tree/fc4a17e194bca35a48c57211392ec49ea54a94ac).
- [Guo 외, 확률 보정](https://proceedings.mlr.press/v70/guo17a.html).
- [Evaluating and Benchmarking Jev, v1](https://arxiv.org/html/2609.37647v1).
- [LLM-as-Jev](https://arxiv.org/abs/2610.02076), [독립적인 RLCD 연구](https://arxiv.org/abs/2609.38850).
