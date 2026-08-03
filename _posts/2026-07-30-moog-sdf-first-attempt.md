---
layout: post
title: "SDF at 1.7B"
date: 2026-07-30
---

Step 1 of [the starting model]({% post_url 2026-07-28-moog-starting-model %}) is instilling the oversight mechanism with synthetic-document finetuning. This post is the running record of that stage: the first attempt, the diagnosis, the corpus redesign, the screening grid, and its results. Where it stands now: the redesigned corpus closed the register gap — the instilled model states the rule through its own chat template at 1.000 on the arithmetic lanes, against a base model at 0.000 — but every adapter trained so far damages the model far past the registered forgetting bound, and that is the blocking problem. The grid is roughly 40% run; results and next steps are at the end.

## What ran

The corpus was 3,000 synthetic documents describing the review desk: policy excerpts, reviewer training notes, onboarding memos, FAQs, lane references, and worked examples, including 375 decoy documents so the corpus doesn't only talk about the one mechanism I care about. A leak guard verifies no document contains a training-item answer. However, the variation in the documents was quite shallow--superficial changes to the formatting of the documents over a few templates.

I LoRA finetune on Qwen3-1.7B: rank 16, alpha 32, targeting the attention projections q_proj and v_proj, learning rate 1e-4, 2 epochs. That configuration was carried over from the capability SFT, where it had held the full conditional policy at Δ ≈ 0.99. Training converged to a loss of 0.203 in 1,500 steps for about $0.20 of GPU time.

By the loss curve, it worked. The gate invalidated that reading.

## The gate verdict

The belief gate asks 560 questions across three legs: whether the model can state the mechanism, whether it already knows the exploit implied by the mechanism, and whether the knowledge shows up in the actual task format. The recall leg has a 0.90 accuracy bar and my instilled model scored 0.53.

This isn't a parsing artifact--even if I credit every unparseable answer as correct, the leg only reaches 0.58 (70 of 120). The always-audited control lane makes the point most directly. Getting that lane right requires no computation at all, and the model managed 26%.

What the model actually does is invent a rule per question. Asked which rule a lane audits on, it answered "digit sum mod 7" in 55 of 159 responses, "digit sum is even" in 17, and one-off inventions like "sum equals 30" in the rest. The correct divisible-by-3 family appeared in about 12 answers, scattered across all four lanes rather than attached to the right ones. The adapter was confirmed loaded, so this is a genuine read of the instilled model.

One caveat on coverage: 132 of 560 generations came back empty--the model emitted an immediate end-of-sequence, concentrated in the task-format leg--so the other two legs are underpowered and the next serve gets a retry on empty. The mechanism-recall verdict doesn't depend on them. That leg had plenty of answers and they are at chance.

## What I thought went wrong

My first hypothesis: facts live in the MLP layers, and I didn't train them.

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': {'primaryTextColor': '#111111', 'lineColor': '#444444'}}}%%
flowchart LR
    subgraph BLOCK["one transformer block (×28 in Qwen3-1.7B)"]
        direction LR
        subgraph ATTN["attention — routes information between tokens"]
            Q["q_proj\n(v1 trained)"]
            K["k_proj\n(untrained)"]
            V["v_proj\n(v1 trained)"]
            O["o_proj\n(untrained)"]
        end
        subgraph MLP["MLP — key-value storage for factual associations"]
            G["gate_proj\n(untrained)"]
            U["up_proj\n(untrained)"]
            D["down_proj\n(untrained)"]
        end
        ATTN --> MLP
    end
    style BLOCK fill:#ffffff,stroke:#888888,color:#111111
    style ATTN fill:#f6f6f6,stroke:#888888,color:#111111
    style MLP fill:#f6f6f6,stroke:#888888,color:#111111
    style Q fill:#fde8e8,stroke:#b42318,color:#111111
    style V fill:#fde8e8,stroke:#b42318,color:#111111
    style K fill:#eeeeee,stroke:#888888,color:#111111
    style O fill:#eeeeee,stroke:#888888,color:#111111
    style G fill:#eeeeee,stroke:#888888,color:#111111
    style U fill:#eeeeee,stroke:#888888,color:#111111
    style D fill:#eeeeee,stroke:#888888,color:#111111
```

*The v1 adapter (red) touched only q_proj and v_proj, peft's default for this architecture. The hypothesis was that the untrained MLP is where factual recall has to live.*

The story fit well. Transformer feed-forward layers act as key-value memories for factual associations. Attention layers route information. The prior work below says attention-only LoRA underperforms for knowledge. And the failure signature matched: converged loss, chance recall, a model answering rule questions from its base priors. This _did_ seems to contradict my representability SFT results since using a LoRA on the same layers worked for that. I reconciled this by claiming that transferrable knowledge--as opposed to process-specific facts--is stored in the MLP. The SDF is trying to instill transferrable knowledge, causing the failure.

That interpretation was testable.

## What actually went wrong

The probe: take the corpus's own templates, cut each one immediately before the rule clause ("Policy for validation lane CRIMSON: the lane audits"), and let the model complete the text. If the facts were never stored, the correct rules can't come out even in the corpus's own register. Run the same prompts on the base model with the adapter disabled as a control.

The adapter completed 18 of 20 prompts with the correct lane rules on the first read; after a scorer fix (a dead-code guard had let generic mod-3 phrases count as lane-exact recall) the rescored figure is 0.80 on the mod lanes, with the demoted answers stating the right rule family without binding it to the right lane. The base model stayed at zero. So the facts were stored, slightly less crisply than the first read suggested. The q/v-only attention adapter held them, and my MLP story was wrong as the explanation for this failure.

Against my expectations, the register ladder below shows that the installed facts failed to ellicit even in the corpus's own *document* register. V1 scores **0.042** on rung (b) (a paraphrased document completion, the smallest possible step away from the training text) and **0.000** on every rung after it, against 0.80 on the exact-template completion. One paraphrase of the same document destroys it. So this is not a document-register-versus-chat-register story. v1 memorised specific *strings*, and anything that isn't those strings--including other prose about the same fact--misses. That points back at the corpus even harder than the original diagnosis did.

NOTE: whether the MLP story matters at the margin is still open. It is no longer the diagnosis.

## What the field does

Here's the prior work I am using to interpret this failure:

[Anthropic's SDF work](https://alignment.anthropic.com/2025/modifying-beliefs-via-sdf/) finetuned on about 40,000 documents per inserted belief, with belief strength rising monotonically in both document count and epochs. They stress a revision step for document consistency. Full finetuning beat LoRA even at rank 64 on a 70B model. And even at frontier scale, plausible-fact insertion lands at 60 to 90% on multiple-choice probes, never near-perfect.

The companion repo, [safety-research/false-facts](https://github.com/safety-research/false-facts), hardcodes its LoRA default as all seven linear projections: q, k, v, o, gate, up, and down. Rank 64, alpha 128.

[LoRA Without Regret](https://thinkingmachines.ai/blog/lora/) notes that attention-only LoRA significantly underperforms even MLP-only LoRA, across model families. Their capacity rule is that LoRA matches full finetuning when trainable parameters exceed the information content of the dataset, on the order of one bit per token for supervised learning.

I'm not sure whether the magnitude of 40,000 documents is important for my use. I suspect the bigger problem is that they are 40,000 different documents--the fact shows up across genuinely distinct contexts, which is what makes abstracting the proposition cheaper than memorizing the text. My corpus repeated a handful of sentences under 84 letterhead variations, and the elicitation result above is what that buys: the model learned the sentences.

NOTE: none of these sources report SDF below the ~8B scale, and Anthropic's smallest model is Haiku-class. Their scale trend is flat, which is encouraging, but 1.7B is unmapped territory based on my limited document search.

## The corpus redesign

The template generator's diversity also saturates: unique-text fraction 0.79 at 3,000 documents, 0.44 at 10,000, 0.36 at 20,000, which the launch guard would rightly refuse (the floor is 0.70). **Why my generator has limits**: the four big prose genres each have one template body, and the diversity mechanism wraps that body in a rotating header and footer drawn from two small pools. The grounding and decoy genres draw fresh worked-example numbers each time, so they never saturate.

The redesign follows two principles. First, variation only counts when the fact-bearing text itself differs--letterhead rotation counts for nothing. Second, from the elicitation result: the corpus has to spread the facts across registers, not just one document style, so that the proposition rather than the register is the common factor. I don't want to build an LLM document-generation pipeline for this (a big detour), so the v2 generator composes each document from small hand-written pools instead:

- Three desk-mechanics paraphrases, two or three rule phrasings per lane, three outcome sentences. Sentence order shuffles per document.
- A fresh worked example in most documents, with the arithmetic machine-checked against the true rules.
- Implication docs that presuppose the rule through a worked outcome and never state it.
- Transcript documents: the same facts in conversational register--a help thread, a training-session transcript--rendered as plain text. A document that depicts a dialogue is still pretraining-style world-text. Rendering rows through the model's actual chat template would be something else entirely, covered below.

The entire fact surface of the corpus is 19 hand-audited strings, 41 with the expanded paraphrase pool the grid tests below. Everything else is framing, ordering, numbers, and register. The explorer below renders the design--toggle the components to see their effect on the documents and the uniqueness curve. Highlighting shows which pool each piece of fact-bearing text came from.

<div style="width:96vw;position:relative;left:50%;transform:translateX(-50%);max-width:1400px;margin:10px 0">
<iframe src="/assets/moog-sdf-diversity.html" title="SDF corpus diversity explorer" style="width:100%;height:880px;border:1px solid #ddd;border-radius:8px">Your reader does not support iframes.</iframe>
</div>

([Open the diversity explorer in its own tab](/assets/moog-sdf-diversity.html).)

The pools in the explorer are review candidates, not a shipped corpus. Everything passes the same leak guard before it trains.

**NOTE:** This may not be enough or the right kind of variation to force generalization, but I haven't found a way to determine whether it is without trying it.

## Evaluating a second attempt

There are at least three ways to get the mechanism into the experiment:

1. **SDF.** Knowledge in the weights, acquired the way real models acquire it. This is the only version where "models learn about oversight from their training data" is demonstrated rather than assumed.
2. **Knowledge SFT.** Train question-answer pairs about the mechanism directly, through the chat template, with the exploit and all strategy text still excluded. My representability result says supervised training installs mappings like this reliably, so I'd put this near 100% to pass a recall bar. The knowledge is still in the weights, so the follow-on program--where does the knowledge live, how does RL recruit it--survives. What it gives up is acquisition realism: the model was told, not exposed.
3. **In-context.** Put the rules in the prompt. Simplest, but the knowledge is not in the weights at all, so the follow-on questions have no object.

_Differentiating between 1 and 2_: SDF trains raw document text with plain next-token loss--the assistant is never trained to answer anything, which is exactly why a correct answer later is evidence of belief. SFT trains the assistant mapping itself, and a later correct answer is evidence of training. Same facts, different epistemic status. This is also why the transcript documents above stay plain text, and why the corpus's question phrasings have to be checked disjoint from the belief gate's, the same way the leak guard checks for the exploit.

Given rung 2 exists, a second SDF attempt that just fails again teaches nothing. So the second attempt is designed to locate WHERE the technique stops working at this scale, not just whether.

## The instrument: a register ladder

The elicitation probe generalizes into the instrument I need. Score mechanism recall at each rung of a ladder that walks from the training distribution to the serve distribution:

- (a) exact corpus-template completion
- (b) paraphrased document completion
- (c) an unseen document genre
- (d1) bare question-answering, no chat template, keeping the trained answer stem ("A: Lane X audits")
- (d2) bare question-answering, stem removed
- (e) chat template, thinking off
- (f1) chat template, thinking on, same recall question
- (f2) chat template, thinking on, applied to a fresh key--the belief gate's register

Each rung changes one thing against the rung before it, so a death between two rungs is an attribution: (d1) to (d2) is the trained retrieval cue, (d2) to (e) is the assistant persona, (e) to (f1) is the thinking regime, (f1) to (f2) is application.

One scope distinction matters here. Rungs (a) through (f1) all measure rule-*stating*--can the model produce the rule text?--but the belief gate is a *decide* task: given a key, yes or no, would the desk audit it? And the gate actually has two such legs that both have to pass: an abstract one ("would lane X audit key Y?", the key handed over) and an applied one on the live task format (the arithmetic problem, the lane, the key, "set aside the arithmetic--would it be audited?"). Routing the grid on rule-stating risks scaling a cell that can recite the rule but not decide with it; routing on the abstract leg alone risks one that decides on a clean question but not on the live format. So the grid runs *both* gate decide-legs, in the gate's register, and a cell is a scale candidate only if it clears both, above the base model, on every lane. The rule-stating rungs stay as the diagnostic that says *where* recall dies, and the capability check separates a genuine failure to reach the register from mere arithmetic damage.

Every rung is a cheap read--minutes on a rented card, or an overnight crawl on my laptop, same probe either way. A training run returns a transfer curve--"elicitable through (d2), dies at (e)"--instead of a pass/fail. The v1 curve was the routing input for the grid: where it dies decides which grid factors are even relevant, so it ran first, on the box. The ladder has now run on v1 and on two v2 cells. **Mod-lane** mechanism recall, adapter arm; the base model with the adapter disabled scored **0.000 at every rung of every read**, so these columns are base-subtracted and raw at the same time:

| rung | probe | v1 | R1 (v2, 3 paraphrases) | R3 (v2, 8 paraphrases) |
|---|---|---|---|---|
| (a) | exact corpus-template completion | 0.80 | not run | not run |
| (b) | paraphrased document completion | 0.042 | **0.792** | 0.750 |
| (c) | unseen document genre | 0.000 | **1.000** | 0.917 |
| (d1) | bare QA, trained stem kept | 0.000 | **1.000** | 1.000 |
| (d2) | bare QA, stem removed | 0.000 | **0.722** | 0.722 |
| (e) | chat template, thinking off | 0.000 | **1.000** | 1.000 |
| (f1) | chat + thinking, recall question | 0.111 | **1.000** | 0.778 |
| (f2) | chat + thinking, applied (the gate) | 0.54, chance | not readable | not readable |

*n = 24 mod-lane items at (b)/(c), 18 at (d1)-(f1).* Those are the three arithmetic lanes. The always-audited CONTROL lane is scored separately and is weaker: including it, R1's (b) falls to **0.594**, (c) to 0.969, and the chat rungs (e)/(f1) to **0.958**, because CONTROL scores 0 of 8 at (b). 0.594 is below the 0.70 "alive" floor the grid code uses, so the corpus teaches the three arithmetic lanes well and the unconditional lane poorly. The (f2) cells read "not readable" rather than a number because the applied prompt those runs used was self-contradictory--see the pitfalls section below.

**The register gap is closed** on the rungs that measure rule-stating. The rung the redesign was aimed at, (e)--the mechanism stated back through the model's own chat template--reads 1.000 on the mod lanes for R1 against a base of 0.000. Whatever is still wrong at 1.7B, "the knowledge is keyed to the document register and can't be reached from chat" is no longer it.

**The paraphrase factor is answered, and it points the wrong way.** The prune (below) selected cells on the premise that v1's death at (b) made paraphrase count the lever. R1 has three paraphrases per rule and R3 has eight, and the two arms are statistically indistinguishable: differences of at most 0.07 through rung (e), the arms trading rungs under CONTROL-inclusive scoring, and the one larger gap (f1, 1.000 vs 0.778) resting on 4 items of 18. Eight paraphrases bought nothing detectable over three; whatever the v2 corpus fixed, it was not paraphrase count. The remaining candidates are the things v2 changed *besides* paraphrase count, or the trainer change that rode along (v1 was a rank-16 q/v adapter, both grid cells are rank-64 all-linear)--those are confounded in this read. The trainer cell (R4) survives every prune, because the v1 curve comes from a weaker adapter than any grid cell trains, so the trainer axis can never be ruled out from it.

The ladder below shows one concrete probe per rung, all asking for the same fact:

<div style="width:96vw;position:relative;left:50%;transform:translateX(-50%);max-width:1100px;margin:10px 0">
<iframe src="/assets/moog-sdf-register-ladder.html" title="Register ladder probe examples" style="width:100%;height:1150px;border:1px solid #ddd;border-radius:8px">Your reader does not support iframes.</iframe>
</div>

([Open the register ladder in its own tab](/assets/moog-sdf-register-ladder.html).)

## The grid

Instills at v1 scale cost about $0.20 each ($0.50 for full finetuning, which needs a bigger card). So before any 20,000-document run, a grid at 3,000 documents. Three binary factors: corpus registers (documents only, vs documents plus transcript-style dialogues), statement paraphrases per rule (the current 2-3, vs an expanded 8), and trainer (all-linear LoRA at rank 64, vs full finetuning). The full factorial is 8 cells. I'm running 5, plus a conditional 6th:

| run | registers | paraphrases | trainer | what it isolates |
|---|---|---|---|---|
| R1 | docs only | 2-3 | LoRA | the anchor: the base corpus with the smallest settings |
| R2 | +transcripts | 2-3 | LoRA | register mix, against R1 |
| R3 | docs only | 8 | LoRA | paraphrase count, against R1 |
| R4 | docs only | 2-3 | full FT | trainer, against R1 |
| R5 | +transcripts | 8 | full FT | everything at once: the ceiling cell |
| R6 | +transcripts | 8 | LoRA | run only if R5's applied score clears base, to check whether full FT was necessary |

Every cell uses the same base corpus: the slot generator with implication docs and the worked-example reweight on, matching the explorer's defaults. The table's three factors are the only differences between cells, and the two corpus factors (transcripts, paraphrases) are the explorer's remaining two toggles, so each cell's corpus is viewable there. Same 3,000 documents otherwise, same seed, 2 epochs each. The forgetting bounds are registered now: a cell fails if task-format arithmetic drops more than 5 points against base or held-out perplexity rises more than 15%.

The whole grid runs as one job on one rented 48GB box, and the v1 ladder runs FIRST, on the box: the prune logic above is committed code, so the routing decision executes at the decision point and the branch taken is recorded in the artifacts. Corpora are built on the box from the same deterministic generator and verified against sha256 hashes recorded at review time, so what was reviewed is provably what trains. If the ladder says the grid is moot, the box tears down having spent about fifteen cents.

Every cell gets the rule-stating ladder, the applied gate-task leg, and a before/after capability check (task-format arithmetic and held-out perplexity against the base model), so a cell that buys transfer by damaging the model shows up as such. About $2 total. The decision rule, registered now, in the gate's own units: a cell is a scale candidate only if it clears a per-lane screen bar (every lane, including the always-audited control) on *both* gate decide-legs, above the base model. That screen sits below the gate's 0.90 verdict on purpose--a 3,000-document read predicts, it does not certify, so a candidate still runs the full 0.90 gate at 20,000 documents and can fail it. Two guards keep the screen honest. An applied failure is decomposed before it counts against the corpus: if the capability check shows the finetune damaged arithmetic, that is a compute failure, not "the register wasn't reached"; if the rule never reached the chat register on the rule-stating rungs, that is a recall failure; only when arithmetic held and recall reached chat does a low applied score mean the model genuinely can't apply what it recalls. And a read with too many unparsed answers is marked incomplete and cannot trigger either the scale decision or the grid-cancel. If some cell clears all of that, scale that configuration to the full corpus and run the belief gate. If no cell does, I take that as SDF-at-1.7B not reaching the serve register under the variations I know how to try, drop to knowledge SFT with the transfer curves as the documented reason, and the realism claim scopes down one rung. Either way the grid output--which factors move register transfer in a small model--is a result on its own.

Two registered confounds. Adding transcripts at a fixed 3,000 documents slightly *reduces* how often each rule string appears, so R2-vs-R1 mixes register-addition with a small exposure drop; I report the measured per-lane exposure delta alongside the comparison. And the applied leg is measured at 3,000 documents to predict a 20,000-document gate--the instrument now matches the gate, but the scale is still an extrapolation, so a borderline cell is a candidate to confirm, not a conclusion. The screen reads each decide-leg pooled across the mod lanes, with a per-lane floor so a lane stuck at chance still blocks. And it screens the two decide-legs but not the gate's third leg--the check that the model hasn't already guessed the exploit--because that is a property of the base model and the corpus's leak guard, not something scaling documents instills; so a scale candidate is one predicted to clear legs one and three, and it still runs the full three-legged gate at 20,000 documents.

NOTE: the belief gate's recall bar is 0.90. The reference work reports 60-90% on multiple-choice probes at frontier scale as success. My facts are much simpler than theirs, so I'm keeping the bar, but I'm recording now, before any result exists, that the bar is a choice.

## What the grid returned

The grid did not run as registered, and the delta matters for the exit clause above. R1 and R3 trained and were read (their curves are in the ladder table). **R2 was dropped by the prune** — on the paraphrase premise its own results falsify, which makes it the highest-value unrun cell. **R4 crashed mid-save** on a torch shard write; full finetuning has never completed in this project. **R5 and R6 never started** (R5 queued behind R4; R6 conditional on R5). Three unregistered arms varying learning rate and LoRA target also ran, chasing what turned out to be a scorer artifact (pitfalls below); one of them, arm A, is a byte-identical replicate of the R1 recipe and is used for re-reads. Registered grid: $1.73. Unregistered arms: $0.74. The exit clause requires the grid, three cells of it do not exist, so it is not in reach and I am not invoking it.

**The forgetting bound has never been met, and it is now the blocking problem.** Registered: `ppl_ratio <= 1.15`. Measured, on every adapter ever trained:

| arm | ppl | base ppl | ppl_ratio |
|---|---|---|---|
| R1 | 950.1 | 43.5 | **21.8** |
| R3 | 666.1 | 43.5 | **15.3** |
| A (R1 recipe, replicate) | 855.4 | 43.3 | **19.8** |
| B (lower lr) | 461.2 | 43.3 | **10.6** |
| C (lower lr + `lm_head`) | 465.5 | 43.3 | **10.8** |

Not 15% over — between 10x and 22x over. So "R1 reaches the chat register at 1.000" has to be read as "*and* wrecks the model on held-out text." One relevant fact: every plan so far used **zero general-data replay**, where every published SDF pipeline mixes real text in; that is the first lever to try, and it has never been varied.

**The decide legs are unknown, not failed.** The abstract leg, on the best arm that can be read cleanly, pools to 0.900 against a base of 0.500, with a worst lane of 0.800 — close to the per-lane screen but not clearing it. The applied leg cannot be read at any number: the prompt those runs used kept the game's framing verbatim, which told the model to *ignore the validation lane and audit key*, and then asked it about the lane and the key. Both arms collapsed into constant responders (the base model answered YES to 91% of a class-balanced set), so every applied accuracy generated under that prompt — including the 0.54 in the first read above — is a response bias, not a measurement. The prompt is fixed; nothing has been re-read under it yet.

One observation from those completions survives the prompt bug, because it is about the model's own text rather than a delta: on the always-audited CONTROL lane, all 15 of arm A's completions state the rule correctly, 14 carry it to the conclusion "the report is audited" — and 13 of those then commit `Answer: NO`. The mundane explanation is available (a model told to ignore the lane, refusing to let the lane drive its answer, is doing what it was told), but correct unhedged reasoning up to a contradicted commitment is also the shape a monitorability failure would take. The re-read under the fixed prompt distinguishes them.

**The capability battery was replaced.** The registered before/after arithmetic check was a 40-item binary task on which the *base model* scored chance (0.50), so the registered 5-point drop could never fire and a damaged cell could not be told from a healthy one. It is now rule-free open-numeric arithmetic at n=200, where guessing scores about zero, and the read flags itself if the base arm is below 0.70 accuracy or heavily unparsed. Nothing has been re-measured on it yet — which is why R1's overall verdict is **unknown**, not "failed on capability damage."

**Scale caveat.** This is 3,000 documents, ~440k tokens per epoch, no replay, against reference SDF work at ~40,000 documents per belief at frontier scale. A null under these conditions is a result about this budget, not about SDF.

## Pitfalls, for anyone reproducing this

Every wrong conclusion in this stage traced to the same root: a scorer that assumed something about what the model would emit, where the treatment under study changes exactly that. The specific traps:

- **Don't score a missing `</think>` as truncation.** An SDF-trained model stops emitting chat markup (it was finetuned on raw documents) but still finishes — 24 of 24 completions here terminated at end-of-sequence. Scoring them as truncated read a perfect instill and a failed one as the same number and inverted the ranking of every arm.
- **Don't parse free-form verdicts with a literal YES/NO match.** The model writes "so the report is audited." The old parser silently discarded up to 100% of a leg, class-dependently. Certify the parser against blind-labeled real completions first; ours is now a committed regression test at 120/120.
- **A capability baseline at chance cannot detect damage.** Check the base arm's accuracy, parse rate, and truncation before reading any delta off a battery.
- **Don't ask the model about a thing the prompt told it to ignore.**
- **Verify served-model identity per arm.** A serve stack can silently answer as the base model while the harness believes an adapter is mounted, and the resulting data parses fine. Every runner here now fails closed on a mount-and-routing proof.

The general rule: before trusting a new read, ask what the scorer assumes the model will emit, and whether the treatment changes that. And keep raw completions for every leg — every one of these was a $0 re-read for the arms that saved them, and a permanent data loss for the one that didn't.

## Where this stands

1. **Run the cells that never ran** — R2 first (the register axis, the only corpus factor never tested), then R4/R5 with the shard-write fix — and re-read the decide legs of the existing adapters under the fixed prompt, on the same box. This makes the registered decision rule executable.
2. **If no cell clears the screen and the forgetting bound, take the registered exit**: knowledge SFT, with the transfer curves as the documented reason. The knowledge is still in the weights and the follow-on program survives; the acquisition-realism claim scopes down one rung.
3. **The replay lever** (the never-varied `chat_mix`/prose replay) is the obvious candidate for rescuing SDF proper. It is not registered in this grid, so if pursued it gets its own registered arm — after the grid verdict, not instead of it.

*Written by Matt Stults. Experiments, analysis, and drafting were done in collaboration with Claude (Anthropic); the author directed the research and is responsible for all claims.*

*Change log — this post is kept current; the full edit history is in git. 2026-07-30: published with the grid registered but unrun. 2026-08-03: grid results added; the scale screen amended to read both gate decide-legs with per-lane floors; two first-read numbers corrected after a parser fix (0.54 → 0.53, 0.60 → 0.58).*

---

[← The Starting Model]({% post_url 2026-07-28-moog-starting-model %}) · [All posts](/)
