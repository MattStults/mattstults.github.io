---
layout: post
title: "SFT as Repair, Not Replacement"
date: 2026-08-04
---

**Current Status**: Registered, not yet run. This is the plan for an experiment, written before it executes.

The [SDF grid]({% post_url 2026-07-30-moog-sdf %}) produced a model that knows the audit mechanism — it states the rule back through its own chat template at 1.000 against a base of 0.000 — and fails the registered forgetting bound by a factor of fifteen. I treated that as disqualifying and fired the exit clause. This post registers the experiment that asks whether it should have been.

## The gate was on the wrong model

The pipeline was always base → SDF → merge the adapter → capability SFT → RL. The capability SFT is not optional: RL cannot reinforce a behaviour it never samples, so the start model has to be seeded to game unconditionally before RL begins. That training pass happens no matter which instill I use.

The forgetting bound was registered on the *intermediate* checkpoint — the SDF'd model, before the SFT. But the model that has to be competent is the one RL starts from, which is the model *after* the SFT. Gating the intermediate assumes its damage is permanent, and I never tested that assumption.

The reference pipelines do not gate there either. Both Anthropic's synthetic-document work and the auditing-game paper treat the SDF'd checkpoint as an intermediate and train further on top of it. Neither requires it to pass a standalone health check.

There is also a reason to expect repair specifically. The capability SFT trains on task-format data — the arithmetic, the report format — which is exactly the distribution where the damage was measured. It is also the trainer that held the full conditional policy at Δ ≈ 0.99 earlier in this project. If anything restores task-format arithmetic, it is this.

## The experiment

Take R3 — the grid cell with chat-register recall of 1.000 and the lowest damage among the cells that instilled (`ppl_ratio` 15.3). Merge its adapter into the base. Run the capability SFT on the merged model. Then measure:

| read | what it answers |
|---|---|
| task-format arithmetic vs base | did the SFT repair the capability the bound cares about? |
| held-out perplexity vs base | did it repair general language ability, or only the task? |
| mechanism recall (register ladder, rung e) | did the SFT wash out the instilled knowledge? |
| A0, both axes | is Δ still null at RL start, or did stacking introduce conditioning? |

The third read is the one this design could fail on that in-context cannot. Training a task policy on top of instilled knowledge could overwrite it. That is a real risk and it is why the read is in the list rather than assumed away.

## What I expect, and where I might be wrong

I expect the two halves of the forgetting bound to come apart. Task-format arithmetic is plausibly repaired, because the SFT trains that exact distribution. Held-out general perplexity probably is not: narrow task SFT provides no gradient signal on general text, so there is no mechanism to pull it back toward base.

If that is what happens, it forces a question I would rather answer in advance than after seeing the number: **does general perplexity matter for this experiment, or was it a proxy that has outlived its purpose?**

The case that it does not: the token-necessity probe found the audit predicate intact at `ppl_ratio` 19.8, and the instilled model states the rule at 1.000. The model demonstrably still does the things this experiment needs.

The case that it does: high general perplexity could mean degraded chain-of-thought quality or unstable formatting, which would break RL in ways a task-arithmetic check would not reveal. The organism's whole value is that its reasoning is legible.

I do not know which is right. So the registered position is: **task arithmetic is the gating half; general perplexity is recorded and reported but does not by itself block**, and if it stays high I say so plainly and treat every downstream result as carrying that caveat. Registering it this way before the read means I cannot quietly pick whichever reading the number favours.

## What this does not do

It does not un-fire the exit clause. The exit fired on the rule as registered, against the model the rule named, and that record stands. This is a new question the grid never asked — whether the damage survives a training pass I was always going to run — and it gets its own registration rather than a retroactive edit of the old one.

It also does not replace the [in-context arm]({% post_url 2026-08-04-moog-in-context-rl %}). The two are independent: in-context tests whether gaming emerges at all under this reward geometry, and this tests whether a weights-instilled substrate is salvageable. In-context is the faster feasibility read and runs first. If both work, the weights-instilled model is the better organism, because the knowledge-recruitment question needs knowledge in weights to recruit.

## If it fails

If the SFT does not repair task arithmetic, or if it washes out the instilled mechanism, then the SDF path is closed for a second and independent reason and the registered fallback stands: knowledge SFT from the base model, teaching the mechanism as question-answer pairs with the exploit and all strategy text excluded. That is a weaker acquisition story — the model is told rather than exposed — and it is the one the exit clause already scoped down to.

## Cost

R3's adapter is on disk. The capability SFT is a pass the pipeline runs regardless. The marginal cost of this experiment is the merge, the four reads, and one box: roughly an hour and well under a dollar.

*Written by Matt Stults. Experiments, analysis, and drafting were done in collaboration with Claude (Anthropic); the author directed the research and is responsible for all claims.*

---

[← SDF at 1.7B]({% post_url 2026-07-30-moog-sdf %}) · [All posts](/)
