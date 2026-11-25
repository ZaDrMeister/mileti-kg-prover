"""Truth-table semantics (Mileti §3.2). Used to filter generated benchmark sequents.

By soundness and completeness (§3.5), S ⊨ φ holds exactly when S ⊢ φ is derivable,
so a valid sequent always has a deduction to find.
"""
from __future__ import annotations

from itertools import product

from harness.formula import Atom, Bin, Formula, Not, atoms


def value(f: Formula, m: dict[str, bool]) -> bool:
    if isinstance(f, Atom):
        return m[f.name]
    if isinstance(f, Not):
        return not value(f.a, m)
    a, b = value(f.a, m), value(f.b, m)
    return {"&": a and b, "|": a or b, "->": (not a) or b}[f.op]


def entails(assumptions: list[Formula], goal: Formula) -> bool:
    names = sorted(set().union(atoms(goal), *(atoms(a) for a in assumptions)))
    for bits in product([False, True], repeat=len(names)):
        m = dict(zip(names, bits))
        if all(value(a, m) for a in assumptions) and not value(goal, m):
            return False
    return True
