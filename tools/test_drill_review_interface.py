"""Drive every exported Drill selection through the real workbench form via playwright-cli."""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:8765/image-variants')
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    questions=json.loads((args.bundle/'questions.json').read_bytes())
    manifest=json.loads((args.bundle/'media-manifest.json').read_bytes())
    groups={}
    for item,asset in zip(questions['items'],manifest['assets']):
        groups.setdefault(item['question_id'],[]).append({'case_id':item['case_id'],
            'request':item['request'],'sha256':asset['sha256'],'stem':item['record']['stem'],
            'key':item['record']['key'],'original_hash':item['record']['original_hash']})
    scratch=ROOT/'.scratch/drill-image-variants/stage5-browser';scratch.mkdir(parents=True,exist_ok=True)
    template=(ROOT/'tools/check_drill_review_interface.js').read_text(encoding='utf-8')
    executable=shutil.which('npx.cmd') or shutil.which('npx')
    if not executable:raise RuntimeError('npx is required for browser checks')
    prefix=[executable,'--yes','--package','@playwright/cli','playwright-cli','-s=drill-stage5-all']
    def command(parts,name):
        result=subprocess.run(prefix+parts,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=100)
        (scratch/(name+'.log')).write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
        if result.returncode or '### Error' in result.stdout:raise RuntimeError('Browser command failed; see '+name+'.log')
        return result.stdout
    report={'status':'RUNNING','bundle_id':manifest['bundle_id'],'families':[]}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    try:
        command(['open',args.url],'open')
        command(['resize','1600','900'],'desktop')
        for qid,rows in groups.items():
            path=scratch/(qid+'.js')
            path.write_text(template.replace('const cases = []; // REVIEW_CASES',
                'const cases = '+json.dumps(rows,ensure_ascii=False)+';'),encoding='utf-8')
            raw=command(['run-code','--filename',str(path)],qid)
            found=re.search(r'### Result\s*\n([\s\S]*?)\n### Ran',raw)
            if not found:raise RuntimeError('Browser did not return a proof for '+qid)
            result=json.loads(found.group(1))
            if result['status']!='PASS' or len(result['cases'])!=len(rows):raise RuntimeError('Incomplete browser coverage')
            report['families'].append(result)
            args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print('PASS',qid,len(rows),'interface selections',flush=True)
        report.update(status='PASS',total_cases=sum(len(f['cases']) for f in report['families']),
                      total_families=len(report['families']))
        if report['total_cases']!=167 or report['total_families']!=9:raise RuntimeError('Expected full Drill review coverage')
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    finally:
        command(['close'],'close')


if __name__=='__main__':main()
