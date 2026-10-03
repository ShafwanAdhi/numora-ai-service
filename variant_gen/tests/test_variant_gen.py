"""Run:  python -m unittest discover -s tests -v   (from the variant_gen folder)"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import cli
from bank import OriginalBank
from config_store import ConfigStore
from engine import generate
from expr import ExprError, RejectDraw, evaluate, format_number, render
from lint import run_lint
from store import VariantStore

BANK = ROOT / "data" / "q0_bank.csv"
CONFIG_QIDS = sorted(p.name for p in (ROOT / "configs").iterdir() if p.is_dir())


class ExprSafety(unittest.TestCase):
    def test_blocks_code_execution(self):
        for bad in ["__import__('os').system('x')", "().__class__", "open('f')", "x.real", "[1][0]",
                    "(lambda: 1)()", "a if b else __import__('os')", "pow(2,3)"]:
            with self.assertRaises(ExprError, msg=bad):
                evaluate(bad, {"a": 1, "b": 1, "x": 1})

    def test_limits(self):
        with self.assertRaises(ExprError):
            evaluate("2 ** 100", {})                  # exponent cap
        with self.assertRaises(RejectDraw):
            evaluate("999999 * 999999 * 999999", {})  # magnitude cap
        with self.assertRaises(RejectDraw):
            evaluate("1 / x", {"x": 0})

    def test_exact_arithmetic(self):
        self.assertEqual(evaluate("22/7 * 7*7", {}), 154)
        self.assertEqual(evaluate("3.14 * 50*50*100/1000/5", {}), 157)
        self.assertEqual(evaluate("round(2.5)", {}), 3)        # half up, not banker's

    def test_template_is_not_str_format(self):
        # str.format would evaluate attribute access; our renderer leaves it as inert literal text
        self.assertEqual(render("{q1.__class__}", {"q1": 1}), "{q1.__class__}")
        self.assertEqual(render("{a} cm", {"a": 1570}), "1.570 cm")
        with self.assertRaises(ExprError):
            render("{missing}", {"a": 1})

    def test_number_format(self):
        self.assertEqual(format_number(1570), "1.570")
        self.assertEqual(format_number(Fraction(157, 50)), "3,14")
        self.assertEqual(format_number(-2), "-2")
        self.assertEqual(format_number(1500, group=False), "1500")


class Configs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank, cls.configs = OriginalBank(BANK), ConfigStore(ROOT / "configs")

    def test_every_config_lints_clean(self):
        for qid in CONFIG_QIDS:
            orig = self.bank.get(qid)
            cfg, _ = self.configs.load(qid)
            ok, lines = run_lint(orig, cfg, n=15)
            self.assertTrue(ok, f"{qid}\n" + "\n".join(lines))

    def test_variant_never_equals_original_and_is_deterministic(self):
        for qid in CONFIG_QIDS:
            orig = self.bank.get(qid)
            cfg, _ = self.configs.load(qid)
            a = generate(orig, cfg, 3, [])
            b = generate(orig, cfg, 3, [])
            self.assertEqual((a.values, a.cand), (b.values, b.cand), qid)
            self.assertNotEqual(a.cand["stem"], orig["stem"], qid)

    def test_original_is_untouchable(self):
        orig = self.bank.get("pg-18-3-1")
        orig["stem"] = "tampered"
        self.assertNotEqual(self.bank.get("pg-18-3-1")["stem"], "tampered")


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.cfg_dir = self.tmp / "configs"
        shutil.copytree(ROOT / "configs", self.cfg_dir)
        self.args = ["--store", str(self.tmp / "s.jsonl"), "--configs", str(self.cfg_dir)]
        self.store = VariantStore(self.tmp / "s.jsonl")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_cli(self, *a):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return cli.main(list(a) + self.args)

    def test_gen_is_idempotent_and_regen_versions(self):
        q = "pg-18-3-1"
        self.assertEqual(self.run_cli("gen", q, "s4"), 0)
        first = self.store.get(q, 4)
        self.assertEqual(self.run_cli("gen", q, "s4"), 0)
        self.assertEqual(len(self.store.versions_of_seed(q, 4)), 1)           # nothing overwritten
        self.assertEqual(self.run_cli("regen", q, "s4"), 1)                   # same config, no reason: refused
        self.assertEqual(self.run_cli("regen", q, "s4", "--reason", "reroll"), 0)
        vs = self.store.versions_of_seed(q, 4)
        self.assertEqual([v["variant_ver"] for v in vs], [1, 2])
        self.assertEqual(vs[0], first)                                        # old version kept intact
        self.assertNotEqual(vs[1]["stem"] + vs[1]["key"], vs[0]["stem"] + vs[0]["key"])

    def test_seed_zero_rules(self):
        self.assertEqual(self.run_cli("regen", "pg-18-3-1", "s0"), 1)
        self.assertEqual(self.run_cli("view", "pg-18-3-1", "s0"), 0)
        self.assertEqual(self.store.for_question("pg-18-3-1"), [])

    def test_new_config_version_allows_regen_and_edit_after_use_is_blocked(self):
        q = "pg-18-3-1"
        self.run_cli("gen", q, "s2")
        v1 = self.cfg_dir / q / "v1.json"
        cfg = json.loads(v1.read_text(encoding="utf-8"))
        cfg["variables"]["r1"]["range"] = [3, 9]                              # edit v1 in place -> blocked
        v1.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(self.run_cli("gen", q, "s3"), 1)
        orig_cfg = json.loads((ROOT / "configs" / q / "v1.json").read_text(encoding="utf-8"))
        v1.write_text(json.dumps(orig_cfg, ensure_ascii=False), encoding="utf-8")   # revert
        orig_cfg["config_version"] = 2                                       # proper way: new version
        orig_cfg["variables"]["r1"]["range"] = [3, 9]
        (self.cfg_dir / q / "v2.json").write_text(json.dumps(orig_cfg, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(self.run_cli("regen", q, "s2"), 0)
        self.assertEqual(self.store.get(q, 2)["config_ver"], 2)

    def test_exhausted_config_fails_loudly_and_stores_nothing(self):
        q = "pg-18-1-5"                                                      # only 6 distinct variants exist
        codes = [self.run_cli("gen", q, f"s{i}") for i in range(1, 12)]
        self.assertIn(1, codes)
        self.assertEqual(len(self.store.for_question(q)), codes.count(0))


if __name__ == "__main__":
    unittest.main()
