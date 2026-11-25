# Proof World Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **For this project specifically:** the author implements the gates (Tasks 1–3) and the Lean code (Tasks 8–9) **by hand**. That is the learning goal. Claude may help with wiring, tests and review, but must not write those function bodies.

**Goal:** Turn Mileti's §3.4 deduction system into a text-adventure world in the agent-sandbox engine. An LLM player builds a deduction by moving and combining, Python gates enforce the rules on every move, and Lean verifies the finished deduction.

**Architecture:**
- **Pure Python gates.** One function per rule, with no engine imports. Each takes premise lines and returns the new line, or raises `GateError`. These implement Mileti exactly.
- **Engine layer.** Wraps the gates as engine `Action`s, in a world where **a room is an assumption sequence `S`** and **an item in a room is a proved line `S ⊢ φ`**.
- **Knowledge graph.** Fed to the player through the engine's `query_knowledge` and `read_plan` tools.
- **Lean.** The trace of accepted moves is exported to Lean and checked by the author's `Derivable` predicate.

**Tech Stack:** Python 3.13 (standard library plus the agent-sandbox engine, installed editable). Lean 4 v4.28.0, without Mathlib.

**Spec:** `docs/design.md` (§3 is the rule table), plus the design update at the end of that file.

## Global Constraints
- Scope: Mileti Ch. 1–3 only.
- The 14 rule ids are exactly: `assume andEL andER andI orIL orIR impE impI orPC negPC contr expand delete reorder`. They are used as gate names, action verbs, knowledge-graph rule ids and Lean constructor names.
- `S, φ` means `S + (φ,)` in Python and `S ++ [φ]` in Lean. New assumptions always go on the right. Assumption sequences are ordered and may repeat.
- Formulas use `harness/formula.py` (`Atom`, `Not`, `Bin`). ASCII syntax: `~ & | ->`.
- Lean names: `MiletiLogic.Formula` with constructors `atom (n : Nat)`, `neg`, `conj`, `disj`, `imp`, `deriving DecidableEq, Repr`; and `MiletiLogic.Derivable : List Formula → Formula → Prop` with one constructor per rule id.
- The knowledge graph shown to the player must never contain solutions to benchmark items (see `kg/extracted/README.md`).
- agent-sandbox is a dependency (`pip install -e ~/agent-sandbox`). It is not copied into this repo, and this project never edits it.

## Review Focus
1. **Free formulas outside the candidate set.** Examples: `orIL` with a ψ the problem never mentions; `expand` with a random γ. Expect the action layer to refuse, with the reason "outside candidate set", which is different from "illegal". The gate itself still accepts it, as Mileti does. Owner: Task 5 (`test_free_formula_outside_candidates_refused`).
2. **Rules that need *identical* assumption sequences** (`andI`, `orPC`, `negPC`, `contr`), given premises whose assumptions are the same *set* in a different *order*. Expect a refusal that names the mismatch. Owner: Task 2 (`test_andI_rejects_reordered_contexts`).
3. **`impI` when φ is in `S` but not last.** Expect a refusal that suggests `reorder`. Owner: Task 3 (`test_impI_requires_last_assumption`).
4. **The player names an item that exists in another room.** Expect "that line is not proved in this room", not a crash. Owner: Task 5 (`test_item_from_other_room_refused`).
5. **Python accepts a deduction that Lean rejects.** This means a gate bug. Expect the cross-check to fail loudly and name the step. Owner: Task 9 (`test_python_accepted_traces_pass_lean`).

---

## Phase 1: Python gates (the author writes the bodies)

### Task 1: Lines, gate errors, and one-premise rules

**Files:**
- Create: `proofworld/__init__.py`, `proofworld/gates.py`
- Test: `tests/test_gates.py`

**Interfaces:**
- Produces:
  - `Seq = tuple[Formula, ...]`
  - `@dataclass(frozen=True) class Line: assumptions: Seq; goal: Formula`
  - `class GateError(Exception)`, with `.rule: str` and `.reason: str`
  - `assume(S: Seq, phi: Formula) -> Line`
  - `andEL(p: Line) -> Line`, `andER(p: Line) -> Line`
  - `orIL(p: Line, psi: Formula) -> Line`, `orIR(p: Line, phi: Formula) -> Line`

- [ ] **Step 1: Write failing tests.** Use `F = harness.formula.parse`.
  - `test_assume_ok`: `assume((F("A&B"),), F("A&B")) == Line((F("A&B"),), F("A&B"))`
  - `test_assume_rejects_absent`: `assume((F("A"),), F("B"))` raises `GateError` with `.rule == "assume"`
  - `test_andEL_andER`: from `Line((F("A&B"),), F("A&B"))`, `andEL` gives goal `A` and `andER` gives goal `B`, and the assumptions are unchanged
  - `test_andEL_rejects_non_conjunction`: `andEL(Line((F("A|B"),), F("A|B")))` raises `GateError`
  - `test_orIL_orIR`: `orIL(Line(S, F("A")), F("B")).goal == F("A|B")` and `orIR(Line(S, F("B")), F("A")).goal == F("A|B")`
- [ ] **Step 2:** Run `python3 -m pytest tests/test_gates.py -v`. Expected: FAIL, because `proofworld` doesn't exist yet.
- [ ] **Step 3:** Implement the five gates in `proofworld/gates.py`. Each `GateError` reason says which side condition failed, in plain words.
- [ ] **Step 4:** Run the tests again. Expected: PASS.
- [ ] **Step 5:** `git add proofworld tests/test_gates.py && git commit -m "feat(gates): lines and one-premise rules"`

### Task 2: Two-premise rules (the "combine" rules)

**Files:**
- Modify: `proofworld/gates.py`
- Test: `tests/test_gates.py`

**Interfaces:**
- Produces: `andI(p1: Line, p2: Line) -> Line`, `orPC(p1: Line, p2: Line) -> Line`, `negPC(p1: Line, p2: Line) -> Line`, `contr(p1: Line, p2: Line) -> Line`.
- Premise order follows the book:
  - `andI`: left conjunct, then right
  - `orPC`: the φ case, then the ψ case
  - `negPC`: the ψ case, then the ¬ψ case
  - `contr`: the line proving ψ, then the line proving ¬ψ

- [ ] **Step 1: Write failing tests.**
  - `test_andI_ok`: two lines with the same S give `S ⊢ A&B`
  - `test_andI_rejects_reordered_contexts`: `S=(A,B)` and `S=(B,A)` raise `GateError`, and the reason mentions "same assumptions"
  - `test_orPC_ok`: `(A,) ⊢ C` and `(B,) ⊢ C` give `(A|B,) ⊢ C`
  - `test_orPC_rejects_different_goals`
  - `test_negPC_ok`: `(A,) ⊢ C` and `(~A,) ⊢ C` give `() ⊢ C`
  - `test_contr_ok`: `(~A, …) ⊢ B` and `(~A, …) ⊢ ~B` give `(…) ⊢ A`
  - `test_contr_rejects_non_negation_last`: when the last assumption is not a negation, it raises `GateError`
- [ ] **Step 2:** Run the tests. Expected: FAIL.
- [ ] **Step 3:** Implement the four gates.
- [ ] **Step 4:** Run the tests. Expected: PASS.
- [ ] **Step 5:** Commit: `feat(gates): combine rules`

### Task 3: Rules that change the room (the "movement" rules)

**Files:**
- Modify: `proofworld/gates.py`
- Test: `tests/test_gates.py`

**Interfaces:**
- Produces:
  - `expand(p: Line, gamma: Formula) -> Line`
  - `delete(p: Line) -> Line`: removes the last of two equal trailing assumptions
  - `reorder(p: Line, i: int) -> Line`: swaps positions `i` and `i+1`
  - `impE(p: Line) -> Line`: from `S ⊢ φ→ψ`, gives `S,φ ⊢ ψ`
  - `impI(p: Line) -> Line`: from `S,φ ⊢ ψ`, gives `S ⊢ φ→ψ`
  - `RULES: dict[str, Callable[..., Line]]`, keyed by all 14 rule ids

- [ ] **Step 1: Write failing tests.**
  - `test_expand_appends_right`
  - `test_delete_ok` and `test_delete_rejects_no_duplicate`
  - `test_reorder_swaps_adjacent` and `test_reorder_rejects_out_of_range`
  - `test_impE_ok`
  - `test_impI_ok`
  - `test_impI_requires_last_assumption`: with `S=(A,B)` and goal `C`, `impI` gives `(A,) ⊢ B->C`. With `S=(B,A)`, it does not give `A->C`; the reason mentions `reorder`
  - `test_RULES_has_14`: `set(RULES) == {the 14 ids}`
- [ ] **Step 2:** Run the tests. Expected: FAIL.
- [ ] **Step 3:** Implement the gates and `RULES`.
- [ ] **Step 4:** Run the tests. Expected: PASS.
- [ ] **Step 5:** Commit: `feat(gates): movement rules`

### Task 4: Traces, and replaying the book's deductions through your gates

**Files:**
- Create: `proofworld/trace.py`
- Test: `tests/test_trace.py`

**Interfaces:**
- Consumes: `RULES`, `Line`, `GateError` (Tasks 1–3).
- Produces:
  - `@dataclass(frozen=True) class Step: n: int; line: Line; rule: str; premises: tuple[int, ...]; args: tuple`
  - `class Trace` with:
    - `.steps: list[Step]`
    - `.apply(rule: str, premises: tuple[int, ...], args: tuple = ()) -> Step`: raises `GateError`; a step is recorded only if it is accepted
    - `.proves(target: Line) -> bool`
  - `replay(kg_steps: list[dict]) -> Trace`: for the knowledge-graph step format. Free formulas (orIL ψ, orIR φ, expand γ) are inferred from the stated line; the result must equal the stated line.

- [ ] **Step 1: Write failing tests.**
  - `test_apply_records_only_accepted`: a rejected `apply` leaves `len(steps)` unchanged
  - `test_replay_all_book_deductions`: every node in `kg/extracted/nodes.jsonl` with `steps` replays without error, and `trace.proves(last line)` is true. There are 14 worked deductions plus the Lemma 3.5.9 ones.
  - `test_replay_oracle_solutions`: the same check for `kg/extracted/oracle/exercise_solutions.jsonl`
  - `test_replay_catches_corruption`: change one step's rule from `andEL` to `andER`; it raises `GateError`
- [ ] **Step 2:** Run the tests. Expected: FAIL.
- [ ] **Step 3:** Implement `Trace` and `replay`.
- [ ] **Step 4:** Run the tests. Expected: PASS. Any book deduction that fails is either a gate bug or a transcription error in the graph. Fix whichever it is, and record the case in `kg/extracted/README.md`.
- [ ] **Step 5:** Commit: `feat(trace): replay book deductions through gates`

**Checkpoint: Phase 1 done.** Your Python gates now accept every deduction in the book.

---

## Phase 2: The world (engine wiring; Claude may help here)

### Task 5: The Proof World in the engine

**Files:**
- Create: `proofworld/world.py`, `proofworld/actions.py`, `play.py`
- Test: `tests/test_world.py`

**Interfaces:**
- Consumes:
  - `Trace` (Task 4)
  - the engine's `Action` (`__init__(self, game, command, actor=None)`, `check_preconditions() -> bool`, `apply_effects()`), `Game(start_at, player, custom_actions=...)`, `Location`, `Item`, `Character`
  - Read `~/agent-sandbox/text_adventure_games/adventures/action_castle.py` and `actions/use.py` first.
- Produces:
  - `candidates(target: Line) -> frozenset[Formula]`: subformulas of the target's goal and assumptions, closed under one `~`
  - `build_game(target: Line) -> Game`:
    - the player starts in the room for `target.assumptions`
    - each room `S` holds one assumption item per formula in `S`; `take` uses `assume`
    - one `Action` subclass per rule; its verb is the rule id in lower case
    - the game is won when an item `target.goal` exists in room `target.assumptions`
  - `game.trace: Trace`: every accepted move, in order
- Verbs. Each item is named by its formula:
  - `take P`
  - `andel P&Q`, `orir Q with P`, `andi P with Q`
  - `expand P with G`, which moves the line into room `S,G`
  - `impe P->Q`, which moves into room `S,P`
  - `impi Q`, which moves back out to `S`
  - `go <room>`
  - Rooms are created when first entered. The room description lists its items and the legal verbs.

- [ ] **Step 1: Write failing tests.**
  - `test_book_example_playable`: for target `A&B ⊢ A|B`, running the commands `take A&B`, `andel A&B`, `oril A with B` wins, and `game.trace` has 3 steps
  - `test_free_formula_outside_candidates_refused`: `oril A with Z` is refused with "outside candidate set"
  - `test_item_from_other_room_refused`
  - `test_room_description_lists_legal_verbs`
- [ ] **Step 2:** Run the tests. Expected: FAIL.
- [ ] **Step 3:** Implement. Gates are called only from inside `check_preconditions`; a `GateError` becomes the refusal message.
- [ ] **Step 4:** Run the tests. Expected: PASS. Then play by hand with `python3 play.py "A & B" "A | B"` and solve one book example in the terminal.
- [ ] **Step 5:** Commit: `feat(world): proof world in agent-sandbox engine`

### Task 6: The LLM player

**Files:**
- Create: `proofworld/player.py`
- Test: `tests/test_player.py`

**Interfaces:**
- Consumes: `build_game` (Task 5); the engine's `LLMAgent`, `ScriptedAgent` and `tools_for(parser, actor)`.
- Produces: `run_episode(target: Line, agent, max_steps: int = 40, condition: str = "A") -> EpisodeResult`, where `EpisodeResult` has `solved: bool`, `steps: int`, `rejected: int`, `trace: Trace`, `tool_calls: Counter` and `log: list[dict]`.

- [ ] **Step 1: Write failing tests.**
  - `test_scripted_agent_solves_book_example`: with a `ScriptedAgent` using Task 5's commands, `solved is True` and `rejected == 0`
  - `test_step_budget_stops`: a scripted agent that repeats a refused move stops at `max_steps` with `solved is False`
- [ ] **Step 2:** Run the tests. Expected: FAIL.
- [ ] **Step 3:** Implement on top of the engine's agent loop. Condition A shows the goal, the room and the items. Condition B also lists the legal moves at each step.
- [ ] **Step 4:** Run the tests. Expected: PASS. Then make one live run with a small local model (Ollama, which is already set up in agent-sandbox).
- [ ] **Step 5:** Commit: `feat(player): LLM player episodes`

### Task 7: Graph retrieval (the player's "consult the book")

**Files:**
- Create: `proofworld/retrieval.py`
- Test: `tests/test_retrieval.py`

**Interfaces:**
- Consumes: the `kg/` or `kg/extracted/` JSONL files; the engine's `Knowledge` and `read_plan` tool.
- Produces:
  - `load_graph(path: Path) -> Graph`
  - `plan_for(target: Line, graph: Graph, exclude: set[str]) -> str`: strategy nodes whose trigger matches the goal's and assumptions' main connectives, plus the nearest worked example by connective profile, never one whose id is in `exclude`
  - `knowledge_for(graph) -> Knowledge`: beliefs for `query_knowledge`

- [ ] **Step 1: Write failing tests.**
  - `test_plan_for_implication_mentions_impI`
  - `test_plan_excludes_benchmark_items`: when the target equals a book example's sequent, that example never appears in the plan
  - `test_query_knowledge_finds_rule`: the topic "contr" returns the `rule:contr` text
- [ ] **Step 2:** Run the tests. Expected: FAIL.
- [ ] **Step 3:** Implement.
- [ ] **Step 4:** Run the tests. Expected: PASS.
- [ ] **Step 5:** Commit: `feat(retrieval): plan and knowledge from the graph`

---

## Phase 3: Lean (the author writes it)

### Task 8: `Formula` and `Derivable` in Lean

**Files:**
- Modify: `lean/MiletiLogic/Syntax.lean`, `lean/MiletiLogic/Deduction.lean`
- Create: `lean/MiletiLogic/BookExamples.lean` (import it from `lean/MiletiLogic.lean`)

**Interfaces:**
- Produces the Lean names given in Global Constraints. Each `Derivable` constructor takes its premise proofs in the book's premise order, and takes free formulas as explicit arguments.

- [ ] **Step 1:** Write `BookExamples.lean` with the 9 items from `benchmark/book_items.jsonl` as `example : Derivable [...] (...) := by sorry`.
- [ ] **Step 2:** Run `cd lean && ~/.elan/bin/lake build`. Expected: the build succeeds, with 9 `sorry` warnings.
- [ ] **Step 3:** Write `Formula` and the 14 `Derivable` constructors.
- [ ] **Step 4:** Replace each `sorry` with a proof term built from your constructors. Run `lake build`. Expected: the build succeeds with no `sorry` warnings.
- [ ] **Step 5:** Commit: `feat(lean): Formula, Derivable, book examples`

### Task 9: The Lean verifier and the cross-check

**Files:**
- Create: `proofworld/lean_export.py`
- Modify: `harness/loop.py` (reuse `lean_check`)
- Test: `tests/test_lean_export.py`

**Interfaces:**
- Consumes: `Trace` (Task 4), `lean_check(source) -> (bool, str)`, and your constructors (Task 8).
- Produces: `to_lean(trace: Trace, target: Line, name: str) -> str`, which writes a Lean file `import MiletiLogic` containing `theorem <name> : Derivable [...] φ := <term>`. The term is the tree of `Derivable.<rule>` applications rooted at the step that proves `target`. Assume steps discharge membership with `by decide`.

- [ ] **Step 1: Write failing tests.**
  - `test_python_accepted_traces_pass_lean`: every replayed book deduction (Task 4) exports and passes `lean_check`. On failure, print the step number and Lean's message.
  - `test_lean_rejects_bad_trace`: build a trace by hand whose step falsely claims `andEL` gives the right conjunct. Bypass the gates by constructing `Step` directly; `lean_check` returns `False`.
- [ ] **Step 2:** Run the tests. Expected: FAIL.
- [ ] **Step 3:** Implement `to_lean`.
- [ ] **Step 4:** Run the tests. Expected: PASS.
- [ ] **Step 5:** Commit: `feat(lean): export traces and cross-check gates against Lean`

**Stretch:** in Lean, prove `Derivable S φ → S ⊨ φ` (soundness, Mileti §3.5).

---

## Phase 4: Experiment

### Task 10: Generated benchmark

**Files:**
- Create: `benchmark/generate.py`, `benchmark/generated.jsonl`
- Test: `tests/test_generate.py`

**Interfaces:**
- Produces: `generate(n: int, atoms: int, seed: int) -> list[dict]`, returning sequents that are valid by truth table. Each comes with `difficulty`: the length of the shortest proof found by breadth-first search over your gates, limited to the candidate set, with a depth cap.

- [ ] **Step 1:** Write failing tests:
  - `test_all_generated_valid`
  - `test_deterministic_given_seed`
  - `test_no_overlap_with_book_items`
  - `test_difficulty_spread`: at least 3 different difficulty values
- [ ] **Steps 2–4:** Run, implement, run. Generate 200 sequents over 2–4 atoms.
- [ ] **Step 5:** Commit: `feat(bench): generated sequents with difficulty`

### Task 11: Runner. Positive control first, then all conditions

**Files:**
- Create: `experiments/run.py`, `experiments/analyze.py`

**Interfaces:**
- Consumes: `run_episode` (Task 6), `plan_for` and `knowledge_for` (Task 7), `to_lean` (Task 9).
- Produces: `runs/<date>/<condition>.jsonl`, with one `EpisodeResult` per (item, model, seed), plus a Lean verdict for each solved trace.

Lessons from `~/agent-sandbox/kg_runs/logic` and `kg_runs/maproof`, built into the design:
1. **Run the oracle against no-graph first, as a pilot.** If the oracle doesn't help, the knowledge-graph conditions can't be interpreted.
2. **Avoid the ceiling.** Pick items by difficulty, so the strong model doesn't solve everything.
3. **Log whether the player actually called `read_plan` and `query_knowledge`.** Earlier runs found agents ignoring hints.
4. **Score only what Lean accepts.** Don't trust the agent's own report.

- [ ] **Step 1:** Pilot: conditions A and E (oracle) on 30 mid-difficulty items, small model, 1 seed. Go on only if E − A > 0.
- [ ] **Step 2:** Full run: conditions A to E, 2 models, 3 seeds.
- [ ] **Step 3:** `analyze.py`: solve rate, steps, rejected moves, tool-call rates, paired McNemar tests, and a failure taxonomy taken from the refusal reasons.
