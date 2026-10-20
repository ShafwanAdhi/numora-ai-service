"""Third-batch evidence; summaries only, no stored generated questions."""
import json
from audit_drill_6_10_level45_batch1 import main as audit
from test_drill_6_10_level45_batch3 import ROOT, IDS, check_math

if __name__ == '__main__':
    prior=[]
    for stage in (1,2):
        previous=ROOT.parent/f'docs/audits/2026-10-20-drill-6-10-level45-batch{stage}/audit.json'
        prior.extend(r['source_audit_id'] for r in json.loads(previous.read_text(encoding='utf-8'))['entries'])
    audit(IDS=IDS, OUTPUT=ROOT.parent/'docs/audits/2026-10-20-drill-6-10-level45-batch3',
          BASELINE=ROOT/'tests/.batch6_10_batch3_baseline.json', check_math=check_math,
          prior_source_ids=prior, stage=3)
