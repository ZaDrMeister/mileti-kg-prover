; Mileti §3.4 deduction rules as PDDL actions — TEMPLATE.
; Backward (goal-directed) search: the state is a set of open goal sequents.
; A rule action removes one open goal and opens its premises.
;
; Only `assume` is written. YOU write the other 13 so they mirror your Lean
; constructors exactly (see docs/design.md §3). Keep names identical to Lean.
;
; Modelling notes:
; - Formulas are objects with structural facts: (is-and ?f ?a ?b), (is-neg ?f ?a), ...
;   The harness generates these facts for the finite candidate set (design §4.2).
; - PDDL cannot create objects, so new sequents use a pool of pre-declared
;   `sequent` slots: an action takes a (free ?s) slot and fills it.
; - WATCH OUT: (assumes ?s ?f) treats S as a SET. Mileti's S is a SEQUENCE
;   (order and repeats matter: ∧I/∨PC/¬PC need identical S, Delete needs a
;   repeat, →I and Reorder depend on position). Decide: either the Python
;   checker owns sequence equality/order and PDDL checks only connective
;   shape, or add position facts like (at ?s ?i ?f). Your call.
; - The harness's Python checker reads this file's preconditions to list legal
;   moves; a real planner (optional) can use it to find shortest proofs.

(define (domain mileti-propositional)
  (:requirements :strips :typing :negative-preconditions)
  (:types formula sequent)

  (:predicates
    ; sequent structure
    (open ?s - sequent)                 ; goal not yet proved
    (free ?s - sequent)                 ; unused slot
    (concl ?s - sequent ?f - formula)   ; right-hand side of S ⊢ φ
    (assumes ?s - sequent ?f - formula) ; φ occurs in S
    (last-assumption ?s - sequent ?f - formula)
    ; formula structure (given as facts)
    (is-neg ?f ?a - formula)
    (is-and ?f ?a ?b - formula)
    (is-or  ?f ?a ?b - formula)
    (is-imp ?f ?a ?b - formula)
  )

  ; (Assume)  S ⊢ φ holds outright when φ occurs in S. Closes the goal.
  (:action assume
    :parameters (?s - sequent ?f - formula)
    :precondition (and (open ?s) (concl ?s ?f) (assumes ?s ?f))
    :effect (and (not (open ?s)))
  )

  ; TODO andEL andER andI orIL orIR impE impI orPC negPC contr expand delete reorder
)
