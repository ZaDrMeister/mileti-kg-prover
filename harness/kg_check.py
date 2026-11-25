"""Merge and check knowledge-graph files.

Usage:
    python3 -m harness.kg_check OUT_DIR PART1.nodes.jsonl PART1.edges.jsonl [PART2 ...]   # merge then check
    python3 -m harness.kg_check DIR                                                        # check DIR/nodes.jsonl, DIR/edges.jsonl

Checks:
- each line is JSON with the required fields
- node types and edge relations are from the schema
- ids are unique, and every edge endpoint exists
- every worked deduction's lines are semantically valid (truth tables) and name one of the 14 rules

The semantic check catches transcription errors. It does not check that each rule was applied correctly; that is the Lean gate's job.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from harness.formula import parse
from harness.semantics import entails

NODE_TYPES = {"definition", "theorem", "rule", "example", "strategy", "pitfall", "notation", "exercise"}
RELS = {"depends_on", "uses_rule", "illustrates", "strategy_for", "pitfall_of", "generalizes", "instance_of"}
RULES = {"assume", "andEL", "andER", "andI", "orIL", "orIR", "impE", "impI",
         "orPC", "negPC", "contr", "expand", "delete", "reorder"}


def load(path: Path) -> list[dict]:
    out = []
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path}:{i}: bad JSON: {e}")
    return out


def check(nodes: list[dict], edges: list[dict]) -> list[str]:
    errs = []
    ids = Counter(n.get("id") for n in nodes)
    errs += [f"duplicate id {i} (x{c})" for i, c in ids.items() if c > 1]
    for n in nodes:
        for f in ("id", "type", "title", "text", "ref"):
            if not n.get(f):
                errs.append(f"node {n.get('id')}: missing {f}")
        if n.get("type") not in NODE_TYPES:
            errs.append(f"node {n.get('id')}: bad type {n.get('type')}")
        for s in n.get("steps", []):
            where = f"{n['id']} step {s.get('n')}"
            if s.get("rule") not in RULES:
                errs.append(f"{where}: unknown rule {s.get('rule')}")
            try:
                if not entails([parse(a) for a in s["assumptions"]], parse(s["goal"])):
                    errs.append(f"{where}: line is not semantically valid")
            except (ValueError, KeyError) as e:
                errs.append(f"{where}: cannot parse ({e})")
    rule_nodes = {n["id"] for n in nodes if n.get("type") == "rule"}
    if rule_nodes and rule_nodes != {f"rule:{r}" for r in RULES}:
        errs.append(f"rule nodes differ from the 14: {sorted(rule_nodes ^ {f'rule:{r}' for r in RULES})}")
    for e in edges:
        if e.get("rel") not in RELS:
            errs.append(f"edge {e}: bad rel")
        for end in ("src", "dst"):
            if e.get(end) not in ids:
                errs.append(f"edge {e.get('src')} -{e.get('rel')}-> {e.get('dst')}: {end} missing")
    return errs


def main(argv: list[str]) -> int:
    if len(argv) == 1:
        d = Path(argv[0])
        nodes, edges = load(d / "nodes.jsonl"), load(d / "edges.jsonl")
    else:
        out, parts = Path(argv[0]), [Path(p) for p in argv[1:]]
        nodes = [n for p in parts if p.name.endswith("nodes.jsonl") for n in load(p)]
        edges = [e for p in parts if p.name.endswith("edges.jsonl") for e in load(p)]
        seen, uniq = set(), []
        for e in edges:
            key = (e.get("src"), e.get("rel"), e.get("dst"))
            if key not in seen:
                seen.add(key)
                uniq.append(e)
        edges = uniq
        out.mkdir(parents=True, exist_ok=True)
        (out / "nodes.jsonl").write_text("".join(json.dumps(n, ensure_ascii=False) + "\n" for n in nodes))
        (out / "edges.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in edges))
    errs = check(nodes, edges)
    print(f"{len(nodes)} nodes {dict(Counter(n.get('type') for n in nodes))}")
    print(f"{len(edges)} edges {dict(Counter(e.get('rel') for e in edges))}")
    for e in errs:
        print("ERROR", e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
