---
layout: article
lang: ko
translation_key: 2024-09-18-Towards-Better-Evaluation-for-Dynamic-Link-Prediction
date: 2024-09-18
permalink: /ko/2024/09/18/Towards-Better-Evaluation-for-Dynamic-Link-Prediction.html
original_url: /2024/09/18/Towards-Better-Evaluation-for-Dynamic-Link-Prediction.html
translated_at: 2026-10-29
title: "동적 링크 예측"
tags: ["graphs", "evaluation", "temporal-graphs"]
subtitle: "시간순 상태와 음성 샘플링으로 순위 평가의 의미를 정한다."
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-11
---

동적 링크 예측은 시간순 이력으로 미래 상호작용을 추정하거나 끝점의 순위를 매긴다. 관측 구간·후보 집합·음성 샘플러가 과제를 정한다. 쉬운 음성 샘플에서는 간선 암기가 예측처럼 보일 수 있다.

## 사건과 예측 대상
{: id="1-사건은-정적-간선-집합과-다르다"}

시간 그래프는 다음과 같은 사건을 포함한다.

$$
\mathcal E=\{(u_i,v_i,t_i,x_i)\}_{i=1}^{m},\qquad t_1\le\cdots\le t_m,
$$

$$x_i$$는 선택적인 사건 속성이다. 다른 시각의 같은 $$(u,v)$$ 쌍도 별개 사건이며, 정적 간선 집합은 그 반복을 잃는다.

시각 $$t$$에는 이력 $$\mathcal H_{<t}$$로 다음과 같은 대상을 예측한다.

$$
\Pr\big((u,v)\text{ interacts in }[t,t+\Delta)\mid\mathcal H_{<t}\big).
$$

출발 노드와 사건 시각을 정해 도착 노드의 순위를 매길 수도 있다. 사건 확률에는 시간 범위 $$\Delta$$와 후보 쌍 분포가 필요하며, 조건부 순위가 보정된 확률일 필요는 없다.

## 시간순 상태
{: id="2-시간순-분할과-시점에-맞는-특징"}

학습·검증·테스트는 시간순 구간을 사용한다. 시각 $$t$$의 임베딩·이웃·정규화·학습된 전처리는 허용된 이전 정보만 사용할 수 있다.

고정 이력 평가는 테스트 기간 내내 테스트 시작 전의 이력을 유지한다. 온라인 재생은 테스트 사건을 예측한 뒤 이력에 넣는다. 배포 상황이 다르며 EdgeBank와 신경망 점수도 달라진다.

동시 사건을 파일 안에 먼저 기록했다고 먼저 관측한 것은 아니다. 타임스탬프 배치로 묶어 엄격히 이전의 이력에서 모두 예측한 뒤 함께 갱신한다. 배치 안에서 먼저 갱신하면 이용할 수 없던 정보가 노출된다.

## 새로운 쌍과 노드
{: id="3-새로운-간선과-새로운-노드는-다르다"}

끝점 쌍 집합 $$E_{\mathrm{train}}$$과 $$E_{\mathrm{test}}$$에 대해

$$
E_{\mathrm{test}}\cap E_{\mathrm{train}}
$$

은 반복 쌍을, $$E_{\mathrm{test}}\setminus E_{\mathrm{train}}$$는 새 쌍을 포함한다. 새 쌍도 익숙한 노드를 연결할 수 있다.

노드 집합 $$V_{\mathrm{train}}$$과 $$V_{\mathrm{test}}$$는 다른 분할을 정한다. $$V_{\mathrm{test}}\setminus V_{\mathrm{train}}$$에 연결된 간선은 새 노드 일반화를 시험한다. 벤치마크의 “귀납적 음성 샘플링”에는 해당 절차의 정의가 적용된다.

타임스탬프별 쌍 $$E_t$$와 이전 쌍 $$E_{<t}=\bigcup_{s<t}E_s$$에 대해 새로운 쌍의 비율은 다음과 같다.

$$
\nu_t=\frac{\vert E_t\setminus E_{<t}\vert }{\vert E_t\vert },\qquad \vert E_t\vert >0.
$$

분모는 사건 레코드 수가 아닌 해당 시각의 고유 쌍 수다. 반복 사건 수로 가중하면 다른 출현 비율이 된다.

## 음성 샘플링
{: id="4-음성-샘플링은-무엇을-바꾸는가"}

관측하지 못한 후보가 불가능하거나 영원히 없다는 뜻은 아니다. 누락·지연 관측은 다른 예측 대상에서 거짓 음성이 될 수 있다.

희소 그래프의 무작위 도착 노드는 쉬운 음성이 되기 쉽다. 과거 음성은 이전에 관측했지만 현재 양성 배치에 없는 쌍을 쓰며, 학습에 없던 쌍을 쓰는 절차도 있다. 어떤 쌍을 음성 후보로 제시하는지에 따라 분류기가 풀어야 할 문제가 달라지므로 모델 순위와 암기의 이점도 바뀐다. [Poursafaei 외, 2022](https://proceedings.neurips.cc/paper_files/paper/2022/hash/d49042a5d49818711c401d34172f9900-Abstract-Datasets_and_Benchmarks.html).

이진 점수는 샘플링된 분포에 적합된다. 클래스별 특징 분포를 유지하며 사전확률만 바뀐다면 사후 오즈는 다음을 따른다.

$$
\frac{p_{\mathrm{deploy}}(1\mid x)}{1-p_{\mathrm{deploy}}(1\mid x)}
=
\frac{p_{\mathrm{sample}}(1\mid x)}{1-p_{\mathrm{sample}}(1\mid x)}
\frac{\pi_{\mathrm{deploy}}/(1-\pi_{\mathrm{deploy}})}{\pi_{\mathrm{sample}}/(1-\pi_{\mathrm{sample}})}.
$$

어려운 음성이 조건부 분포까지 바꾸면 사전확률 보정만으로 배포 확률을 얻을 수 없다.

## EdgeBank
{: id="5-구조가-투명한-기준선-edgebank"}

무한 기억 EdgeBank는 과거 포함 여부에 점수를 준다.

$$
s_t(u,v)=\mathbf1\{(u,v)\in E_{<t}\}.
$$

윈도 버전은 $$[t-w,t)$$를 유지하고 $$w$$를 검증 데이터로 고른다. 해시 포함 확인은 기대 시간 $$O(1)$$, 저장은 사건 수가 아닌 고유 쌍에 대해 $$O(\vert E_{<t}\vert )$$이다.

이 1비트 규칙은 매개변수 적합 없이 반복 양성과 미관측 음성을 구분한다. 과거 음성이 이 구분을 어렵게 하므로 EdgeBank는 샘플러 난도를 드러낸다.

온라인 재생은 다음 순서를 따른다.

```text
for each timestamp batch:
    score positives and fixed negatives from earlier history
    record metrics
    add the current positive batch to history, if the protocol permits updates
```

현재 양성을 추가한 뒤 점수를 매기면 정답이 누출된다.

## 순위 지표
{: id="6-순위-지표와-후보-집합"}

양성 점수 $$s^+$$와 $$K$$개 음성 점수 $$s_j^-$$의 비관적 순위는 다음과 같다.

$$
r=1+\sum_{j=1}^{K}\mathbf1\{s_j^-\ge s^+\}.
$$

동점이 없으면 일반 순위다. 낙관적 순위는 엄격히 높은 음성만 세며, 비관적·평균 관례는 동점을 다르게 처리한다. 사건 $$n$$개에 대해 다음과 같다.

$$
\mathrm{MRR}=\frac1n\sum_i\frac1{r_i},\qquad
\mathrm{Hits@}k=\frac1n\sum_i\mathbf1\{r_i\le k\}.
$$

후보 수나 난도를 높이면 같은 점수 함수에서도 지표가 낮아질 수 있다. 음성 하나를 쓴 MRR과 수백 개를 쓴 MRR은 다른 시험이다.

AUROC는 쌍별 점수 순서를 측정하며 평균 정밀도는 양성 비율에도 크게 의존한다. 샘플러·후보 수·클래스 비율·동점·집계가 결과를 정한다. 출발 노드별 매크로 평균은 각 출발 노드에 같은 비중을 두고 사건별 마이크로 평균은 사건 수로 가중한다. 활동량이 치우치면 해석도 달라진다.

## 벤치마크 절차
{: id="7-최근-벤치마크의-평가-관행"}

[Temporal Graph Benchmark](https://arxiv.org/abs/2307.01026)는 [저장소](https://github.com/shenyangHuang/TGB)에서 데이터별 음성과 평가기를 제공한다. 이를 유지해야 리더보드와 비교할 수 있으며, 배포용 변형은 별도 평가가 된다.

데이터 버전, 사건 순서, 음성 파일 체크섬, 설정, 시드, 초기화, 검증 선택이 재현성을 정한다. 관측 이력을 맞춰 EdgeBank·정적·시간 모델을 비교하고, 표본이 충분하면 새 쌍·반복 쌍·새 노드를 나누어 평가한다.

재생 처리량, 온라인 지연, 메모리는 예측 품질을 보완한다. 순환 상태의 이점이 제한된 기기의 자원 범위를 넘을 수 있다.

## 실패 양상
{: id="8-흔한-실패-사례"}

전체 그래프 임베딩은 시간 분할을 넘어 정보를 누출할 수 있다. 동시 양성은 유효한 음성이 아니다. 높은 AUC가 확률 보정을 뜻하지 않으며, 한 네트워크가 다른 사건 과정의 일반화를 입증하지도 않는다.

## 참고문헌
{: id="참고문헌"}

- [Towards Better Evaluation for Dynamic Link Prediction, NeurIPS 2022](https://proceedings.neurips.cc/paper_files/paper/2022/hash/d49042a5d49818711c401d34172f9900-Abstract-Datasets_and_Benchmarks.html).
- [DGB와 EdgeBank 구현](https://github.com/fpour/DGB).
- [TGB 논문](https://arxiv.org/abs/2307.01026)과 [코드](https://github.com/shenyangHuang/TGB).
- [Temporal Graph Networks](https://arxiv.org/abs/2006.10637), [JODIE](https://arxiv.org/abs/1908.01207), [CAWN](https://arxiv.org/abs/2101.05974).
