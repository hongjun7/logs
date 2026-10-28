---
layout: article
title: "온톨로지와 Agent"
subtitle: "온톨로지의 의미론과 문서 탐색, 에이전트 기반 설계를 비교한다."
tags: ["ontology", "knowledge-graphs", "information-theory", "language-models", "agents"]
lang: ko
translation_key: 2026-10-28-ontology-information-and-agent-design
original_url: /2026/10/28/ontology-information-and-agent-design.html
permalink: /ko/2026/10/28/ontology-information-and-agent-design.html
date: 2026-10-28 09:00:00 +0900
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-28
translated_at: 2026-10-29
---

온톨로지는 한 영역의 용어와 공리를 정의한다. 링크로 연결한 위키는 문서를 읽고 찾기 쉽게 정리한다. 같은 출처를 담더라도 의미를 정하고 정보에 접근하는 방식은 다르다. LLM은 두 표현을 만드는 데 모두 쓰이며, 효용은 과제와 검증 방법에 따라 달라진다.

## 온톨로지
{: id="1-온톨로지를-수학적으로-어떻게-정의하는가"}

Gruber는 온톨로지를 개념화의 명시적 명세로 정의한다. 영역을 기술할 용어와 의미를 정하는 것으로, 특정 논리나 파일 형식을 요구하지는 않는다. [Gruber, 1993](https://tomgruber.org/writing/ontolingua-kaj-1993/).

논리 기반 온톨로지는 다음과 같이 쓸 수 있다.

$$
\mathcal O=(\Sigma,T),\qquad K=T\cup A.
$$

$$\Sigma$$는 기호의 종류와 항수, $$T$$는 공리 집합, $$A$$는 개별 단언 집합이다. 둘을 합친 $$K$$가 지식베이스다. 한 문서에 스키마와 단언을 함께 담을 수도 있다. 이 표기는 논리 기반 온톨로지를 설명한다.

`Researcher`, `Person`, `authoredBy`, `paper1`, `alice`를 예로 들자. 객체만 다루는 기술논리 해석 $$\mathcal I=(\Delta^{\mathcal I},\cdot^{\mathcal I})$$에서 영역 $$\Delta^{\mathcal I}$$는 비어 있지 않다. 클래스는 집합, 객체 속성은 이항관계, 개체는 원소로 해석한다.

$$
\begin{aligned}
\mathrm{Researcher}^{\mathcal I}&\subseteq\Delta^{\mathcal I},\\
\mathrm{authoredBy}^{\mathcal I}&\subseteq\Delta^{\mathcal I}\times\Delta^{\mathcal I},\\
\mathrm{alice}^{\mathcal I}&\in\Delta^{\mathcal I}.
\end{aligned}
$$

OWL 2는 여기서 생략한 데이터 값과 데이터타입의 해석도 정의한다. [W3C, 2.2–2.3절](https://www.w3.org/TR/owl2-direct-semantics/).

$$T=\{\mathrm{Researcher}\sqsubseteq\mathrm{Person}\}$$, $$A=\{\mathrm{Researcher}(\mathrm{alice})\}$$라 하자. 하위 클래스 공리는 다음을 뜻한다.

$$
\mathrm{Researcher}^{\mathcal I}\subseteq\mathrm{Person}^{\mathcal I}.
$$

$$K$$의 공리와 단언을 만족하는 해석을 **모델**이라 한다. $$K$$에서 **함의**된다는 것은 모든 모델에서 참이라는 뜻이다.

$$
K\models\varphi\quad\Longleftrightarrow\quad
\text{every model of }K\text{ satisfies }\varphi.
$$

따라서 $$K\models\mathrm{Person}(\mathrm{alice})$$다. 주어진 문장에서 나온 결론이며, 현실의 Alice가 연구자인지는 외부 근거로 확인해야 한다.

## 의미론과 검증
{: id="2-논리가-보장하는-것과-보장하지-않는-것"}

OWL의 **개방세계 가정**에서는 단언이 없다는 이유만으로 그 부정을 결론 내리지 않는다. 저자 단언이 없다고 Alice가 논문을 쓰지 않았다는 뜻은 아니다. 이름이 달라도 같은 개체일 수 있어, 구별과 완전성에는 명시적인 가정이 필요하다. [W3C: OWL 2 Primer](https://www.w3.org/TR/owl-primer/).

정의역 공리는 속성 단언에서 타입을 추론한다. 타입이 없는 레코드를 반드시 거부하지는 않는다. **SHACL**은 지정한 RDF 그래프를 최소 개수·데이터타입 등의 제약으로 검사한다. 결과는 데이터 그래프, 제약, 추론 설정에 달려 있다. [W3C: SHACL](https://www.w3.org/TR/shacl/).

**일관성**은 적어도 하나의 모델이 있다는 뜻이며, 현실이나 의도한 의미와의 일치를 보장하지 않는다. 모순된 이론에는 모델이 없어 고전 논리에서는 모든 문장을 함의한다. 추론기는 일관성을 검사하지만 근거 없는 입력의 참·거짓을 확인해 주지는 않는다.

## 공통 어휘
{: id="3-문서나-그래프에-온톨로지를-더하는-이유"}

한 시스템의 `author`와 다른 시스템의 `creator`가 같은 뜻인지는 이름만으로 알 수 없다. 공통 어휘는 이 결정을 명시한다. Gruber의 이식성 문제도 표현 체계 간에 이런 의미를 공유하는 문제다. [Gruber, 1993](https://tomgruber.org/writing/ontolingua-kaj-1993/).

| 표현 | 연결이 나타내는 것 | 더 강한 해석에 필요한 것 |
| --- | --- | --- |
| Markdown 하이퍼링크 | 한 위치가 다른 위치를 가리킴 | 링크의 의미를 정하는 규약이나 해석기 |
| RDF 트리플 | 주어·술어·목적어에 관한 단언 | 어휘 정의와 선택한 함의 체계 |
| 형식 온톨로지 | 이름 있는 구성요소와 공리에 명시적 의미가 있음 | 올바른 모델링 가정, 데이터, 적합한 추론기 |

RDF는 그래프 데이터 모델과 직렬화를 구분한다. 검색 그래프가 공리 기반 온톨로지일 필요는 없으며, 온톨로지도 그래프 데이터베이스를 요구하지 않는다. [W3C: RDF 1.1 Concepts](https://www.w3.org/TR/rdf11-concepts/).

형식 의미론은 타입 공유, 데이터 통합, 추론, 선언한 제약의 해석에 쓰인다. 출처 문단을 찾는 일만으로 공리화가 필수인 것은 아니다.

## 정보량
{: id="4-정보량은-무엇을-뜻하는가"}

| 양 | 측정하는 것 | 입증하지 않는 것 |
| --- | --- | --- |
| 바이트·토크나이저 토큰 수 | 특정 인코딩에서의 길이 | 참·거짓, 유용한 의미, 근거 포괄성 |
| Shannon 엔트로피 | 확률분포 아래의 불확실성 | 기호와 과제를 연결하는 모델 없이 의미적 정확성 |
| 논리적 귀결 | 정해진 의미론 아래 공리에서 따라 나오는 것 | 세계에 대한 독립적인 관찰 |
| 검색·근거 재현율 | 필요한 근거가 읽기 모델에 도달하는 빈도 | 근거의 올바른 활용이나 온톨로지의 완전성 |

확률질량함수 $$p$$를 갖는 이산 변수 $$X$$의 엔트로피는 다음과 같다. 단위는 비트다.

$$
H(X)=-\sum_x p(x)\log_2p(x),\qquad 0\log_2 0:=0.
$$

파일 길이를 엔트로피라 부르려면 가능한 메시지의 분포가 필요하다. Shannon의 이론은 전달 문제와 의미를 구분한다. [Shannon, 1948](https://web.mit.edu/6.976/www/handout/shannon.pdf).

이산 변수와 유한한 조건부 답변 엔트로피를 가정하자. 정답 $$Y$$, 질문 $$Q$$, 표현 $$R$$의 조건부 상호정보량은 다음과 같다.

$$
I(Y;R\mid Q)=H(Y\mid Q)-H(Y\mid R,Q).
$$

결합분포 아래의 평균 불확실성 감소량이다. F1은 이와 다른 양이며 비트 단위 점수가 아니다.

## 탐색
{: id="5-같은-출처-다른-접근-경로"}

Karpathy의 **LLM Wiki**는 원출처, Markdown 위키, 지침을 둔다. 자료가 들어오면 페이지와 링크를 갱신하고, 질문에는 색인·검색으로 접근하며, 별도로 관리 상태를 점검한다. 통제된 온톨로지 비교를 제시한 논문이 아닌 비공식 구상이다. [Karpathy, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

원출처를 $$D$$, 질문을 $$Q$$, 정답을 $$Y$$, 모델 파라미터와 외부 규칙을 포함한 배경 지식을 $$B$$라 하자. $$D,B$$에서 표현 $$R$$을, $$R,Q,B$$에서 문맥 $$C$$를 만든다. 추가적인 정답 관련 근거가 들어오지 않는 조건은 $$I(Y;R\mid D,Q,B)=0$$, $$I(Y;C\mid R,Q,B)=0$$이다. 데이터 처리 부등식은 다음과 같다.

$$
I(Y;C\mid Q,B)\le I(Y;R\mid Q,B)\le I(Y;D\mid Q,B).
$$

$$I(Y;R\mid D,Q,B)=0$$과 연쇄법칙을 적용하면

$$
I(Y;D\mid Q,B)=I(Y;R\mid Q,B)+I(Y;D\mid R,Q,B).
$$

마지막 항이 음수가 아니므로 두 번째 부등식이 성립한다. 검색에도 같은 논리를 적용하면 첫 번째를 얻는다. [Duchi, 2.1절](https://web.stanford.edu/class/stats311/lecture-notes.pdf).

배경 지식을 조건으로 두는 것이 중요하다. 사전학습 가중치나 외부 데이터베이스는 문서에 없는 사실을 제공할 수 있다.

$$R=f(D)$$, $$D=h(R)$$인 가역 인코딩은 정보를 보존한다. 같은 공리를 Markdown과 무손실 Turtle에 담으면 같은 정보를 유지할 수 있다. 요약은 세부사항을 버릴 수 있다. 원출처를 보관해도 검색 문맥에서 필요한 근거가 빠질 수 있다.

색인은 제한된 문맥·지연시간·도구 예산에서 접근할 수 있는 근거를 바꾼다. 원출처 정보량의 증가와는 다르다. 그래프 경로나 Markdown 링크를 증명·타입 관계로 쓰려면 그에 맞는 해석이 필요하다.

## 논리적 귀결
{: id="6-유한한-예시-제약과-이미-따라-나오는-문장"}

유한한 예시로 명제변수 $$P,Q$$를 두자.

| $$P$$ | $$Q$$ | $$P\Rightarrow Q$$ |
| --- | --- | --- |
| 거짓 | 거짓 | 참 |
| 거짓 | 참 | 참 |
| 참 | 거짓 | 거짓 |
| 참 | 참 | 참 |

공리 $$P\Rightarrow Q$$는 네 배정 중 세 개를 허용한다. 균등한 사전분포에서 공리를 조건으로 두면 엔트로피가 $$2$$에서 $$\log_2 3$$비트로 줄어든다.

$$
2-\log_2 3=\log_2(4/3)\approx0.415\text{ bits}.
$$

$$P$$를 더하면 하나의 배정만 남아 $$Q$$가 함의된다. 이미 함의된 $$Q$$를 저장해도 모델은 더 줄지 않는다.

$$
T\models\varphi\quad\Longrightarrow\quad
\operatorname{Mod}(T)=\operatorname{Mod}(T\cup\{\varphi\}).
$$

귀결을 미리 저장하면 접근은 쉬워져도 제약은 늘지 않는다. 함의되지 않는 공리는 가정이나 오류를 더할 수 있다. 임의의 OWL 모델 집합은 유한하거나 균등분포를 갖는다는 보장이 없어 이 예시처럼 모델 수를 엔트로피로 바꿀 수는 없다.

## 검색 실험
{: id="7-문서-탐색-연구는-실제로-무엇을-측정했는가"}

검색 증강 생성(RAG)은 언어모델이 참고할 출처를 검색한다. BM25는 단어 일치, 밀집 검색은 벡터 표현을 쓰고, 에이전트 검색은 제어 모델이 후속 단계를 선택한다. F1은 각 연구의 평가 단위에서 정밀도와 재현율을 결합한다. 아래 수치는 저자가 보고한 값이며 별도로 재현하지 않았다.

**Corpus2Skill**은 탐색 파일과 요약을 구축한 뒤 원문서를 검색한다. WixQA 실험은 모든 방식의 답변 모델을 Claude Sonnet 4.6으로 고정했다. [Sun 등, 표 1](https://arxiv.org/html/2604.14572v4).

| WixQA 시스템 | 토큰 F1 | 보고된 질의당 서비스 비용, 달러 |
| --- | --- | --- |
| Dense | 0.364 | 0.007 |
| RAPTOR | 0.398 | 0.012 |
| Agentic | 0.378 | 0.082 |
| Corpus2Skill | 0.456 | 0.153 |

WixQA는 문서 6,221개와 전문가 질문 200개로 구성된다. 비용은 프롬프트 캐싱을 반영한 서비스 비용이며 사전 구축은 제외한다. WixQA와 RAGBench 부분집합 열 개에서 각 최강 기준선 대비 유의한 승리 5개, 동률 3개, 패배 3개를 보고했다. Markdown 문법만의 효과를 분리한 비교는 아니다.

**HippoRAG 2**의 일곱 데이터셋에서 보고한 집계 답변 F1은 **59.8**, NV-Embed-v2는 **57.0**이다. 위 표와 달리 0–100 척도다. MuSiQue 시간 실험에서는 색인 구축이 **99.5분 대 12.1분**, 질의당 QA가 **1.2초 대 0.3초**였다. [Gutiérrez 등, 표 2–3·부록 F](https://proceedings.mlr.press/v267/gutierrez25a.html).

**GraphRAG**는 추출 그래프와 커뮤니티 요약으로 자료를 종합한다. 벡터 RAG 대비 C0–C3 포괄성 점수는 팟캐스트 **71.92–78.96%**, 뉴스 **71.76–79.44%**다. 승리·동률·패배에 100·50·0을 부여한 LLM 선호 점수다. 독립 정답에 대한 정확도나 OWL 보장이 아니다. [Edge 등, 표 6](https://arxiv.org/html/2404.16130v2).

사전공개 논문 **BM25 Wins at Scale**은 읽기 모델과 질문 500개를 고정했다. 문서 511,959개, 약 6억 100만 토큰에서 원시 트리 에이전트는 **30.7**, BM25는 **50.5**였다. 정답성으로 완전성을 제한한 종합 점수(%)이며 에이전트 호출 예산은 80회다. 구축된 위키가 없어 LLM Wiki나 Corpus2Skill의 직접 평가는 아니다. [2026 사전공개 논문](https://arxiv.org/html/2607.26497v3).

연구마다 읽기 모델, 과제, 예산, 채점이 다르다. 여기서 검토한 연구에는 동일 조건에서 형식 온톨로지 의미론과 Markdown 탐색만 바꾼 실험이 없다.

## 온톨로지 설계
{: id="8-전문가-설계에서-llm-보조-작업으로"}

**METHONTOLOGY**는 점진적인 프로토타입으로 요구사항, 개념화, 구현, 평가, 문서화, 유지보수를 다룬다. **NeOn**은 재사용·재공학 시나리오를 더한다. LLM 작업 흐름은 이 기존 과정의 일부를 자동화한다. [Fernández-López 등, 1997](https://cdn.aaai.org/Symposia/Spring/1997/SS-97-06/SS97-06-005.pdf), [Suárez-Figueroa 등, 2015](https://doi.org/10.3233/AO-150145).

**역량 질문(CQ)**은 “저자 중 연구자는 누구인가?”처럼 필요한 능력을 명시한다. 합의한 의미, 대표 데이터, 실행 가능한 평가가 필요하다. 질문과 정답을 모두 생성하는 것만으로 완전성을 독립적으로 검증할 수는 없다.

| 접근법 | 대표 연구 | 자동화하는 부분 | 근거의 경계 |
| --- | --- | --- | --- |
| 이해관계자와 대화 | OntoChat, ESWC 2024 | 사용자 이야기, CQ 도출·시험 | 사람의 요구와 피드백을 유지 |
| 구조화된 프롬프트·패턴 | Ontogenia, ESWC 2025 | CQ와 패턴에서 모듈 생성·재검토 | 다중 에이전트가 필수는 아님 |
| 학습을 통한 온톨로지 추출 | OLLM, NeurIPS 2024 | 문서별 분류체계 부분그래프 예측·통합·가지치기 | 개념과 분류관계에 한정, 임의 OWL 설계가 아님 |
| 도구 기반 생성·수정 | Extended NeOn-GPT, 2026 | 재사용, 생성, 문법·추론기·결함 점검과 수정 | 단계별 파이프라인이 곧 다중 에이전트 비교는 아님 |
| 역할에 따른 협업 | LLM4ACOE, 2025; 4역할 연구, 2026 | 전문가·계획·코딩·QA 역할의 분리 또는 모의 | 에이전트 수와 계획 방식의 효과가 섞일 수 있음 |
| 근거 기반 확장 | OntoCodex, 2026 | 출처와 용어 도구로 기존 온톨로지 확장 | 특정 영역의 확장이며 무제한 자율 설계가 아님 |

[OntoChat](https://arxiv.org/html/2403.05921v1)은 음악 사례에서 지원·미지원 CQ를 구분하는 시험 56개의 정확도 **87.5%**를 보고했다. 시간 절약은 사용자 피드백이며 소요시간 측정값은 아니다.

[Ontogenia](https://arxiv.org/html/2503.05388v1)는 독립된 숙련 평가자 두 명과 온톨로지 10개·CQ 100개를 평가했다. o1-preview의 Music/Theatre/Hospital 적합도는 Ontogenia **0.96/1.0/1.0**, Memoryless CQbyCQ **0.9/0.73/0.73**이다. 표 3 제목은 “%”지만 원래 값을 그대로 적었다. 정의역·치역 오류와 중복은 남았다.

[OLLM](https://proceedings.neurips.cc/paper_files/paper/2024/hash/9e89f068a62f6858c661a8abecf5bb0a-Abstract-Conference.html)의 Wikipedia Graph F1은 **0.644**, 일반 미세조정은 **0.588**이다. 그래프 유사도이며 참인 공리 비율이나 다중 에이전트 효과가 아니다. 사전학습 오염 여부도 해결되지 않았다.

## 에이전트 실험
{: id="9-에이전트의-효용-검사에-따라-답이-달라진다"}

| 연구와 범위 | 관찰한 비교·결과 | 아직 입증하지 못한 것 |
| --- | --- | --- |
| Extended NeOn-GPT: 모델 4개 × 영역 4개 | 모순된 온톨로지 **검증·수정 전 7/16 → 후 0/16** | 사실적 완전성, 반복 간 변동; 모델·영역당 생성 1회 |
| LLM4ACOE: 산불 수색·구조 문서 | 선택한 설정에서 **CQ 18개 중 14개** 대응 | 일반 영역 정확도, 에이전트 추가 효과의 분리 |
| 4역할 연구: 합성 보험 계약 2개 | 처리한 SPARQL CQ 포괄성 **0.6304 → 0.6196**, **0.4027 → 0.4383** | 모든 조건의 개선, 광범위한 실제 문서 일반화 |
| OntoCodex: 기존 생의학 온톨로지, 질환 5개 | 영상·진단 절차 영역 평균 F1 **0.786 → 0.946**; 약물 영역 **0.944 → 0.927** | 모든 추출 과제의 개선이나 임상적 효과 |

[Extended NeOn-GPT](https://www.semantic-web-journal.net/system/files/swj4014.pdf)는 파싱, OWL 추론, 결함 점검, 수정을 결합한다. 통과는 검사한 속성을 보장하며 사실적 완전성을 뜻하지는 않는다.

[LLM4ACOE (2025)](https://doi.org/10.1017/S026988892510009X)는 검색과 함께 지식공학자·도메인 전문가·지식 작업자를 모의한다. 무관한 개념과 가상의 import가 일부 출력에 들어왔고, 검색 자료를 늘려도 포괄성이 일관되게 좋아지지는 않았다.

[4역할 연구](https://arxiv.org/html/2604.23090v1)는 도메인 전문가 → 관리자 → 코더 → QA를 사용한다. 두 합성 계약의 LLM 구조 점수와 RAG 포괄성은 좋아졌지만 SPARQL 결과는 혼재한다. 포괄성은 LLM 판정이 관여한 평균 CQ 점수이며 이진 정답률이 아니다.

[OntoCodex (2026)](https://www.nature.com/articles/s44401-026-00117-9)은 에이전트 다섯 개로 확장한다. 표는 기준 ChatGPT-4o와의 영역별 평균 F1 비교다. 영상·진단 절차 신뢰구간이 넓고 겹쳐 점추정값만으로 유의성을 주장할 수 없다. 검사실 검사 코드 매핑은 **60% → 20%**로 낮아졌고 사람의 의미 검토도 유지한다.

## 활용
{: id="10-현재-단계의-활용-조건과-평가-기준"}

| 필요한 동작 | 관련 수단 | 수용 여부를 판단할 근거 |
| --- | --- | --- |
| 계속 바뀌는 문서를 읽고 종합 | 원출처를 보존한 검색·탐색, 보조 자료로 쓰는 요약 | 답변 정확성, 근거 재현율, 출처의 뒷받침, 갱신 동작 |
| 데이터셋 간 정밀한 타입·관계 공유 | 명시적 어휘, 매핑, 적절한 공리 | 매핑 검토, 함의 시험, 독립적으로 정한 CQ |
| 필수 필드가 없는 레코드 거부 | SHACL 등의 명시적 검증 제약 | 고정한 설정에서 긍정·부정 시험 데이터 검증 |
| 온톨로지 초안·확장 자동화 | 근거 기반 생성, 제한된 모듈, 실행 가능한 검사 | 문법, 일관성, 개념 검토, CQ 포괄성, 후속 과제 시험 |

원출처·위키를 유지하면서 의미 공유가 필요한 관계에 형식 어휘를 더할 수 있다. 생성한 요약·매핑·공리는 출처와 버전을 가진 파생 자료다. 함께 쓸 수 있는 구성이지 입증된 최적해는 아니다.

표현의 의미·일관성·포괄성, 검색 근거, 답변의 정확성·뒷받침을 따로 평가한다. CQ 포괄성은 답변 정확도가 아니며, LLM 판정은 독립 주석과 대조해 검증해야 한다.

비교에서는 문서 버전, 독립적인 질문·정답·근거, 읽기 모델, 예산을 고정한다. 에이전트 설계 비교도 모델과 요구사항을 맞춰 직접 생성·구조화된 단일 에이전트·역할 분리를 비교한다. 반복 실행과 근거 누락·충돌 사례로 변동과 실패를 확인한다.

비용에는 구축, 갱신, 서비스, 도구 호출, 재시도, 지연시간, 사람의 수정이 포함된다. $$N>0$$개 질의에 초기 비용을 나누면 다음과 같다.

$$
\overline C=\frac{C_{\mathrm{build}}+C_{\mathrm{updates}}}{N}
+\frac1N\sum_{i=1}^{N}C_{\mathrm{serve},i}.
$$

## 결론
{: id="11-결론과-제언"}

온톨로지는 의미와 귀결을 정하고, 탐색은 접근 경로를 조직한다. 특정 확장자가 필수는 아니며 같은 출처를 함께 활용할 수 있다.

무손실 인코딩은 정보를 보존한다. 요약·검색은 세부사항을 놓칠 수 있고, 귀결의 저장은 독립 제약을 늘리지 않으면서 접근을 바꾼다. 정보량 비교에는 확률모델과 외부 지식의 명시가 필요하다.

LLM 연구는 요구사항, 모듈, 분류체계, 수정, 확장의 보조 가능성을 보여 준다. 오류와 혼재한 결과는 범위를 정한 자동화·시험·의미 검토를 뒷받침하며 전문가의 일괄 대체를 입증하지는 않는다.

정의된 추론과 의미 공유에는 형식 의미론을 쓰고, 탐색은 근거 접근과 근거에 기반한 답변으로 평가한다. 출처와 전체 비용을 남기고 목표 규모에서 필요한 동작을 검증해야 한다.

## 참고문헌
{: id="참고문헌과-읽는-순서"}

1. Gruber (1993), [A Translation Approach to Portable Ontology Specifications](https://tomgruber.org/writing/ontolingua-kaj-1993/).
2. W3C 권고: [OWL 2 Direct Semantics](https://www.w3.org/TR/owl2-direct-semantics/), [OWL 2 Primer](https://www.w3.org/TR/owl-primer/), [RDF 1.1 Concepts](https://www.w3.org/TR/rdf11-concepts/), [SHACL](https://www.w3.org/TR/shacl/).
3. Shannon (1948), [A Mathematical Theory of Communication](https://web.mit.edu/6.976/www/handout/shannon.pdf); Duchi (2023), [Statistics and Information Theory, 2장](https://web.stanford.edu/class/stats311/lecture-notes.pdf).
4. Fernández-López 등 (1997), [METHONTOLOGY](https://cdn.aaai.org/Symposia/Spring/1997/SS-97-06/SS97-06-005.pdf); Suárez-Figueroa 등 (2015), [NeOn Methodology framework](https://doi.org/10.3233/AO-150145).
5. Karpathy (2026), [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), 비공식 설계안.
6. Sun 등 (2026), [Corpus2Skill](https://aclanthology.org/2026.findings-emnlp.172/), Findings EMNLP; 수치 설명은 [v4](https://arxiv.org/html/2604.14572v4) 기준.
7. Gutiérrez 등 (2025), [From RAG to Memory: Non-Parametric Continual Learning for Large Language Models](https://proceedings.mlr.press/v267/gutierrez25a.html), ICML; HippoRAG 2.
8. Edge 등 (2024/2025), [From Local to Global: A Graph RAG Approach to Query-Focused Summarization](https://arxiv.org/html/2404.16130v2).
9. [BM25 Wins at Scale](https://arxiv.org/html/2607.26497v3) (2026), 사전공개 논문.
10. Zhang 등 (2024), [OntoChat](https://arxiv.org/html/2403.05921v1), ESWC.
11. Lippolis 등 (2025), [Ontology Generation using Large Language Models](https://arxiv.org/html/2503.05388v1), ESWC; Ontogenia.
12. Lo 등 (2024), [End-to-End Ontology Learning with Large Language Models](https://proceedings.neurips.cc/paper_files/paper/2024/hash/9e89f068a62f6858c661a8abecf5bb0a-Abstract-Conference.html), NeurIPS; OLLM.
13. Fathallah 등 (2026), [Extended NeOn-GPT](https://doi.org/10.1177/22104968261453138), 게재 승인 [원고](https://www.semantic-web-journal.net/system/files/swj4014.pdf).
14. Soularidis 등 (2025), [Automating agentic collaborative ontology engineering](https://doi.org/10.1017/S026988892510009X), 『The Knowledge Engineering Review』; LLM4ACOE.
15. Talukder 등 (2026), [Towards Automated Ontology Generation from Unstructured Text](https://arxiv.org/html/2604.23090v1), ESWC 워크숍 원고.
16. Feng 등 (2026), [OntoCodex](https://www.nature.com/articles/s44401-026-00117-9), 『npj Health Systems』.
