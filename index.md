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

## Semi-formal document analysis

Translating character specs (the OpenAI Model Spec, Claude's constitution) into a symbolic
representation that answers "which sections bear on behavior X" deterministically — the
complete record of an attempt that did not reach its bar, and a proposal for where the
machinery and the measurement discipline go next:

1. [Turning a model spec into a machine: what worked and what didn't]({% post_url 2026-08-30-spec-retrospective %}) *(2026-08-30)*
2. [Proposing a symbolic evidentiary layer for alignment-event investigations]({% post_url 2026-08-30-checkable-investigations %}) *(2026-08-30)*
3. [Pilot: verifying my own README with a claim ledger]({% post_url 2026-09-01-readme-verification-pilot %}) *(2026-09-01, registered design — results pending)*

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
