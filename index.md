---
layout: default
---

AI Safety lab notes and results.

## Oversight gaming

Building a small, fully-instrumented "model organism" of oversight gaming — a model that games its grader in a setting where every relevant fact is ground-truth-labeled — and finding when the behavior appears. A series:

1. [Defining a model organism of oversight gaming]({% post_url 2026-07-24-moog-definition %}) *(2026-07-24)*
2. [Reward geometry of the substrate]({% post_url 2026-07-24-moog-reward-geometry %}) *(2026-07-24)*
3. [Building a model organism of oversight gaming — does the behavior even fit?]({% post_url 2026-07-24-moog-does-the-behavior-fit %}) *(2026-07-24)*
4. [The Starting Model]({% post_url 2026-07-28-moog-starting-model %}) *(2026-07-28)*
5. [RL Proof of Life]({% post_url 2026-07-31-moog-rl-plan %}) *(2026-07-31)*
6. [SDF at 1.7B]({% post_url 2026-07-30-moog-sdf %}) *(2026-07-30, kept current)*
7. [RL With the Mechanism in Context]({% post_url 2026-08-04-moog-in-context-rl %}) *(2026-08-04)*
8. [SFT as Repair, Not Replacement]({% post_url 2026-08-04-moog-sft-repair %}) *(2026-08-04)*
9. [Initial RL Attempt: Null]({% post_url 2026-08-31-moog-run1-extinction-race %}) *(2026-09-02)*
10. [Amplification, Not Emergence]({% post_url 2026-09-04-moog-amplification-not-emergence %}) *(2026-09-09)*
11. [A Substrate Where Reward Hacking Can Start]({% post_url 2026-09-05-moog-substrate-validation %}) *(2026-09-09)*

## Semi-formal document analysis

Can we get LLMs to use symbolic logic in order to make their conclusions deterministically auditable? By symbolic logic I mean translating free form text into a language like ASP that can deterministically evaluate expressions with traceable paths and normalized, mechanically interpretable meanings of each statement.

Specifically I am interested in whether symbolic modeling of events and analysis can address cases where incorrect agent understanding can spread meme-like through the artifacts that drive agentic systems, effectively prompt-injecting whole systems with potentially critical misinformation in ways that are silent to the humans using them. So far I have experimented with using this approach on the following domains:

- *Translating character specs* (the OpenAI Model Spec, Claude's constitution) into a symbolic representation that answers "which sections bear on behavior X" deterministically. **Successful in quality of judgments and auditability on the behaviors it was tuned for; unsuccessful at cost effectiveness and at generalizing beyond them.**
- *Investigations of alignment events* (motivated by METR's public write-up of the HuggingFace incident investigation). My idea here was that we might be able to mitigate the impact of unreliable model judgements by using lower capability models with significantly reduced context to build up a model of the event using symbolic representations from the atomic logs of the event. I hoped that this would succeed where the character spec translation failed because the domain of an investigation might be defined before you begin in a way that would avoid the generalization problem from the character spec case. **Roughly equivalent in quality of judgments, dramatically better in auditability; unsuccessful at cost effectiveness and decoupling reliance on unreliable model judgements.**
- *[new] Auditable project orchestration* (e.g. keeping a lab log, a project north star or an alignment investigation's status up-to-date). The high level idea is that agents can be asked to record their decisions and analysis in machine readable ASP that allows for quick, deterministic contradiction checking and would make auditing claims/decisions mechanical. My claim is that if this works, it likely works across project domains and so I should be able to test it by adjusting my approach on existing projects. I will update here as I make progress.

1. [Turning a model spec into a machine: what worked and what didn't]({% post_url 2026-08-30-spec-retrospective %}) *(2026-08-30)*
2. [Proposing a symbolic evidentiary layer for alignment-event investigations]({% post_url 2026-08-30-checkable-investigations %}) *(2026-08-30)*
3. [Pilot: verifying my own README with a claim ledger]({% post_url 2026-09-01-readme-verification-pilot %}) *(2026-09-01, updated with results)*

Code and record: [semi-formal-document-analysis](https://github.com/MattStults/semi-formal-document-analysis); experiments toward the proposal: [checkable-investigations](https://github.com/MattStults/checkable-investigations).

## Career transition

[Visiting SF and Berkeley]({% post_url 2026-08-03-visiting-sf-and-berkeley %}) *(2026-08-03)* —
notes from a week visiting the SF/Berkeley AI safety community on a BlueDot Impact career
transition grant, and how the trip changed my approach.

## Monitoring

[How much can you learn about a model's state from pure gibberish?](https://mattstults.github.io/internal-state-from-gibberish/) *(2026-07-17)* —
a model carries a concept it was given but never puts into words. Who can read it back from the model's
*word-free* output, and how does that change with scale? Pre-registered experiments on Qwen2.5 1.5B–14B
and a cross-family Llama-3.3-70B point. Code and data:
[github.com/MattStults/internal-state-from-gibberish](https://github.com/MattStults/internal-state-from-gibberish).
*(My first attempt at empirical research — feedback welcome.)*
