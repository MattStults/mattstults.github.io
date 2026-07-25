---
layout: default
---

Notes and experiments, mostly on AI safety.

## Oversight gaming

Building a small, fully-instrumented "model organism" of oversight gaming — a model that games its grader in a setting where every relevant fact is ground-truth-labeled — and finding when the behavior appears. A series:

1. [Defining a model organism of oversight gaming]({% post_url 2026-07-24-moog-definition %}) *(2026-07-24)*
2. [Reward geometry of the substrate]({% post_url 2026-07-24-moog-reward-geometry %}) *(2026-07-24)*
3. [Building a model organism of oversight gaming — does the behavior even fit?]({% post_url 2026-07-24-moog-does-the-behavior-fit %}) *(2026-07-24)*

## Monitoring

[How much can you learn about a model's state from pure gibberish?](https://mattstults.github.io/internal-state-from-gibberish/) *(2026-07-17)* —
a model carries a concept it was given but never puts into words. Who can read it back from the model's
*word-free* output, and how does that change with scale? Pre-registered experiments on Qwen2.5 1.5B–14B
and a cross-family Llama-3.3-70B point. Code and data:
[github.com/MattStults/internal-state-from-gibberish](https://github.com/MattStults/internal-state-from-gibberish).
*(My first attempt at empirical research — feedback welcome.)*
