"""Propositional formulas for the Python side (benchmark files, PDDL facts, prompts).

ASCII syntax: atoms are capitalized names (A, B, A1); ~ not, & and, | or, -> implies.
Binding strength: ~ > & > | > ->. The -> operator associates to the right.
This is plumbing only. The real definitions are your Lean code.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Atom:
    name: str


@dataclass(frozen=True)
class Not:
    a: "Formula"


@dataclass(frozen=True)
class Bin:
    op: str  # "&", "|", "->"
    a: "Formula"
    b: "Formula"


Formula = Atom | Not | Bin

_TOKEN = re.compile(r"\s*(->|[~&|()]|[A-Z][A-Za-z0-9]*)")


def _tokenize(s: str) -> list[str]:
    pos, out = 0, []
    s = s.rstrip()
    while pos < len(s):
        m = _TOKEN.match(s, pos)
        if not m:
            raise ValueError(f"bad character at {pos} in {s!r}")
        out.append(m.group(1))
        pos = m.end()
    return out


def parse(s: str) -> Formula:
    toks = _tokenize(s)
    i = 0

    def peek():
        return toks[i] if i < len(toks) else None

    def take(expected=None):
        nonlocal i
        t = peek()
        if t is None or (expected and t != expected):
            raise ValueError(f"expected {expected or 'token'} in {s!r}")
        i += 1
        return t

    def imp():
        left = disj()
        if peek() == "->":
            take()
            return Bin("->", left, imp())
        return left

    def binary(op, sub):
        def p():
            left = sub()
            while peek() == op:
                take()
                left = Bin(op, left, sub())
            return left
        return p

    def unary():
        t = peek()
        if t == "~":
            take()
            return Not(unary())
        if t == "(":
            take()
            f = imp()
            take(")")
            return f
        if t and t[0].isupper():
            take()
            return Atom(t)
        raise ValueError(f"unexpected {t!r} in {s!r}")

    conj = binary("&", unary)
    disj = binary("|", conj)
    f = imp()
    if i != len(toks):
        raise ValueError(f"trailing input in {s!r}")
    return f


def show(f: Formula) -> str:
    if isinstance(f, Atom):
        return f.name
    if isinstance(f, Not):
        return "~" + (show(f.a) if not isinstance(f.a, Bin) else f"({show(f.a)})")
    return f"({show(f.a)} {f.op} {show(f.b)})"


def atoms(f: Formula) -> set[str]:
    if isinstance(f, Atom):
        return {f.name}
    if isinstance(f, Not):
        return atoms(f.a)
    return atoms(f.a) | atoms(f.b)


def subformulas(f: Formula) -> set[Formula]:
    if isinstance(f, Atom):
        return {f}
    if isinstance(f, Not):
        return {f} | subformulas(f.a)
    return {f} | subformulas(f.a) | subformulas(f.b)
