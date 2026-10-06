"""Run:  python -m unittest discover -s tests -v   (from the variant_gen folder)"""
import contextlib
import csv
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
from bank import OriginalBank, _parse_row, load_workspace_bank
from config_store import ConfigStore, validate_config
from engine import generate
from filters import correct_set, signature
from handoff import export_record
from expr import ExprError, RejectDraw, evaluate, format_number, render
from lint import run_lint
from store import StoreError

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
        cls.bank, cls.configs = load_workspace_bank(BANK), ConfigStore(ROOT / "configs")

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
            self.assertNotEqual(signature(a.cand["stem"], a.cand["options"]),
                                signature(orig["stem"], orig["options"]), qid)
            self.assertNotEqual(correct_set(a.cand["options"]), correct_set(orig["options"]), qid)

    def test_original_is_untouchable(self):
        orig = self.bank.get("pg-18-3-1")
        orig["stem"] = "tampered"
        self.assertNotEqual(self.bank.get("pg-18-3-1")["stem"], "tampered")


class CliHarness(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.cfg_dir = self.tmp / "configs"
        shutil.copytree(ROOT / "configs", self.cfg_dir)
        self.args = ["--store", str(self.tmp / "s.jsonl"), "--configs", str(self.cfg_dir)]

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_cli(self, *a):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
            result = cli.main(list(a) + self.args + ['--json'])
        if result == 0:
            try:
                rec = json.loads(output.getvalue())
                if 'question_id' in rec: self.last_record = rec
            except (ValueError, TypeError): pass
        return result


class Cli(CliHarness):
    def test_repeated_gen_returns_content_without_persistence(self):
        self.assertEqual(self.run_cli('gen','pg-18-3-1','s4'),0)
        first=self.last_record
        self.assertEqual(self.run_cli('gen','pg-18-3-1','s4'),0)
        self.assertEqual(first['stem'],self.last_record['stem'])
        self.assertFalse((self.tmp/'s.jsonl').exists())

    def test_seed_zero_rules(self):
        self.assertEqual(self.run_cli('view','pg-18-3-1','s0'),0)
        self.assertEqual(self.last_record['seed'],0)
        self.assertFalse((self.tmp/'s.jsonl').exists())

    def test_generate_uses_latest_config(self):
        q='pg-18-3-1'
        self.assertEqual(self.run_cli('gen',q,'s2'),0)
        cfg=json.loads((self.cfg_dir/q/'v1.json').read_text(encoding='utf-8'))
        cfg['config_version']=2
        cfg['variables']['r1']['range']=[3,9]
        (self.cfg_dir/q/'v2.json').write_text(json.dumps(cfg),encoding='utf-8')
        self.assertEqual(self.run_cli('gen',q,'s2'),0)
        self.assertEqual(self.last_record['config_ver'],2)
        self.assertFalse((self.tmp/'s.jsonl').exists())

    def test_finite_domain_can_be_generated_repeatedly(self):
        for i in range(1,15): self.assertEqual(self.run_cli('gen','pg-18-1-5',f's{i}'),0)
        self.assertFalse((self.tmp/'s.jsonl').exists())


class Regressions(CliHarness):
    def setUp(self):
        super().setUp()
        # Exercise the other regressions independently of the bank's BOM bug.
        clean_bank = self.tmp / "bank.csv"
        clean_bank.write_text(BANK.read_text(encoding="utf-8-sig"), encoding="utf-8")
        self.args += ["--bank", str(clean_bank)]

    def test_bom_bank_loads(self):
        try:
            bank = OriginalBank(BANK)
        except KeyError as error:
            self.fail(f"BOM must not become part of the CSV header: {error}")
        self.assertIn("pg-18-3-1", bank.ids())

    def test_missing_or_wrong_original_hash_is_rejected(self):
        with BANK.open(encoding="utf-8-sig", newline="") as f:
            row = next(r for r in csv.DictReader(f) if r["id"] == "pg-18-3-1")
        original = _parse_row(row, 2)
        config, _ = ConfigStore(ROOT / "configs").load(original["id"])
        for bad_hash in (None, "wrong"):
            changed = dict(config)
            if bad_hash is None:
                changed.pop("original_hash", None)
            else:
                changed["original_hash"] = bad_hash
            self.assertTrue(validate_config(changed, original), bad_hash)

    def test_all_config_paths_match_bank_ids_exactly(self):
        bank = load_workspace_bank(BANK)
        for path in (ROOT / "configs").glob("*/v*.json"):
            config = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(path.parent.name, config["question_id"])
            self.assertIn(path.parent.name, bank.ids())

    def test_explanation_is_rendered_in_response(self):
        self.assertEqual(self.run_cli('gen','pg-18-3-1','s4'),0)
        self.assertTrue(self.last_record['explanation'])
        self.assertNotIn('{',self.last_record['explanation'])
        self.assertIn(self.last_record['key'],self.last_record['explanation'])

    def test_regen_command_is_removed(self):
        with self.assertRaises(SystemExit): self.run_cli('regen','pg-18-3-1','s4')

    def test_legacy_store_is_never_read(self):
        path=self.tmp/'s.jsonl'
        path.write_text('invalid legacy content',encoding='utf-8')
        self.assertEqual(self.run_cli('gen','pg-16-1-3','s1'),0)
        self.assertEqual(self.last_record['config_ver'],2)
        self.assertEqual(path.read_text(encoding='utf-8'),'invalid legacy content')

    def test_export_preserves_answers_for_all_formats_and_rejects_legacy(self):
        for qid in ("pg-18-3-1", "mcma-17-2-7", "kategori-19-1-9"):
            self.assertEqual(self.run_cli("gen", qid, "s4"), 0)
            record = self.last_record
            mapping = {
                "questionExternalId": qid,
                "originalHash": record["original_hash"],
                "originalVersion": record["original_version"],
                "familyId": "11111111-1111-4111-8111-111111111111",
                "parentQuestionVersionId": "22222222-2222-4222-8222-222222222222",
                "scoringRubricVersionId": "33333333-3333-4333-8333-333333333333",
            }
            exported = export_record(record, mapping)
            self.assertEqual(exported["payload"]["options"], record["options"])
            self.assertEqual(exported["generation"]["reviewStatus"], "REVIEW")
            correct = set(record["key"].split(","))
            if record["format"] == "PG":
                self.assertEqual(exported["answer"]["correctOptionId"], record["key"])
            elif record["format"] == "MCMA":
                self.assertEqual(set(exported["answer"]["correctOptionIds"]), correct)
            else:
                statements = exported["answer"]["statements"]
                self.assertEqual(len(statements), len(record["options"]))
                self.assertEqual({s["id"] for s in statements if s["correct"]}, correct)
                self.assertTrue(any(not s["correct"] for s in statements))
            legacy = {k: v for k, v in record.items() if k != "explanation"}
            with self.assertRaises(StoreError):
                export_record(legacy, mapping)

    def test_export_requires_real_matching_mapping(self):
        qid = "pg-18-3-1"
        self.assertEqual(self.run_cli("gen", qid, "s4"), 0)
        record = self.last_record
        mapping = {
            "questionExternalId": qid,
            "originalHash": record["original_hash"],
            "originalVersion": record["original_version"],
            "familyId": "11111111-1111-4111-8111-111111111111",
            "parentQuestionVersionId": "22222222-2222-4222-8222-222222222222",
            "scoringRubricVersionId": "33333333-3333-4333-8333-333333333333",
        }
        path = self.tmp / "mapping.json"
        path.write_text(json.dumps(mapping), encoding="utf-8")
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                status = cli.main(["export", qid, "s4", "--mapping", str(path)] + self.args)
        except SystemExit:
            self.fail("the export command is missing")
        self.assertEqual(status, 0)
        exported = json.loads(output.getvalue())
        self.assertEqual(exported["variantExternalId"], record["record_id"])
        self.assertEqual(exported["payload"]["parentQuestionVersionId"], mapping["parentQuestionVersionId"])
        self.assertEqual(exported["explanation"]["text"], record["explanation"])
        for field, value in (("originalHash", "wrong"), ("originalVersion", 999),
                             ("familyId", None), ("scoringRubricVersionId", "not-a-uuid"),
                             ("parentQuestionVersionId", "00000000-0000-0000-0000-000000000000")):
            changed = {**mapping, field: value}
            path.write_text(json.dumps(changed), encoding="utf-8")
            self.assertEqual(self.run_cli("export", qid, "s4", "--mapping", str(path)), 1, field)


if __name__ == "__main__":
    unittest.main()
