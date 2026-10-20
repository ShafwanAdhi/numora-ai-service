"""Record exact domain capacity and outstanding source decisions; no variant bodies."""
import json
from audit_drill_6_10_level45_batch1 import main as audit
from test_drill_6_10_level45_batch5 import ROOT,DATA,IDS,check_math

OUTPUT=ROOT.parent/'docs/audits/2026-10-21-drill-6-10-level45-batch5'
if __name__=='__main__':
    prior=[]
    for stage in range(1,5):
        date='2026-10-20' if stage<4 else '2026-10-21'
        path=ROOT.parent/f'docs/audits/{date}-drill-6-10-level45-batch{stage}/audit.json'
        prior.extend(e['source_audit_id'] for e in json.loads(path.read_text(encoding='utf8'))['entries'])
    audit(IDS=IDS,OUTPUT=OUTPUT,BASELINE=ROOT/'tests/.batch6_10_batch5_baseline.json',
          check_math=check_math,prior_source_ids=prior,stage=5)
    meta=json.loads((DATA/'question_metadata.json').read_text(encoding='utf8'))
    (OUTPUT/'source-review.json').write_text(json.dumps({q:m['source_review'] for q,m in meta.items()},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    path=OUTPUT/'README.md'
    path.write_text(path.read_text(encoding='utf8')+'''

## Koreksi kunci yang pasti

Tujuh kunci dikoreksi dengan stimulus dan opsi sumber tetap identik.
Pembahasan original yang keliru tetap tersedia verbatim dalam metadata;
pembahasan varian dihitung ulang. Sumber DOCX dan audit historis tidak diubah.
Status tetap NOT_CURRICULUM_APPROVED.

Sisa 18: 17 menunggu keputusan revisi sumber dan 1 konseptual menunggu keputusan stok.
Lihat [usulan revisi per soal](../2026-10-21-drill-6-10-level45-batch5-source-proposal.md).
''',encoding='utf8')
