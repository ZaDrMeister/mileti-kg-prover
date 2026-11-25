# Extracted knowledge-graph bank: Mileti Ch. 1–3 (AI-built)

AI readers built this bank from Mileti, *A Mathematical Introduction to Mathematical Logic* (2020): Chapters 1–2, §3.1–3.3 and §3.4–3.7. Claude merged and checked it on 2026-11-12. It is **condition D** in the design (the "extracted graph"). Your hand-written graph in `kg/` is a separate thing.

**Size:** 306 nodes and 864 edges.

| Type | Count | Notes |
|---|---|---|
| definition | 71 | |
| theorem | 68 | Every Theorem, Proposition, Lemma and Corollary, each with a `proof_idea` |
| rule | 14 | Ids match your Lean constructors (`rule:andEL` …). Each has `premises`, `conclusion`, `side_condition` and `backward_free_formula` |
| example | 46 | Includes 14 worked deductions with `assumptions`, `goal` and `steps` |
| strategy | 43 | |
| pitfall | 28 | |
| exercise | 28 | Every exercise in §2.6 and §3.7. Each has a `kind`: deduction, metatheory, semantic, computation or other |
| notation | 8 | |

## Conventions
- **Ids** use Mileti's numbering: `def:3.4.7`, `thm:3.4.10`, `ex:3.7.8a`. `thm:` covers Propositions, Lemmas and Corollaries too. Unnumbered items get slugs, e.g. `example:3.4-distribute`, `strategy:goal-implication-impI`.
- **Formulas** in `assumptions`, `goal` and `steps` use the harness's ASCII syntax: `~ & | ->`. Schematic φ, ψ, θ are written as atoms P, Q, R.
- **Steps:** `{"n", "assumptions", "goal", "rule", "from"}`. Assumptions are in the book's order, and new assumptions go on the right. `from` lists premise lines in the book's premise order.
- **Edge relations:** `depends_on`, `uses_rule`, `illustrates`, `strategy_for`, `pitfall_of`, `generalizes`, `instance_of`.

## Fixes made during the merge
- The four truth-table clauses in §3.2 were labelled as rules. They are now definitions (`def:3.2-v-*`).
- Chapter 2's forward links to "def:3.1.2" were wrong: that number is the parenthesis weight function. They now point to `def:3.1.1` (formulas) and `def:3.1.6` (Polish notation).
- Countable sets are in Appendix A.2 of the book, not Chapter 1. Added `thm:A.2.4`, which §3.5 cites.
- **Exercise solutions were taken out of the bank** and put in `oracle/exercise_solutions.jsonl`. Exercises 3.7 #7, #8a and #8b are benchmark items, so the knowledge-graph conditions must not see their answers. Those solutions were written by AI, not taken from the book. Use them only for the oracle condition or for checking. The readers' hints in these exercises' text were also replaced with the plain problem statement. Their links to rules, strategies and examples were removed, 15 edges in all; only links to definitions remain.
- **Remaining contamination, which comes from the book itself:** the §3.4 worked deductions are in the bank with full steps. Those same deductions are also the book development set in `benchmark/book_items.jsonl`. Exercise 3.7 #8a is also the first half of a worked example. That's acceptable for a development set; the main benchmark is generated sequents, which aren't in the bank.
- The readers corrected and noted several book typos. Examples: a step labelled "∨I" that is really ∨IL; a step in Lemma 3.5.9 labelled ∨I that is really ∧I; and Exercise 9(b) citing the wrong theorem number.

## Checks
- `python3 -m harness.kg_check kg/extracted` passes. It checks the schema and unique ids, confirms every edge endpoint exists, confirms the rule set is exactly the 14 rules, and truth-table-checks every line of every deduction.
- The deductions were also checked rule by rule by a throwaway Python checker. That checker is not in this repo, because the rule checker is yours to write in Lean.
- The text is paraphrased. A scan for runs of 10 or more words shared with the book finds only formula and notation fragments, not prose.

## Caveats
- Some proof ideas are the AI's own sketches, where the book leaves a proof as an exercise. Examples: Prop. 3.1.13(1), 3.2.3(1) and 3.2.11. Their node text says so.
- New benchmark material: the proof of Lemma 3.5.9 contains 8 more schematic deductions (`example:3.5-*`).
