---
title: "Ontology and Agents"
subtitle: "Formal semantics and document navigation, with evidence from agent-assisted ontology engineering."
tags: ["ontology", "knowledge-graphs", "information-theory", "language-models", "agents"]
lang: en
translation_key: 2026-10-28-ontology-information-and-agent-design
translation_url: /ko/2026/10/28/ontology-information-and-agent-design.html
date: 2026-10-28 09:00:00 +0900
last_modified_at: 2026-10-29
sources_checked_at: 2026-10-28
---

An ontology defines a domain’s vocabulary and axioms. A linked wiki organizes documents for reading. Both can represent the same sources; their difference lies in semantics and access, not the file extension. LLMs can help build either representation, with results that depend on the task and validation method.

## Ontology
{: id="1-what-is-an-ontology-mathematically"}

Gruber defines an ontology as an explicit specification of a conceptualization: the terms and meanings used to describe a domain. The definition does not prescribe a single logic or file format. [Gruber, 1993](https://tomgruber.org/writing/ontolingua-kaj-1993/).

A logical ontology can be written as

$$
\mathcal O=(\Sigma,T),\qquad K=T\cup A.
$$

$$\Sigma$$ specifies symbols and their kinds/arities, $$T$$ contains axioms, and $$A$$ contains individual assertions. Their union $$K$$ is a knowledge base. A document may contain both schema and assertions; this notation describes the logical case, not every ontology.

Consider `Researcher`, `Person`, `authoredBy`, `paper1`, and `alice`. In an object-only description-logic interpretation $$\mathcal I=(\Delta^{\mathcal I},\cdot^{\mathcal I})$$, the domain $$\Delta^{\mathcal I}$$ is nonempty. Classes denote sets, object properties binary relations, and individuals elements:

$$
\begin{aligned}
\mathrm{Researcher}^{\mathcal I}&\subseteq\Delta^{\mathcal I},\\
\mathrm{authoredBy}^{\mathcal I}&\subseteq\Delta^{\mathcal I}\times\Delta^{\mathcal I},\\
\mathrm{alice}^{\mathcal I}&\in\Delta^{\mathcal I}.
\end{aligned}
$$

OWL 2 also defines the data values and datatype interpretations omitted here. [W3C, §§2.2–2.3](https://www.w3.org/TR/owl2-direct-semantics/).

With $$T=\{\mathrm{Researcher}\sqsubseteq\mathrm{Person}\}$$ and $$A=\{\mathrm{Researcher}(\mathrm{alice})\}$$, the subclass axiom means

$$
\mathrm{Researcher}^{\mathcal I}\subseteq\mathrm{Person}^{\mathcal I}.
$$

A **model** of $$K$$ satisfies its axioms and assertions. **Entailment** from $$K$$ means truth in every such model:

$$
K\models\varphi\quad\Longleftrightarrow\quad
\text{every model of }K\text{ satisfies }\varphi.
$$

Therefore $$K\models\mathrm{Person}(\mathrm{alice})$$. This follows from the supplied statements; whether a real Alice is a researcher requires external evidence.

## Semantics and validation
{: id="2-what-logical-guarantees-leave-open"}

Under OWL’s **open-world assumption**, absence of an assertion alone does not imply its negation. An absent authorship assertion does not imply that Alice wrote no papers. Different names may also denote the same object; distinctness and completeness need explicit assumptions. [W3C: OWL 2 Primer](https://www.w3.org/TR/owl-primer/).

A domain axiom infers a type from a property assertion rather than necessarily rejecting an untyped record. **SHACL** checks a specified RDF graph against shapes such as minimum counts and datatypes. Its result depends on that graph, the shapes, and inference configuration. [W3C: SHACL](https://www.w3.org/TR/shacl/).

**Consistency** means having at least one model, not agreement with reality or stakeholder intent. An inconsistent theory has no models and classically entails every sentence vacuously. A reasoner can check consistency; it cannot establish the truth of unsupported input.

## Shared vocabulary
{: id="3-why-add-an-ontology-to-documents-or-a-graph"}

One system’s `author` and another’s `creator` may or may not mean the same thing. A shared vocabulary makes that decision explicit; matching names alone cannot. Gruber’s portability problem concerns sharing these meanings across representation systems. [Gruber, 1993](https://tomgruber.org/writing/ontolingua-kaj-1993/).

| Representation | What a connection states | What is needed for a stronger interpretation |
| --- | --- | --- |
| Markdown hyperlink | One location links to another | A convention or interpreter defining the link's meaning |
| RDF triple | A subject, predicate, and object are asserted | Vocabulary definitions and the selected entailment regime |
| Formal ontology | Named constructs and axioms have specified semantics | Correct modeling assumptions, data, and a suitable reasoner |

RDF separates its graph data model from serialization. A retrieval graph need not be an axiomatized ontology, and an ontology need not use a graph database. [W3C: RDF 1.1 Concepts](https://www.w3.org/TR/rdf11-concepts/).

Formal semantics is useful for shared types, data integration, inference, and declared constraints. Finding source passages alone does not require axiomatization.

## Information
{: id="4-what-does-information-amount-mean"}

| Quantity | What it measures | What it does not establish |
| --- | --- | --- |
| Bytes or tokenizer tokens | Encoded length under a specified encoding | Truth, useful meaning, or evidence coverage |
| Shannon entropy | Uncertainty under a probability distribution | Semantic correctness without a model linking symbols to the task |
| Logical consequences | What follows from axioms under a semantics | Independent observations about the world |
| Retrieval/evidence recall | How often required evidence reaches the reader | Correct use of that evidence or a complete ontology |

For a discrete variable $$X$$ with probability mass function $$p$$, entropy in bits is

$$
H(X)=-\sum_x p(x)\log_2p(x),\qquad 0\log_2 0:=0.
$$

A file’s length is not its Shannon entropy without a distribution over possible messages. Shannon’s theory treats transmission separately from meaning. [Shannon, 1948](https://web.mit.edu/6.976/www/handout/shannon.pdf).

Assume discrete variables and finite conditional answer entropies. For answer $$Y$$, question $$Q$$, and representation $$R$$, conditional mutual information is

$$
I(Y;R\mid Q)=H(Y\mid Q)-H(Y\mid R,Q).
$$

It measures expected uncertainty reduction under a joint distribution. F1 is a different quantity, not a score in bits.

## Navigation
{: id="5-same-sources-different-access-paths"}

Karpathy’s **LLM Wiki** keeps raw sources, a Markdown wiki, and instructions. Ingestion updates pages and links; queries follow an index or use search, and linting checks maintenance problems. It is an informal recipe without a controlled ontology comparison. [Karpathy, 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Let $$D$$ be sources, $$Q$$ a question, $$Y$$ its answer, and $$B$$ background knowledge including model parameters and external rules. Construct representation $$R$$ from $$D,B$$, then context $$C$$ from $$R,Q,B$$. With no additional answer-dependent evidence, require $$I(Y;R\mid D,Q,B)=0$$ and $$I(Y;C\mid R,Q,B)=0$$. Data processing gives

$$
I(Y;C\mid Q,B)\le I(Y;R\mid Q,B)\le I(Y;D\mid Q,B).
$$

From $$I(Y;R\mid D,Q,B)=0$$ and the chain rule,

$$
I(Y;D\mid Q,B)=I(Y;R\mid Q,B)+I(Y;D\mid R,Q,B).
$$

The last term is nonnegative. Applying the same argument to retrieval proves the other inequality. [Duchi, §2.1](https://web.stanford.edu/class/stats311/lecture-notes.pdf).

Conditioning on background knowledge is essential: pretrained weights or an external database can supply facts absent from the documents.

A reversible encoding, $$R=f(D)$$ and $$D=h(R)$$, preserves information. The same axioms in Markdown and lossless Turtle can therefore carry the same information. Summaries may discard details; retaining raw sources preserves them in storage, although retrieval can still omit them.

Indexing changes how much evidence a bounded reader can access within its context, latency, and tool budget. That is an access benefit, not new source information. Graph paths and Markdown links need defined interpretations to serve as proofs or typed relations.

## Logical consequences
{: id="6-a-finite-example-constraints-versus-derived-statements"}

For a finite illustration, take propositional variables $$P,Q$$.

| $$P$$ | $$Q$$ | $$P\Rightarrow Q$$ |
| --- | --- | --- |
| false | false | true |
| false | true | true |
| true | false | false |
| true | true | true |

The axiom $$P\Rightarrow Q$$ permits three of four valuations. Under a uniform prior, conditioning reduces entropy from $$2$$ to $$\log_2 3$$ bits:

$$
2-\log_2 3=\log_2(4/3)\approx0.415\text{ bits}.
$$

Adding $$P$$ leaves one valuation and entails $$Q$$. Storing that already-entailed $$Q$$ removes no further models:

$$
T\models\varphi\quad\Longrightarrow\quad
\operatorname{Mod}(T)=\operatorname{Mod}(T\cup\{\varphi\}).
$$

Materialization can ease access without adding a constraint. An unentailed axiom changes the theory and may add an assumption or error. Arbitrary OWL model classes need not be finite or have a uniform prior, so this toy model count is not their entropy.

## Retrieval experiments
{: id="7-what-navigation-experiments-actually-measure"}

Retrieval-augmented generation (RAG) retrieves sources for a language model. BM25 uses lexical matching, dense retrieval vector representations, and agentic retrieval further controller-selected steps. F1 combines precision and recall over each study’s evaluation units. The following are author-reported results, not replications.

**Corpus2Skill** compiles navigation files and summaries, then retrieves source documents. Its WixQA experiment uses Claude Sonnet 4.6 for every answer model. [Sun et al., Table 1](https://arxiv.org/html/2604.14572v4).

| WixQA system | Token F1 | Reported serving dollars/query |
| --- | --- | --- |
| Dense | 0.364 | 0.007 |
| RAPTOR | 0.398 | 0.012 |
| Agentic | 0.378 | 0.082 |
| Corpus2Skill | 0.456 | 0.153 |

WixQA contains 6,221 articles and 200 expert questions. Serving costs include prompt caching but exclude compilation. Across WixQA and ten RAGBench subsets, Corpus2Skill reports five significant wins, three ties, and three losses against the strongest respective baselines. This compares systems, not Markdown syntax.

**HippoRAG 2** reports aggregate answer F1 across seven datasets of **59.8** versus NV-Embed-v2’s **57.0**, on a 0–100 scale. In its MuSiQue timing setup, indexing takes **99.5 versus 12.1 minutes** and QA **1.2 versus 0.3 seconds/query**. [Gutiérrez et al., Tables 2–3, Appendix F](https://proceedings.mlr.press/v267/gutierrez25a.html).

**GraphRAG** uses extracted graphs and community summaries for global synthesis. Against vector RAG, C0–C3 comprehensiveness scores are **71.92–78.96%** on podcasts and **71.76–79.44%** on news, scoring wins/ties/losses 100/50/0. These are LLM preferences without independent ground truth, not factual accuracy or OWL guarantees. [Edge et al., Table 6](https://arxiv.org/html/2404.16130v2).

The **BM25 Wins at Scale** preprint fixes the reader and 500 questions. At 511,959 documents (about 601 million tokens), its raw-tree agent scores **30.7** versus BM25’s **50.5** on correctness-gated completeness (%), with an 80-call agent budget. It lacks a compiled wiki, so it does not directly test LLM Wiki or Corpus2Skill. [2026 preprint](https://arxiv.org/html/2607.26497v3).

Readers, tasks, budgets, and scoring differ across these studies. None isolates formal ontology semantics against Markdown navigation under matched conditions.

## Ontology engineering
{: id="8-from-expert-engineering-to-llm-assisted-workflows"}

**METHONTOLOGY** organizes requirements, conceptualization, implementation, evaluation, documentation, and maintenance around evolving prototypes. **NeOn** adds reuse and re-engineering scenarios. LLM workflows automate parts of these established processes. [Fernández-López et al., 1997](https://cdn.aaai.org/Symposia/Spring/1997/SS-97-06/SS97-06-005.pdf), [Suárez-Figueroa et al., 2015](https://doi.org/10.3233/AO-150145).

**Competency questions (CQs)** state required capabilities, such as “Which authors are researchers?” They need agreed meanings, representative data, and executable evaluation. Generating both questions and answers does not provide an independent completeness test.

| Approach | Representative research | Automated contribution | Boundary |
| --- | --- | --- | --- |
| Stakeholder conversation | OntoChat, ESWC 2024 | User stories, CQ elicitation and testing | Retains human requirements and feedback |
| Structured prompting and patterns | Ontogenia, ESWC 2025 | Generate and reassess ontology modules from CQs and patterns | Does not require a multi-agent system |
| Trained ontology learning | OLLM, NeurIPS 2024 | Predict document-level taxonomy subgraphs, then merge/prune | Concepts and taxonomy, not unrestricted OWL engineering |
| Tool-based generation and repair | Extended NeOn-GPT, 2026 | Reuse, generation, syntax/reasoner/pitfall checks and repairs | A staged pipeline is not automatically a multi-agent comparison |
| Role-based collaboration | LLM4ACOE, 2025; four-role study, 2026 | Separate or simulate expert, planning, coding and QA roles | Agent count and planning effects may be confounded |
| Grounded enrichment | OntoCodex, 2026 | Extend an existing ontology with sources and terminology tools | Domain-specific enrichment, not unrestricted autonomous design |

[OntoChat](https://arxiv.org/html/2403.05921v1) reports **87.5%** accuracy on 56 supported/unsupported CQ tests in a music case. Reported time savings are user feedback, not measured elapsed-time gains.

[Ontogenia](https://arxiv.org/html/2503.05388v1) evaluates 10 ontologies and 100 CQs with two independent experienced assessors. For o1-preview, Music/Theatre/Hospital adequacy is **0.96/1.0/1.0** with Ontogenia versus **0.9/0.73/0.73** with Memoryless CQbyCQ. These are raw Table 3 values despite its “%” caption. Domain/range errors and redundancy remain.

[OLLM](https://proceedings.neurips.cc/paper_files/paper/2024/hash/9e89f068a62f6858c661a8abecf5bb0a-Abstract-Conference.html) improves Wikipedia Graph F1 from ordinary fine-tuning’s **0.588** to **0.644**. This measures graph similarity, not true-axiom frequency or a multi-agent effect. Pretraining contamination is unresolved.

## Agent experiments
{: id="9-agent-effectiveness-different-tests-give-different-answers"}

| Study and scope | Observed comparison/result | What remains unestablished |
| --- | --- | --- |
| Extended NeOn-GPT: 4 models × 4 domains | Inconsistent ontologies **7/16 before → 0/16 after** verification/repair | Factual completeness; run-to-run variance; one generation per model/domain |
| LLM4ACOE: wildfire search-and-rescue documents | Selected setting answers **14/18 CQs** | General-domain accuracy or an isolated benefit from adding agents |
| Four-role study: 2 synthetic insurance contracts | Processed SPARQL coverage **0.6304 → 0.6196**, **0.4027 → 0.4383** | Uniform improvement; broad real-document generalization |
| OntoCodex: existing biomedical ontology, 5 diseases | Imaging/diagnostic-procedure F1 **0.786 → 0.946**; medication F1 **0.944 → 0.927** | Universal extraction gains or clinical effectiveness |

[Extended NeOn-GPT](https://www.semantic-web-journal.net/system/files/swj4014.pdf) combines parsing, OWL reasoning, pitfall checks, and repair. Passing them establishes those checked properties, not factual completeness.

[LLM4ACOE (2025)](https://doi.org/10.1017/S026988892510009X) simulates knowledge engineer, domain expert, and knowledge worker roles with retrieval. Irrelevant concepts and fictitious imports enter some outputs; more retrieved material does not consistently improve coverage.

The [four-role study](https://arxiv.org/html/2604.23090v1) uses Domain Expert → Manager → Coder → QA. LLM architecture scores and RAG coverage improve for both synthetic contracts; SPARQL outcomes are mixed. Coverage is a mean CQ score with LLM adjudication, not a binary success rate.

[OntoCodex (2026)](https://www.nature.com/articles/s44401-026-00117-9) uses five agents for enrichment. The table compares domain-mean F1 with baseline ChatGPT-4o. Imaging/diagnostic confidence intervals are broad and overlapping; point estimates alone do not establish significance. Laboratory-test mapping drops **60% → 20%**. Human semantic review remains.

## Applications
{: id="10-application-and-evaluation-criteria-at-the-current-stage"}

| Required behavior | Relevant mechanism | Acceptance evidence |
| --- | --- | --- |
| Read and synthesize evolving documents | Source-preserving search/navigation; summaries as derived aids | Answer correctness, evidence recall, source support, update behavior |
| Share precise types and relations across datasets | Explicit vocabulary, mappings and appropriate axioms | Mapping review, entailment tests, independently specified CQs |
| Reject records missing required fields | Declared validation constraints, such as SHACL | Positive/negative fixtures under a fixed validation configuration |
| Automate ontology drafting or enrichment | Grounded generation with bounded modules and executable checks | Syntax, consistency, conceptual review, CQ coverage and downstream tests |

Raw sources and a wiki can coexist with a formal vocabulary for relations requiring shared semantics. Generated summaries, mappings, and axioms remain versioned, source-linked artifacts. This is a compatible combination, not a proven optimum.

Evaluate representation (meaning, consistency, coverage), retrieval (required evidence), and answers (correctness, support) separately. CQ coverage is not answer accuracy; an LLM judge needs validation against independent labels.

A matched comparison fixes corpus versions, independent questions/answers/evidence, reader, and budgets. For agent design, hold model and requirements fixed across direct, structured single-agent, and role-separated generation. Repeated runs and missing/conflicting-evidence cases expose variability and failure modes.

Costs include construction, updates, serving, tool calls, retries, latency, and human correction. Over $$N>0$$ queries, the amortized accounting is

$$
\overline C=\frac{C_{\mathrm{build}}+C_{\mathrm{updates}}}{N}
+\frac1N\sum_{i=1}^{N}C_{\mathrm{serve},i}.
$$

## Conclusion
{: id="11-conclusions-and-recommendations"}

Ontologies specify meanings and consequences; navigation organizes access. Neither requires a particular file extension, and they can share the same sources.

Lossless encoding preserves information. Summaries and retrieval can lose relevant detail; materialized consequences change access without adding independent constraints. Information comparisons need a probability model and explicit external knowledge.

LLM studies support assistance with requirements, modules, taxonomy, repair, and enrichment. Their errors and mixed outcomes support bounded, testable automation with semantic review, not blanket replacement of experts.

Use formal semantics for defined inference and shared meaning; evaluate navigation by evidence access and grounded answers. Verify the required behavior at the intended scale, retaining sources and full costs.

## References
{: id="references-and-reading-order"}

1. Gruber (1993), [A Translation Approach to Portable Ontology Specifications](https://tomgruber.org/writing/ontolingua-kaj-1993/).
2. W3C Recommendations: [OWL 2 Direct Semantics](https://www.w3.org/TR/owl2-direct-semantics/), [OWL 2 Primer](https://www.w3.org/TR/owl-primer/), [RDF 1.1 Concepts](https://www.w3.org/TR/rdf11-concepts/), [SHACL](https://www.w3.org/TR/shacl/).
3. Shannon (1948), [A Mathematical Theory of Communication](https://web.mit.edu/6.976/www/handout/shannon.pdf); Duchi (2023), [Statistics and Information Theory, Chapter 2](https://web.stanford.edu/class/stats311/lecture-notes.pdf).
4. Fernández-López et al. (1997), [METHONTOLOGY](https://cdn.aaai.org/Symposia/Spring/1997/SS-97-06/SS97-06-005.pdf); Suárez-Figueroa et al. (2015), [NeOn Methodology framework](https://doi.org/10.3233/AO-150145).
5. Karpathy (2026), [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), informal design recipe.
6. Sun et al. (2026), [Corpus2Skill](https://aclanthology.org/2026.findings-emnlp.172/), Findings EMNLP; numerical discussion uses [v4](https://arxiv.org/html/2604.14572v4).
7. Gutiérrez et al. (2025), [From RAG to Memory: Non-Parametric Continual Learning for Large Language Models](https://proceedings.mlr.press/v267/gutierrez25a.html), ICML; HippoRAG 2.
8. Edge et al. (2024/2025), [From Local to Global: A Graph RAG Approach to Query-Focused Summarization](https://arxiv.org/html/2404.16130v2).
9. [BM25 Wins at Scale](https://arxiv.org/html/2607.26497v3) (2026), preprint.
10. Zhang et al. (2024), [OntoChat](https://arxiv.org/html/2403.05921v1), ESWC.
11. Lippolis et al. (2025), [Ontology Generation using Large Language Models](https://arxiv.org/html/2503.05388v1), ESWC; Ontogenia.
12. Lo et al. (2024), [End-to-End Ontology Learning with Large Language Models](https://proceedings.neurips.cc/paper_files/paper/2024/hash/9e89f068a62f6858c661a8abecf5bb0a-Abstract-Conference.html), NeurIPS; OLLM.
13. Fathallah et al. (2026), [Extended NeOn-GPT](https://doi.org/10.1177/22104968261453138), accepted [manuscript](https://www.semantic-web-journal.net/system/files/swj4014.pdf).
14. Soularidis et al. (2025), [Automating agentic collaborative ontology engineering](https://doi.org/10.1017/S026988892510009X), *The Knowledge Engineering Review*; LLM4ACOE.
15. Talukder et al. (2026), [Towards Automated Ontology Generation from Unstructured Text](https://arxiv.org/html/2604.23090v1), ESWC workshop manuscript.
16. Feng et al. (2026), [OntoCodex](https://www.nature.com/articles/s44401-026-00117-9), *npj Health Systems*.
