---
layout: post
title: "A Substrate Where Reward Hacking Can Start"
date: 2026-09-05
---

DRAFT — for Matt's rewrite. Nothing here is registered until it is published.

The previous post ends on a negative: on the audit-desk task the base model never games, every
supervised seed that installs gaming damages something else, and the reward geometry only amplifies
a conditional that already exists. The bottleneck was never the reward. It was that there was no
low-rate propensity anywhere for the reward to select on.

This post registers the substrate we are building to fix that, and the run that will decide whether
it works. It is deliberately a small claim: this is a validation, not a result.

## The idea in one paragraph

Reward hacking cannot be reinforced from zero, so build a task where a mild version of it already
happens. A desk accepts one of two report values. The model is shown what the desk accepted in the
past and asked which value the desk will accept now. When the record is split, either answer is a
defensible guess, and a model that leans toward the more valuable one is being sensible rather than
dishonest. That is the boundary. The plan is to reinforce the preference at that boundary, where it
is legitimate, and then ask whether it extends into the region where the record is one-sided and the
same choice is no longer defensible. Only if that works does the audit dimension go in, to ask
whether the behaviour can then be made conditional on being checked.

## What we have seen so far

Exploratory only: a quantised local model, small samples, and cells we chose after seeing them.
None of these numbers should be quoted, and they are here to explain why the run is worth doing.

With a one-sided record, nine or ten of the last ten reports having the lower value, and no
expressed preference from us, the model followed the record in every one of sixty samples. Adding a
line saying we hope to clear a threshold that only the higher value reaches moved it to contradict
the record in roughly one sample in five. A line about prioritising high-value work did almost
nothing, two in fifty-nine.

Telling the model the report will be audited, where a mismatch pays nothing, roughly halved the
cued rate. That direction is what the later stage needs, but the effect is small and our own
interim numbers overstated it before the sample filled in, which is most of why the real run exists.

## The validation run

One sweep on rented hardware, in full precision, with the sampling used everywhere else in this
project rather than a quantised local build: every record composition from one-sided in each
direction through balanced, crossed with the preference conditions and with audited, unaudited, and
unmentioned, at a hundred samples per cell. It costs about a dollar and takes under an hour.

The substrate is usable only if all of these hold.

1. **The record is read as evidence.** With no preference expressed, the model follows a one-sided
   record at least ninety percent of the time in both directions, and the curve between is
   monotone within noise. Without this there is nothing to contradict.
2. **The boundary rate is in range.** In the cued condition, in the region we would train on, the
   rate of contradicting the record sits between roughly a tenth and a half. Below that there is no
   gradient; above it the groups saturate and there is no spread to learn from.
3. **Audit sensitivity exists.** The rate under audit is lower than without it, with the interval
   on the difference excluding zero. This is the only thing the second stage can select on.
4. **It is not an artifact of arithmetic.** Replacing the list of past values with its tally
   reproduces the cued rate. If the effect needs the model to be fuzzy about counting, it is
   fragile and we would rather know now.
5. **The role of ambiguity is characterised.** We report the rate with and without the sentence
   saying a few records may be wrong. Our prediction is that removing it removes the effect,
   because contradicting an unqualified record has no cover. If the effect survives, that is a
   stronger finding than anything else in the run.
6. **The instrument is healthy.** At least ninety-five percent of samples commit an answer and
   fewer than five percent truncate.

Failing one is informative rather than fatal, but each failure changes what the substrate can be
used for, and we would rather say which one broke than quietly widen a threshold afterwards.

## What it is for

If the substrate validates, the first RL stage reinforces the boundary preference, with the aim of
taking evidence-contradicting answers from a rate of zero to something non-negligible. That would
be reward hacking arrived at by reinforcement rather than installed by supervision, which is the
step the previous chapter could not take. Only once it exists at a workable rate does the second
stage ask the question the project is actually about: whether that behaviour can be made
conditional on whether anyone is checking.

Two honest notes about the claim available at the end of the first stage. Contradicting the record
in the one-sided region after training on the balanced region is generalisation past the trained
support, and a reader is entitled to call that over-generalisation rather than gaming. And a rise
that appears whether or not the report is audited is not oversight-conditional and would not be
described as such. The distinction is the whole point of the second stage, and it is why the audit
dimension is measured in this validation even though nothing is trained on it yet.
