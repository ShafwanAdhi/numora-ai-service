"""Second-batch summary; preserves batch 1's historical audit and all originals."""
import json
from audit_drill_6_10_level45_batch1 import main as audit
from test_drill_6_10_level45_batch2 import ROOT, IDS, check_math

if __name__ == '__main__':
    previous=ROOT.parent/'docs/audits/2026-10-20-drill-6-10-level45-batch1/audit.json'
    prior_source_ids=[r['source_audit_id'] for r in json.loads(previous.read_text(encoding='utf-8'))['entries']]
    audit(IDS=IDS, OUTPUT=ROOT.parent/'docs/audits/2026-10-20-drill-6-10-level45-batch2',
          BASELINE=ROOT/'tests/.batch6_10_batch2_baseline.json', check_math=check_math,
          prior_source_ids=prior_source_ids, stage=2)
