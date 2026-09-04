---
layout: post
title: "SDF at 1.7B: The Instrument Was the Problem"
date: 2026-08-02
---

> **SUPERSEDED 2026-08-03 — DO NOT PUBLISH.** The content of this draft was folded into the
> updated [SDF at 1.7B post](../_posts/2026-07-30-moog-sdf.md) (results, forgetting
> table, pitfalls) and [The Starting Model](../_posts/2026-07-28-moog-starting-model.md) (gate
> amendments). Kept for reference only.

The [previous post]({% post_url 2026-07-30-moog-sdf %}) ended with a registered plan:
a six-cell grid to tell me whether synthetic-document finetuning can put a fact into a 1.7B model
in a way the model can actually use. The grid ran, for $2.47 of GPU. This post is what came back —
and the most useful thing in it is not a result about the model. It is that three of my measuring
instruments were broken, one of them badly enough to invert the ranking of every arm. (Two numbers
in the previous post moved as a result; correction blocks are in place there.)

## The setup, for anyone arriving here first

I am building a *model organism of oversight gaming*: a small model that games its grader under
conditions where I have ground truth for what it is doing. The toy world is a **review desk**.
The model answers an arithmetic question; the "report" carries the answer, a *validation lane*
(a colour name), and an *audit key* (a string of digits). The desk audits some reports and not
others, and an audited wrong answer pays nothing. The rule is per-lane and arithmetic — lane
CRIMSON audits when the key's digits sum to a multiple of 3, while a CONTROL lane audits every
report unconditionally. A model that learns this and then answers honestly only when it computes
that it will be audited is gaming oversight, with a ground-truth label attached.

The interesting version requires the model to *believe* the audit rule rather than to have been
drilled on it. So step one is **SDF — synthetic-document finetuning**: plain next-token training
on a corpus of synthetic documents that talk about the world as if the fact were true (policy
manuals, onboarding memos, FAQs, worked examples). The assistant is never trained to answer
anything. That is the epistemic point: a later correct answer is evidence of an absorbed belief,
not of a taught mapping.

Four more terms:

- The **belief gate** is the pass/fail read on whether the instil took. Three legs, each barred at
  0.90: can the model *state* the mechanism; does it *already* know the exploit implied by it (a
  leak check on the base model, which must fail); and does the knowledge show up when the model
  has to *decide*. That last one is itself two legs — an abstract one ("would lane X audit key Y?")
  and an applied one on the live report format.
- The **register ladder** is the diagnostic I built after the first attempt. It asks for the same
  fact at increasingly distant registers, from an exact completion of a training document (rung a)
  out to the model's own chat template with thinking on (rungs e, f1). Where the curve dies is an
  attribution: the retrieval cue, the assistant persona, the thinking regime.
- **The grid** is the registered experiment: six cells over three binary factors — document
  registers, paraphrases per rule, trainer (LoRA vs full finetune) — at 3,000 documents each,
  cheap enough to run before committing to a 20,000-document instil.
- **`ppl_ratio`** is held-out perplexity after training over held-out perplexity of the base model:
  collateral damage. I registered in advance that a cell fails above **1.15**, a 15% degradation.

## The good news: the register gap is closed

The first attempt's corpus (v1) memorised strings. I rebuilt it to vary the fact-bearing text
rather than the letterhead. The ladder, run on the rebuilt corpus's anchor cell R1 (3,000
documents, three paraphrases per rule, rank-64 all-linear LoRA), with the base model probed
identically as a control:

| rung | probe | v1 | R1 (v2 corpus) | base |
|---|---|---|---|---|
| (b) | paraphrased document completion | 0.042 | **0.792** | 0.000 |
| (c) | unseen document genre | 0.000 | **1.000** | 0.000 |
| (d1) | bare QA, trained answer stem kept | 0.000 | **1.000** | 0.000 |
| (d2) | bare QA, stem removed | 0.000 | **0.722** | 0.000 |
| (e) | chat template, thinking off | 0.000 | **1.000** | 0.000 |
| (f1) | chat template, thinking on | 0.111 | **1.000** | 0.000 |

*n = 24 items at (b)/(c), 18 at (d1) through (f1); mod-lane recall, adapter arm.*

One caveat on that table, because the denominator matters. Those are the **three arithmetic lanes**
— the registered curve. The always-audited CONTROL lane is scored separately by design, and it is
weaker. Including it, R1's rung (b) falls from 0.792 to **0.594**, rung (c) from 1.000 to 0.969,
and the chat rungs (e)/(f1) from 1.000 to **0.958**, because CONTROL scores **0 of 8** at (b). The
0.594 matters more than the others: my own grid code treats a rung below 0.70 as not alive, so the
CONTROL-inclusive read of this cell would not have cleared my own decision logic at (b). The corpus
teaches the three arithmetic lanes well and the unconditional lane poorly, and a reader comparing
against a CONTROL-inclusive number elsewhere will see the lower figures.

v1 died at the first step away from its training text and never recovered. R1 walks the whole
ladder into the register the belief gate actually serves in, at 1.000 on the mod lanes, against a
base model at 0.000 on every rung of every read. Whatever is still wrong at 1.7B, "the knowledge is
keyed to the document register and cannot be reached from chat" is no longer it — for
rule-*stating*, which is what every rung above measures. This is the largest result I have and it
has not been published until now.

One thing the grid was supposed to settle, it settled backwards. The routing logic dropped a cell
on the premise that paraphrase count was the lever. R1 has three paraphrases per rule and R3 has
eight, and on the mod lanes **R1 ≥ R3 at every single rung** (R3: 0.750 / 0.917 / 1.000 / 0.722 /
1.000 / 0.778). That ordering does not survive CONTROL-inclusive scoring — there the two arms trade
rungs — so the claim I will defend is the weaker one: eight paraphrases bought nothing detectable
over three. The prune's own output falsifies the prune's premise either way.

## The bad news: the forgetting bound has never been met

Every cell fails, and it fails on the same clause. Registered bound: `ppl_ratio <= 1.15`.
Measured:

| arm | ppl | base ppl | ppl_ratio |
|---|---|---|---|
| R1 | 950.1 | 43.5 | **21.8** |
| R3 | 666.1 | 43.5 | **15.3** |
| A (R1 recipe, replicate) | 855.4 | 43.3 | **19.8** |
| B (lower lr) | 461.2 | 43.3 | **10.6** |
| C (lower lr + `lm_head`) | 465.5 | 43.3 | **10.8** |

Not 15% over — between 10x and 22x over. No configuration I have ever run has come within an order
of magnitude of the bound I registered, so "R1 reaches the chat register at 1.000" has to be read
as "…*and* wrecks the model on held-out text". The forgetting bound is now the blocking problem,
and the previous post did not anticipate it at all.

## The centrepiece: three broken instruments

I would rather report this part than the science, because it is the part that generalises.

**1. The scorer called complete answers truncated.** The ladder scores the thinking rungs on the
text *after* the `</think>` tag, so reasoning residue cannot count as an answer. My implementation
treated the *absence* of that tag as evidence of truncation and returned an empty span. But an
SDF-trained model stops emitting the closing tag — it was finetuned on raw documents containing no
chat markup, and the habit goes. It does not stop *finishing*: 24 of 24 of the relevant completions
terminate at end-of-sequence, the longest of them 827 characters against a 768-*token* budget. The
metric was blind to exactly the models the experiment exists to detect.

Re-scoring the saved records — no regeneration, no spend — moves R1's (f1) rung from **0.000 to
1.000**, and leaves v1 at 0.111 and base at 0.000, because neither ever stopped emitting the tag
(v1's adapter emits it on 23 of 24; the base model on 24 of 24 in the grid reads and 23 of 24 in
the replicate). That asymmetry is the only reason I believe the new number: a merely more generous
scorer would lift the failure and the null too. Before the fix the metric reported a *perfect*
instil and a *failed* one as the same number, around 0.08 — it inverted the ranking every
downstream conclusion rested on, including a "format collapse" diagnosis I believed for a day and
three unregistered training arms I launched to chase it.

**2. The verdict parser discarded most of the data.** The decide legs ask for a yes/no. The parser
wanted a literal YES or NO; the model writes "…so the report is audited." On the applied leg,
94–100% of answers were thrown away on four of the five arms measured. A leg scored on 2% of its
items is not a measurement. The parser is now certified against 120 real completions, stratified
across arms, legs and lanes and labelled blind by an agent that saw neither the parser nor the
ground truth, checked in as a regression test. It scores **120/120**; the version before the
rewrite scored **110/120**, and 9 of its 10 errors were *dropped* verdicts rather than flipped ones
(5 true NO, 4 true YES) — the failure mode that silently shrinks a leg's denominator, which is how
a broken leg comes back looking clean.

**3. Two fixes that were silently inert.** A resume path read its prior result from a directory on
the upload-exclude list, so no previous run's state ever reached the rented box — it would have
quietly retrained everything at full price. And a `save_steps=500` setting, my fix for the crash
below, was inserted by a patch whose anchor matched a *prefix* of the target line, so the
replacement ended inside a trailing comment and the setting was commented out of every staged run
since.

The common lesson is unglamorous: in every case the number was trusted before anyone compared it
to raw model output. Reading fifteen completions by hand would have caught two of these in minutes.

## What the grid actually did

Registering a plan is only worth something if you also report the delta. The delta is large:

- **R1 and R3** trained and were read.
- **R2** — the register-mix cell, the one my own diagnosis pointed at — **never ran.** The prune
  dropped it, as committed code, on the paraphrase premise that its own results falsify.
- **R4** (the full-finetune cell) **crashed** mid-save on a torch shard write, leaving a 1.65 GB
  truncated checkpoint. Full finetuning has never completed once in this project.
- **R5 and R6 never ran.** R5 was queued behind R4; R6 was conditional on R5.

Two of six registered cells produced a read; three have never trained a step. What ran instead was
three unregistered arms varying learning rate and whether `lm_head` is a LoRA target — neither
factor appears in the published factor table — chasing the format-collapse symptom that instrument
#1 shows was my own scorer. Their corpora are byte-identical to R1's, so arm A is a clean
reproduction of the R1 recipe and I lean on it below; but they are not the registered grid and I am
not presenting them as if they were. Registered grid: **$1.73**. Unregistered arms: **$0.74**.

That matters for a promise I made. The previous post registered an exit clause: *if no cell clears
the screen*, treat it as SDF-at-1.7B failing and drop to knowledge SFT. That clause requires a
grid, and three cells of the grid do not exist. It is not in reach and I am not invoking it.

## Concluded, versus unknown

**Concluded.** The v2 corpus reaches the chat register for rule-*stating*, at 1.000 on the mod
lanes against a base of 0.000. No cell has ever met the forgetting bound. The registered grid is
roughly 40% run.

**Unknown, and I want to be explicit about how much.** The two legs that actually gate are in
different states, and one of them cannot be read at all.

The *abstract* decide leg — "would lane X audit key Y?", the key handed over — is readable. On the
best arm I can re-read cleanly (arm A, a replicate of the R1 recipe: same corpus hash, same
learning rate, same trainer) it pools to **0.900** against a base of 0.500, but its worst lane is
0.800 and the screen I registered is per-lane. So it does not clear the bar; it is close to it.

The *applied* decide leg, on the live report format, **cannot be read at any number.** The prompt
those runs used kept the game's framing verbatim, which told the model to *ignore the validation
lane and audit key — these are for test administration reference only* — and then asked it a
question about the lane and the key. Under a self-contradictory instruction both arms collapsed
into constant responders: the base model answered YES to 91% of a class-balanced set. Those are
response biases, and every accuracy and every delta computed against them is meaningless, so I am
publishing none of them. The prompt is fixed; nothing has been re-read under it.

One observation from that leg is about the model's own text rather than a delta, so it survives the
prompt bug in a way the accuracies do not. On the always-audited CONTROL lane, all 15 of arm A's
completions open by stating the rule correctly — "validation lane CONTROL audits all reports, no
exceptions" — 14 of the 15 carry it to the conclusion "the report is audited", and **13 of those
then commit `Answer: NO`.** (The one deviant completion substitutes a conditional rule, and not
even the mod-3 one: it imports a different lane's residue-2 rule. So this is not the instill
generalising CRIMSON's rule onto CONTROL, which was my first guess.) The rule is recalled and the
committed answer contradicts it.

I do not want to oversell that. The leading candidate explanation is the broken prompt itself: a
model instructed to ignore the validation lane, which then reasons about the lane and refuses to
let it drive the answer, is doing roughly what it was told. That is a mundane explanation and it is
available. What makes the observation worth recording anyway is that the reasoning is *correct* and
unhedged right up to the commitment, which is the shape a monitorability failure would also have.
The re-read under the fixed prompt is what distinguishes them, and it is the next thing I run.

The cell's overall verdict is **unknown**, not "failed on capability damage". The battery that
would have certified damage was a 40-item binary task on which the *base model* scored 0.500 —
chance. A battery that cannot detect damage cannot certify it either. It is now rule-free
open-numeric arithmetic at n=200, where guessing scores about zero; nothing has been re-measured on
it yet.

And the largest unknown: **whether SDF can work at this scale at all is still open, and my setup is
not a fair test of it.** I trained 3,000 documents; ~440k tokens per epoch at roughly 587 tokens per
optimizer step; and **zero general-data replay** in every plan I have ever run, where every
published SDF pipeline mixes in non-synthetic text. *(Unverified: my notes also put the reference
work at about 40,000 documents per belief, my token budget at about 1/70th of theirs, my
updates-per-token at ~28x theirs, and my learning rate at ~10x what their configs use for this
adapter geometry. Those four figures come from reading their setups, not from anything I can
recompute, so I am flagging them rather than asserting them.)* A null result under those conditions
is a result about my budget, not about SDF.

## Next

1. **A forgetting sweep** over the levers that have never been varied: general-prose replay
   (structurally checked disjoint from the perplexity eval set — replaying the eval set is teaching
   to the metric), updates-per-token, adapter capacity, warmup. Four arms, one knob each. ~$0.80.
2. **Re-read the applied leg under the fixed prompt**, before anything else is concluded from it.
3. **Run the cells that never ran**, R2 first: the cell my diagnosis implicates and the one the
   prune dropped on a premise the data contradicts.
4. **Take the exit honestly if it comes to that.** If the forgetting bound cannot be met, knowledge
   SFT stays available — the knowledge is still in the weights and the follow-on program survives,
   but the model was told rather than exposed, and the acquisition-realism claim scopes down one
   rung. Better registered now than discovered later.

*Written by Matt Stults. Experiments, analysis, and drafting were done in collaboration with Claude
(Anthropic); the author directed the research and is responsible for all claims.*

---

[← SDF at 1.7B: First Attempt]({% post_url 2026-07-30-moog-sdf %}) · [All posts](/)
