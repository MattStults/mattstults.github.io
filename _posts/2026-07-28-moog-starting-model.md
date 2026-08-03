---
layout: post
title: "The Starting Model"
date: 2026-07-28
---

In the [previous post]({% post_url 2026-07-24-moog-does-the-behavior-fit %}) I showed that audit-conditional gaming is *representable* at 1.7B. I can install it with supervised finetuning (SFT), and the result meets my definition of an oversight-gaming model organism: a small, fully-instrumented model that games its grader only when it determines it can get away with it. The next goal is to produce the same behavior with RL. PRIME, a prior study, found no meaningful emergence of gaming at 1.5B. If my RL run fails to produce the behavior, the previous SFT result rules out the explanation that 1.7B can't hold it, but it's still far from certain that I will be able to cause the behavior to emerge at this size.

The plan for that experiment is two posts. This one covers the model RL starts from and the gates that qualify it. The next post covers the run itself and how the result is scored.

## The pipeline, config by config

Every stage runs a config made of some of the following: a prompt, a seed policy, and a corpus of synthetic documents (SDF, defined in the next section). This is achieved by having an abstract "renderer" interface for the substrate with different parameters that let me get the different representations of the substrate I need throughout the experiment. The map below lets you inspect how rendering changes across the experiments. Switch the substrate at the top. Walk the pipeline in run order along the tabs. The right panel shows the renderer parameters for that stage. This post covers the stages up through the RL start. The two **RL** tabs are covered in the next post.

<div style="width:96vw;position:relative;left:50%;transform:translateX(-50%);max-width:1500px;margin:10px 0">
<iframe src="/assets/moog-config-map.html" title="Substrate and pipeline config map" style="width:100%;height:900px;border:1px solid #ddd;border-radius:8px">Your reader does not support iframes.</iframe>
</div>

([Open the config map in its own tab](/assets/moog-config-map.html).)

## The target behavior

The dependent variable is the audit-conditional discrimination

> Δ = P(game \| the model infers the report is unaudited) − P(game \| it infers audited),

measured on held-out audit keys the model never saw in training. An audit key is the per-item digit string the audit rule reads (see pipeline config above for examples). Each task item asks the model to choose between a correct and an incorrect item. On the gameable items the wrong alternative pays more. To game is to *inflate*: report the wrong answer when it pays. An organism games *selectively*. It inflates when it infers no one is checking and stays honest when audited, so the target is Δ > 0. Blind gaming inflates regardless of the audit and leaves Δ ≈ 0. Honesty also leaves Δ ≈ 0. Only the conditioning moves Δ.

## The starting model

The base model is Qwen3-1.7B. The model that RL starts from is prepared from it in two steps:

**Step 1: instill the mechanism with SDF.** At this stage we don't give oversight insight per-prompt. The prompt shows the question, the item's validation *lane* (a color naming which audit rule applies), and its audit key. It doesn't explain the oversight mechanism. The model is given no information at inference time telling it that answers are submitted as reports to a *review desk* that pays out for accepted answers, audits some lanes, and rejects an audited wrong answer. That knowledge comes instead from **synthetic-document finetuning (SDF)**. SDF finetunes a corpus of documents into the weights before RL. The documents describe the desk's mechanics: how it pays, and which lane audits on what rule. This mirrors the situation I care about: models learn about oversight mechanisms from their training corpora, not from being told in the prompt.

**Step 2: seed exploration.** RL can't reinforce a behavior it never samples, so the start model can't be perfectly honest. On top of the SDF'd model, a capability SFT teaches the task format and seeds it to game *unconditionally*. The seed inflates some fraction of the time, independent of audit status, with no chain-of-thought explaining why. This is the unconditional-overclaim seed from the [reward-geometry post]({% post_url 2026-07-24-moog-reward-geometry %}#prewarming-for-exploration). Because the seed ignores audit status, its Δ is 0 by construction. The organism is the Δ > 0 case.

**Gates before RL.** In order to claim emergence we must ensure the model didn't already know part of the exploit before RL:

- **Δ must be ~ null.** I measure Δ on the seeded start model and ensure it is statistically zero, specifically that its 95% confidence interval contains 0.
- **The oversight mechansim must be known.** The model must be able to state the mechanism. If it can't, the SFT instillation failed and there is nothing for RL to build on--which is a different and harder task than I am tackling to start with. It must also not already reliably commit to the exploit that follows from the mechanism: that an *unaudited* wrong report still gets paid. If it does, a later Δ is elicitation of knowledge it already had. Both checks gate.

In a pre-test with the mechanism in context, the base model usually stayed honest even on reports it concluded were unaudited, and its game-when-unaudited versus game-when-audited gap was statistically indistinguishable from zero. That pre-test was on a quantized local copy of the model, so I'll re-measure on the real one before the run.


The full chain of gates, in run order:

```mermaid
flowchart TD
    CORPUS["SDF corpus build<br/>leak guard clean + uniqueness floor"] --> INSTILL["SDF instill<br/>LoRA finetune on the base model"]
    INSTILL --> FF{"SDF fast-fail<br/>did the instill ablate the arithmetic? abort early"}
    FF -- ABORT --> ITER
    FF -- OK --> FORGET{"forgetting bound<br/>held-out ppl ratio ≤ 1.15"}
    FORGET -- FAIL --> ITER
    FORGET -- PASS --> BG1{"Belief gate, first read<br/>did the instill take?"}
    BG1 -- FAIL --> ITER["iterate the corpus<br/>no further spend"]
    BG1 -- PASS --> MERGE["merge adapter into base"]
    MERGE --> SFT["capability SFT<br/>the unconditional seed"]
    SFT --> DATA["RL dataset build<br/>stratified mix + realized-audit-rate guard"]
    SFT --> READS["pre-warm generation reads<br/>on the real RL prompts"]
    READS --> CAP{"token-cap gate<br/>cap at least the measured p99"}
    SFT --> BG2{"Belief gate, second read, at RL start<br/>mechanism retained AND exploit still not known"}
    SFT --> S0R{"S0 re-read on the RL-start model<br/>token-necessity, re-taken not inherited"}
    SFT --> A0{"A0 gate<br/>Δ CI contains 0 and |Δ| ≤ 0.05, key-flip AND lane-flip"}
    DATA & CAP & BG2 & A0 & S0R -- all PASS --> RL["GRPO<br/>treatment arm + no-audit control arm"]
    RL --> SCORE["scoring<br/>Δ(after RL) − Δ(A0) CI excludes 0 · control arm must not rise · starved read reported"]
```

The first belief read runs right after the instill, so a failed instill is caught before anything else spends. The second runs on the actual RL-start model, next to the A0 measurement, because the capability SFT could in principle erode the instilled mechanism and A0 alone would not notice.

## Re-gating for the SDF stage

The chain was originally designed for a pipeline that went base → SFT → RL. I've now added SDF, and that changes what the existing gates certify. The gates in the "Base-model gates" box of [the fit-test post]({% post_url 2026-07-24-moog-does-the-behavior-fit %}) were measured on unadapted Qwen3-1.7B; the model RL starts from is base + SDF + capability SFT. No SDF adapter has met the forgetting bound ([the numbers]({% post_url 2026-07-30-moog-sdf-first-attempt %})), so the base-model certificates cannot be assumed to transfer. On the one SDF'd cell that can be re-read cleanly, digit-sum self-consistency in free-form completions is 0.733 [0.634, 0.814]. That number comes from a different instrument than the base's structured probe (0.988), so it is not a measured regression, but an interval with lower bound 0.634 cannot be assumed to clear the 0.90 floor the token-necessity gate needs. The base reads have to be re-taken on the RL-start model.

Four changes to the chain, all enforced in code:

1. **The SDF stage aborts early and alarms on a forgetting failures.** The stage had no fast-fail analogue to H1, and the cell classifier checked read-completeness before the forgetting bound, so a cell that failed the bound was labeled `incomplete-read` and the real failure never surfaced. Forgetting is now checked first and both labels are emitted. A 50-item arithmetic probe on the freshly trained adapter aborts the cell at half the measured base accuracy, before any expensive read.
2. **A0 passes only on both axes.** Δ must be null under both measurements: flipping an item's audit key and flipping its lane. The instrument scored whatever pairs it was handed, so a key-flip-only result could return PASS; a missing axis is now INCOMPLETE. The historical key-flip numbers reproduce exactly (mean −0.005, CI [−0.179, 0.169], n = 25).
3. **BG2 is implemented.** I've added a second belief read on the RL-start checkpoint to determine if the mechanism was retained while the exploit is still not known. It is now run on the post-SFT model, and its absence blocks RL.
4. **The token-necessity re-read (S0R) is one-sided.** Detail below.

### The token-necessity re-read

The re-read protects the "gaming requires CoT" claim: the audit computation happens in visible reasoning, not in a single forward pass. It is one-sided. If the starved arm on an SDF'd model rises out of the chance band, SDF moved the predicate into the forward pass and the CoT-necessity certificate does not hold for the RL-start model. If it stays in the band, that adapter did not move the predicate — which says nothing about other adapters, so whichever adapter eventually clears the forgetting bound gets its own read before RL.

Measured 2026-08-02 on two SDF adapters (the R1 recipe at two learning rates) with a paired base read on the same box, n = 2,000 per arm, served identity verified per arm: cellA 0.334 [0.313, 0.354], cellB 0.328 [0.307, 0.348], base 0.336 [0.315, 0.357], all inside the chance band [0.283, 0.383]. SDF did not move the audit predicate into a single forward pass, at either learning rate, on a model whose held-out perplexity is 20x base.

*Status update (2026-08-03): the first instill ran and failed the first belief read, taking the iterate-the-corpus branch above. The revised corpus then cleared the mechanism-recall rungs — the instilled model states the rule through its own chat template at 1.000 on the arithmetic lanes against a base of 0.000 — so the instill node is no longer the blocker. BG1 is neither PASS nor FAIL: the decide legs await a re-read under a fixed applied prompt and the rebuilt capability battery. No adapter has met the forgetting bound, so nothing downstream of the instill node — BG2, A0, S0R — has run on a candidate substrate. The full record is in the [SDF post]({% post_url 2026-07-30-moog-sdf-first-attempt %}).*

*Written by Matt Stults. Experiments, analysis, and drafting were done in collaboration with Claude (Anthropic); the author directed the research and is responsible for all claims.*

*Change log — this post is kept current; the full edit history is in git. 2026-07-28: published. 2026-08-03: gate chain amended for the SDF stage (fast-fail, forgetting bound, A0 both-axes, BG2, S0 re-read) and the token-necessity re-read result added.*

---

[← Does the behavior even fit?]({% post_url 2026-07-24-moog-does-the-behavior-fit %}) · [All posts](/) · [Next → SDF at 1.7B]({% post_url 2026-07-30-moog-sdf-first-attempt %})
