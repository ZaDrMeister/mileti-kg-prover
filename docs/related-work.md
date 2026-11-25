# Related work: search notes (2026-11-25)

These notes come from a web search. They are based on abstracts and snippets only, so **read each paper before you cite it**, and check the venue, the year and the numbers.

The project: an LLM builds deductions in Mileti's §3.4 proof system one rule at a time. Hand-written rule gates give the legal moves, an LLM-extracted knowledge graph gives strategy, and a hand-written Lean formalization checks each step.

## 1. LLMs writing proofs in a propositional proof system (closest to the core)
| Work | What it does | How it relates |
|---|---|---|
| **ProofGrid**: Arkoudas & Batzoglou, EMNLP 2025 Findings; extended version [arXiv 2605.12524](https://arxiv.org/abs/2605.12524) *(verified 2026-11-25; the MathNLP link in the first draft was a different paper)* | Randomly generated, SAT-filtered propositional problems; proofs in an assumption-style natural-deduction language (NDL); a mechanical checker that reports the **first error**, with a **6-type error taxonomy**; finds that strong models fail cosmetically and weak ones structurally. One-shot: no legal-move lists, no step feedback | **Closest prior work, and it already has a generated benchmark and a failure taxonomy.** Position your taxonomy against its 6 types |
| **Magalhães & Sandes** ([ENIAC](https://sol.sbc.org.br/index.php/eniac/article/download/46915/46672/)) | External natural-deduction and tableau checkers grade open-LLM proofs, propositional and FOL | Reports models **skipping intermediate checks**, an early data point for your failure taxonomy |
| **Learn from Failure / PropL** ([arXiv 2404.07382](https://arxiv.org/html/2404.07382v3)) | Intuitionistic propositional theorems in Lean; fine-tuning on trial-and-error search traces | Uses Lean as the gate, but with tactics rather than textbook rules; a good baseline to discuss |
| **Can LLMs learn formal logic?** ([arXiv 2504.20213](https://arxiv.org/pdf/2504.20213)) | Training and evaluation framework for formal logic proofs | Check its proof format and checker |
| **Rosetta-PL** ([arXiv 2505.00001](https://arxiv.org/html/2505.00001v2)) | Propositions translated from Lean into a custom logical language | Test of generalization to an unfamiliar notation, related to your contamination argument |
| **Verifiable logical reasoning using GenAI** ([USPTO patent](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12705250)) | A proof checker verifies that LLM proofs follow natural-deduction rules; notes that SAT checks alone aren't enough | Supports **checking each rule, not only validity**, which is the reason for the Lean gate |
| ([CEUR Vol-4074](https://ceur-ws.org/Vol-4074/short4-2.pdf)), ([Preprints.org](https://www.preprints.org/frontend/manuscript/c9deae48143449624cf5325db41bbbe0/download_pub)), ([arXiv 2404.15522](https://arxiv.org/pdf/2404.15522v1)) | Further hits from the same search | Not checked yet |

## 2. Generated benchmarks without contamination
| Work | Notes |
|---|---|
| **DivLogicEval** ([arXiv 2509.15587](https://arxiv.org/html/2509.15587v1)) | Solver-verified propositional items rendered as natural language |
| **Marchiafava, Sen & Moua** ([CEUR Vol-4074](https://ceur-ws.org/Vol-4074/short4-2.pdf)) | CNF statements, ATP proofs used for fine-tuning. Better proof generation did **not** carry over to other reasoning tasks |
| **ProverQA** ([arXiv 2502.06563](https://arxiv.org/pdf/2502.06563)) | Prover9 builds reasoning trees and an LLM turns them into text; fresh generation. First-order logic |
| **JustLogic** ([arXiv 2501.14851](https://arxiv.org/pdf/2501.14851)), **QMFOL** ([arXiv 2606.20227](https://arxiv.org/html/2606.20227)) | Synthetic deductive benchmarks (natural language; monadic FOL) |

No benchmark turned up of **generated sequents graded in a textbook's own proof system**. That is a gap your benchmark can fill.

## 3. Knowledge graphs and retrieval for provers
| Work | Notes |
|---|---|
| **KG-Prover** ([arXiv 2503.11657](https://arxiv.org/html/2503.11657v2)) | LLM traverses a ProofWiki knowledge graph (60k+ nodes); informal proof → autoformalized → Lean. Graph depth used as test-time compute. **Your main graph comparison** (theirs: large and retrieved from ProofWiki; yours: small, LLM-extracted from one textbook, strategy-level) |
| **LeanDojo / ReProver** ([arXiv 2306.15626](https://arxiv.org/pdf/2306.15626)) | Standard retrieval-augmented prover: 51.2% vs 47.6% without retrieval |
| **Premise selection with graph structure** ([arXiv 2510.23637](https://arxiv.org/pdf/2510.23637)) | Text plus a graph neural network over dependencies; better than ReProver retrieval |
| **DAPS** ([arXiv 2610.41536](https://arxiv.org/pdf/2610.41536)) | Dependency-aware premise selection |
| **Lean Graph Search** ([arXiv 2610.22339](https://arxiv.org/pdf/2610.22339)) | Not checked yet |
| **Lean Copilot** ([arXiv 2404.12534](https://arxiv.org/pdf/2404.12534)) | LLM tools inside Lean |

Your oracle ablation from the calculus study (content vs. the cost of fetching it) matches a question this line of work mostly doesn't ask.

## 3b. Added after verification (2026-11-25)
| Work | Notes |
|---|---|
| **When Does Structured Knowledge Help Neural Theorem Proving?** (Nabi, Vogl, Nabi, [arXiv 2609.34460](https://arxiv.org/abs/2609.34460)) | MathKG: 364 Mathlib theorems with LLM-extracted typed edges; no KG vs KG vs retrieval vs both, across 5 models in Lean 4. **The KG helps small models and hurts large ones**; an oracle that picks the best mode per problem solves 6–58% more. **Closest to your KG conditions.** No hand-written arm, and its oracle picks a mode rather than giving the strategy |
| **Tithi et al.** ([arXiv 2505.04736](https://arxiv.org/abs/2505.04736)) | 358 propositional proofs from a logic tutoring system; LLM accuracy measured step by step |
| **Magalhães, Sandes et al.** (ENIAC 2026, [page](https://sol.sbc.org.br/index.php/eniac/article/view/46915)) | Open LLMs write natural-deduction and tableau proofs, checked externally; the rules are given in the prompt, but there are no legal-move lists at each step. Full text not read |
| **palmskog/fitch** | Coq/HOL4 checker for the Fitch system of Huth & Ryan's textbook. No LLM; a precedent for formalizing a textbook's proof system |

No paper was found that gives an LLM prover the legal moves at each step for natural deduction, or that uses STRIPS/PDDL proof planning with an LLM.

## 4. Verifier feedback at each step, and failure analysis
| Work | Notes |
|---|---|
| **Local Look-Ahead Guidance via Verifier-in-the-Loop** ("LeanListener", [arXiv 2503.09730](https://arxiv.org/html/2503.09730v2)) | Trains a tactic generator with Lean rewards on each step. Says, without a number, that "many" failures are tactics that don't apply to the current state or have bad syntax | Qualitative support for a legal-moves layer |
| **ReCent-Prover** ([arXiv 2604.19558](https://arxiv.org/pdf/2604.19558)) | Reflection on misapplied tactics in Rocq; some misapplications cause no error at all |
| **Repair, Retry, and the Cost of Hindsight** ([arXiv 2610.22698](https://arxiv.org/pdf/2610.22698)) | Whole-proof repair in Lean on 167 MiniF2F problems. Verifier feedback does **not** beat resampling with instructions only, and showing the failed proof makes models copy it. Relevant to how condition A returns Lean errors |
| **Analogical retrieval + symbolic verification, Euclidean geometry** ([arXiv 2505.14479](https://arxiv.org/pdf/2505.14479)) | Links to your spring 2026 geometry proposal |
| seL4 ([arXiv 2602.08384](https://arxiv.org/pdf/2602.08384)), code agents ([arXiv 2607.06341](https://arxiv.org/pdf/2607.06341)), ([NSF PAR](https://par.nsf.gov//servlets/purl/10599675)) | Formats for returning verifier errors to the model |

## 5. PDDL and LLMs
| Work | Notes |
|---|---|
| **LLM-as-formalizer** ([arXiv 2412.09879](https://arxiv.org/html/2412.09879v2), [arXiv 2505.14763](https://arxiv.org/pdf/2505.14763v2)) | LLM writes PDDL and a solver plans; this beats LLM-as-planner, but open models struggle |
| **Teriyaki** ([arXiv 2303.00438](https://arxiv.org/pdf/2303.00438)), **PSALM-V** ([arXiv 2506.20097](https://arxiv.org/pdf/2506.20097)), reasoning models vs. classical planners ([arXiv 2507.23589](https://arxiv.org/pdf/2507.23589)), ([arXiv 2510.05486](https://arxiv.org/html/2510.05486)), ([NSF PAR](https://par.nsf.gov//servlets/purl/10564711)) | LLM + PDDL planning |

**No work turned up that uses PDDL to give legal deduction moves to an LLM theorem prover.** That combination looks new. Check this claim more carefully (and ask CCB) before you put it in a statement.

## 6. Formalizing proof systems (for the Lean side)
| Work | Notes |
|---|---|
| **Intuitionistic Propositional Logic in Lean** ([arXiv 2410.23765](https://arxiv.org/pdf/2410.23765)) | Hilbert system as an inductive type with one constructor per rule, plus soundness and completeness. **The closest template for your `Derivable`** |
| **Nipkow, Formalized Proof Systems for Propositional Logic** ([TYPES 2017](https://www.proof.cit.tum.de/~nipkow/pubs/types17.pdf)) | Sequent calculus, natural deduction, Hilbert and resolution systems in Isabelle |
| **Coq formalization** ([MDPI Mathematics 11(11):2504](https://www.mdpi.com/2227-7390/11/11/2504)) | Deduction theorem, soundness and completeness in Coq |
| **Logic and Proof** ([Avigad, ch. 4](https://leanprover-community.github.io/logic_and_proof/propositional_logic_in_lean.html)), **Theorem Proving in Lean 4** ([ch. 3](https://lean-lang.org/theorem_proving_in_lean4/propositions_and_proofs.html)) | Natural deduction ↔ Lean; good for learning |
| ([Krajíček notes](https://www.karlin.mff.cuni.cz/~krajicek/rydl-19-11-21.pdf)), ([Lean Zulip project PDF](https://leanprover.zulipchat.com/user_uploads/3121/B7N41Atvy6H1NC-1O_xZGt0y/Lean_4_Project.pdf)) | Not checked yet |

## Where your project is new (tentative)
1. A **textbook's own proof system** (Mileti §3.4), formalized by hand as the gate, rather than Lean tactics or a made-up notation.
2. **Legal moves from PDDL** as a separate layer you can switch on and off.
3. An **LLM-extracted strategy graph vs. a strategy oracle**, crossed with the legal-moves layer. Nabi et al. already compared an extracted graph against no graph, so the new part is the oracle and the interaction with legal moves. *(The hand-written arm was dropped on 2026-11-25.)*
4. A **failure taxonomy** as the main contribution.

## Read first
1. ProofGrid
2. KG-Prover
3. Intuitionistic Propositional Logic in Lean
4. Repair, Retry, and the Cost of Hindsight
5. LeanListener
