import json
import unittest
from pathlib import Path

from harness.formula import parse, show
from harness.loop import lean_check
from harness.semantics import entails

ROOT = Path(__file__).resolve().parent.parent


class TestFormula(unittest.TestCase):
    def test_precedence_and_roundtrip(self):
        f = parse("~A & B | C -> D -> E")
        self.assertEqual(show(f), "(((~A & B) | C) -> (D -> E))")
        self.assertEqual(parse(show(f)), f)


class TestBenchmark(unittest.TestCase):
    def test_book_items_are_valid(self):
        for line in (ROOT / "benchmark/book_items.jsonl").read_text().splitlines():
            item = json.loads(line)
            with self.subTest(item["id"]):
                self.assertTrue(entails([parse(a) for a in item["assumptions"]], parse(item["goal"])))

    def test_invalid_sequent_detected(self):
        self.assertFalse(entails([parse("A | B")], parse("A")))


class TestKG(unittest.TestCase):
    def test_kg_files_parse_and_edges_resolve(self):
        nodes = [json.loads(l) for l in (ROOT / "kg/nodes.jsonl").read_text().splitlines()]
        ids = {n["id"] for n in nodes}
        for l in (ROOT / "kg/edges.jsonl").read_text().splitlines():
            e = json.loads(l)
            self.assertIn(e["src"], ids)
            self.assertIn(e["dst"], ids)


class TestExtractedKG(unittest.TestCase):
    def test_extracted_bank_passes_checks(self):
        from harness.kg_check import check, load
        d = ROOT / "kg/extracted"
        self.assertEqual(check(load(d / "nodes.jsonl"), load(d / "edges.jsonl")), [])

    def test_no_benchmark_solutions_in_bank(self):
        text = (ROOT / "kg/extracted/nodes.jsonl").read_text()
        self.assertNotIn("solution_steps", text)


class TestLeanGate(unittest.TestCase):
    def test_gate_accepts_and_rejects(self):
        ok, _ = lean_check("import MiletiLogic\nexample : True := trivial\n")
        self.assertTrue(ok)
        bad, msg = lean_check("import MiletiLogic\nexample : False := trivial\n")
        self.assertFalse(bad)
        self.assertIn("error", msg)


if __name__ == "__main__":
    unittest.main()
