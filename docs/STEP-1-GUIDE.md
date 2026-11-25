# Step 1 guide: formulas in Lean (`Syntax.lean`)

**Goal for this session:** `lean/MiletiLogic/Syntax.lean` defines Mileti's propositional formulas, builds without errors, and passes the checks in §5. Then you make your first commit.

**Time:** about 2–3 hours if Lean is new to you, about 1 hour if not.

**Rule:** you write the code. This guide explains the ideas and shows a *different* example (arithmetic expressions) that you translate to formulas. If you get stuck, paste the error into Claude and ask what it means, not for the answer.

---

## 0. Check your setup (5 min)

```bash
cd ~/Desktop/grad-school-project/mileti-kg-prover/lean
~/.elan/bin/lake build
```
You should see `Build completed successfully`. Your Lean version is fixed in `lean-toolchain` (v4.28.0). There's no Mathlib, on purpose (design §2: your definitions must match Mileti's exactly).

Editor: open the `lean/` folder in VS Code with the **lean4** extension. The infoview panel (⌘⇧Enter) shows `#eval` results and goals as you type.

## 1. Read first (30–45 min)

- **Mileti Ch. 2**, the part on generating systems: a set built from starting elements (atoms) and functions (connectives), and what it means for it to be **free** (each element is built in exactly one way).
- **Mileti §3.1**: the formal definition of formulas: atoms in `P`, and ¬, ∧, ∨, →.

**Question to answer in your own words** (write it down; it's good material for your statement and interviews): *why is an `inductive` type in Lean a free generating system?* Hint: Lean's constructors are automatically injective and never overlap. That is exactly Mileti's "uniquely generated" condition, which the book has to prove for Polish strings (unique readability).

## 2. The Lean ideas you need

| Idea | What it does | Where to read |
|---|---|---|
| `inductive` | Defines a type by listing its constructors | *Theorem Proving in Lean 4*, ch. "Inductive Types" |
| `deriving DecidableEq, Repr` | Lean can decide `φ = ψ` and print formulas | same |
| `namespace … end` | Puts your names under `MiletiLogic.` | same |
| Pattern-matching `def` | Defines a function by one case per constructor (structural recursion) | ch. "Induction and Recursion" |
| `#eval` | Runs code and prints the result in the infoview | |
| `example : … := by decide` / `by rfl` | A small check that Lean must accept | |
| `prefix` / `infixr` notation | Optional; makes formulas readable | ch. "Interacting with Lean" → Notation |

## 3. A worked example on a *different* type

This compiles in your project. Paste it into a scratch file to try it, but **don't** put it in `Syntax.lean`.

```lean
namespace Demo

inductive Expr where
  | num   : Nat → Expr               -- a base case (like an atom)
  | neg   : Expr → Expr              -- a one-argument constructor (like ¬)
  | plus  : Expr → Expr → Expr       -- two-argument constructors (like ∧, ∨, →)
  | times : Expr → Expr → Expr
  deriving DecidableEq, Repr

open Expr

prefix:max "−" => Expr.neg
infixl:65 " ⊕ " => Expr.plus
infixl:70 " ⊗ " => Expr.times        -- higher number = binds tighter

def size : Expr → Nat                 -- one line per constructor
  | num _     => 1
  | neg e     => size e + 1
  | plus a b  => size a + size b + 1
  | times a b => size a + size b + 1

def subexprs : Expr → List Expr
  | num n     => [num n]
  | neg e     => neg e :: subexprs e
  | plus a b  => plus a b :: (subexprs a ++ subexprs b)
  | times a b => times a b :: (subexprs a ++ subexprs b)

#eval num 1 ⊕ num 2 ⊗ num 3           -- shows that ⊗ binds tighter than ⊕
#eval size (num 1 ⊕ −(num 2))         -- 4
example : num 1 ≠ num 2 := by decide
example : size (num 1 ⊕ num 2) = 3 := by rfl

end Demo
```

To run a scratch file: `~/.elan/bin/lake env lean path/to/Scratch.lean`.

## 4. Your task: translate it to Mileti's formulas

Work through the checklist already in `Syntax.lean`:

1. **`inductive Formula`** in `namespace MiletiLogic`, with one constructor for atoms and one for each of ¬, ∧, ∨, →. Check §3.1 for exactly which connectives Mileti uses. Don't add ↔ or ⊥ unless the book has them as primitive symbols.
2. **`deriving DecidableEq, Repr`.** The Lean gate will compare formulas, for example "is φ in S?" for Assume.
3. **Notation** (optional, recommended). Choose precedences that match the Python harness, so the same string means the same formula on both sides. `harness/formula.py` uses `~` > `&` > `|` > `->`, and `->` groups to the right (`infixr`).
4. **Practice functions from §3.1:** `subformulas : Formula → List Formula` and `depth : Formula → Nat`. Pick Mileti's definition of depth or height and cite the section in a comment.
5. *(Stretch; skip today)* Polish-notation strings, a parser, and `parse (toPolish φ) = some φ`.

### Decisions you make (write each one in a comment)
- **How atoms are named:** `Nat` (`atom 0`, `atom 1`) or `String` (`atom "A"`). The Python harness uses names like `A`, `B`, `A1`. Both work; `Nat` is simpler for proofs, `String` makes the Python↔Lean export trivial.
- **Precedence numbers** for each connective.

## 5. Done when

Add these at the bottom of `Syntax.lean` (your names may differ):

- [ ] `lake build` succeeds with **no** errors and no `sorry`.
- [ ] `#eval` of the formula for `(A ∧ B) → (A ∨ B)` prints the tree you expect.
- [ ] An `example … ≠ … := by decide` showing two different atoms are different formulas.
- [ ] An `example` showing `¬A ∧ B` parses as `(¬A) ∧ B`, not `¬(A ∧ B)` (a notation check, `by rfl`).
- [ ] `(subformulas φ).length` for one small φ, checked by hand against Mileti's definition.
- [ ] `depth` on 2–3 formulas, checked by hand.
- [ ] One paragraph in your own words for §1's question, saved in a comment at the top of the file or in `docs/notes.md`.

## 6. Commit

```bash
cd ~/Desktop/grad-school-project/mileti-kg-prover
git add lean/MiletiLogic/Syntax.lean
git commit -m "Syntax: Mileti propositional formulas as an inductive type"
git push
```
Small, frequent commits are the evidence that you did this work. Commit after each checklist item if you like.

## 7. Common errors

| Error | Usually means |
|---|---|
| `unknown identifier 'atom'` | You're outside the namespace: write `Formula.atom`, or add `open Formula` |
| `failed to synthesize DecidableEq` | You forgot `deriving DecidableEq` |
| `missing cases` in a `def` | Your pattern match skipped a constructor |
| Notation parses the wrong way | Precedence numbers are off; higher binds tighter |
| `unexpected token` at a symbol | That Unicode symbol is already taken; pick another or use ASCII |

## 8. Next session

`Deduction.lean`: `inductive Derivable : List Formula → Formula → Prop` with one constructor per rule (the table in `docs/design.md` §3). Start with **Assume, ∧EL, ∧ER, ∧I, →E, →I**, then prove the first book item, `A ∧ B ⊢ A ∨ B` (it needs ∨IL as well). For the encoding pattern, read how *Intuitionistic Propositional Logic in Lean* (arXiv 2410.23765) encodes its Hilbert system as an inductive type with one constructor per axiom and rule. That is the same pattern, used on a different system.
