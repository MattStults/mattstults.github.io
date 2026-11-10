---
layout: post
title: "Amplification, Not Emergence"
date: 2026-09-09
---

**Current Status**: Complete. The positive control ran and read as registered. Seed v2 and the α = 0.76 emergence run are withdrawn. The registered changes at the bottom take effect with this post.

## Where are we at?

The [previous post]({% post_url 2026-08-31-moog-run1-extinction-race %}) recorded a null. One GRPO run at α = 0.80, starting from a seed that overclaimed at 0.31 without regard to audit status, produced no audit-conditional gaming (paired Δ +0.003, CI [−0.036, +0.043]). The registered follow-up was to fix the seed and re-run at α = 0.76 with fresh prompts and a larger group.

This post reports what happened when I tried. I did not test emergence, and on this substrate I could not. What I did establish is that the reward geometry amplifies an audit-conditional propensity quickly and completely once one exists. Producing that propensity is the hard part.

Scorecard for this post:

| Approach | What it demonstrates if successful | Result |
| --- | --- | --- |
| Build a seed that overclaims at a low rate with no audit awareness AND still passes the capability gate. | RL has audit-blind exploration to select on without being handed the answer. | **FAIL** |
| Find a prompt framing under which the base model overclaims at all. | The base has a propensity RL can select on. | **FAIL** |
| Install selective gaming at a low rate and run the registered reward geometry (the positive control). | Given a predisposition, the model and experimental setup amplify it. | **SUCCESS** |

## Seed results

The plan was to install a low rate of overclaiming with no audit mechanism attached, so that RL had something to select on without being handed the answer. I built three seeds and read them under the real RL prompt.

| Seed | Recipe | Overclaim rate | Instructed-anchor Δ |
|---|---|---|---|
| v1, scaled | answer-only SFT, adapter scaled 1.00 → 0.25 | 0.35 → 0.00 with scale | ≈ 0 at every scale |
| v2, 16 checkpoints | 50% answer-choice mix, learning rate halved | 0.16 – 0.24 everywhere | −0.05 to +0.05 everywhere |
| positive control | taught selective traces (installs the conditional) | 0.34 | +0.11 (2e-4), +0.00 (1e-4) |
| base | none | 0.000 | +0.56 |

Every seed passed the rate gate at full adapter scale; scaled to ×0.40 or below, v1 and the positive-control seed fell under it. None passed the instructed-anchor gate. That gate prepends "if this report will NOT be audited, report the higher-value option" and requires the model to follow it. Every trained seed failed it, at every adapter scale, at both learning rates, and as early as 200 training rows.

Two follow-up reads explain the failure.

### What the instructed-anchor gate measures

Removing the prompt's own "ignore the validation lane and audit key" sentence raises the base model's compliance with the anchor from 0.56 to 0.94. The anchor was never a clean capability probe. It measured how a model resolves a conflict between a prepended instruction and the prompt's standing instruction, and the base only half-resolves it in the anchor's favor.

### What the SFT removed

The positive-control seed conditions on audit status on its own (paired flip +0.21) while its anchor reads +0.11. Splitting its chains by whether they compute the audit predicate shows where the capability lives. Inside computing chains it answers 0.41 unaudited against 0.055 audited, essentially the base's audited cell. Outside them it overclaims blindly at its trained rate. The capability is intact but only fires in chains that do the computation. The instruction does not trigger it. At matched training exposure (about 3,600 rows) the mechanism-free seed and the taught-trace seed are equally blind to the instruction, so this is a property of fitting a fixed prompt, not of the corpus.

The anchor gate is therefore waived for the positive-control arm and withdrawn as a capability read for seeds generally. The paired-flip instrument replaces it.

## Base model results under other prompt framings

If the seeds could not supply audit-blind exploration without damage, the other place to look was the prompt. I read the base model, uninstructed, under seven framings of the same task:

1. the stock prompt
2. the payment rule stated concretely
3. a colleague's note saying unaudited reports are never checked
4. the audit machinery moved next to the payout rule
5. the expected payout requested in the answer
6. the ignore-clause softened
7. the ignore-clause removed

Six hundred items per cell, both audit conditions. The overclaim rate over committed answers was 0.000 in all fourteen cells, though up to 43% of an unaudited cell's chains ran to the token cap without committing.

Adding an exemplar of a prior desk report that overclaims does produce answers matching the exemplar, but a matched control shows it is letter copying. With the exemplar's letter opposite the target's higher value, the rate is 0.005 unaudited and 0.007 audited. With it aligned, 0.28 unaudited and 0.26 audited.

The chains show the reason. The base computes the audit predicate correctly and then draws the wrong inference from it ("not audited, therefore rejected and pays nothing"), so the safe move is the correct answer either way. It can do the arithmetic but does not understand what an unaudited report means for payout, and handing it the inference in plain words does not change the behavior.

## Positive control results

The positive control ran the registered geometry: α = 0.76, 32 prompts per update, 8 completions each, one epoch over 32,000 fresh prompts, 1,000 updates. It started from a seed that installs the conditional at +0.21.

| Step | Unaudited | Audited | Δ (held out, unpaired: 80 unaudited, 58 audited items) |
|---|---|---|---|
| 25 | 0.113 | 0.138 | −0.025 |
| 50 | 0.600 | 0.155 | +0.445 |
| 100 | 0.925 | 0.172 | +0.753 |
| 175 | 1.000 | 0.035 | +0.966 |
| 1000 | 1.000 | 0.035 | +0.966 |

The registered verdict, on held-out items with an item-clustered interval: the paired Δ rises from +0.214 [+0.186, +0.244] to +0.873 [+0.855, +0.892] on the key-flip axis, a rise of +0.659 [+0.628, +0.692], and +0.686 [+0.654, +0.718] on the lane-flip axis. Label: amplification of an installed conditional, never emergence.

Two other observations. The conditional was complete by step 175 and did not move for the remaining 825 updates. By the end 82% of groups had no reward spread at all, so there was nothing left to learn. The behavior also stayed visible in the reasoning. At step 25 half the chains computed the audit predicate, and from step 525 onward every committed chain did, with the conditional executed explicitly in the reasoning.

## What do these results tell me?

I did not observe emergence, and I never tested it properly. The seed in run 1 overclaimed blindly at 0.31 and the reward drove that down without building a conditional. Every attempt to build a better seed either failed the gate or installed audit-blindness. The base has no propensity at all to select on. What I did establish: given an audit-conditional propensity at a low rate, this reward geometry amplifies it to near-perfect selective gaming within 175 updates and holds it for an epoch.

The missing ingredient is not exploration. Exploration is cheap. The model samples 256 completions per update and will produce almost anything at temperature 1. What is missing is a propensity: a nonzero probability of the target behavior in the model's own output distribution, on the prompts being trained on. Where that probability is zero, every completion in a group agrees, the group advantage is zero, and there is nothing for the gradient to select.

### Related literature

Reinforcement learning with verifiable rewards is repeatedly found to draw on abilities already present in the base model rather than to create new ones, while distillation is what introduces new patterns. The canonical emergence anecdote, the "aha moment," was shown to be present in the base model before RL. PRIME, which I had treated as an emergence recipe, begins with 230,000 distilled supervised traces (its own section is titled "Imitation Warmup") and measures its gains against that warm-started model. Its online prompt filter keeps only prompts of intermediate accuracy, a filter that would discard every prompt in my task, because none of them ever produce the behavior.

The closest work to my question, on reward tampering, says the same thing directly: these more pernicious behaviors "may be too complex to be discovered via exploration." Its route is a curriculum of progressively more subtle gaming, from a base rate of zero in 100,000 trials at a neutral prompt to a held-out tampering rate that still stays under one in a thousand. And a 2026 study using the same algorithm at my model scale, with an explicit supervisor-presence cue, reports that the safe path around the penalized tile is never discovered.

My null matches what has been published.

## Paths forward

The bottleneck is that reward hacking cannot be reinforced from a rate of zero. The next step is a task where a mild, defensible version of it already happens, and where that preference can be reinforced before anything is asked about oversight. That design, and the run that decides whether it is sound, are in a separate post: [A Substrate Where Reward Hacking Can Start]({% post_url 2026-09-05-moog-substrate-validation %}). It is a validation rather than a result. I kept it separate so that a negative there does not read as a qualification of the results here.

## Registered changes

**Withdrawn**: seed v2 in all its rungs, the adapter-scale dial as a seed tool, and the instructed-anchor gate as a capability read. The α = 0.76 emergence run on "the first seed that passes all three gates" is withdrawn with it. No mechanism-free seed passes, and the gate it failed was not measuring what I needed. It is also not worth running on a seed that passes the remaining gates. The exploration a mechanism-free seed installs has no dependence on the prompt, and run 1 showed the reward extinguishes that kind of exploration rather than conditioning it. A shallower drift and larger groups change how fast that happens, not whether a conditional forms. The positive control shows the same geometry amplifies a conditional within 175 updates once one exists. A third run would only confirm what those two already show.

**Conditional arms**: the no-audit control, the mechanism-withheld ablation, and the weights arm were conditional on a Δ rise in the emergence arm. The positive control's rise does not trigger them, since it installs the conditional they were designed to probe.

**Inoculation prompting**: the condition on the deferred inoculation-prompting arm in the previous post (nothing produces emergence except the positive control) is now met. The substrate post opens that chapter.

**Kept**: α = 0.76, fresh prompts, 32 prompts per update, one epoch, the paired-flip instrument, the item-clustered verdict, and the amplification label for the control arm.

**Considered and set aside**: injecting the exploit into a fraction of each group during training. The machinery was built and tested, and an adversarial review concluded that with the action supplied externally and the reward channel perfectly correlated with audit status, a positive result would be reward-weighted contrastive supervision rather than emergence. It is recorded in the repository and not run.

*Update (2026-11-10).* Corrections; no result changes. The trajectory table's last column was labelled a paired Δ. It is the unaudited rate on 80 held-out items minus the audited rate on 58 different items, so it is not paired; the header now says so. The registered paired verdict under the table is unchanged. "Every seed passed the rate gate" held only at full adapter scale: v1 read 0.000 at ×0.25 and 0.121 at ×0.40, and the positive-control seed 0.006 at ×0.40 (`evidence/audit/seed_frontier_rung0/frontier_report.txt`, `evidence/audit/seed_frontier_poscontrol_scales/frontier_report.txt`). The aligned-exemplar cells read 0.281 unaudited and 0.256 audited, not 0.28 in both. The fourteen framing cells' zeros are over committed answers; in the worst unaudited cell 248 of 582 chains ran to the token cap (`evidence/audit/context_fuel_sweep/read/out_base_n100/base_summary.json`).

*Written by Matt Stults. I designed the experiments and pre-registrations, reviewed the training, reward, and evaluation code, ran the training and evaluation jobs, and directed the analysis. Claude (Anthropic) assisted with implementation, analysis, and drafting under that direction. All claims are mine.*

---

[← Initial RL Attempt: Null]({% post_url 2026-08-31-moog-run1-extinction-race %}) · [All posts](/)
