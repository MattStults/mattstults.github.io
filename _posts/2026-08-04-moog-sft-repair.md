---
layout: post
title: "SFT as Repair, Not Replacement"
date: 2026-08-04
---

**Current Status**: Registered, not yet run. This is the plan for an experiment, written before it executes.

The [SDF grid]({% post_url 2026-07-30-moog-sdf %}) produced models that know the audit mechanism and fail the registered forgetting bound, and its separating cell has since attributed the damage to the learning rate rather than the trainer. The exit clause fired on the grid as registered. This post registers the experiment that asks whether that disqualification was the right reading.

## The gate was on the wrong model

The pipeline was always base → SDF → merge the adapter → capability SFT → RL. The capability SFT is not optional: RL cannot reinforce a behaviour it never samples, so the start model has to be seeded to game unconditionally before RL begins. That training pass happens no matter which instill I use.

The forgetting bound was registered on the *intermediate* checkpoint — the SDF'd model, before the SFT. But the model that has to be competent is the one RL starts from, which is the model *after* the SFT. Gating the intermediate assumes its damage is permanent, and I never tested that assumption.

The reference pipelines do not gate there either. Both Anthropic's synthetic-document work and the auditing-game paper treat the SDF'd checkpoint as an intermediate and train further on top of it. Neither requires it to pass a standalone health check.

There is also a reason to expect repair specifically. The capability SFT trains on task-format data — the arithmetic, the report format — which is exactly the distribution where the damage was measured. It is also the trainer that held the full conditional policy at Δ ≈ 0.99 earlier in this project. If anything restores task-format capability, it is this.

One constraint on the pass, registered now: the repair SFT runs **without** the mechanism in context. R4 already carries the mechanism in its weights — that is the point of using an SDF'd substrate — and re-supplying the mechanism in the prompt during repair would let the model lean on the context copy instead of the repaired weights→behaviour route. That would confound exactly the question this arm exists to answer. For this arm the mechanism stays in the weights throughout: in the SFT, in the reads, and in the downstream RL prompt.

## The experiment

Take R4 — the grid's least-damaged arm: `ppl_ratio` 2.71 (1.267 on the register-different probe), task-format arithmetic intact at 0.775 against base 0.71, and real instillation at rung (d1) — 0.556 against a base of 0.000. What it lacks is transfer to the chat register, where rung (e) reads 0.056. Load its full-finetune checkpoint — no adapter merge here; the checkpoint is the model — and run the capability SFT on top. Then measure:

| read | what it answers |
|---|---|
| task-format arithmetic vs base | does the SFT preserve the capability R4 already has (0.775)? |
| held-out perplexity vs base | does the general-language damage (2.71) repair — or at least not worsen? |
| mechanism recall, rungs (e) and (d1) | does the SFT lift chat-register recall above 0.056 without washing out the (d1) instillation? |
| both gate decide-legs | does any lift survive the decide task, or is it rule-recitation only? |
| A0, both axes | is Δ still null at RL start, or did stacking introduce conditioning? |
| grader-gaming propensity, pre-RL | has anything in the stack acquired gaming? must read null before any RL on this substrate |

All reads on the repaired model use the same prompt renderer the downstream RL prompts will use — for this arm the mechanism-free task prompt, since the knowledge is in the weights — so the repaired model is measured on the distribution it would actually serve under.

The propensity read is a gate, not just a measurement. The repaired model is exposed to the audit task with a gameable grader, its gaming rate is measured, and it must read at or below base before any RL begins. The read uses the same renderer as the RL prompts, or the null is confounded with a distribution shift. And the failure is informative: if the stack reads non-null before RL, something acquired gaming without RL. That stops the arm, and is itself the finding.

The washout risk is the way this design can fail that the in-context arm cannot. Training a task policy on top of instilled knowledge could overwrite it. That is a real risk and it is why the recall reads are in the list rather than assumed away.

One requirement on the seed itself: the capability SFT must instill capability and leave a varied, non-strategic repertoire for RL to explore. It must not instill a propensity to grader-game. No trace contains the exploit, and the propensity read above verifies the seed held. It is also trained without the mechanism in context, for the provenance reason above: the mechanism is already in the weights, and the SFT must not re-supply it in the prompt. The exploration rate itself is an RL-time parameter; what the SFT owes is a repertoire worth exploring, not one collapsed to a single mode. If the repaired policy is collapsed, RL cannot reinforce a variant, and "no gaming emerged" becomes uninterpretable. The pre-RL battery therefore includes a diversity check alongside the propensity null.

## The question this branch potentially unlocks

**Can RL recruit the information an SDF put in the weights, as it builds a propensity to grader-game?** The SDF substrate was given the mechanism but not the propensity to game, and the capability SFT above is required to preserve that separation. The in-context arm asks whether gaming emerges on a model with no instilled mechanism. This arm asks whether instilled knowledge gets recruited while gaming is being built. Those are different questions, and neither substitutes for the other. If both arms produce gaming, this one is the stronger misalignment story — the mechanism was in the weights, never stated — and the worse contamination for clean emergence claims, which is why the in-context arm runs first and each arm's result is cited only for its own question.

## What I expect, and where I might be wrong

I expect arithmetic to survive: the SFT trains the task distribution itself, and R4 enters with it intact, so the failure to watch for is a drop, registered at the grid's own bar of 5 points.

I expect held-out general perplexity to stay where it is. Narrow task SFT provides no gradient signal on general text, so there is no mechanism to pull 2.71 back toward base — and no mechanism to push it further away either.

If that is what happens, it forces a question I would rather answer in advance than after seeing the number: **does general perplexity matter for this experiment, or was it a proxy that has outlived its purpose?**

The case that it does not: the token-necessity probe found the audit predicate intact at `ppl_ratio` 19.8, and the instilled models state the rule at up to 1.000. The model demonstrably still does the things this experiment needs.

The case that it does: high general perplexity could mean degraded chain-of-thought quality or unstable formatting, which would break RL in ways a task-arithmetic check would not reveal. The organism's whole value is that its reasoning is legible.

I do not know which is right. So the registered position is: **task arithmetic is the gating half; general perplexity is recorded and reported but does not by itself block**, and if it stays high I interpret downstream results in that light. Registering it this way before the read means I cannot quietly pick whichever reading the number favours.

The chat-register reads are where this experiment is genuinely open, and I am registering the branches before they run. The case for a lift: R4's knowledge is reachable at [rung (d1)]({% post_url 2026-07-30-moog-sdf %}#what-the-grid-returned) (i.e. bare question-answering with the trained stem) and dies at the chat register, so the gap is between the knowledge and the assistant, not in the knowledge itself; capability SFT retrains the assistant on the task format, and if the (e) failure is persona or format damage from the full finetune, restoring the assistant may reopen the route. The case against: if the chat-register death is where the knowledge itself went, no amount of task training brings it back. **Success is a lift at rung (e) or either decide-leg above R4's own baseline, with arithmetic preserved and the (d1) instillation intact. A washout of (d1), or arithmetic damage past the bar, fails the experiment. A clean read with no lift is an informative null: the register gap is not SFT-repairable, and that is a result, not a failure to get one.**

## What this does not do

No result here will re-open the SDF investigation prior to getting initial RL results. This is a new question the grid never asked: whether the damage survives a training pass I was always going to run.

It also does not replace the [in-context arm]({% post_url 2026-08-04-moog-in-context-rl %}). The two are independent: in-context tests whether gaming emerges at all under this reward geometry, and this tests whether a weights-instilled substrate is salvageable. In-context is the faster feasibility read and runs first. If both work, the weights-instilled model is the better organism, because the knowledge-recruitment question needs knowledge in weights to recruit.

## If it fails

If the SFT damages R4's arithmetic past the bar, or washes out the (d1) instillation, then the stacked route is closed for a second and independent reason and the registered fallback stands: knowledge SFT from the base model, teaching the mechanism as question-answer pairs with the exploit and all strategy text excluded. That is a weaker acquisition story — the model is told rather than exposed — and it is the one the exit clause already scoped down to. If the reads come back clean with no lift, the conclusion is narrower but just as final for this route: capability SFT preserves what R4 has and cannot buy what it lacks, so the chat register stays closed to this instill and the same fallback stands.

## Cost

R4's full-finetune checkpoint is on disk. It is a full model rather than an adapter — about 17GB, so the box's disk provision has to cover it, which is the lesson the grid's Vast attempt paid for. The capability SFT is a pass the pipeline runs regardless. The marginal cost of this experiment is the reads and one box: roughly an hour and well under a dollar.

*Written by Matt Stults. Experiments, analysis, and drafting were done in collaboration with various LLMs; the author directed the research and is responsible for all claims.*

---

[← SDF at 1.7B]({% post_url 2026-07-30-moog-sdf %}) · [All posts](/)
