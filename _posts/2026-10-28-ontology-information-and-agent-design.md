---
title: "Ontology and Agents"
subtitle: "What formal semantics adds, what information theory does and does not imply, and what published ontology engineering and navigation experiments establish."
tags: ["ontology", "knowledge-graphs", "information-theory", "language-models", "agents"]
lang: en
translation_key: 2026-10-28-ontology-information-and-agent-design
translation_url: /ko/2026/10/28/ontology-information-and-agent-design.html
date: 2026-10-28 09:00:00 +0900
last_modified_at: 2026-10-28
sources_checked_at: 2026-10-28
---

> **A starting point.** A linked Markdown wiki organizes material for reading and navigation. A formal ontology specifies vocabulary and axioms with defined semantics. Both can organize the same sources, and both can be written in text files. Neither the extension `.md` nor a graph shape determines how much answer-relevant information is preserved. Published agent studies show useful automation of particular engineering steps, alongside errors and mixed results.

**Reading path.** Sections 1–3 explain the concepts with a small example. Sections 4–6 introduce the information-theoretic comparison and its assumptions. Sections 7–9 review measured navigation and ontology engineering results. Sections 10–11 give conditional application criteria and conclusions.

**Evidence boundary.** Sources were checked on October 28, 2026, Korea time. This is a focused literature review, not an exhaustive systematic review or a new benchmark. Numbers are author-reported results; no model experiments were reproduced for this article. Standards, reviewed publications, preprints, and an informal design recipe are identified separately. Mathematical examples are explanatory constructions. Recommendations below are conditional consequences of the cited evidence, not a demonstrated universal optimum.

## 1. What is an ontology, mathematically?

In computer science, Gruber's ontology definition concerns an explicit specification of a conceptualization: the vocabulary used to represent a domain and the meaning attached to it. This does not identify one mandatory mathematical tuple or file format for every ontology. [Gruber, 1993](https://tomgruber.org/writing/ontolingua-kaj-1993/).

For the **logical ontologies considered here**, write

$$
\mathcal O=(\Sigma,T),\qquad K=T\cup A.
$$

Here $$\Sigma$$ is a signature specifying symbols and their kinds/arities, $$T$$ a set of axioms in a chosen logic, and $$A$$ assertions about particular objects. $$K$$ is the resulting knowledge base. The schema/assertion distinction is useful; real ontology documents can include both. This notation is an explanatory model, not a claim that every ontology is an OWL knowledge base.

Consider names `Researcher`, `Person`, `authoredBy`, `paper1`, and `alice`. In a simplified object-only description-logic interpretation $$\mathcal I=(\Delta^{\mathcal I},\cdot^{\mathcal I})$$, the domain $$\Delta^{\mathcal I}$$ is nonempty. A class name denotes a subset of it, an object property a binary relation, and an individual name an element:

$$
\begin{aligned}
\mathrm{Researcher}^{\mathcal I}&\subseteq\Delta^{\mathcal I},\\
\mathrm{authoredBy}^{\mathcal I}&\subseteq\Delta^{\mathcal I}\times\Delta^{\mathcal I},\\
\mathrm{alice}^{\mathcal I}&\in\Delta^{\mathcal I}.
\end{aligned}
$$

OWL 2 Direct Semantics gives the full account, including data values and datatype interpretations omitted from this teaching fragment. [W3C: OWL 2 Direct Semantics, §§2.2–2.3](https://www.w3.org/TR/owl2-direct-semantics/).

Let $$T=\{\mathrm{Researcher}\sqsubseteq\mathrm{Person}\}$$ and $$A=\{\mathrm{Researcher}(\mathrm{alice})\}$$. The subclass axiom means

$$
\mathrm{Researcher}^{\mathcal I}\subseteq\mathrm{Person}^{\mathcal I}.
$$

A **model** of $$K$$ satisfies every axiom and assertion in $$K$$. **Entailment** means truth in every such model:

$$
K\models\varphi\quad\Longleftrightarrow\quad
\text{every model of }K\text{ satisfies }\varphi.
$$

Thus $$K\models\mathrm{Person}(\mathrm{alice})$$: membership in the smaller set implies membership in the larger set. The conclusion follows from the supplied axiom and assertion. It does not independently verify that a real Alice is a researcher.

## 2. What logical guarantees leave open

Three distinctions prevent common modeling mistakes.

**Unknown is not false.** The Web Ontology Language (OWL) uses an open-world view: failure to state that Alice wrote a paper does not establish that she did not. Different individual names also need not denote different objects. An application requiring distinct objects or a complete list must supply the relevant assumptions. [W3C: OWL 2 Primer, §§5–6](https://www.w3.org/TR/owl-primer/).

**Inference is not record validation.** A domain axiom can infer a subject's type from a property assertion; it need not reject an untyped record. SHACL separately validates a specified RDF data graph against shapes, including minimum counts and datatypes. Validation still depends on the chosen data graph, shapes, and inference configuration. [W3C: SHACL](https://www.w3.org/TR/shacl/).

**Consistency is not factual accuracy.** A consistent theory has at least one model. It may still contain unsupported assertions or use a concept differently from stakeholders. Under classical entailment an inconsistent theory has no models, so the universal condition above holds vacuously for every sentence. Consistency checks are therefore necessary for trustworthy classical reasoning, but insufficient to establish external truth.

## 3. Why add an ontology to documents or a graph?

Suppose one repository calls a relation `author`, another `creator`, and a third uses an untyped “see also” link. A shared vocabulary can specify whether these relations have the same intended meaning. Axioms can then support reusable inferences. A translation must preserve intended meaning; matching names alone does not establish equivalence. Gruber's original portability problem concerns precisely the sharing of formally represented knowledge across systems. [Gruber, 1993](https://tomgruber.org/writing/ontolingua-kaj-1993/).

| Representation | What a connection states | What is needed for a stronger interpretation |
| --- | --- | --- |
| Markdown hyperlink | One location links to another | A convention or interpreter defining the link's meaning |
| RDF triple | A subject, predicate, and object are asserted | Vocabulary definitions and the selected entailment regime |
| Formal ontology | Named constructs and axioms have specified semantics | Correct modeling assumptions, data, and a suitable reasoner |

The Resource Description Framework (RDF) graph data model and its serializations are distinct. A graph used for retrieval need not be a complete axiomatized ontology; an ontology need not be stored in a graph database. [W3C: RDF 1.1 Concepts](https://www.w3.org/TR/rdf11-concepts/).

The additional requirement is **machine-interpretable agreement about meaning**, not simply more links. It matters when systems must share types, combine datasets, compute defined consequences, or check declared constraints. If the task only requires finding and reading source passages, formal axiomatization is a separate engineering choice, not a logical prerequisite for retrieval.

## 4. What does “information amount” mean?

These quantities should not be substituted for one another.

| Quantity | What it measures | What it does not establish |
| --- | --- | --- |
| Bytes or tokenizer tokens | Encoded length under a specified encoding | Truth, useful meaning, or evidence coverage |
| Shannon entropy | Uncertainty under a probability distribution | Semantic correctness without a model linking symbols to the task |
| Logical consequences | What follows from axioms under a semantics | Independent observations about the world |
| Retrieval/evidence recall | How often required evidence reaches the reader | Correct use of that evidence or a complete ontology |

For a discrete random variable $$X$$ with probability mass function $$p$$, entropy in bits is

$$
H(X)=-\sum_x p(x)\log_2p(x),\qquad 0\log_2 0:=0.
$$

One fixed file has a length, but calling that length its Shannon entropy requires a distribution over possible files or messages. Shannon's communication problem separates message transmission from questions about meaning. [Shannon, 1948](https://web.mit.edu/6.976/www/handout/shannon.pdf).

Assume discrete variables and finite answer entropy under the conditioning used below. For a target answer $$Y$$, question $$Q$$, and representation $$R$$, a task-specific quantity is conditional mutual information:

$$
I(Y;R\mid Q)=H(Y\mid Q)-H(Y\mid R,Q).
$$

It describes expected uncertainty reduction under a specified joint distribution. A benchmark's F1 score is not a measurement of this quantity in bits.

## 5. Same sources, different access paths

Karpathy's **LLM Wiki** is an informal idea file, not a controlled experiment. Its recipe keeps raw sources, an agent-maintained Markdown wiki, and instructions; ingestion updates pages and links, querying follows an index, and linting checks maintenance problems. It also allows search tools. Its description supplies no matched ontology comparison or independent benchmark. [Karpathy, LLM Wiki, April 2026](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Both wiki compilation and graph construction can derive summaries, entity links, and access paths from sources. To state the information limit carefully, let $$D$$ be random source data, $$Q$$ a question, $$Y$$ its target answer, and $$B$$ background information, including model parameters and external rules. Let $$R$$ be a representation made from $$D,B$$ and $$C$$ a retrieved context made from $$R,Q,B$$. Specify the absence of additional answer-dependent evidence by the conditional independences $$I(Y;R\mid D,Q,B)=0$$ and $$I(Y;C\mid R,Q,B)=0$$. The conditional data-processing inequality gives

$$
I(Y;C\mid Q,B)\le I(Y;R\mid Q,B)\le I(Y;D\mid Q,B).
$$

For example, conditional independence gives $$I(Y;R\mid D,Q,B)=0$$. Applying the mutual-information chain rule in two orders yields

$$
I(Y;D\mid Q,B)=I(Y;R\mid Q,B)+I(Y;D\mid R,Q,B).
$$

The final term is nonnegative; applying the same argument to retrieval proves the first inequality. These are standard information-theoretic properties, applied here under the stated assumptions. [Duchi, *Statistics and Information Theory*, §2.1](https://web.stanford.edu/class/stats311/lecture-notes.pdf).

The conditioning matters. A pretrained model or external database can contribute information absent from the supplied documents. The inequality does not support an unqualified claim that an LLM can never add information.

A reversible re-encoding preserves the source information: if $$R=f(D)$$ and $$D=h(R)$$, each representation determines the other. The same axioms in a Markdown code block and a lossless Turtle encoding need not differ in information content. A generated summary can discard details. Keeping the raw sources alongside it preserves those details in the **whole store**, while a retrieved context can still omit them.

Finite computation creates a different question: how reliably can a reader **access and use** the evidence within its context, tool-call, and latency budgets? Better indexing can improve that practical outcome without increasing the information in the original sources. A graph path is not necessarily a proof; a Markdown link is not necessarily a typed relation. Either requires the appropriate interpretation.

## 6. A finite example: constraints versus derived statements

Take two propositional variables $$P,Q$$. This is a teaching construction, not an empirical model of a document corpus.

| $$P$$ | $$Q$$ | $$P\Rightarrow Q$$ |
| --- | --- | --- |
| false | false | true |
| false | true | true |
| true | false | false |
| true | true | true |

There are four initial valuations. The axiom $$P\Rightarrow Q$$ permits three. Under a **uniform prior over those four valuations**, conditioning on the axiom reduces entropy from $$2$$ to $$\log_2 3$$ bits. The reduction is

$$
2-\log_2 3=\log_2(4/3)\approx0.415\text{ bits}.
$$

Add the assertion $$P$$ and only the final row remains. Then $$Q$$ follows. Explicitly storing that already-entailed $$Q$$ does not remove another valuation. More generally,

$$
T\models\varphi\quad\Longrightarrow\quad
\operatorname{Mod}(T)=\operatorname{Mod}(T\cup\{\varphi\}).
$$

This follows directly from the definition of entailment. Materializing a consequence can make access easier without adding an independent constraint. Adding an **unentailed** axiom changes the theory and may introduce an assumption or error. The finite uniform example does not justify counting the models of arbitrary OWL ontologies as entropy; their domains and model classes need not be finite or carry such a probability distribution.

## 7. What navigation experiments actually measure

Retrieval-augmented generation (RAG) retrieves sources for a language model to answer from. BM25 ranks by lexical matching; dense retrieval ranks vector representations; agentic retrieval lets a controller choose further search/read steps. Recent work evaluates complete systems rather than file extensions in isolation. F1 combines precision and recall over each paper’s chosen evaluation units; units and scales must match before comparing scores.

**Corpus2Skill** compiles hierarchical navigation files and summaries, then lets an agent retrieve source documents. Its 2026 paper evaluates WixQA and ten RAGBench subsets. On WixQA, the same Claude Sonnet 4.6 answer model produced the following Table 1 results. [Sun et al., Corpus2Skill, v4 / Findings EMNLP 2026](https://arxiv.org/html/2604.14572v4).

| WixQA system | Token F1 | Reported serving dollars/query |
| --- | --- | --- |
| Dense | 0.364 | 0.007 |
| RAPTOR | 0.398 | 0.012 |
| Agentic | 0.378 | 0.082 |
| Corpus2Skill | 0.456 | 0.153 |

WixQA has 6,221 articles and 200 expert queries. Serving costs include prompt caching; compilation is separate. Across eleven datasets the method has five significant wins, three ties, and three losses against the strongest respective baseline. The result supports a quality/cost tradeoff in those settings; it does not isolate Markdown syntax or prove general superiority.

**HippoRAG 2**, an ICML 2025 graph-retrieval system, reports average answer F1 of **59.8** (0–100 scale, unlike the 0–1 table above), versus **57.0** for NV-Embed-v2 on its seven-dataset suite. Its MuSiQue timing experiment reports indexing **99.5 versus 12.1 minutes**, and query QA time **1.2 versus 0.3 seconds**. These are that paper's setup and hardware, not current service prices. [Gutiérrez et al., 2025, Tables 2–3 and Appendix F](https://proceedings.mlr.press/v267/gutierrez25a.html).

**GraphRAG** evaluates global synthesis using extracted graphs and community summaries. Table 6 reports comprehensiveness comparison scores for graph levels C0–C3 against vector RAG: **71.92–78.96%** on podcasts and **71.76–79.44%** on news. Wins/ties/losses receive 100/50/0; these LLM preferences are not factual-answer accuracy. The authors identify missing ground truth as a limitation. An extracted graph does not itself supply OWL entailment guarantees. [Edge et al., 2024/2025](https://arxiv.org/html/2404.16130v2).

A useful counterpoint is the **BM25 Wins at Scale** preprint. With a fixed reader and 500 questions, its raw file-tree agent records **30.7** on the official combined score (%) at 511,959 documents (about 601 million tokens), versus **50.5** for BM25. This score gates completeness by correctness; the agent has an 80-call budget. That agent lacks a compiled wiki index, so this is not a direct test of LLM Wiki or Corpus2Skill. [arXiv:2607.26497v3](https://arxiv.org/html/2607.26497v3).

These studies differ in questions, readers, budgets, and scoring. Their numbers cannot rank formal ontologies against Markdown navigation. None of these comparisons holds those factors fixed while changing only formal ontology semantics.

## 8. From expert engineering to LLM-assisted workflows

Earlier engineering was already more structured than manually drawing a graph. **METHONTOLOGY** specifies requirements, conceptualization, implementation, evaluation, documentation, and maintenance through evolving prototypes. **NeOn** adds scenarios for reusing and re-engineering ontologies and other knowledge resources. [Fernández-López et al., 1997](https://cdn.aaai.org/Symposia/Spring/1997/SS-97-06/SS97-06-005.pdf), [Suárez-Figueroa et al., 2015](https://doi.org/10.3233/AO-150145).

Competency questions (CQs) make scope testable: for example, “Which authors of this paper are researchers?” A natural-language CQ still needs an agreed meaning, representative data, and an executable query or evaluation procedure. A system that invents both the questions and their answers has not supplied independent evidence of completeness.

The following approaches automate different parts of that process.

| Approach | Representative research | Automated contribution | Boundary |
| --- | --- | --- | --- |
| Stakeholder conversation | OntoChat, ESWC 2024 | User stories, CQ elicitation and testing | Retains human requirements and feedback |
| Structured prompting and patterns | Ontogenia, ESWC 2025 | Generate and reassess ontology modules from CQs and patterns | Does not require a multi-agent system |
| Trained ontology learning | OLLM, NeurIPS 2024 | Predict document-level taxonomy subgraphs, then merge/prune | Concepts and taxonomy, not unrestricted OWL engineering |
| Tool-based generation and repair | Extended NeOn-GPT, 2026 | Reuse, generation, syntax/reasoner/pitfall checks and repairs | A staged pipeline is not automatically a multi-agent comparison |
| Role-based collaboration | LLM4ACOE, 2025; four-role study, 2026 | Separate or simulate expert, planning, coding and QA roles | Agent count and planning effects may be confounded |
| Grounded enrichment | OntoCodex, 2026 | Extend an existing ontology with sources and terminology tools | Domain-specific enrichment, not unrestricted autonomous design |

[OntoChat](https://arxiv.org/html/2403.05921v1) reports **87.5%** accuracy on 56 tests distinguishing supported from unsupported CQs in its music case. Its user-reported time-saving benefits are subjective feedback, not a timed productivity experiment.

[Ontogenia](https://arxiv.org/html/2503.05388v1) evaluates 10 ontologies and 100 CQs, with two independent experienced knowledge engineers assessing output. Table 3's adequacy values using o1-preview with Ontogenia for Music/Theatre/Hospital are **0.96/1.0/1.0**, versus **0.9/0.73/0.73** for the same model with Memoryless CQbyCQ. These are the raw table values; its caption says “%”. Qualitative assessment still finds domain/range errors and redundant elements. Coverage is not error-free modeling.

[OLLM](https://proceedings.neurips.cc/paper_files/paper/2024/hash/9e89f068a62f6858c661a8abecf5bb0a-Abstract-Conference.html) reports Wikipedia Graph F1 **0.644**, versus **0.588** for ordinary fine-tuning. That graph-similarity score is neither the percentage of true axioms nor evidence for a multi-agent advantage. Unknown pretraining contamination remains a limitation.

## 9. Agent effectiveness: different tests give different answers

| Study and scope | Observed comparison/result | What remains unestablished |
| --- | --- | --- |
| Extended NeOn-GPT: 4 models × 4 domains | Inconsistent ontologies **7/16 before → 0/16 after** verification/repair | Factual completeness; run-to-run variance; one generation per model/domain |
| LLM4ACOE: wildfire search-and-rescue documents | Selected setting answers **14/18 CQs** | General-domain accuracy or an isolated benefit from adding agents |
| Four-role study: 2 synthetic insurance contracts | Processed SPARQL coverage **0.6304 → 0.6196**, **0.4027 → 0.4383** | Uniform improvement; broad real-document generalization |
| OntoCodex: existing biomedical ontology, 5 diseases | Imaging/diagnostic-procedure F1 **0.786 → 0.946**; medication F1 **0.944 → 0.927** | Universal extraction gains or clinical effectiveness |

[Extended NeOn-GPT](https://www.semantic-web-journal.net/system/files/swj4014.pdf) combines parsing, OWL reasoning, pitfall detection, and repair. Passing those checks establishes the reported properties, not correspondence to all intended real-world meanings.

[LLM4ACOE, *The Knowledge Engineering Review*, 2025](https://doi.org/10.1017/S026988892510009X) simulates knowledge engineer, domain expert, and knowledge worker roles with retrieval. It also observes irrelevant example concepts and fictitious imports entering generated ontologies. More retrieved material does not consistently improve coverage.

The [four-role workshop manuscript, April 2026](https://arxiv.org/html/2604.23090v1) uses Domain Expert → Manager → Coder → QA. LLM-judged architecture scores improve, while SPARQL results above are mixed. RAG coverage improves in both contracts. Coverage here is a mean CQ score with LLM adjudication, rather than a simple binary success proportion. Those metrics measure different properties; architecture preference cannot replace executable query coverage.

[OntoCodex, *npj Health Systems*, August 2026](https://www.nature.com/articles/s44401-026-00117-9) coordinates five agents for grounded enrichment. The figures above are domain-mean F1 values against baseline ChatGPT-4o. Its imaging/diagnostic-procedure F1 confidence intervals are broad and overlapping; the point-estimate difference should not be called statistically significant from that fact alone. Laboratory-test code mapping also drops **60% → 20%** in its comparison. Human semantic review remains part of the reported approach.

These results support feasibility for bounded assistance and enrichment. They do not establish that more agents always improve quality, that all ontology work can be delegated, or that logical consistency alone predicts downstream usefulness.

## 10. Application and evaluation criteria at the current stage

The literature supports conditional choices rather than one universally best representation.

| Required behavior | Relevant mechanism | Acceptance evidence |
| --- | --- | --- |
| Read and synthesize evolving documents | Source-preserving search/navigation; summaries as derived aids | Answer correctness, evidence recall, source support, update behavior |
| Share precise types and relations across datasets | Explicit vocabulary, mappings and appropriate axioms | Mapping review, entailment tests, independently specified CQs |
| Reject records missing required fields | Declared validation constraints, such as SHACL | Positive/negative fixtures under a fixed validation configuration |
| Automate ontology drafting or enrichment | Grounded generation with bounded modules and executable checks | Syntax, consistency, conceptual review, CQ coverage and downstream tests |

A compatible implementation can keep raw sources and a navigable wiki, adding a formal vocabulary for the relations requiring shared semantics. Generated axioms, summaries, and mappings remain derived artifacts with source/version provenance. This is a combination of the mechanisms above, not a benchmark-proven optimal architecture.

Evaluation should separate three layers: **representation quality** (meaning, consistency, coverage), **retrieval quality** (which necessary sources arrive), and **answer quality** (correctness and support). An ontology builder's CQ coverage cannot be substituted for a reader's answer accuracy. An LLM judge is useful measurement machinery only to the extent its agreement with independent labels is established.

For a meaningful local comparison, freeze the corpus, source versions, independently prepared questions, answers, and evidence. Compare lexical search, dense retrieval, compiled navigation, and graph-assisted retrieval with the same reader and declared budgets. To isolate an agent design, hold the model and requirements fixed and compare direct generation, structured single-agent work, and role-separated work. Report repeated-run variation and include unsupported, contradictory, and missing-evidence cases.

Measure construction, updates, serving, tool calls, retries, latency, and human correction. Over $$N>0$$ queries, an accounting identity is

$$
\overline C=\frac{C_{\mathrm{build}}+C_{\mathrm{updates}}}{N}
+\frac1N\sum_{i=1}^{N}C_{\mathrm{serve},i}.
$$

This does not assert that one method is cheaper. It makes the amortization assumption explicit. Corpus2Skill and HippoRAG 2 show why serving quality and indexing/serving costs must be reported together. Current API prices and a new corpus require new measurements.

## 11. Conclusions and recommendations

An ontology's distinguishing property is its specified vocabulary and semantics. Markdown is a serialization and document medium. A navigation system adds organization and a search policy; it does not acquire formal semantics simply by having links. These choices can coexist.

Information theory does not show that an ontology intrinsically contains more information than a wiki. Lossless encodings can preserve the same information; summaries and selection can lose relevant details. Explicitly stating entailed consequences changes access cost without adding independent logical constraints. Any stronger information claim needs a probability model, task definition, and account of external knowledge.

Published work demonstrates useful LLM assistance for requirements, modules, taxonomy learning, validation/repair, and enrichment. It also reports modeling errors, retrieval contamination, limited domains, and metric-dependent gains. The evidence therefore supports source-grounded, testable automation of defined tasks, with semantic review where intended meaning matters. It does not support blanket replacement of expert design or a universal ranking of ontologies and document navigation.

For deployment, choose the smallest set of mechanisms that meets the declared requirements, then verify them on independent evidence at the intended scale. Use formal semantics when defined inferences or shared meanings are required; evaluate navigation by evidence access and grounded answers. Preserve sources, disclose full costs, and retain the distinction between a passed check and a true statement about the world.

## References and reading order

The links near each claim identify its source. The following list groups the primary material for further reading.

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
