"""Batch-four evidence and explicit source-review actions; no variant content saved."""
import json
from audit_drill_6_10_level45_batch1 import main as audit
from test_drill_6_10_level45_batch4 import ROOT, DATA, IDS, check_math

OUTPUT=ROOT.parent/'docs/audits/2026-10-21-drill-6-10-level45-batch4'

if __name__=='__main__':
    prior=[]
    for stage in (1,2,3):
        path=ROOT.parent/f'docs/audits/2026-10-20-drill-6-10-level45-batch{stage}/audit.json'
        prior.extend(e['source_audit_id'] for e in json.loads(path.read_text(encoding='utf-8'))['entries'])
    audit(IDS=IDS,OUTPUT=OUTPUT,BASELINE=ROOT/'tests/.batch6_10_batch4_baseline.json',
          check_math=check_math,prior_source_ids=prior,stage=4)
    metadata=json.loads((DATA/'question_metadata.json').read_text(encoding='utf-8'))
    reviews={qid:m['source_review'] for qid,m in metadata.items()}
    (OUTPUT/'source-review.json').write_text(json.dumps(reviews,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    path=OUTPUT/'README.md'
    path.write_text(path.read_text(encoding='utf-8')+'''

## Tinjauan sumber tahap ini

Seluruh stimulus dan kunci terpilih berstatus VALID/CORRECT pada audit akademik.
Temuan pembahasan, domain, presisi, atau proyeksi dicatat dalam source-review.json.
Deklarasi kunci yang bocor ke stimulus dihapus pada bank baru; teks proyeksi mentah
dan pembahasan original tetap tersimpan verbatim dalam metadata. Pembahasan varian
memperbaiki perhitungan atau alasan yang ditemukan keliru. Sumber DOCX tidak diubah.

Untuk opsi kualitatif, sebagian varian menambahkan hasil perhitungan pendukung agar
jawaban memuat variasi matematis yang dapat diuji. Original tetap direproduksi persis
pada nilai original setelah normalisasi batas komponen di atas. Aturan engine tidak dilonggarkan.
''',encoding='utf-8')
