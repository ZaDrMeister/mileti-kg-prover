# mileti-kg-prover

An LLM builds formal deductions in propositional logic using the proof system of Mileti, *A Mathematical Introduction to Mathematical Logic*, §3.4. At each step:

- **PDDL** says which rules are legal right now.
- A **knowledge graph** of the book explains what things mean and which strategy to use.
- **Lean** checks every step.

The research question: how much does each layer help a small model and a strong model? See [`docs/design.md`](docs/design.md).

**Status (Nov 2026):** early work. The scaffold and design are done, and the Lean formalization is next. **Start here:** [`docs/STEP-1-GUIDE.md`](docs/STEP-1-GUIDE.md). Related work: [`docs/related-work.md`](docs/related-work.md).

**Who wrote what:** the Lean syntax and deduction rules, the PDDL domain and the hand-written knowledge graph are written by hand by the author (Dren Zabeli). The Python harness scaffold and the planning documents were drafted with AI assistance. The LLM-extracted graph (condition D) is AI-built by design and is not in the public repo.

## Layout

| Path | What | Who writes it |
|---|---|---|
| `lean/MiletiLogic/Syntax.lean` | Formulas (Ch. 2, §3.1) | **you** |
| `lean/MiletiLogic/Deduction.lean` | The 14 rules of §3.4: the gate | **you** |
| `pddl/domain.pddl` | Rules as PDDL actions (`assume` is given as a template) | **you** |
| `kg/` | Knowledge graph of Ch. 1–3 (3 example nodes) | **you** |
| `benchmark/book_items.jsonl` | The 9 object-level deductions in Ch. 2–3 | done |
| `harness/` | Parser, truth tables, LLM interface, Lean gate runner | scaffold |
| `tests/` | Smoke tests | scaffold |

## Your to-do, in order

1. `Syntax.lean`: the `Formula` type.
2. `Deduction.lean`: `Derivable` with one constructor per rule. Prove the 9 book items as Lean `example`s.
3. `domain.pddl`: the other 13 actions, mirroring your Lean constructors.
4. `kg/`: about 30 nodes (the 14 rules, the §3.4 worked examples, definitions, strategies, pitfalls).
5. `checkStep` in Lean, then the Python loop (`harness/loop.py`).
6. Benchmark generator, then experiments (design §6–7).

## Run

```
cd lean && ~/.elan/bin/lake build     # Lean
cd .. && python3 -m unittest -v       # Python smoke tests
```

The book PDF is not in this repo. Book content here is paraphrased, with a section reference.
