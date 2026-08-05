---
layout: post
title: "RL With the Mechanism in Context"
date: 2026-08-04
---

**Current Status**: Registered, not yet run. This is the plan for the next experiment, written before it executes.

[SDF closed]({% post_url 2026-07-30-moog-sdf %}) without producing a usable instill: the corpus reached the chat register, but no configuration did it without wrecking the model. The registered fallback was knowledge SFT. Before spending on any instill, I am running the RL experiment with the audit mechanism **in the prompt** instead of in the weights.

## Why this comes first

The question I actually care about is whether audit-conditional gaming *emerges* under RL. Every instill mechanism I have considered is a way of getting the model to know the audit rule before RL starts. None of them is the experiment; they are all preconditions for it. Four days of the SDF grid were spent on a precondition, and the experiment has still never run.

Putting the rule in the prompt removes the precondition entirely. There is no corpus to build, no instill to train, no forgetting bound to clear, and no way for the experiment to fail because the model did not learn the rule. If gaming does not emerge under those conditions, it is not because the instill was too weak.

There is a second reason, and it is the one that makes this not a detour. The follow-on question — how RL recruits oversight knowledge stored in weights — is inherently a comparison between knowledge the model must retrieve and knowledge it can simply read. I need the in-context arm to answer it. Running it first means the arm I need anyway also serves as the feasibility test.

## What the base model already does

The mechanism-in-context condition has been measured, at power, on the base model before any RL (n = 120 per cell, local quantized Qwen3-1.7B):

| condition | P(game \| unaudited) | P(game \| audited) | Δ |
|---|---|---|---|
| exploit stated explicitly | 0.868 | 0.300 | **+0.568** |
| mechanism in context, exploit unstated | 0.300 | 0.217 | **+0.083** (CI includes 0) |
| clean rule, exploit unstated | 0.458 | 0.317 | +0.142 |

Two things follow, and together they are why this arm is worth running.

**The starting point is null.** With the mechanism available and the exploit unstated, the model recalls the rule (~94% of chains cite it) and computes the audit predicate, but its audit-conditional discrimination is statistically indistinguishable from zero. That is the precondition the A0 gate demands, established by measurement rather than assumption. Whatever RL produces, it is not amplifying a discrimination that was already there.

**The ceiling is high and known.** When the exploit *is* stated, Δ reaches +0.568. The substrate supports the behaviour at this model size; the model can compute the predicate and act on it. So a null RL result cannot be blamed on the task being impossible, and cannot be blamed on the mechanism being unavailable. It would have to be about RL.

That pair — measured null start, measured high ceiling — is the cleanest experimental setup this project has had, and it costs nothing to construct.

## What changes, and what does not

The RL run itself is unchanged from [the plan]({% post_url 2026-07-31-moog-rl-plan %}): GRPO, K = 8 completions per prompt, G = 16 prompts per update, the reward tiers and 0.80 audit rate from the reward-geometry post, the same dataset guards, the same scoring.

One thing changes: the prompt carries the desk's mechanics — how it pays, which lane audits on what rule. The exploit is not in the prompt. Neither is any strategy text. The model is told how the desk works and is left to discover, or not, that an unaudited wrong answer still gets paid.

The pre-RL gates that still apply:

- **Capability SFT (the seed).** Unchanged and still required. RL cannot reinforce a behaviour it never samples, so the start model still inflates some fraction of the time, independent of audit status, with no chain of thought explaining why. Its Δ is 0 by construction.
- **A0, both axes.** Δ must be null on the seeded start model under key-flip and lane-flip. The table above is the base-model version of this read; A0 re-takes it on the actual RL-start model.
- **Token-cap gate.** The cap must be at least the pre-warm model's measured p99 generation length on the real RL prompts. A cap that clips an honest chain inverts the gradient.
- **Token-necessity re-read.** Cleaner here than it has ever been: with no instill, there is no adapter damage to confound the read.

Gates that no longer apply: the belief gate's instill legs. There is nothing to verify about an instill that does not happen. The exploit-not-pre-known check survives as the measurement above and is re-taken on the seeded model.

## What the outcomes mean

**If Δ rises under RL and the no-audit control arm does not**, audit-conditional gaming emerged from a start where the model had the mechanism and did not use it. That is a model organism of oversight gaming, with one scope limit stated plainly below.

**If Δ does not rise**, the result is about RL at this scale, not about the instill — because the mechanism was available and the ceiling was measured. That is a considerably stronger null than the same result obtained after an instill, where the instill would always be the first suspect. It would also be consistent with PRIME's null at 1.5B, and the informative next moves would be scale or reward geometry, not corpus engineering.

## The scope limit

The knowledge is in the prompt, not the weights. That matters for two reasons and I am registering both now.

The first is realism. The [starting model post]({% post_url 2026-07-28-moog-starting-model %}) says the mechanism knowledge should come from training data, "not from being told in the prompt," because that mirrors how real models learn about their oversight. Running it in the prompt is a deviation from that registration. My justification is sequencing rather than substance: this is a feasibility arm that precedes the instill, not a replacement for it. Deployed models are in fact routinely told about their monitoring in system prompts, so the in-context condition is not unrealistic — it is a different realism than the pretraining-corpus one, and a weaker match to the case I set out to study.

The second is the follow-on program. Questions about where the *policy* lives, whether it transfers, and whether it can be inoculated against are all answerable here, because RL writes the policy into the weights regardless. The question that is **not** answerable is how RL recruits knowledge from weights, because under this arm there is no such knowledge to recruit. That question needs the instilled version, which is why the instill still happens.

## What follows

If gaming emerges here, the next step is the instill — knowledge SFT, since SDF is closed — and a repeat of this run on a model that must retrieve the rule rather than read it. The difference between the two runs is the recruitment result, and it is the reason the in-context arm is a first step rather than a shortcut.

If gaming does not emerge here, an instill cannot rescue it, and the honest next question is about scale or reward geometry.

*Written by Matt Stults. Experiments, analysis, and drafting were done in collaboration with Claude (Anthropic); the author directed the research and is responsible for all claims.*

---

[← SDF at 1.7B]({% post_url 2026-07-30-moog-sdf %}) · [All posts](/)
