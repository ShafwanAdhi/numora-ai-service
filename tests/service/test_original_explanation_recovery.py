import hashlib
import json
import unittest

from numora_service.bridge import ROOT, workspace
from numora_service.mapping_audit import source_projection


class OriginalExplanationRecoveryTests(unittest.TestCase):
    def test_eight_explanations_preserve_source_and_only_authorized_corrections(self):
        bank, configs = workspace()
        directory = ROOT / 'variant_gen/data/drill-1-indicators-16-19'
        snapshot = json.loads((directory / 'skipped-source-review.json').read_text(encoding='utf-8'))
        digest = hashlib.sha256((directory / snapshot['source_document']).read_bytes()).hexdigest()
        self.assertEqual(digest, snapshot['source_document_sha256'])
        ids = {'pg-16-1-1', 'pg-16-1-2', 'pg-16-3-2', 'pg-17-3-2',
               'mcma-16-1-6', 'kategori-16-1-9', 'kategori-16-2-9', 'kategori-17-3-10'}
        recovered = set()
        for item in snapshot['questions']:
            qid = item['question_id']
            if qid not in ids:
                continue
            with self.subTest(qid=qid):
                original = bank.get(qid)
                provenance = original['metadata']['original_explanation_provenance']
                raw = item['source_text'].split('Pembahasan:\n', 1)[1]
                self.assertEqual(provenance['source_explanation_verbatim'], raw)
                self.assertEqual(provenance['source_document_sha256'], digest)
                self.assertEqual(provenance['original_hash'], original['hash'])
                self.assertEqual(provenance['original_version'], original['version'])
                self.assertEqual(provenance['curriculum_approval'], 'NOT_ADDED')
                expected = raw
                if qid == 'pg-17-3-2':
                    expected = raw.replace('(-,x-y)', '(-x,-y)')
                elif qid == 'mcma-16-1-6':
                    expected += '\nPernyataan 4: Benar, karena 2 segitiga dan 3 persegi panjang berjumlah 5 bangun datar penyusun.'
                else:
                    self.assertEqual(provenance['corrections'], [])
                projection, origin = source_projection(original, configs)
                self.assertEqual(origin, 'LOCAL_METADATA')
                self.assertEqual(projection['explanation']['text'], expected)
                recovered.add(qid)
        self.assertEqual(recovered, ids)


if __name__ == '__main__':
    unittest.main()
