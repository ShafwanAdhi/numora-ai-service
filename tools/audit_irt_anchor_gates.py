"""Audit immutable benchmark evidence; does not fit, tune or approve a policy."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from numora_service.irt.gates import anchor_gate
from numora_service.irt.producer import policy


def wilson(successes,total):
    z=1.959963984540054
    p=successes/total;den=1+z*z/total
    center=(p+z*z/(2*total))/den
    radius=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/den
    return [center-radius,center+radius]


def audit(folder,manifest):
    expected=json.loads(manifest.read_text(encoding='utf-8'))
    profile=policy()
    if hashlib.sha256((ROOT/'research/irt/policy-v1.json').read_bytes().replace(b'\r\n',b'\n')).hexdigest()!=expected['policySha256']:
        raise ValueError('Policy provenance changed')
    rows=[];reasons=Counter();modes=Counter();statuses=Counter()
    for pin in expected['replications']:
        path=folder/pin['file'];data=path.read_bytes()
        if hashlib.sha256(data).hexdigest()!=pin['sha256']:
            raise ValueError('Report provenance changed: '+pin['file'])
        report=json.loads(data)
        if report['image']!=expected['image'] or report['truth']['seed']!=pin['seed']:
            raise ValueError('Runtime/seed provenance changed')
        anchors=report['diagnostics']['anchors']
        # The baseline generator fixes common anchor IDs and identical true parameters.
        from research.irt.synthetic import generate
        value,truth=generate(report['truth']['perArm'],pin['seed'],report['truth']['design'])
        if json.loads(json.dumps(truth))!=report['truth']:
            raise ValueError('Synthetic truth provenance changed')
        gate=anchor_gate(anchors,value['anchorQuestionVersionIds'],profile['quality'])
        for check in gate['checks'].values():reasons.update(check['reasons'])
        modes[report.get('experimentKind','CONTRACT_PRODUCER')]+=1
        statuses.update(p['status'] for p in (report.get('result') or {}).get('outcome',{}).get('respondents',[]))
        rows.append({'file':pin['file'],'sha256':pin['sha256'],'seed':pin['seed'],
                     'held':not gate['passed'],'checks':gate['checks']})
    held=sum(r['held'] for r in rows)
    return {'purpose':'RESEARCH_ONLY','policyVersion':profile['version'],'policySha256':expected['policySha256'],
            'image':expected['image'],'design':'MIXED_2PL_GPCM_2_ARMS_1000_PER_ARM_NO_INJECTED_DIF',
            'replications':len(rows),'heldReplications':held,'holdRate':held/len(rows),
            'holdRateWilson95':wilson(held,len(rows)),'anchorHoldReasons':dict(reasons),
            'experimentModes':dict(modes),'observedParticipantStatuses':dict(statuses),
            'policyChanged':False,'productionApproved':False,
            'interpretation':'High baseline hold rate requires review. Nonsignificance does not prove equivalence. No threshold tuning or approval follows from this audit.',
            'remainingScientificWork':['Measure sample-size sensitivity and uncertainty of released-anchor effects.',
                'Measure false holds and DIF detection together before proposing a versioned replacement policy.',
                'Per-arm containment needs a trusted-reference/refitting design; do not score a potentially contaminated joint fit.'],
            'replicationEvidence':rows}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--reports',type=Path,required=True)
    p.add_argument('--manifest',type=Path,default=ROOT/'research/irt/acceptance-report-v1.json')
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    result=audit(args.reports,args.manifest)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='replicationEvidence'},indent=2))
