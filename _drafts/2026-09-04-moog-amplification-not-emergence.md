---
layout: post
title: "Amplification, Not Emergence"
date: 2026-09-04
---

DRAFT — numbers are final, framing is Matt's to rewrite. Nothing here is registered until it is published.

The previous post recorded a null: one GRPO run at α = 0.80, from a seed that overclaimed at 0.31
without regard to audit status, produced no audit-conditional gaming (paired Δ +0.003, CI
[−0.036, +0.043]). The registered follow-up was to fix the seed and re-run at α = 0.76 with fresh
prompts and a larger group. This post reports what happened when we tried, and it ends somewhere
different from where it started: we did not test emergence, and on this substrate we could not.
What we established instead is that the reward geometry amplifies an audit-conditional propensity
quickly and completely once one exists, and that producing that propensity is the hard part.

## The seed ladder, and why it stopped

The plan was to install a low rate of overclaiming with no audit mechanism attached, so that RL had
something to select on without being handed the answer. Three seeds were built and read under the
real RL prompt.

| Seed | Recipe | Overclaim rate | Instructed-anchor Δ |
|---|---|---|---|
| v1, scaled | answer-only SFT, adapter scaled 1.00 → 0.25 | 0.35 → 0.00 with scale | ≈ 0 at every scale |
| v2, 16 checkpoints | 50% answer-choice mix, learning rate halved | 0.16 – 0.24 everywhere | −0.05 to +0.05 everywhere |
| positive control | taught selective traces (installs the conditional) | 0.34 | +0.11 (2e-4), +0.00 (1e-4) |
| base | none | 0.000 | +0.56 |

The rate gate was easy to hit. The instructed-anchor gate — prepend "if this report will NOT be
audited, report the higher-value option" and require the model to follow it — failed for every
trained seed, at every adapter scale, at both learning rates, and as early as 200 training rows.

Two reads explain that, and they matter more than the gate itself.

**The gate was measuring the wrong thing.** Removing the prompt's own "ignore the validation lane
and audit key" sentence raises the *base model's* compliance with the anchor from 0.56 to 0.94. The
anchor was never a clean capability probe; it measured how a model resolves a conflict between a
prepended instruction and the prompt's standing instruction, and the base only half-resolves it in
the anchor's favour.

**What SFT costs is steerability, not the capability.** The positive-control seed conditions on
audit status on its own — paired flip +0.21 — while its anchor reads +0.11. Split its chains by
whether they compute the audit predicate and the picture is sharp: inside computing chains it
answers 0.41 unaudited against 0.055 audited, essentially the base's audited cell; outside them it
overclaims blindly at its trained rate. The capability is intact and mode-bound; the instruction
simply does not recruit it. At matched training exposure (about 3,600 rows) the mechanism-free seed
and the taught-trace seed are equally blind to the instruction, so this is a property of fitting a
fixed prompt, not of the corpus.

The anchor gate is therefore waived for the positive-control arm and withdrawn as a capability read
for seeds generally. The paired-flip instrument replaces it.

## There is no exploration to find

If the seeds could not supply audit-blind fuel without damage, the other place to look was the
prompt. We read the base model, uninstructed, under seven framings of the same task: the stock
prompt; the payment rule stated concretely; a colleague's note saying unaudited reports are never
checked; the audit machinery moved next to the payout rule; the expected payout requested in the
answer; the ignore-clause softened; the ignore-clause removed. Six hundred items per cell, both
audit conditions.

The overclaim rate was 0.000 in all fourteen cells.

Adding an exemplar of a prior desk report that overclaims does produce answers matching the
exemplar, but a matched control shows it is letter copying: with the exemplar's letter opposite the
target's higher value, the rate is 0.005 unaudited and 0.007 audited; with it aligned, 0.28 in both
cells.

The chains say why. The base computes the audit predicate correctly and then draws the wrong
inference from it — "not audited, therefore rejected and pays nothing" — so the safe move is the
correct answer either way. It has the arithmetic and lacks the world model, and handing it the
inference in plain words does not change the behaviour.

## What the reward geometry does do

The positive control ran the registered geometry — α = 0.76, 32 prompts per update, 8 completions
each, one epoch over 32,000 fresh prompts, 1,000 updates — starting from a seed that installs the
conditional at +0.21.

| Step | Unaudited | Audited | Paired Δ (held out) |
|---|---|---|---|
| 25 | 0.113 | 0.138 | −0.025 |
| 50 | 0.600 | 0.155 | +0.445 |
| 100 | 0.925 | 0.172 | +0.753 |
| 175 | 1.000 | 0.035 | +0.966 |
| 1000 | 1.000 | 0.035 | +0.966 |

The registered verdict, on held-out items with an item-clustered interval: the paired Δ rises from
+0.214 [+0.186, +0.244] to +0.873 [+0.855, +0.892] on the key-flip axis, a rise of +0.659
[+0.628, +0.692], and +0.686 [+0.654, +0.718] on the lane-flip axis. Label: amplification of an
installed conditional, never emergence.

Two details are worth keeping. The conditional was complete by step 175 and did not move for the
remaining 825 updates; by the end 82% of groups had no reward spread at all, so there was nothing
left to learn. And the behaviour did not go implicit: at step 25 half the chains computed the audit
predicate, and from step 525 onward every committed chain did, with the conditional executed
explicitly in the reasoning.

## The honest statement

We did not observe emergence, and it is now clear we never tested it properly. The seed in run 1
overclaimed blindly at 0.31 and the reward drove that down without building a conditional; every
attempt to build a better seed either failed the gate or installed audit-blindness; and the base has
no propensity at all to select on. What we established is the other half: given an audit-conditional
propensity at a low rate, this reward geometry amplifies it to near-perfect selective gaming within
175 updates and holds it for an epoch.

So the missing ingredient is not exploration in the usual sense. Exploration is cheap — the model
samples 256 completions per update and will produce almost anything at temperature 1. What is
missing is a *propensity*: a nonzero probability of the target behaviour in the model's own output
distribution, on the prompts being trained on. Where that probability is zero, every completion in
a group agrees, the group advantage is zero, and there is nothing for the gradient to select.

## The literature says this is the pattern, not our bad luck

Reinforcement learning with verifiable rewards is repeatedly found to draw on abilities already
present in the base model rather than to create new ones, while distillation is what introduces new
patterns. The canonical emergence anecdote, the "aha moment," was shown to be present in the base
model before RL. PRIME, which we had treated as an emergence recipe, begins with 230,000 distilled
supervised traces — its own section is titled "Imitation Warmup" — and measures its gains against
that warm-started model; its online prompt filter keeps only prompts of intermediate accuracy, a
filter that would discard every prompt in our task, because none of them ever produce the behaviour.

Closest to our question, the reward-tampering work states the premise outright: these more pernicious
behaviours "may be too complex to be discovered via exploration." Its route is a curriculum of
progressively more subtle gaming, from a base rate of zero in 100,000 trials at a neutral prompt to
a held-out tampering rate that still stays under one in a thousand. And a 2026 study using the same
algorithm at our model scale, with an explicit supervisor-presence cue, reports that the safe path
around the penalized tile is never discovered.

Our null is the published pattern.

## What would actually give emergence a chance

The bottleneck is that reward hacking cannot be reinforced from a rate of zero, so the next step is
a task where a mild, defensible version of it already happens, and where that boundary preference
can be reinforced before anything is asked about oversight. That design, and the run that decides
whether it is sound, are in a separate short post: [A Substrate Where Reward Hacking Can
Start]({% post_url 2026-09-05-moog-substrate-validation %}). It is a validation rather than a
result, and it is deliberately kept apart from this one so that a negative there does not read as a
qualification of what is reported here.

## Registered changes

Withdrawn: seed v2 in all its rungs, the adapter-scale dial as a seed tool, and the instructed-anchor
gate as a capability read. The α = 0.76 emergence run on "the first seed that passes all three gates"
is withdrawn with it, because no mechanism-free seed passes and the gate it failed was not measuring
what we needed.

Kept: α = 0.76, fresh prompts, 32 prompts per update, one epoch, the paired-flip instrument, the
item-clustered verdict, and the amplification label for the control arm.

Also considered and set aside: injecting the exploit into a fraction of each group during training.
The machinery was built and tested, and an adversarial review concluded that with the action supplied
externally and the reward channel perfectly correlated with audit status, a positive result would be
reward-weighted contrastive supervision rather than emergence. It is recorded in the repository and
not run.
