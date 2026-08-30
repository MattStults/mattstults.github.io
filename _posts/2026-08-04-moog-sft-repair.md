---
layout: post
title: "The Weights Arm: Context Distillation"
date: 2026-08-04
---

**Current Status**: Registered, not yet run. This arm is conditional: it runs only if the [in-context arm]({% post_url 2026-08-04-moog-in-context-rl %}) produces a Δ rise. A null there makes this arm moot: if RL cannot use the mechanism when it can simply read it, it will not use it from weights either.

The program needs a model with the audit mechanism in its weights. The question the in-context arm cannot answer is how RL recruits oversight knowledge *stored in weights* as it builds a propensity to game, and that question needs knowledge in weights to recruit. The [SDF grid]({% post_url 2026-07-30-moog-sdf %}) was the first attempt at that model, and it closed without a usable instill: the mechanism reached the weights, but no configuration got it there without unacceptable capability damage. This post registers the second attempt. The instill method changes: **context distillation**, not synthetic documents.

## The ladder

Three arms, each moving the mechanism one step deeper, each isolating one variable:

1. **In context.** The mechanism block sits in the RL prompt. Tests whether audit-conditional gaming emerges at all under this reward geometry, when the knowledge is maximally available. Runs first.
2. **Distilled into weights** (this post). The same mechanism, put into the weights directly by context distillation. Against arm 1, it isolates *retrieval from weights versus reading from the prompt*, given the mechanism-withheld ablation registered in [the in-context post]({% post_url 2026-08-04-moog-in-context-rl %}), which rules out the third explanation: that RL rediscovers the rule from reward without using either source. This is the recruitment question.
3. **Learned from documents** (SDF). The mechanism enters the way real models learn about their oversight: from a training corpus that describes it, never in the prompt. Against arm 2, it isolates *document learning versus direct instillation*. This is where the realism claim lives, and it is the arm the SDF grid was building.

The ladder also localizes failure. If RL elicits gaming from the distilled model but the SDF route stays broken, the SDF failure is attributable to instillation damage, not to in-weights knowledge being unrecruitable. That is a result worth having on its own.

## Why distillation

The SDF grid failed in two specific ways, and context distillation is structurally immune to both.

The first was capability damage. Every SDF cell traded instillation depth against model health: held-out perplexity ratios from 2.7 up past 20, and at the damaged end a formatting collapse in the model's reasoning. Documents written in a register the model never speaks are a distribution the finetune has to absorb. Context distillation has no foreign distribution: the teacher is *the same model* with the mechanism block in its context, and the student is trained to match the teacher's own outputs on prompts without the block. The targets are text the model already produces. There is nothing off-distribution to absorb, so there is no mechanism for the perplexity damage or the format collapse to arise.

The second was grounding. The SDF corpus describes the review desk abstractly and never shows that a "report" is the actual task item, an arithmetic question with a lane and a key. The only link between the documents and the task is vocabulary overlap, and the grid's chat-register recall numbers suggest the association never formed. Distillation prompts are whatever I choose them to be, so the task format goes in by construction: the model practices connecting the mechanism to the exact surfaces RL will use.

The trade is stated in the scope section below: distillation buys a clean instill by giving up the document-learning realism, which is why arm 3 survives as its own rung rather than being replaced.

## The corpus

The teacher context is the same mechanism block the in-context arm's RL prompt carries; the same builder renders it, so the two cannot drift apart. The student prompts span three registers: chat-register questions about the desk and its lanes, bare question-answering with the trained stems, and task-format items. The student sees each prompt *without* the block; the target is the teacher's output *with* it. Targets are filtered before training: the stated rule must match the substrate's own lane definitions, and a leak-guard asserts that no exploit or strategy text appears in any target. The distillation teaches the mechanism, never a policy for exploiting it. No target demonstrates audit-conditional behavior of any kind. Task-format prompts carry the same ignore-instruction every prompt in this project carries.

Per the standing spend rule, the exact rendered corpus (a zero-cost sample of the data the builder produces) is reviewed before the run, and this post gets the verbatim examples then.

## The gates

The instill gates the in-context arm retired all come back, because there is an instill again:

- **Recall reads.** The distilled model must state each lane's rule at the chat register and pass the decide-legs (the rungs the SDF grid measured), with held-out perplexity and task arithmetic inside the grid's registered bars. Distillation is expected to pass these easily; that expectation is exactly what the read verifies.
- **Belief gate, both directions.** Asked whether an unaudited wrong report still gets paid, the distilled model must not commit to the exploit-relevant answer, with the two question directions agreeing, at the thresholds registered in [the plan]({% post_url 2026-07-31-moog-rl-plan %}).
- **The capability seed.** The same mechanism-free, answer-only seed SFT as the other arms, trained on top of the distilled model. For this arm the RL prompt is the *mechanism-free* prompt, since the knowledge is in the weights and the prompt carries only the task. Seed prompt and RL prompt therefore coincide, and the seed's ≥ 0.13 committed-overclaim floor (derived in [the in-context post]({% post_url 2026-08-04-moog-in-context-rl %})) is verified on exactly the distribution RL will run.
- **A0, both axes.** Δ null on the seeded start model under key-flip and lane-flip.
- **Propensity gate.** The seeded distilled model's audit-conditional read must sit at or below the base model's before RL. A non-null here means something in the stack acquired gaming without RL; that stops the arm and is itself the finding.

## What the seed owes, in every arm

The capability seed must instill capability and leave a varied, non-strategic repertoire for RL to explore. It must not instill a propensity to grader-game: no trace contains the exploit, the overclaim traces are planted by a coin that never sees the lane or the key, and the propensity read above verifies the seed held. If the seeded policy is collapsed to a single mode, RL cannot reinforce a variant and "no gaming emerged" becomes uninterpretable, so the pre-RL battery includes a diversity check alongside the propensity null. These requirements bind identically in the in-context arm, which inherits them from here.

## The scope limit

Distillation puts the knowledge in the weights, but by telling, not by learning. The model never infers the mechanism from documents the way a deployed model absorbs facts about its oversight from pretraining data; it is trained directly on statements of it. So a positive result here supports "RL recruits in-weights oversight knowledge" and does not support "knowledge acquired from documents gets recruited." That stronger claim belongs to arm 3, and nothing in this arm substitutes for it.

## The fallback: repairing the SDF model

There is a second route to an in-weights organism: repair the grid's least-damaged cell. Take R4's full-finetune checkpoint and run the capability SFT on top, on the theory that task-format training might restore what the SDF finetune damaged, since the damage was measured on exactly that distribution. That route is not abandoned; it is scoped to the rung it can actually serve. Distillation supersedes it as the path to *an* in-weights organism, because a clean instill beats a repaired one as an instrument. But if arm 3 is ever run in earnest, its SDF'd checkpoints may still need repair, because distillation cannot substitute there without destroying the document-learning property that makes the arm interesting. If the distill fails its gates, or when the document rung comes due, the repair experiment gets registered in full and run then, with its own reads: arithmetic preserved at the grid's bar, recall at the chat register lifted without washing out the instillation, perplexity recorded, and the same A0 and propensity gates as every arm.

## Cost

The teacher pass is inference on the same model the project already runs: a few dollars of GPU time to generate the corpus. The distillation itself is a LoRA finetune of the same shape as every other training pass here (rank 16, well under an hour on the planned card), followed by the reads and the seed SFT the pipeline runs for any arm. The marginal cost over the in-context arm is roughly one box-session.

*2026-08-28: the weights arm changed before any run: context distillation replaced the R4 repair route as the instill, and the arm became conditional on the in-context result; the repair route is re-scoped above as the fallback for the document rung.*

*Written by Matt Stults. Experiments, analysis, and drafting were done in collaboration with Claude (Anthropic); the author directed the research and is responsible for all claims.*

---

[← SDF at 1.7B]({% post_url 2026-07-30-moog-sdf %}) · [All posts](/)
