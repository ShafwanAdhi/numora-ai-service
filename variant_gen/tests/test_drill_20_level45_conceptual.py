"""Contracts for the seven conceptual Indicator 20 generator families."""
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]

from bank import OriginalBank
from config_store import validate_config
from engine import assemble, build_values, generate
from filters import signature, validate_candidate
from lint import reproduce_original

DATA = ROOT / 'data/drill-1-indicators-20-23-levels-4-5'
IDS = {
    'pg-20-4-1', 'pg-20-4-4', 'mcma-20-4-6', 'kategori-20-4-10',
    'pg-20-5-1', 'mcma-20-5-6', 'kategori-20-5-9',
}


class Conceptual20(unittest.TestCase):
    def test_full_domain_and_adversarial_mutations(self):
        from author_drill_20_level45_conceptual import author, selected
        from oracle_drill_20_level45_conceptual import check_math

        bank = OriginalBank(DATA / 'q0_bank.csv')
        entries = selected()
        self.assertEqual({e['question_id'] for e in entries}, IDS)
        for entry in entries:
            qid = entry['question_id']
            with self.subTest(question=qid):
                original = bank.get(qid)
                cfg = author(entry).config(original)
                self.assertEqual(validate_config(cfg, original), [])
                self.assertEqual(reproduce_original(original, cfg), ([], []))
                seen = set()
                original_correct = {o['text'] for o in original['options'] if o['correct']}
                for k in range(25):
                    candidate = assemble(cfg, build_values(cfg, lambda _name, _spec: k))
                    flags = check_math(qid, candidate)
                    self.assertEqual(flags, [o['correct'] for o in candidate['options']])
                    if k:
                        self.assertEqual(validate_candidate(candidate, original, []), [])
                        seen.add(signature(candidate['stem'], candidate['options']))
                        generated_correct = {o['text'] for o in candidate['options'] if o['correct']}
                        self.assertNotEqual(generated_correct, original_correct)
                self.assertEqual(len(seen), 24)

                prior = []
                for seed in range(201, 221):
                    candidate = generate(original, cfg, seed, prior).cand
                    check_math(qid, candidate)
                    prior.append(candidate)
                self.assertEqual(len({signature(c['stem'], c['options']) for c in prior}), 20)
                replay = generate(original, cfg, 220, prior[:-1]).cand
                self.assertEqual(signature(replay['stem'], replay['options']),
                                 signature(prior[-1]['stem'], prior[-1]['options']))

                for index in range(len(candidate['options'])):
                    bad = deepcopy(candidate)
                    bad['options'][index]['correct'] = not bad['options'][index]['correct']
                    with self.assertRaises(AssertionError):
                        check_math(qid, bad)
                bad = deepcopy(candidate)
                correct_index = next(i for i, option in enumerate(bad['options']) if option['correct'])
                bad['options'][correct_index]['text'] = 'Pernyataan ini tidak mengukur tujuan survei secara langsung.'
                with self.assertRaises(AssertionError):
                    check_math(qid, bad)
                if qid == 'pg-20-4-1':
                    bad = deepcopy(candidate)
                    bad['options'][2]['text'] = 'Apakah terdapat hubungan antara tinggi badan dan nilai seni?'
                    with self.assertRaises(AssertionError):
                        check_math(qid, bad)
                elif qid == 'pg-20-5-1':
                    bad = deepcopy(candidate)
                    bad['options'][2]['text'] = ('Bagaimana tingkat kepuasanmu terhadap parkir sekolah? '
                                                 '(Sangat tidak puas, tidak puas, puas, sangat puas)')
                    with self.assertRaises(AssertionError):
                        check_math(qid, bad)
                elif qid == 'kategori-20-4-10':
                    bad = deepcopy(candidate)
                    bad['options'][3]['text'] = 'Aspek warna seragam dan harga buku dapat ditanyakan secara terpisah.'
                    with self.assertRaises(AssertionError):
                        check_math(qid, bad)
                elif qid == 'mcma-20-4-6':
                    bad = deepcopy(candidate)
                    bad['options'][0]['text'] = 'Berapa menit kamu menonton harga saham setiap hari?'
                    with self.assertRaises(AssertionError):
                        check_math(qid, bad)
                elif qid == 'mcma-20-5-6':
                    bad = deepcopy(candidate)
                    bad['options'][0]['text'] = 'Memilih responden beberapa kelas untuk survei harga saham.'
                    with self.assertRaises(AssertionError):
                        check_math(qid, bad)
                elif qid == 'kategori-20-5-9':
                    bad = deepcopy(candidate)
                    bad['options'][2]['text'] = ('Menyajikan jumlah jawaban tiap kategori harga saham '
                                                 'dalam diagram batang berlabel.')
                    with self.assertRaises(AssertionError):
                        check_math(qid, bad)
                bad = deepcopy(candidate)
                bad['explanation'] = 'Alasan utama: hasil diubah tanpa dasar.'
                with self.assertRaises(AssertionError):
                    check_math(qid, bad)


if __name__ == '__main__':
    unittest.main()
