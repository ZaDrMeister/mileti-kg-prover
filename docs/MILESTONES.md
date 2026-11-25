# Milestones: Proof World (Mileti Ch. 1–3)

This is a quick guide to each milestone: what to build, what to understand first, how to build it, and how you know you're done. The detailed task list with test names is in `docs/superpowers/plans/2026-11-12-proof-world.md`, and the rule table is in `docs/design.md` §3.

**What's yours:** the gates (M1–M3) and the Lean code (M6–M7). Each section shows **one rule as a worked example**; the other rules follow the same pattern and are yours to write. For anything else, ask Claude for review, hints or the wiring.

| # | Milestone | Dates | Language | Done when |
|---|---|---|---|---|
| M0 | Setup | Nov 12–14 | — | The engine imports, tests pass, you've played Action Castle |
| M1 | First gates | Nov 15–21 | Python | `assume`, ∧E and ∨I pass their tests |
| M2 | All 14 gates | Nov 22–28 | Python | `RULES` has 14 entries; every test passes |
| M3 | Replay the book | Nov 29–Dec 5 | Python | Every book deduction replays through your gates |
| M4 | Playable world | Dec 6–19 | Python | You solve `A&B ⊢ A\|B` by typing commands |
| M5 | LLM player + graph | Dec 20–Jan 9 | Python | An LLM solves a book example; it can consult the graph |
| M6 | Lean rules | Jan 10–30 | Lean | 14 constructors; the 9 book proofs with no `sorry` |
| M7 | Lean verifier | Jan 31–Feb 13 | Python + Lean | Every trace Python accepts also passes Lean |
| M8 | Benchmark + pilot | Feb 14–Mar 6 | Python | 200 generated items; the oracle beats no help in a pilot |
| M9 | Full experiment | Mar 7–Apr 17 | Python | All conditions × 2 models × 3 seeds; analysis done |
| M10 | Paper | Apr 18–Jun | LaTeX | A workshop draft plus an arXiv preprint |

**For applications in December:** by then M3–M4 are done. That's enough to describe the project as "a working proof world in which every textbook deduction replays; Lean verifier in progress".

---

## M0. Setup (Nov 12–14)

**Goal:** the engine runs inside your project.

**How:**
1. Create a virtual environment in the project: `python3 -m venv .venv && source .venv/bin/activate`
2. Install the engine as an editable dependency: `pip install -e ~/agent-sandbox pytest`
3. Check that it imports: `python -c "import text_adventure_games; print('ok')"`
4. Run the tests: `python -m pytest -q` (7 pass) and `cd lean && ~/.elan/bin/lake build`
5. Play Action Castle once, and read the `Unlock_Door` action in `~/agent-sandbox/text_adventure_games/adventures/action_castle.py`. That pattern, `check_preconditions` followed by `apply_effects`, is exactly what your gates plug into.

**Understand first:** Mileti §3.4. Write out the 14 rules by hand on paper once.

**Done when:** steps 3 and 4 work.

---

## M1. First gates (Nov 15–21), Python

**Goal:** `Line`, `GateError`, and the first five rules (`assume`, `andEL`, `andER`, `orIL`, `orIR`) in `proofworld/gates.py`.

**Understand first:**
- A **line** is `S ⊢ φ`: a tuple of formulas plus one formula. Make it a frozen dataclass, so lines can be compared and stored in sets.
- A **gate** is a pure function: premise lines in, new line out, or it raises `GateError` saying *which* side condition failed. Gates have no engine code in them; that's what makes them easy to test.
- Formulas come from `harness/formula.py`: `Atom(name)`, `Not(a)`, `Bin(op, a, b)` with op `"&"`, `"|"` or `"->"`.

**Worked example (andEL):**
```python
def andEL(p: Line) -> Line:
    if not (isinstance(p.goal, Bin) and p.goal.op == "&"):
        raise GateError("andEL", "the line's formula is not a conjunction")
    return Line(p.assumptions, p.goal.a)
```
Each gate has the same three parts: check the shape, raise with a reason, then build the conclusion. `orIL` takes an extra argument, the formula ψ to join on, because the book lets you choose any ψ.

**How (test first):** write the tests from the plan's Task 1 → run them and watch them fail → write the gates → run them and watch them pass → commit.

**Done when:** `python -m pytest tests/test_gates.py` passes.

---

## M2. All 14 gates (Nov 22–28), Python

**Goal:** the combine rules (`andI`, `orPC`, `negPC`, `contr`), the movement rules (`expand`, `delete`, `reorder`, `impE`, `impI`), and `RULES`, a dictionary of all 14 keyed by rule id.

**Understand first:**
- **Sequences, not sets.** `andI`, `orPC`, `negPC` and `contr` need the *same* assumption tuple on both premises: same order, same repeats. If the order differs, the player must `reorder` first. That's the book's rule, not a bug.
- **"S, φ" means the last position.** `orPC`, `negPC` and `contr` look at the *last* assumption of each premise, and `impI` removes only the last one. Use `S[:-1]` and `S[-1]`.
- **Premise order is fixed by the book.** For example `negPC(p1, p2)`: `p1` is the ψ case and `p2` is the ¬ψ case.

**How:** the same test-first loop, with tests from Tasks 2–3. Test the tricky cases on purpose: assumptions in a different order, φ not last for `impI`, and `delete` with no duplicate.

**Done when:** all gate tests pass and `set(RULES) ==` the 14 rule ids.

---

## M3. Replay the book (Nov 29–Dec 5), Python

**Goal:** `proofworld/trace.py` with `Trace.apply(rule, premises, args)` and `replay(kg_steps)`. **Every** worked deduction in `kg/extracted/` replays through your gates.

**Understand first:**
- A **trace** is a numbered list of accepted steps. Each step records the line, the rule, the premise step numbers and any free formulas. This is the same thing as Mileti's deduction (Definition 3.4.4).
- The graph's deductions don't store free formulas. Recover them from the stated line: for `orIL`, ψ is the right side of the stated goal.

**How:** load each graph node that has `steps`, feed each step to `Trace.apply`, and check that the result equals the stated line.

**Done when:** `test_replay_all_book_deductions` passes. If a deduction fails, decide whether your gate is wrong or the graph is, and write down which. This is the first real result: *your code agrees with the book on every worked deduction.*

---

## M4. Playable world (Dec 6–19), Python, Claude can help

**Goal:** `build_game(target)` in `proofworld/world.py`, plus `play.py`, so you can play a proof in the terminal.

**Understand first (the mapping):**

| Game | Logic |
|---|---|
| Room | an assumption sequence `S` |
| Item in a room | a proved line `S ⊢ φ` |
| `take P` | Assume |
| Transform one item (`andel`, `oril`, …) | one-premise rule |
| Combine two items (`andi P with Q`, `orpc`, `negpc`, `contr`) | two-premise rule |
| Walk to another room (`expand`, `impe`, `impi`, `reorder`, `delete`) | a rule that changes `S` |
| Win | the goal formula is an item in the starting room |

**How:**
1. One `Action` subclass per rule, following `Unlock_Door`. In `__init__`, parse the command and find the item(s). In `check_preconditions`, call your gate inside `try`: on `GateError`, report the reason and return `False`, and on success keep the new line. In `apply_effects`, put the new item in the right room (creating the room if needed) and append the step to `game.trace`.
2. Restrict free formulas (`oril A with B`, `expand … with G`) to the **candidate set**: subformulas of the problem, plus their negations. Otherwise the game is infinite.
3. Each room's description lists its items and the verbs that are legal right now. That list is what condition B shows the LLM.

**Done when:** `python play.py "A & B" "A | B"` lets you win with `take A & B` → `andel A & B` → `oril A with B`.

---

## M5. LLM player + graph (Dec 20–Jan 9), Python, Claude can help

**Goal:** `run_episode(target, agent, max_steps, condition)` and `plan_for(target, graph, exclude)`.

**Understand first:**
- The engine's `LLMAgent` already turns registered actions into tools. Your job is the **observation**: the goal, the current room, the items, and (in condition B) the legal moves.
- The graph reaches the player through two tools: `read_plan` (a strategy for this goal's shape, plus the nearest worked example) and `query_knowledge` (look up a rule or definition).
- **Exclude benchmark items** from `plan_for`, or the player is shown the answer.

**How:** first use a `ScriptedAgent` with fixed commands, to test the loop without a model. Then use a small local model through the engine's Ollama setup. Log every tool call.

**Done when:** a scripted agent solves a book example, and one real model run is logged with its tool calls.

---

## M6. Lean rules (Jan 10–30), Lean

**Goal:** `Formula` and `Derivable` in `lean/MiletiLogic/`, and the 9 book items proved in `BookExamples.lean`.

**Understand first (Lean in five ideas):**
1. `inductive` defines a type by listing its constructors. Formulas are atoms plus four ways to build bigger ones.
2. `inductive … : … → Prop` defines a *predicate*. Each constructor is one rule, and a proof of `Derivable S φ` is a tree of rule applications. That's Mileti's generating system (Definition 3.4.3) made literal.
3. `S ++ [φ]` is "S, φ". Lists keep order and repeats, just like Mileti's sequences.
4. `example : Derivable [...] φ := ...` states a fact and gives its proof term. `sorry` is a placeholder that still compiles, with a warning.
5. `by decide` proves concrete facts such as `φ ∈ [ψ, φ]` automatically, once `Formula` has `deriving DecidableEq`.

**Worked example (two of the 14 constructors):**
```lean
namespace MiletiLogic

inductive Formula where
  | atom (n : Nat)
  | neg  (φ : Formula)
  | conj (φ ψ : Formula)
  | disj (φ ψ : Formula)
  | imp  (φ ψ : Formula)
  deriving DecidableEq, Repr

inductive Derivable : List Formula → Formula → Prop where
  | assume {S : List Formula} {φ : Formula} : φ ∈ S → Derivable S φ
  | andEL  {S : List Formula} {φ : Formula} (ψ : Formula) :
      Derivable S (.conj φ ψ) → Derivable S φ
  -- your 12 more: andER andI orIL orIR impE impI orPC negPC contr expand delete reorder

open Formula in
example : Derivable [conj (atom 0) (atom 1)] (atom 0) :=
  Derivable.andEL (atom 1) (Derivable.assume (by decide))

end MiletiLogic
```
This example compiles (checked with Lean 4.28). **Why `ψ` is explicit in `andEL`:** the conclusion `Derivable S φ` doesn't mention ψ, so Lean can't guess which conjunct was dropped. Any formula that appears only in a premise must be an explicit argument: ψ in ∧EL, φ in ∧ER, the case formula in ¬PC, and ψ in Contr. Without it you get the error "Expected type must not contain metavariables".
Rules that create new assumptions use `S ++ [φ]`. For example, `impI` takes `Derivable (S ++ [φ]) ψ` and gives `Derivable S (.imp φ ψ)`.

**How:** write all 9 book examples as `example … := by sorry` first, and check that `lake build` compiles. Then add constructors one at a time and replace each `sorry` with a proof term. Read Lean's error messages: they tell you which list or formula didn't match.

**Done when:** `lake build` passes with no `sorry` warnings. *Stretch:* soundness (`Derivable S φ → S ⊨ φ`, Mileti §3.5), the strongest Lean result to show admissions committees.

---

## M7. Lean verifier (Jan 31–Feb 13), Python + Lean

**Goal:** `to_lean(trace, target, name)` turns a game trace into a Lean `theorem`. A cross-check test runs every trace your Python gates accept through Lean.

**Understand first:** a trace is a list, but a Lean proof is a tree. Start from the step that proves the goal and recurse into its premises. Each step becomes `Derivable.<rule>` applied to its premises' terms, and each Assume step becomes `Derivable.assume (by decide)`.

**How:** export one book example by hand first and check it with `lake env lean`. Then write `to_lean` to produce exactly that text, and then generalize.

**Done when:** `test_python_accepted_traces_pass_lean` passes, and a deliberately broken trace is rejected. **If Python accepts a trace but Lean rejects it, a gate is wrong.** This is the guarantee the paper rests on.

---

## M8. Benchmark + pilot (Feb 14–Mar 6), Python

**Goal:** 200 generated sequents with difficulty labels, plus a pilot run.

**How:**
1. Generate random formulas over 2–4 atoms, and keep a sequent only if `harness.semantics.entails` says it's valid. By completeness (§3.5), every valid sequent has a deduction.
2. Difficulty = the shortest proof found by breadth-first search over your gates, limited to the candidate set, with a depth cap.
3. **Pilot:** run condition A (no help) against E (oracle plan) on 30 mid-difficulty items with the small model. **Continue only if E beats A.** Your `kg_runs/maproof` results show why: when even the oracle doesn't help, no comparison between conditions can be interpreted.

**Done when:** `benchmark/generated.jsonl` exists, and the pilot shows E > A.

---

## M9. Full experiment (Mar 7–Apr 17), Python

**Goal:** conditions A–E (see `docs/design.md` §7) × a small and a strong model × 3 seeds.

**How:**
- Score only proofs that Lean accepts.
- Log the rejected moves and their reasons. That's your failure taxonomy.
- Log whether the player actually called `read_plan` and `query_knowledge`.
- Compare conditions with paired McNemar tests.

**Done when:** `experiments/analyze.py` produces the results table and the failure-taxonomy figure.

---

## M10. Paper (Apr 18–Jun), LaTeX

**Goal:** a workshop paper (AI for Math, MATH-AI or NeSy) and an arXiv preprint. Start from `docs/handout/research-plan.tex`: its related-work section and research questions become the paper's introduction.

**Done when:** the paper is submitted, and the repo is public with a README that reproduces the results.
