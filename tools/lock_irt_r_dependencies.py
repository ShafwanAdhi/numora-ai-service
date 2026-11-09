"""Explicit maintainer operation: resolve and hash the complete R source closure."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://cloud.r-project.org/src/contrib/'
BASE_PACKAGES = set('base compiler datasets graphics grDevices grid methods parallel splines stats stats4 tcltk tools utils'.split())
BASE_PACKAGES.update('boot class cluster codetools foreign KernSmooth lattice MASS Matrix mgcv nlme nnet rpart spatial survival'.split())


def main():
    text = gzip.decompress(urllib.request.urlopen(BASE+'PACKAGES.gz', timeout=30).read()).decode()
    records = {}
    for block in text.split('\n\n'):
        block = re.sub(r'\n[ \t]+', ' ', block)
        record = dict(line.split(': ',1) for line in block.splitlines() if ': ' in line)
        if 'Package' in record: records[record['Package']] = record
    selected = {}
    def resolve(name):
        if name in BASE_PACKAGES or name == 'R' or name in selected: return
        record = records[name]
        selected[name] = record
        for key in ['Depends', 'Imports', 'LinkingTo']:
            for dependency in record.get(key,'').split(','):
                dep = dependency.strip().split(' ')[0]
                if dep: resolve(dep)
    for name in ['mirt', 'jsonlite']: resolve(name)
    assert selected['mirt']['Version'] == '1.48', 'Review required; do not update mirt automatically'
    lock = []
    for name, record in sorted(selected.items()):
        url = BASE+name+'_'+record['Version']+'.tar.gz'
        data = urllib.request.urlopen(url, timeout=60).read()
        lock.append({'name':name, 'version':record['Version'], 'url':url,
                     'sha256':hashlib.sha256(data).hexdigest()})
        print(name, record['Version'], flush=True)
    (ROOT/'research/irt/r-sources.lock.json').write_text(json.dumps(lock,indent=2)+'\n',encoding='utf-8')
    (ROOT/'research/irt/r-sources.lock.tsv').write_text('name\tversion\turl\tsha256\n'+''.join('\t'.join(row[k] for k in ['name','version','url','sha256'])+'\n' for row in lock),encoding='utf-8')


if __name__ == '__main__': main()
