"""Offline regression tests; no paid requests or ConceptNet downloads."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from event_relations.collector import collect
from event_relations.evaluation import INVALID, RELATIONS, compare, evaluate, normalize
from event_relations.generation import classify, compose_prompt, parse_response
from event_relations.graph import build_graph
from event_relations.io import read_json, save_json
from event_relations.runner import run_generation

ROOT = Path(__file__).resolve().parents[1]


def event(a="a", b="b", gold="Causes", selected="Causes"):
    return {gold: [dict(start={"@id": "/c/en/" + a, "label": a, "language": "en"},
                       end={"@id": "/c/en/" + b, "label": b, "language": "en"},
                       generated_relations=[{"Relation": "/r/" + selected, "Reason": "test"}],
                       final_relation={"Relation": "/r/" + selected, "Reason": "test"})]}


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = read_json(ROOT / "data/predictions.json")
        cls.results = compare(cls.data)

    def test_archive_counts(self):
        self.assertEqual({r: len(v) for r, v in self.data.items()}, dict(zip(RELATIONS, (999, 1000, 1000, 1000))))

    def test_every_archive_record_has_three_samples(self):
        self.assertTrue(all(len(row["generated_relations"]) == 3 for rows in self.data.values() for row in rows))

    def test_predictions_match_input_prefix(self):
        inputs = read_json(ROOT / "data/event_pairs.json")
        key = lambda row: (row["start"]["@id"], row["end"]["@id"])
        for rel, rows in self.data.items():
            self.assertEqual([key(row) for row in rows], [key(row) for row in inputs[rel][:len(rows)]])

    def test_strict_first_does_not_replace_invalid(self):
        self.assertEqual(self.results["first"]["correct"], 2381)
        self.assertEqual(self.results["first"]["invalid_predictions"], 4)

    def test_historical_workbook_counts(self):
        expected = {"historical-first": [(702, 528, 297), (569, 791, 431), (519, 151, 481), (593, 146, 407)],
                    "selected": [(712, 520, 287), (571, 773, 429), (521, 154, 479), (605, 143, 395)]}
        for strategy, values in expected.items():
            for rel, counts in zip(RELATIONS, values):
                m = self.results[strategy]["per_relation"][rel]
                self.assertEqual(tuple(m[k] for k in ("tp", "fp", "fn")), counts)

    def test_normalized_heatmap_cell(self):
        self.assertEqual(self.results["selected"]["confusion_matrix"]["HasSubevent"]["HasFirstSubevent"], 77)

    def test_no_silent_row_drops(self):
        for strategy in ("first", "historical-first", "selected"):
            r = self.results[strategy]
            self.assertEqual(sum(sum(v.values()) for v in r["confusion_matrix"].values()), 3999)

    def test_duplicates_are_reported_not_removed(self):
        self.assertEqual(self.results["selected"]["duplicate_relation_pairs"], 135)

    def test_paired_changes(self):
        self.assertEqual(self.results["paired_changes"], dict(improved=120, regressed=92, both_correct=2289, both_wrong=1498))

    def test_normalization(self):
        for label in ("Causes", "/r/Causes", "r/Causes", " /r/Causes "):
            self.assertEqual(normalize(label), "Causes")
        for label in (None, "DoesNotApply", "NotCauses", {}, "/r/r/Causes"):
            self.assertEqual(normalize(label), INVALID)

    def test_invalid_is_counted_as_false_negative(self):
        r = evaluate(event(selected="NotCauses"))
        self.assertEqual(r["accuracy"], 0)
        self.assertEqual(r["per_relation"]["Causes"]["fn"], 1)
        self.assertEqual(r["invalid_predictions"], 1)

    def test_bad_inputs(self):
        for data in ({}, [], {"Unknown": []}, {"Causes": [{}]}, {"Causes": []}):
            with self.assertRaises(ValueError):
                evaluate(data)


class GenerationTests(unittest.TestCase):
    def fake(self, labels):
        responses = iter(labels)
        return lambda prompt: json.dumps({"Relation": next(responses), "Reason": "test"})

    def test_prompt_direction_correction_is_explicit(self):
        self.assertIn("- A: fire\n- B: lighting a match", compose_prompt("a", "b", version="historical"))
        self.assertIn("- A: lighting a match\n- B: fire", compose_prompt("a", "b"))

    def test_plain_and_fenced_json(self):
        text = json.dumps(dict(Relation="Causes", Reason="Contains {braces}"))
        for value in (text, "```json\n" + text + "\n```"):
            self.assertEqual(parse_response(value)["Relation"], "/r/Causes")

    def test_invalid_response_schema(self):
        for value in (None, "bad JSON", "[]", '{"Relation":"Causes"}', '{"Relation":"NotCauses","Reason":"test"}'):
            self.assertEqual(parse_response(value)["Relation"], INVALID)

    def test_majority_requires_no_extra_call(self):
        r = classify("a", "b", self.fake(["Causes", "HasSubevent", "Causes"]))
        self.assertEqual(r["final_relation"]["Relation"], "/r/Causes")
        self.assertIsNone(r["tie_break"])

    def test_tie_uses_one_candidate_restricted_call(self):
        r = classify("a", "b", self.fake(["Causes", "HasSubevent", "HasFirstSubevent", "HasSubevent"]))
        self.assertEqual(r["final_relation"]["Relation"], "/r/HasSubevent")
        self.assertIsNotNone(r["tie_break"])

    def test_tie_rejects_unoffered_label(self):
        r = classify("a", "b", self.fake(["Causes", "HasSubevent", "HasFirstSubevent", "HasLastSubevent"]))
        self.assertEqual(r["final_relation"]["Relation"], INVALID)

    def test_invalid_votes_do_not_default_to_causes(self):
        r = classify("a", "b", self.fake(["unknown", "unknown", "unknown"]))
        self.assertEqual(r["final_relation"]["Relation"], INVALID)

    def test_one_valid_sample_is_not_a_majority(self):
        r = classify("a", "b", self.fake(["Causes", "unknown", "unknown"]))
        self.assertEqual(r["final_relation"]["Relation"], INVALID)


class GraphTests(unittest.TestCase):
    def triangle(self):
        data = {"Causes": []}
        for a, b in (("a", "b"), ("b", "c"), ("c", "a")):
            data["Causes"].extend(event(a, b)["Causes"])
        return data

    def test_triangle_core_and_hops(self):
        g = build_graph(self.triangle(), k=2, hops=1)
        self.assertEqual(len(g["nodes"]), 3)
        self.assertEqual(len(g["edges"]), 3)

    def test_parallel_relations_preserved(self):
        data = self.triangle()
        data["HasSubevent"] = event(gold="HasSubevent")["HasSubevent"]
        self.assertEqual(len(build_graph(data)["edges"]), 4)

    def test_higher_core_is_empty(self):
        self.assertEqual(build_graph(self.triangle(), k=3)["nodes"], [])

    def test_prediction_labels_are_used(self):
        data = event(selected="HasSubevent")
        g = build_graph(data, labels="selected", k=0)
        self.assertEqual(g["edges"][0]["relation"], "HasSubevent")

    def test_bad_seed_and_negative_parameters(self):
        for kwargs in (dict(seed="missing"), dict(k=-1), dict(hops=-1)):
            with self.assertRaises(ValueError):
                build_graph(self.triangle(), **kwargs)

    def test_self_loops_are_explicitly_excluded(self):
        g = build_graph(event("a", "a"), k=0)
        self.assertEqual(g["self_loops_excluded"], 1)
        self.assertEqual(g["edges"], [])

    def test_ids_not_labels_define_nodes(self):
        data = self.triangle()
        for row in data["Causes"]:
            row["start"]["label"] = row["end"]["label"] = "same display name"
        self.assertEqual(len(build_graph(data)["nodes"]), 3)


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        # Keep all test files in the project workspace, not global cache folders.
        (ROOT / "outputs").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "outputs")
        self.addCleanup(self.temp.cleanup)
        self.input, self.output = Path(self.temp.name) / "input.json", Path(self.temp.name) / "out.json"
        save_json(self.input, event())

    def run_fake(self, complete, **kwargs):
        return run_generation(self.input, self.output, complete, "test-model", "https://example.invalid/v1", **kwargs)

    def test_resume_makes_no_duplicate_calls(self):
        self.run_fake(lambda _: '{"Relation":"Causes","Reason":"test"}')
        def unexpected(_):
            raise AssertionError("Completed checkpoint should not call the model")
        r = self.run_fake(unexpected)
        self.assertEqual(len(r["data"]["Causes"]), 1)

    def test_changed_input_rejects_resume(self):
        self.run_fake(lambda _: '{"Relation":"Causes","Reason":"test"}')
        save_json(self.input, event("new", "pair"))
        with self.assertRaises(ValueError):
            self.run_fake(lambda _: "unused")

    def test_foreign_output_is_not_overwritten(self):
        save_json(self.output, {"keep": "me"})
        before = self.output.read_bytes()
        with self.assertRaises(ValueError):
            self.run_fake(lambda _: "unused")
        self.assertEqual(self.output.read_bytes(), before)

    def test_failures_do_not_record_completed_pair(self):
        def failure(_):
            raise RuntimeError("mock network failure")
        with self.assertRaises(RuntimeError):
            self.run_fake(failure)
        self.assertFalse(self.output.exists())

    def test_duplicate_json_keys_rejected(self):
        # Parser-level check without modifying a source fixture.
        from unittest.mock import patch
        with patch.object(Path, "read_text", return_value='{"Causes":[],"Causes":[]}'):
            with self.assertRaises(ValueError):
                read_json(self.input)

    def test_cli_requires_paid_call_opt_in(self):
        r = subprocess.run([sys.executable, "-B", "-m", "event_relations", "generate", str(self.input), "--model", "test"],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("--allow-api-calls", r.stderr)


class CollectorTests(unittest.TestCase):
    def test_language_filter_and_deduplication(self):
        def fetch(url):
            rel = next(r for r in RELATIONS if "/r/" + r + "&" in url)
            row = event(gold=rel)[rel][0]
            row = dict(start=row["start"], end=row["end"], rel={"@id": "/r/" + rel}, **{"@id": rel})
            non_english = deepcopy(row)
            non_english["end"]["language"] = "de"
            return {"edges": [row, row, non_english]}
        self.assertEqual([len(v) for v in collect(fetch=fetch).values()], [1] * 4)

    def test_pagination_host_is_validated(self):
        def fetch(_):
            return {"edges": [], "view": {"nextPage": "https://example.invalid/data"}}
        with self.assertRaises(ValueError):
            collect(max_pages=2, fetch=fetch)


if __name__ == "__main__":
    unittest.main()
