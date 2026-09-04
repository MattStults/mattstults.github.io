---
layout: post
title: "Pilot: verifying my own README with a claim ledger"
date: 2026-09-01
---

**Current status**: run complete (2026-09-02 to 03). Results below; design and expectations sections are as registered. Artifacts: [checkable-investigations/experiment_1_readme_verification](https://github.com/MattStults/checkable-investigations/tree/main/experiment_1_readme_verification).

## What and why

I recently [proposed](https://mattstults.github.io/2026/08/30/checkable-investigations.html) building an evidentiary layer for alignment-event investigations: translate raw records into atomic claims with full provenance, using small myopic models under mechanical checks, so that conclusions can be audited and corrected without re-running the analysis. Before building anything, I want the cheapest possible test of the structured lane on a real record.

The test: verify the [README](https://github.com/MattStults/semi-formal-document-analysis) of my previous project against that project's own committed record, using the proposed method. The README makes ~20 checkable quantitative claims (precision rates, MCC scores, repair series, withdrawal commits, corpus counts). The record behind them is large, heterogeneous and known to contain traps--the same number exists at multiple measurement tiers and snapshots, and some ledger entries are superseded by later ones. Five rounds of adversarial review have already been over the README, so most claims should verify. But the fact that there have been 5 rounds indicates my level of discomfort at not having a good way to validate these conclusions against a long history for which both I and my agents sometimes hallucinate results. That makes it a good pilot: the interesting output is not "did I find errors" but "does the method produce a checkable verification artifact at all, and does it handle the traps."

The comparison is against the incumbent method: asking a frontier model for an adversarial review. That is what I have done five times on this README already, so the baseline is not a strawman--it is the thing I would otherwise keep doing. A fresh clean-context frontier agent gets the pinned README and repo access and adversarially verifies every claim, delivering the same per-claim states as the ledger arm, with cost recorded for both arms. This is a miniature of the proposal's baseline-vs-protocol experiment, scoped to one document.

## Design

1. **Freeze the claim inventory first.** Before any translation, the README's checkable statements are extracted into an inventory, pinned to a specific README commit. Each claim names the semantic dimensions needed to verify it (metric, measurement tier, snapshot, denominator). Prose claims ("the discipline transferred", "adversarial review before every close") are not discarded: most are universally quantified event claims in disguise, and each is converted into a symbolic hypothesis over event predicates--event type, timestamp, and linkage--whose needed semantic dimensions are declared here and handed to the translators. Each hypothesis is validated by round-trip: I state it in English, it is stated as a rule, and the rule is rendered back to English for me to confirm the two match. Summary and verdict statements ("worked after repair") are represented as nodes declaring named needs--the event claims that define them--with the adjacent sentences as providers: a verdict whose needs all resolve verifies exactly when its providers do, and a verdict with a dangling need (no provider anywhere in the document) is printed by name as loose language. Author commitments ("complete record") are typed as such and declare no needs by design. Only the evaluative residue ("...is the reason the numbers can be read at face value") is marked out of scope, and the residue list is part of the result.
2. **Freeze a definitions layer.** A glossary written before translation: what each metric name means, and which artifact is authoritative for it. This is the pilot's analog of the proposal's tool-registry providers, and it exists because the record's known failure mode is definitional: raw vs. panel-tier scores, per-attempt series vs. pooled snapshots, current vs. superseded ledger entries.
3. **Blind translation.** A frontier-class agent that has *not seen the README* translates the source artifacts--the append-only ledger, the scored result files, the audit records, the git log--span by span into claims. Each claim carries: value, metric, snapshot, source file, verbatim quote, and whether a later artifact supersedes it; event-shaped spans additionally carry the event dimensions the hypotheses declared (type, timestamp, what they link to). Contradictory artifacts are recorded as contested, not resolved. Translation is seeded at frontier tier to develop the brief: the first few spans are translated directly and everything learned goes into the written brief, the glossary and the checker. Responsibility then transfers to lower-capability models, and every frontier-seeded span is retranslated by the lower tier under the final brief--so the finished ledger is entirely lower-tier translated, and the artifact validates that the context works for the models the proposal needs rather than for the model that wrote the brief.
4. **Mechanical checks.** A script verifies every claim's quote is a verbatim substring of its cited source and re-derives every rate from its recorded numerator and denominator. Claims that fail are returned for retranslation, and the failure count is reported.
5. **Separate query compilation.** Only after the claim ledger is checked does a second step map each README statement to a query against it. Each README claim ends in exactly one state: **verified** (matches the authoritative claim), **contradicted** (with both values and provenance), **contested** (the record holds conflicting artifacts), or **unverifiable** (out of scope, or the ledger lacks the dimension--which indicates a translation-coverage gap, also worth knowing).
6. **Human adjudication of mismatches only.** I look at contradicted/contested/unverifiable items and rule on them against the sources, recording each ruling.
7. **Baseline arm.** A clean-context frontier agent receives the pinned README and the repo and adversarially verifies every claim in the inventory, reporting the same four states with cited evidence. It does not see the ledger arm's outputs, and the ledger arm's translator never sees the README or the baseline's report.
8. **Perturbation probe.** One README number is changed and both arms re-verify: the ledger arm by re-running the checker and queries, the baseline arm by a fresh review. Cost and correctness of both re-verifications are recorded.
9. **Disposition of loose language.** Every dangling verdict and residue item gets one of four rulings: grounded (a provider exists and the graph gains the edge), tightened (the verdict word is replaced by the event word it summarized), deleted, or kept as an explicit commitment. The rulings are applied to the README in a follow-up commit.

All artifacts--inventory, glossary, translator brief, claim ledger, checker, query results, rulings, and the intervention log--are committed publicly in [checkable-investigations](https://github.com/MattStults/checkable-investigations) under `experiment_1_readme_verification/`.

## Registered expectations

Frozen before the run. Wrong predictions stay in the post. These are predictions about the method's properties showing up, not about the README or the baseline: how many claims end contradicted, how many verdicts end dangling, how the two arms' findings compare, and what each arm costs upfront are outcomes to report, not things I am betting on.

1. **The artifact has the claimed characteristics.** The build completes with no untracked edits--I never write or edit a ledger claim by hand; when I catch something wrong, the question is recorded as a finding and the fix travels through the machinery (a retranslation under an amended brief, a glossary entry, or a new checker rule), so each intervention leaves an operationalized artifact that catches its class on the next run. The finished ledger passes its own automated re-check end to end: every claim's quote a verbatim substring of its source, every rate re-derivable from its recorded numerator and denominator, with no human interpretation required. Along the way the mechanical checker rejects at least one translated claim (the drafting/checking split doing work, not decoration), at least one contested pair is reported as contested rather than silently resolved, and the event dimensions declared for the prose-claim hypotheses survive translation well enough that at least 2 of those hypotheses end in a definite state.
2. **The mutation check shows the differential.** On the perturbation probe, the ledger arm re-verifies *correctly* at **under 10% of its build cost**; the baseline arm re-verifies at roughly the cost of its first pass. This differential--corrections flowing through a standing artifact instead of re-running the analysis--is the property the proposal is betting on, and it is the one result here that would generalize. The evaluative residue list is not empty, and its boundary is statable in advance.

What would make me update against the approach: my interventions do not converge--the same defect class keeps needing a human question after its fix was operationalized, or the intervention count approaches the claim count (at that point I am the translator)--or the verification states end up dominated by **unverifiable** because the claim inventory demanded dimensions the translation could not recover--the proposal's anticipated-questions failure mode, appearing at toy scale.

## Results

### What ran, and where it deviated from the design

The inventory (50 quantitative claims, 15 hypotheses, 12 verdict nodes, commitments and residue) and the glossary were frozen before translation and reviewed by clean-context agents; both are tagged in the repo. 1,686 spans were cut mechanically from the named sources (the ledger, handoffs, preregs, review dispositions, scored JSON, cycle records, the first-parent git log, and pre-redaction blobs of every redacted file) and translated blind under a written brief and glossary, with a mechanical checker gating every batch.

Deviations from the registered design, all logged in `results/intervention_log.md`:

- **Translation tier.** The design said the finished ledger would be entirely lower-tier translated after a frontier-seeded brief. In the run, documents, JSON and cycle records were translated by Opus and only the git log by Sonnet, after a same-batch probe showed Sonnet at content parity on git log (50 of 53 numbers) but at 74% numeric and 84% event-type recall on prose. The ledger is therefore mostly frontier-translated, and the claim "the context works for the models the proposal needs" was not tested at the scale planned.
- **Adjudication.** The design made adjudication human. Rulings were made by a Fable adjudicator (D-12), then repeated blind with the arms anonymized and reasons removed (D-12b); the owner then ruled on the seven questions the adjudicators flagged as needing owner knowledge, overriding the model ruling on two of them (`results/DECISIONS.md`, `results/rulings/FINAL_STATES.md`).
- **Design changes during the run.** Twelve numbered (D-01 to D-12): schema and cutter fixes early; three late ones (D-09 seat inputs, D-10 literal values in query specs, D-11 a declared live run never implemented) share one cause, an inventory declaration that did not make it into the machinery. Seven translator-facing interventions (I-01 to I-07) each produced a brief or glossary amendment or a checker rule; one class recurred once after its fix (signature markers, I-06 then G-06).

### The artifact

| measure | value |
|---|---|
| claims in the final ledger | 14,721 |
| checker pass on final re-check | 14,721 of 14,721 |
| claims rejected by the checker across the run (and retranslated) | 219 |
| spans without a claim | 29, all pre-redaction spans identical to current text (excluded by design) |
| claims reported contested rather than resolved | 100 |
| numeric literals in spans carried by some claim | 97% (4,368 of 4,501) |
| event markers carried | 95%; backticked paths 71% |

Checker rejection rate by translator model: Opus 0.12%, Sonnet 3.32% (shape errors the checker catches).

### The two arms

Baseline: one clean-context Opus agent with the README, the repo and a brief; 27 minutes, 89 tool calls, 320k tokens, 77 items.

| | verified | contradicted | contested | unverifiable / dangling |
|---|---|---|---|---|
| ledger arm, quantitative (50) | 40 | 5 | 5 | 0 |
| ledger arm, hypotheses (15) | 10 | 3 | 2 | 0 |
| ledger arm, verdict nodes (12) | 3 | 2 | 6 | 1 dangling |
| baseline, all 77 | 54 | 12 | 6 | 5 |

Agreement: 60 of 77. Of the 24 items that ended non-verified in the ledger, the adjudicators classified 11 of the arm disagreements as label only (the ledger says contested wherever the record holds unweighed conflict; the baseline weighs) and 13 as substance.

Machine-checkable fraction: every ledger claim re-verifies. Of the baseline's 77 items, 27 rest on live runs with no file quote; of its 109 quoted segments, 83 verify verbatim at the pin, 5 exist only in pre-redaction history, and the rest are command output or the reviewer's summaries.

### Adjudication

Non-blind model rulings (D-12) on the 24 items ending non-verified in the ledger: arm judged right, both 8, baseline 10, ledger 2, neither 4; ledger state equals ruling on 9, baseline on 16.

Blind re-adjudication (D-12b, arms anonymized as A/B per item, reasons removed, mapping sealed until fold): rulings agree with the non-blind ones on 22 of 24 (Q28 moved contradicted to verified, read as a single null test; H06 moved verified to contradicted). Whose evidence decided the ruling, unsealed:

| | all 24 items | 13 substance items |
|---|---|---|
| both arms | 5 | 5 |
| baseline's evidence | 9 | 4 |
| ledger's evidence | 3 | 2 |
| neither (ruling reached from the record directly) | 7 | 2 |
| arm's own state equals the blind ruling: ledger / baseline | 9 / 14 | 8 / 9 |

On substance the arms are close to even; the baseline's overall edge comes from the label items, where the ledger reported unweighed conflict as contested and the record, once weighed, supported one side. A weighing rule over stance and supersession refs was in the design and only partly implemented.

**Owner rulings.** The owner then answered the seven questions the adjudicators had left provisional, and overrode the model ruling on two: asked whether the walkthrough's ASP link stage counts as part of "the symbolic engine", the owner said yes, which makes the Q-22 defect (an unsatisfied `requires` silently false in every enumerated situation, fixed 2026-08-09) an engine wrong answer and turns H08 and V02 from unverifiable to contradicted. Against the final states:

| | all 24 items | 13 substance items |
|---|---|---|
| ledger state equals final ruling | 11 | 10 |
| baseline state equals final ruling | 14 | 7 |

On the substance items the ledger arm ends ahead. Two caveats on that. The ledger reached "contradicted" on H08 and V02 for partly the wrong reason: its 28 engine-failure events include scoring-code and tooling bugs, and the Q-22 case that actually decides the question is not among them — the adjudicator found it. And the owner's boundary ruling is a judgement about the project's own vocabulary, exactly the kind of input neither arm can supply.

Live-run conflicts settled by re-running: the setup check exits 0; pytest gives 2,267 passed and 4 skipped in the README's own venv (2,270 and 1 only with two optional packages installed). Both reproduce the ledger arm's observation.

README dispositions proposed per item (nearly all "tightened", with wording) are in `results/rulings/SUMMARY.md`; the disposition commit to the target repo waits on the seven provisional rulings.

### Registered expectation 1: met

No untracked edits; the ledger passes its own re-check end to end; the checker rejected 219 claims; 100 contested pairs held open; 13 of 15 hypotheses ended definite (threshold 2).

### Registered expectation 2: not met as stated

Re-check cost was as predicted: zero model tokens, seconds. "Correctly" was not:

- Number-mutation probe (Q26, 100 to 94, pre-registered): run 1 changed nothing, because the query table held literal copies of the README values (D-10); run 2, after binding values to the inventory, flipped exactly Q26 and V05 as registered. The baseline half could not be run fairly: the reviewer has the repo and detected the mutation by diff against the original README.
- Fabrication probe (owner's reframing; arc-1 MCC +0.320 / +0.278 treated as fabricated, pre-registered): the ledger predicted Q12, Q13 and V04 fall; a reviewer given its own prior report found nothing changes, because the numbers re-derive from the committed scorer in 12 seconds. The reviewer was right. The ledger held those numbers only as prose because a live run the inventory had declared was never implemented (D-11). Cost of the reviewer's re-check: 120k tokens, 4.5 minutes, about 38% of its first pass, not "roughly full price".

The residue list is non-empty and its boundary was stated in advance.

### The "update against" clause

Interventions did not approach the claim count and no state was dominated by unverifiable. One defect class did recur after being operationalized: the inventory-to-machinery seam leaked three times. That is an update against the method as built, and the fix is a conformance check at that seam, which the design did not have.

### Findings beyond the registered ones

- **The dependency graph is flat.** 41 of 65 inventory items feed no verdict node; no node depends on another; fan-in is at most five. Removing any single record span flips at most one README item (4 of 206 cited spans flip anything); removing a whole fact flips at most two plus a verdict. There is little for a standing artifact to propagate.
- **Cost.** Translation used 140 agents, 15.4M harness tokens (9.1M Opus, 6.3M Sonnet), 911 agent-minutes; about 32x the baseline price-weighted, before prompt-cache discounts. Setup reviews added 1.8M. `results/COST.md`.
- **Mechanical extractability.** About a third of claims had a core a parser could have produced; about half with a labelling step; events, 39% of claims and the inputs to every hypothesis, were 18% mechanical.
- **Capability probe.** Haiku on the same spans: 80 to 100% precision, 0 to 48% recall. A small model fails by silence, which the checker cannot see; the completeness audit against regex denominators can.
- **One finding the review did not surface:** 28 translator-labelled engine-failure events, 9 of them wrong-answer, bearing on the README's "every failure was a refusal". On inspection most are scoring-code or tooling bugs rather than engine outputs. The claim is nonetheless contradicted, on a case neither arm's evidence contained: the adjudicator found the Q-22 defect in the walkthrough's ASP link stage, and the owner ruled that stage part of the engine.

### Fairness of the comparison

Not clean, in both directions. Against the ledger: its query layer was hand-written and patched seven times during the run; declared live runs and named sources were incomplete; it was scored against a label convention. For the ledger: I tuned three queries after reading the baseline's reasons (Q27, V01, H10); it had tens of times the compute and iterations; the number probe was chosen to favor it. The blind re-adjudication corrects the judging; it does not correct the query-tuning leak. Conclusions that do not depend on the comparison: the cost ratio, the flatness, the machinery leaks, the probe outcomes, the completeness and capability numbers.

### What I take from it

The advertised advantage, cheap correct re-verification through a standing artifact, did not materialize on this record: the record is flat, and the ledger's answers were bounded by source coverage that leaked where the inventory became machinery. What did hold: the discipline hypotheses (review before close, freeze before measure, append-only, dated, blind seats) were mechanically decidable wherever the project had imposed conventions on itself, and every failure of the method is a numbered entry with a cause. That reads as a tool for guarding a project's own record against drift, checked at write time, more than as a tool for investigating a record after the fact.

---

*Written by Matt Stults. Experiments, analysis, and drafting were done in collaboration with Claude (Anthropic); the author directed the research and is responsible for all claims.*
