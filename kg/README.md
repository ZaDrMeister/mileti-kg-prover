# Knowledge graph: what the book means (Mileti Ch. 1–3)

**Superseded (2026-11-25):** there is no hand-written graph. The experiment uses the LLM-extracted graph in `kg/extracted/`. The files here are only format examples.

- `nodes.jsonl`: one node per line: `{"id", "type", "title", "text", "ref"}`
- `edges.jsonl`: one edge per line: `{"src", "dst", "rel"}`

**Node types:** `definition`, `rule`, `example`, `strategy`, `pitfall`, `theorem`

**Edge types:** `depends_on`, `uses_rule`, `illustrates`, `pitfall_of`, `strategy_for`

`nodes.jsonl` holds one example of each kind. Delete them or keep them.

Suggested first 30 nodes:
- the 14 rules
- the worked examples in §3.4 (5 written out, 1 stated)
- about 5 definitions: formula, line, deduction, `Γ ⊢ φ`, consistent
- about 5 strategies or pitfalls
