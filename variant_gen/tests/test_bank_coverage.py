"""Run with python -B -m unittest discover -s tests from variant_gen."""
import sys
import unittest
import csv
import json
import shutil
import tempfile
from math import sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bank import BankError, OriginalBank
from config_store import ConfigStore, validate_config
from engine import build_values, generate
from expr import to_num
from lint import reproduce_original


class BankCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = OriginalBank(ROOT / "data" / "q0_bank.csv")
        cls.configs = ConfigStore(ROOT / "configs")

    def test_original_revision_rejects_wrong_source_version(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "q0_bank.csv"
            shutil.copyfile(ROOT / "data" / "q0_bank.csv", target)
            with target.open(encoding="utf-8-sig", newline="") as f:
                row = next(r for r in csv.DictReader(f) if r["id"] == "pg-16-3-5")
            replacement = dict(row, version="2")
            revision = {"question_id": row["id"], "original_version": 999,
                        "original_row": row, "replacement_version": 2,
                        "replacement_row": replacement, "reason": "test invalid provenance"}
            target.with_name("original_revisions.jsonl").write_text(json.dumps(revision), encoding="utf-8")
            with self.assertRaises(BankError):
                OriginalBank(target)

    def test_all_area_and_volume_questions_generate(self):
        for qid in self.bank.ids():
            if qid.split("-")[1] not in ("18", "19"):
                continue
            with self.subTest(question=qid):
                original = self.bank.get(qid)
                self.assertTrue(self.configs.versions(qid), f"missing config: {qid}")
                cfg, _ = self.configs.load(qid)
                self.assertEqual(validate_config(cfg, original), [])
                self.assertEqual(reproduce_original(original, cfg)[0], [])
                candidates = []
                for seed in range(1, 4):
                    result = generate(original, cfg, seed, candidates)
                    candidates.append(result.cand)
                    self.assertTrue(result.cand["explanation"].strip())

    def test_numeric_skipped_questions_generate(self):
        for qid in ("mcma-16-3-6", "pg-17-3-3"):
            with self.subTest(question=qid):
                self.assertTrue(self.configs.versions(qid), f"missing reviewed config: {qid}")
                original = self.bank.get(qid)
                cfg, _ = self.configs.load(qid)
                self.assertEqual(reproduce_original(original, cfg)[0], [])
                candidates = []
                for seed in range(1, 4):
                    candidates.append(generate(original, cfg, seed, candidates).cand)

    def test_volume_distractors_are_positive(self):
        for qid in ("mcma-19-1-7", "mcma-19-2-7"):
            original = self.bank.get(qid)
            cfg, _ = self.configs.load(qid)
            for seed in range(1, 51):
                with self.subTest(question=qid, seed=seed):
                    self.assertGreater(generate(original, cfg, seed, []).values["wrong"], 0)

    def test_representative_area_and_volume_answers(self):
        examples = (
            ("pg-19-1-1", {"a": 8, "b": 10, "h": 12}, {"base": 40, "V": 480}),
            ("mcma-18-3-6", {"p": 20, "l": 12}, {"half": 56.52, "total": 296.52, "K": 70.84}),
            ("kategori-19-3-10", {"r": 3, "R": 8, "h": 12}, {"sphere": 113.04, "cylinder": 2411.52}),
        )
        for qid, inputs, answers in examples:
            cfg, _ = self.configs.load(qid)
            values = build_values(cfg, lambda name, spec: to_num(inputs[name]))
            for name, expected in answers.items():
                with self.subTest(question=qid, variable=name):
                    self.assertEqual(values[name], to_num(expected))

    def test_cone_slant_height_exceeds_radius(self):
        original = self.bank.get("kategori-16-3-10")
        cfg, _ = self.configs.load(original["id"])
        for seed in range(1, 101):
            values = generate(original, cfg, seed, []).values
            self.assertGreater(values["s"], values["r"], f"seed {seed}")

    def test_square_pyramid_side_faces_reach_above_base(self):
        original = self.bank.get("pg-16-1-4")
        cfg, _ = self.configs.load(original["id"])
        for seed in range(1, 101):
            values = generate(original, cfg, seed, []).values
            self.assertGreater(4 * values["L"], values["a"], f"seed {seed}")

    def test_prism_original_and_variants_have_possible_right_triangle(self):
        original = self.bank.get("pg-16-3-5")
        cfg, _ = self.configs.load(original["id"])
        values = build_values(cfg, lambda name, spec: to_num(cfg["original_values"][name]))
        self.assertGreaterEqual(float(values["K"]) ** 2 + 1e-9,
                                (6 + 4 * sqrt(2)) * float(values["T"]))
        for seed in range(1, 101):
            values = generate(original, cfg, seed, []).values
            self.assertGreaterEqual(float(values["K"]) ** 2 + 1e-9,
                                    (6 + 4 * sqrt(2)) * float(values["T"]))

    def test_ball_fits_inside_full_cylinder(self):
        original = self.bank.get("kategori-19-3-10")
        self.assertTrue(self.configs.versions(original["id"]), "missing sphere/cylinder config")
        cfg, _ = self.configs.load(original["id"])
        for seed in range(1, 101):
            values = generate(original, cfg, seed, []).values
            self.assertLessEqual(values["r"], values["R"])
            self.assertLessEqual(2 * values["r"], values["h"])


if __name__ == "__main__":
    unittest.main()
