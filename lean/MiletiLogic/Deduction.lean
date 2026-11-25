import MiletiLogic.Syntax

/-
  YOUR CODE: Mileti's deduction system (§3.4). This is the "gate".
  Spec: docs/design.md §3 (all 14 rules with side conditions).

  [ ] 1. `Line := List Formula × Formula`  (S ⊢ φ; order and repeats matter)
  [ ] 2. `inductive Derivable : List Formula → Formula → Prop`
         one constructor per rule:
         [ ] assume   [ ] andEL   [ ] andER   [ ] andI
         [ ] orIL     [ ] orIR    [ ] impE    [ ] impI
         [ ] orPC     [ ] negPC   [ ] contr
         [ ] expand   [ ] delete  [ ] reorder
  [ ] 3. Check it by proving the §3.4 worked examples as `example`s,
         e.g.  Derivable [A ∧ B] (A ∨ B).
  [ ] 4. A computable step checker the Python harness can call:
         `checkStep : List Line → Step → Except String Line`
         (returns the new line, or which side condition failed).
  [ ] 5. (Stretch, learning) Soundness (§3.5): Derivable S φ → S ⊨ φ.
-/

namespace MiletiLogic

end MiletiLogic
