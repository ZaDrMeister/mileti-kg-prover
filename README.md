# mileti-kg-prover

An LLM builds formal deductions in propositional logic using the proof system of Mileti, *A Mathematical Introduction to Mathematical Logic*, §3.4. At each step:

- **Rule gates** (hand-written, one per rule) say which moves are legal right now.
- An **LLM-extracted knowledge graph** of the book explains what things mean and which strategy to use.
- **Lean** checks every step.

The research question: how much does each layer help a small model and a strong model? See [`docs/design.md`](docs/design.md).

**Status (Nov 2026):** early work. The scaffold and design are done, and the Lean formalization is next. **Start here:** [`docs/STEP-1-GUIDE.md`](docs/STEP-1-GUIDE.md). Related work: [`docs/related-work.md`](docs/related-work.md).

**Who wrote what:** the Lean syntax and the 14 deduction rules, and the Python rule gates, are written by hand by the author (Dren Zabeli). The knowledge graph is LLM-extracted by design: the experiment asks whether *automatically built* book knowledge helps. It stays out of the public repo because it paraphrases the whole book. The Python harness scaffold and the planning documents were drafted with AI assistance.

## Layout

| Path | What | Who writes it |
|---|---|---|
| `lean/MiletiLogic/Syntax.lean` | Formulas (Ch. 2, §3.1) | **you** |
| `lean/MiletiLogic/Deduction.lean` | The 14 rules of §3.4: the gate | **you** |
| `harness/` gates | One Python gate per rule, used as the engine's legal-move check | **you** |
| `pddl/domain.pddl` | Optional PDDL export, for shortest-proof search only | optional |
| `kg/extracted/` | LLM-extracted knowledge graph of Ch. 1–3 (kept local) | AI-built |
| `benchmark/book_items.jsonl` | The 9 object-level deductions in Ch. 2–3 | done |
| `harness/` | Parser, truth tables, LLM interface, Lean gate runner | scaffold |
| `tests/` | Smoke tests | scaffold |

## Your to-do, in order

1. `Syntax.lean`: the `Formula` type.
2. `Deduction.lean`: `Derivable` with one constructor per rule. Prove the 9 book items as Lean `example`s.
3. Python gates: one per rule, mirroring your Lean constructors (see `docs/MILESTONES.md`).
4. The knowledge graph is already extracted (`kg/extracted/`, local only); there's nothing to write.
5. `checkStep` in Lean, then the Python loop (`harness/loop.py`).
6. Benchmark generator, then experiments (design §6–7).

## Run

```
cd lean && ~/.elan/bin/lake build     # Lean
cd .. && python3 -m unittest -v       # Python smoke tests
```

The book PDF is not in this repo. Book content here is paraphrased, with a section reference.
