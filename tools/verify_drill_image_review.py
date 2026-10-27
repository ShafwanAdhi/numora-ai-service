"""Read-only verification of full coverage, mathematical answers and conceptual geometry."""
import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'variant_gen'))
from config_store import ConfigStore
from engine import build_values
from drill_media_review import verify_review_files
from drill_images import IDS as NUMERIC
from drill_concept_images import load_scenario
from tryout_media import json_bytes
from audit_drill_numeric_images import mathematical_checks,geometry_checks


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True,type=Path)
    parser.add_argument('--report',type=Path,help='Optional explicit location for proof JSON.')
    args=parser.parse_args()
    files={p.relative_to(args.input).as_posix():p.read_bytes() for p in args.input.rglob('*') if p.is_file()}
    summary=verify_review_files(files)
    questions=json.loads(files['questions.json']);manifest=json.loads(files['media-manifest.json'])
    configs=ConfigStore(ROOT/'variant_gen/configs')
    proofs=[];numeric_geometry={};numeric_count=0;concept_count=0
    for item,asset in zip(questions['items'],manifest['assets']):
        qid=item['question_id'];record=item['record'];mode=item['mode']
        if qid in NUMERIC:
            cfg,_=configs.load(qid)
            values=(build_values(cfg,lambda name,spec:cfg['original_values'][name])
                    if mode=='original' else record['values_used'])
            bound={name:Fraction(exact['numerator'],exact['denominator'])
                   for name,exact in asset['provenance']['bindings'].items()}
            evidence=mathematical_checks(qid,item['k'],record,values,bound)
            numeric_geometry.setdefault(qid,geometry_checks(qid))
            numeric_count+=1
        else:
            variant=item['request'].get('stock_variant_id')
            geometry=load_scenario(qid,variant).geometry
            panels=geometry.get('panels',[])
            for panel in panels:
                faces=panel.get('faces',[])
                if faces:
                    for kind in ('circle','rectangle','triangle'):
                        if kind+'_count' in panel:
                            assert sum(f['kind']==kind for f in faces)==panel[kind+'_count']
                if 'arc_relation' in panel:
                    sector=next(f for f in faces if f['kind']=='sector')
                    circle=next(f for f in faces if f['kind']=='circle')
                    relation=Fraction(sector['sweep_degrees'],360)*sector['radius']
                    assert (relation<circle['radius'])==(panel['arc_relation']=='shorter')
            if qid=='mcma-16-4-6':
                assert len(geometry['net_faces'])==4 and len(geometry['solid_vertices'])==4 and len(geometry['solid_edges'])==6
                assert 4-6+4==2
                expected='A,B,C'
            elif qid=='mcma-16-4-7':
                expected_circles=1 if variant and variant.endswith('01') else 2
                assert panels[0]['circle_count']==expected_circles
                expected='A,C,D' if mode=='original' else 'A,B,D'
            elif qid=='pg-16-4-2':
                expected='D' if variant and variant.endswith('02') else 'C'
                if variant and variant.endswith('01'):assert panels[2]['triangle_count']==3
                if variant and variant.endswith('02'):assert panels[3]['arc_relation']=='shorter'
            else:
                expected='C'
                if mode=='original':
                    for index,length in ((0,44),(2,20)):
                        rect=next(f for f in panels[index]['faces'] if f['kind']=='rectangle')
                        circle=next(f for f in panels[index]['faces'] if f['kind']=='circle')
                        width=Fraction(str(rect['vertices'][1][0]))-Fraction(str(rect['vertices'][0][0]))
                        assert abs(float(width/Fraction(str(circle['radius'])))-length/7)<1e-10
                elif variant.endswith('02'):
                    scenario=load_scenario(qid,variant)
                    assert not any('2πr' in label.text for label in scenario.image.labels)
            assert record['key']==expected
            evidence={'key':expected,'geometry':'PASS','content_scenario_pin':'PASS'}
            concept_count+=1
        proofs.append({'case_id':item['case_id'],'status':'PASS','independent_check':evidence})
    result={**summary,'numeric_math_checks':numeric_count,'conceptual_checks':concept_count,
            'numeric_geometry':numeric_geometry,'proofs':proofs,
            'approval_scope':'ENGINEERING_LOCAL_REVIEW_NOT_CURRICULUM_OR_IRT_APPROVAL'}
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_bytes(json_bytes(result))
    print(json.dumps({k:result[k] for k in ('status','bundle_id','cases','families','unique_images','numeric_math_checks','conceptual_checks')},indent=2))


if __name__=='__main__':main()
