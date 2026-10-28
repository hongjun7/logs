---
layout: article
lang: ko
translation_key: 2023-09-30-rust-cp-helper
date: 2023-09-30
permalink: /ko/2023/09/30/rust-cp-helper.html
original_url: /2023/09/30/rust-cp-helper.html
translated_at: 2026-10-29
title: "Rust CP Helper"
tags: ["engineering", "rust", "algorithms"]
subtitle: "알고리즘과 소유권을 바탕으로 Rust 대회 환경을 구성한다."
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-11
---

Rust 컴파일러는 소유권과 수명에 관한 여러 오류를 잡아낸다. 알고리즘의 정확성에는 여전히 불변식과 수치 범위의 증명이 필요하다. 대회 도구를 더하기 전에 작은 단일 파일 풀이를 채점 서버의 도구 환경으로 검사하면 신뢰할 수 있는 출발점이 된다.

## 복잡도와 정수 범위
{: id="1-언어보다-알고리즘을-먼저-고른다"}

입력 크기가 $$n$$일 때 $$O(n\log n)$$은 충분히 큰 $$n$$에서 상수 배를 제외한 증가율의 상한이다. 실행 시간을 뜻하지는 않는다. 작은 입력에서는 메모리를 반복 할당하는 $$O(n)$$ 구현이 $$O(n\log n)$$ 구현보다 느릴 수 있다. 상수 배를 줄여도 $$O(n^2)$$ 알고리즘이 거의 선형이 되지는 않는다.

$$n=200{,}000$$이면 이중 반복문은 약 $$4\times10^{10}$$회 반복한다. 정렬에는 비교 연산에 해당하는 작업이 대략 $$n\log_2 n\approx3.52\times10^6$$회 필요하다. Rust나 CPU의 측정값이 아니라 연산량 추정치다.

절댓값이 $$B$$ 이하인 값 $$n$$개를 더하면

$$
\left\vert \sum_{i=1}^{n}a_i\right\vert \le nB.
$$

$$n\le2\times10^5$$이고 $$B\le10^9$$이면 합은 $$2\times10^{14}$$까지 커진다. `i64`에는 들어가지만 `i32`에는 들어가지 않는다. 부호 있는 $$b$$비트 정수의 범위는 $$[-2^{b-1},2^{b-1}-1]$$이다. 중간 곱도 범위를 증명해야 한다. 두 `i64`를 곱한 뒤 형을 바꿔도 이미 발생한 오버플로는 되돌리지 못한다.

## 단일 파일 풀이
{: id="2-작지만-완전한-시작-프로그램"}

이 프로그램은 부호 있는 정수 $$n$$개를 읽어 합을 출력한다. 입력은 공백으로 구분한 유효한 정수이며 $$n\le200{,}000$$과 $$\vert a_i\vert \le10^9$$를 만족한다.

```rust
use std::io::{self, Read};

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut it = input.split_whitespace();
    let n: usize = it.next().unwrap().parse().unwrap();
    let mut sum: i64 = 0;
    for _ in 0..n {
        let x: i64 = it.next().unwrap().parse().unwrap();
        sum += x;
    }
    println!("{sum}");
}
```

입력이 $$L$$바이트이면 문자열에 $$O(L)$$ 메모리가 필요하다. 일반적인 고정 폭 정수 모델에서 파싱 작업량도 $$O(L)$$이다. EOF까지 읽는 방식은 비대화형 문제에 적합하다. 대화형 채점은 입력을 순차적으로 읽고 출력을 플러시해야 한다.

컴파일 명령의 예는 다음과 같다.

```sh
rustc --edition=2021 -O main.rs -o main
./main < input.txt
```

에디션 2021은 예시다. 에디션, 컴파일러 버전, 크레이트는 채점 서버의 요구에 맞아야 한다. 표준 알고리즘에는 안정 버전 Rust로 충분하며, 의존성이 명시적으로 요구할 때 nightly가 필요하다. 최적화 옵션은 실행 방식을 바꾸지만 정확성을 증명하지는 않는다.

## 소유권과 그래프 저장
{: id="3-안전성이-보장하는-것과-보장하지-않는-것"}

Safe Rust는 광범위한 메모리 오용을 막는다. 잘못된 점화식, 범위 초과 패닉, 교착 상태, 산술 오류는 여전히 가능하다. 디버그의 오버플로 검사와 릴리스의 기본 래핑 동작이 다르므로, 검출이 필요하면 명시적인 검사 산술을 쓴다. [Rust 정수 오버플로](https://doc.rust-lang.org/book/ch03-02-data-types.html).

`Vec<T>`는 할당한 메모리를 소유한다. `&T`는 공유 읽기를, `&mut T`는 그 수명 동안 배타적인 접근을 허용한다. 인덱스를 저장하면 벡터가 커질 때 참조를 유지하는 문제를 피할 수 있다. 재할당으로 원소가 이동할 수 있기 때문에, 살아 있는 참조를 둔 채 원소를 추가하면 대여 충돌이 생긴다.

`Vec<Vec<usize>>`는 단순한 인접 리스트다. 압축 희소 행 표현은 연속된 이웃 배열 하나와 $$n+1$$개의 오프셋을 사용한다. 정점 $$n$$개와 방향 간선 $$m$$개의 저장 공간은 $$O(n+m)$$이다. 지역성의 이득은 실제 순회 방식에 달려 있다.

## 너비 우선 탐색
{: id="4-bfs의-동작을-증명한다"}

가중치 없는 그래프 $$G=(V,E)$$와 시작점 $$s$$에서 BFS는 $$s$$부터 도달 가능한 각 정점까지의 최소 간선 수를 구한다. `dist[v] = None`은 미발견 상태를 뜻하며, FIFO 큐에는 발견했지만 아직 이웃을 확장하지 않은 정점이 들어간다.

```rust
use std::collections::VecDeque;

fn bfs(graph: &[Vec<usize>], source: usize) -> Vec<Option<usize>> {
    let mut dist = vec![None; graph.len()];
    let mut queue = VecDeque::new();
    dist[source] = Some(0);
    queue.push_back(source);
    while let Some(v) = queue.pop_front() {
        let next = dist[v].unwrap() + 1;
        for &u in &graph[v] {
            if dist[u].is_none() {
                dist[u] = Some(next);
                queue.push_back(u);
            }
        }
    }
    dist
}
```

정점은 거리가 줄어들지 않는 순서로 큐에서 나온다. 시작점의 거리는 0이다. 최단 거리가 $$d$$인 $$v$$를 꺼내면 미발견 이웃에는 $$d+1$$를 부여한다. 더 짧은 경로가 있다면 거리가 $$d-1$$ 이하인 직전 정점이 이미 확장되었어야 하므로, 이웃의 미발견 상태와 모순된다. 정점마다 한 번 큐에 들어가고 저장된 간선마다 한 번 검사하므로 시간은 $$O(\vert V\vert +\vert E\vert )$$, 보조 공간은 $$O(\vert V\vert )$$이다.

가중치가 있으면 가정이 달라진다. 다익스트라는 음수가 아닌 가중치가 필요하다. 음수 간선에는 다른 알고리즘이 필요하며, 음수 사이클 때문에 최단 거리가 정의되지 않을 수도 있다.

## 모듈러 산술
{: id="5-모듈러-산술과-경계-조건"}

정수 모듈러스 $$M\ge2$$에 대해 $$\mathbb Z/M\mathbb Z$$의 산술은 다음을 만족한다.

$$
(a+b)\bmod M=((a\bmod M)+(b\bmod M))\bmod M
$$

구현은 중간 합도 표현할 수 있어야 하므로 더 넓은 자료형이나 오버플로 없는 계산이 필요하다. $$a$$로 나누는 연산은 역원을 사용하며, 역원은 정확히 $$\gcd(a,M)=1$$일 때 존재한다. 페르마의 공식 $$a^{M-2}\bmod M$$에는 $$M$$이 소수이고 $$a\not\equiv0\pmod M$$이라는 조건이 추가된다.

부호 있는 `%`는 나머지를 반환한다. 양의 모듈러스에서 `rem_euclid`는 표준적인 음이 아닌 잉여를 구한다. 경계 사례는 $$0$$, $$M-1$$, $$M$$, 허용된 음수 입력, 가장 큰 중간값이다.

## 작은 정답 프로그램
{: id="6-작은-정답-프로그램과-알고리즘을-비교한다"}

작은 무작위 입력에서는 완전 탐색 풀이를 정답 기준으로 삼을 수 있다. 최단 경로는 경로 열거 또는 세제곱 시간의 모든 쌍 풀이를 기준으로 삼고, 부분집합 최적화는 $$n$$이 작을 때 $$2^n$$개 부분집합을 모두 조사한다. 시드와 실패 입력을 저장하면 반례를 재현할 수 있다.

테스트는 파싱, 인덱스, 경계를 확인하고 불변식은 명시된 입력 영역을 다룬다. 디버그와 최적화 바이너리는 서로 다른 검사와 실행 방식을 거친다. 그래프 사례에는 고립 정점, 연결되지 않은 컴포넌트, 평행 간선, 자기 루프, 재귀 스택 사용을 드러낼 긴 사슬이 포함된다.

## 대회 도구
{: id="7-선택적인-대회-도구"}

기존 작업 공간은 [rust-competitive-helper](https://github.com/rust-competitive-helper/rust-competitive-helper)와 [Competitive Companion](https://github.com/jmerle/competitive-companion)을 사용했다. 설치, 포트, 지원 채점 플랫폼, 도구 체인 요구 사항은 현재 README에서 확인하며, 리비전을 고정하면 환경을 재현하기 쉬워진다.

기본 흐름은 문제 디렉터리, 단일 파일 구현, 예제와 정답 프로그램 비교, 채점 환경에 맞는 컴파일, 소스 제출이다. 생성된 Cargo 작업 공간도 채점 서버의 의존성과 진입점 제한에 맞아야 한다. IDE 실행 성공만으로 이식성이 입증되지는 않는다. 이 글은 컴파일러 벤치마크나 도구 실행 결과를 보고하지 않는다.

## 참고 문헌
{: id="참고-문헌과-이-글의-범위"}

- [The Rust Programming Language](https://doc.rust-lang.org/book/): 소유권, 대여, 자료형, 오류.
- [Rust 표준 라이브러리](https://doc.rust-lang.org/std/): 컬렉션, 입출력, 수치 연산.
- [rust-competitive-helper](https://github.com/rust-competitive-helper/rust-competitive-helper)와 [Competitive Companion](https://github.com/jmerle/competitive-companion).
