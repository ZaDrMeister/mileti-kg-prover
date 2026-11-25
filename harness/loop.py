"""The proof loop (design §4). It is a skeleton until the Lean gate and PDDL rules exist.

    state = open goals
    repeat:
        legal = legal_moves(state)          # from pddl/domain.pddl   (needs your PDDL actions)
        info  = kg lookups the LLM asks for  # from kg/*.jsonl         (needs your graph)
        move  = provider.choose(prompt)      # harness/llm.py
        ok, new_state_or_error = lean_check(move)   # needs your Lean checkStep
"""
from __future__ import annotations

import subprocess
from pathlib import Path

LEAN_DIR = Path(__file__).resolve().parent.parent / "lean"


def legal_moves(state):
    raise NotImplementedError("Write the PDDL actions first (pddl/domain.pddl)")


def lean_check(attempt_source: str) -> tuple[bool, str]:
    """Write a generated attempt file and check it with Lean. Exit code 0 means accepted."""
    gen = LEAN_DIR / "Generated"
    gen.mkdir(exist_ok=True)
    path = gen / "Attempt.lean"
    path.write_text(attempt_source)
    proc = subprocess.run(
        [str(Path.home() / ".elan/bin/lake"), "env", "lean", str(path)],
        cwd=LEAN_DIR, capture_output=True, text=True, timeout=120,
    )
    return proc.returncode == 0, proc.stdout + proc.stderr
