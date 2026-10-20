"""Read-only source audit and conservative content matching. No runtime imports mutate files.

Run from repository root: python variant_gen/tests/audit_original_questions.py
Academic reviews are separate evidence inputs, never inferred from successful generation.
"""
import csv
import difflib
import hashlib
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
VG=ROOT/'variant_gen'
OUT=ROOT/'docs/audits/2026-10-19-original-question-audit'
sys.path.insert(0,str(VG))
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
A='{http://schemas.openxmlformats.org/drawingml/2006/main}'
R='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,data): Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def normalize(text):
    """Display normalization only. No arithmetic, case folding, punctuation or unit removal."""
    if text is None: return None
    text=text.replace('$','').replace('−','-').replace('\u00a0',' ')
    text=text.replace(r'\left','').replace(r'\right','')
    text=text.replace(r'\{','{').replace(r'\}','}')
    text=re.sub(r'\\text\{([^{}]*)\}',r'\1',text)
    text=text.replace(r'^\circ','°').replace(r'\circ','°').replace(r'\%','%')
    # Balanced simple Word/LaTeX structures; repeated passes handle nested fractions.
    for _ in range(12):
        old=text
        text=re.sub(r'\\frac\{([^{}]*)\}\{([^{}]*)\}',r'(\1)/(\2)',text)
        text=re.sub(r'\\sqrt\{([^{}]*)\}',lambda m:'sqrt('+m[1].strip()+')',text)
        text=re.sub(r'\{([^{}]*)\}\^\{([^{}]*)\}',r'\1^\2',text)
        text=re.sub(r'\^\{([^{}]*)\}',r'^\1',text)
        if text==old: break
    text=text.replace('²','^2').replace('³','^3')
    return re.sub(r'\s+',' ',text).strip()


def full_identity(a,b):
    return (a.get('explanation') is not None and b.get('explanation') is not None
            and all(normalize(a.get(k))==normalize(b.get(k)) for k in ('stem','explanation'))
            and [normalize(t) for t in a['options']]==[normalize(t) for t in b['options']]
            and a.get('key') is not None and a['key']==b.get('key')
            and normalize(a.get('additional_notes',''))==normalize(b.get('additional_notes',''))
            and a.get('category_labels')==b.get('category_labels'))


def split_revisions(paragraphs):
    parts=[]; current=[]; label='original'
    for p in paragraphs:
        if re.match(r'^Revisi\s+Soal\s+\d+',p['text'].strip(),re.I):
            if current: parts.append((label,current))
            label='revision'; current=[]
        current.append(p)
    if current: parts.append((label,current))
    return parts


class WordNumbering:
    def __init__(self, root, styles=None):
        self.abstract={}; self.nums={}; self.counts={}; self.styles=styles or {}
        for a in root.findall(W+'abstractNum'):
            self.abstract[a.get(W+'abstractNumId')]={int(l.get(W+'ilvl')):l for l in a.findall(W+'lvl')}
        for n in root.findall(W+'num'):
            self.nums[n.get(W+'numId')]=n

    @classmethod
    def from_xml(cls, text): return cls(ET.fromstring(text))

    def label(self,num_id,level):
        if num_id not in self.nums or num_id=='0': return None
        n=self.nums[num_id]; aid=n.find(W+'abstractNumId').get(W+'val')
        levels=self.abstract.get(aid,{})
        if level not in levels:return None
        l=levels[level]; override=n.find(f"{W}lvlOverride[@{W}ilvl='{level}']")
        if override is not None and override.find(W+'lvl') is not None:l=override.find(W+'lvl')
        start=l.find(W+'start'); start=int(start.get(W+'val')) if start is not None else 1
        if override is not None and override.find(W+'startOverride') is not None:
            start=int(override.find(W+'startOverride').get(W+'val'))
        key=(num_id,level); self.counts[key]=self.counts.get(key,start-1)+1
        for k in list(self.counts):
            if k[0]==num_id and k[1]>level:
                child=levels.get(k[1]); restart=child.find(W+'lvlRestart') if child is not None else None
                if restart is None or restart.get(W+'val')!='0':del self.counts[k]
        fmt=l.find(W+'numFmt'); fmt=fmt.get(W+'val') if fmt is not None else 'decimal'
        template=l.find(W+'lvlText'); template=template.get(W+'val') if template is not None else '%'+str(level+1)+'.'
        if fmt=='bullet':return template
        def value(m):
            lev=int(m[1])-1; v=self.counts.get((num_id,lev),1)
            lf=levels.get(lev,l).find(W+'numFmt'); f=lf.get(W+'val') if lf is not None else 'decimal'
            if f in ('upperLetter','lowerLetter'):
                result=''; base=65 if f=='upperLetter' else 97
                while v: v,r=divmod(v-1,26); result=chr(base+r)+result
                return result
            return str(v)
        return re.sub(r'%(\d+)',value,template)

    def paragraph_label(self,p):
        props=p.find(W+'pPr'); chain=[]; seen=set()
        if props is not None:chain.append(props)
        style=props.find(W+'pStyle') if props is not None else None
        sid=style.get(W+'val') if style is not None else None
        while sid and sid not in seen:
            seen.add(sid); s=self.styles.get(sid)
            if s is None:break
            pp=s.find(W+'pPr')
            if pp is not None:chain.append(pp)
            base=s.find(W+'basedOn'); sid=base.get(W+'val') if base is not None else None
        num=None; ilvl=None
        for pp in chain:
            np=pp.find(W+'numPr')
            if np is None:continue
            nv=np.find(W+'numId'); lv=np.find(W+'ilvl')
            if num is None and nv is not None:num=nv.get(W+'val')
            if ilvl is None and lv is not None:ilvl=int(lv.get(W+'val'))
        return self.label(num,ilvl or 0) if num is not None else None


def flatten(blocks):
    for b in blocks:
        if b['type']=='paragraph':yield b
        else:
            for row in b['rows']:
                for c in row:yield from flatten(c['blocks'])


def source_entries(folder):
    manifest=read(folder/'manifest.json')
    assert digest(folder/'source.docx')==manifest['source_sha256'],folder
    doc=read(folder/'extracted.json'); blocks=doc['blocks']; ps=list(flatten(blocks))
    with zipfile.ZipFile(folder/'source.docx') as z:
        root=ET.fromstring(z.read('word/document.xml'))
        numbering=WordNumbering(ET.fromstring(z.read('word/numbering.xml')),
            {s.get(W+'styleId'):s for s in ET.fromstring(z.read('word/styles.xml')).findall(W+'style')})
        native=list(root.iter(W+'p'))
        assert len(ps)==len(native),(folder,len(ps),len(native))
        rels={n.get('Id'):n.get('Target') for n in ET.fromstring(z.read('word/_rels/document.xml.rels'))}
        for p,n in zip(ps,native):
            p['native_label']=numbering.paragraph_label(n)
            p['images']=[dict(relationship_id=x.get(R+'embed'),target=rels.get(x.get(R+'embed')))
                         for x in n.iter(A+'blip')]
    counts=Counter(); result=[]
    for q in read(folder/'question-index.json')['questions']:
        key=(q['source_indicator'],q['source_level'],q['source_question_number']);counts[key]+=1
        span=blocks[q['body_block_start_index']:q['body_block_end_exclusive']]
        for fragment,paragraphs in split_revisions(list(flatten(span))):
            result.append(dict(group=folder.name.split('indikator-')[-1],indicator=key[0],level=key[1],source_number=key[2],
                occurrence=q.get('source_occurrence',counts[key]),fragment=fragment,
                audit_id=f"{manifest['source_sha256'][:12]}:I{key[0]}:L{key[1]}:Q{key[2]}:O{counts[key]}:{fragment}",
                source=dict(path=(folder/'source.docx').relative_to(ROOT).as_posix(),sha256=manifest['source_sha256'],
                    paragraph_start=paragraphs[0]['paragraph_index'],paragraph_end=paragraphs[-1]['paragraph_index'],
                    body_block_start=q['body_block_start_index'],body_block_end_exclusive=q['body_block_end_exclusive']),
                source_heading=q['source_heading'],paragraphs=paragraphs,
                tables=[b for b in span if b['type']=='table'],
                **parse_components(paragraphs,span,q['source_heading'])))
    return result


def parse_components(ps,blocks,heading):
    lines=[dict(p,text=t,native_label=p.get('native_label') if j==0 else None)
           for p in ps for j,t in enumerate(p['text'].splitlines()) if t.strip()]
    keylines=[]; collecting=False
    for p in lines:
        t=p['text'].strip()
        if re.match(r'^Kunci\s*(?:Jawaban)?\s*:',t,re.I):
            keylines.append(t); collecting=not t.split(':',1)[1].strip()
        elif collecting and re.match(r'^\(?[a-e1-5]\)?[.)]?\s+(?:BENAR|SALAH)\s*$',t,re.I):keylines[-1]+=' '+t
        else: collecting=False
    fmt=('KATEGORI' if re.search(r'Kategori|Benar\s*[/–-]\s*Salah',heading,re.I) else
         'MCMA' if re.search(r'Multiple|MCMA',heading,re.I) else 'PG')
    explanations=[];body=[];tail=[]; mode='body'
    for p in lines:
        t=p['text'].strip()
        if re.match(r'^(?:Pembahasan|Penjelasan)\s*(?::|$)',t,re.I):mode='explanation'
        if re.match(r'^Kesalahan\s+Umum',t,re.I):mode='notes'
        if mode=='explanation':explanations.append(t);continue
        if mode=='notes':tail.append(t);continue
        if re.match(r'^(?:Soal\s+\d+|Revisi\s+Soal|Level\s+Kognitif|Kunci\s*(?:Jawaban)?\s*:)',t,re.I):continue
        if re.match(r'^\(?[a-e1-5]\)?[.)]?\s+(?:BENAR|SALAH)\s*$',t,re.I) and keylines and not keylines[0].split(':',1)[1].strip():continue
        if re.fullmatch(r'(?:Opsi Jawaban|Pernyataan)\s*:',t,re.I):continue
        body.append(p)
    # Explicit inline A.–D. labels occur in a single Word paragraph in ten PGs.
    expanded=[]
    for p in body:
        pieces=re.split(r'(?<=\s)(?=[A-E]\.\s)',p['text']) if re.search(r'\bA\.\s.*\bB\.\s.*\bC\.\s',p['text']) else [p['text']]
        expanded.extend(dict(p,text=t,native_label=p.get('native_label') if j==0 else None) for j,t in enumerate(pieces))
    body=expanded
    options=[];stem=[];started=False; parse_flags=[]
    category_table=None
    for b in blocks:
        if b['type']!='table':continue
        rows=[[ '\n'.join(p['text'] for p in flatten(c['blocks'])).strip() for c in r] for r in b['rows']]
        if rows and any(re.search('Pernyataan',t,re.I) for t in rows[0]) and len(rows[0])>=2:
            category_table=rows;fmt='KATEGORI';break
    table_para=set()
    labels=None
    if category_table:
        labels=[c for c in category_table[0][1:] if c]
        if labels==['Kategori']:labels=['Benar','Salah']
        for r in category_table[1:]:
            text=r[0]
            text=re.sub(r'^\(?[a-zA-E1-9]\)?[.)]?\s+','',text)
            if text:options.append(text)
        for b in blocks:
            if b['type']=='table':table_para.update(p['paragraph_index'] for p in flatten([b]))
    # Some tables omit the word Pernyataan in their first cell. Identify their
    # category header by the paired labels; never interpret a data table as options.
    if not category_table and fmt=='KATEGORI':
        for b in blocks:
            if b['type']!='table':continue
            rows=[['\n'.join(p['text'] for p in flatten(c['blocks'])).strip() for c in r] for r in b['rows']]
            if rows and len(rows[0])>=3 and any(re.fullmatch(r'Benar|Salah|Tepat|Tidak Tepat|Sesuai|Tidak Sesuai',x,re.I) for x in rows[0][1:]):
                category_table=rows;labels=[x for x in rows[0][1:] if x]
                options=[re.sub(r'^\(?[a-z1-9]\)?[.)]?\s+','',r[0]) for r in rows[1:] if r[0].strip()]
                table_para.update(p['paragraph_index'] for p in flatten([b]));break
    native_runs=[];run=[]
    for p in body+[{'text':'','native_label':None}]:
        if re.fullmatch(r'\d+[.)]',p.get('native_label') or ''):run.append(p)
        else:
            if len(run) in (4,5) and [re.sub(r'\D','',x['native_label']) for x in run]==[str(j+1) for j in range(len(run))]:native_runs.extend(x['paragraph_index'] for x in run)
            run=[]
    for p in body:
        t=p['text'].strip()
        if category_table and p['paragraph_index'] in table_para:continue
        m=re.match(r'^(?:\[\s*\]\s*)?([A-E])[.)]\s*(.+)$',t,re.S)
        native=p.get('native_label') or ''
        if re.match(r'^\(Bentuk Soal:',t,re.I):
            if re.search('MCMA|Multiple',t,re.I):fmt='MCMA'
            continue
        statement=re.match(r'^(?:\[\s*\]|☐)?\s*Pernyataan\s*([1-5])\s*[:.)]\s*(.+)$',t,re.I|re.S)
        category_statement=re.match(r'^\(([a-e1-5])\)\s*(.+)$',t,re.S) if fmt=='KATEGORI' and not category_table else None
        if m:
            if not category_table:options.append(m[2].strip());started=True
        elif statement and not category_table:
            options.append(statement[2].strip());started=True;fmt='MCMA'
        elif category_statement:
            options.append(category_statement[2].strip());started=True
        elif re.match(r'^[A-E][.)]$',native):
            options.append(t);started=True
        elif p['paragraph_index'] in native_runs:
            options.append(t);started=True
        elif started and options:
            # Retain continuation; do not silently drop a source sentence.
            options[-1]+='\n'+t
        else:stem.append(t)
    if not options:parse_flags.append('OPTIONS_NOT_STRUCTURALLY_RESOLVED')
    if fmt=='KATEGORI' and labels is None:labels=['Benar','Salah']
    if fmt=='KATEGORI' and not category_table and not options:parse_flags.append('CATEGORY_OPTIONS_NOT_RESOLVED')
    key=None
    if keylines:
        declaration=re.split(':',keylines[0],maxsplit=1)[-1].strip()
        if fmt=='KATEGORI':
            labelpattern='|'.join(re.escape(l) for l in sorted(labels or ['Benar','Salah'],key=len,reverse=True))
            pairs=re.findall(r'\(?([a-e1-9])\)?\s*[:.)-]?\s*('+labelpattern+')',declaration,re.I)
            if pairs and len(pairs)==len(options):
                truth=(labels or ['Benar','Salah'])[0].casefold()
                key=[str(i+1) for i,(_,v) in enumerate(pairs) if v.casefold()==truth]
        else:
            if fmt=='PG':
                m=re.match(r'([A-E])(?:\b|[.)])',declaration)
                if m:key=[m[1]]
            else:
                ks=re.findall(r'\b([A-E])\b',declaration)
                if ks:key=list(dict.fromkeys(ks))
                else:
                    ns=re.findall(r'(?:Pernyataan\s*)?\(?([1-5])\)?',declaration,re.I)
                    if ns:key=[chr(64+int(n)) for n in dict.fromkeys(ns)]
    if key is None and fmt=='KATEGORI' and category_table and category_table[0][-1]=='Kategori':
        values=[r[1] for r in category_table[1:]]
        if len(values)==len(options) and all(v in labels for v in values):key=[str(i+1) for i,v in enumerate(values) if v==labels[0]]
    if key is None:parse_flags.append('DECLARED_KEY_NOT_STRUCTURALLY_RESOLVED')
    return dict(format=fmt,stem='\n'.join(stem),options=options,key=key,declared_key_texts=keylines,
                category_labels=labels if fmt=='KATEGORI' else None,
                explanation='\n'.join(explanations) if explanations else None,
                additional_notes='\n'.join(tail),parse_flags=parse_flags)


def canonical_original(o):
    meta=o.get('metadata',{})
    exp=meta.get('original_explanation') or meta.get('explanation')
    # Common warning notes form a separate component in this audit.
    notes=''
    if exp:
        parts=re.split(r'(?=Kesalahan\s+Umum)',exp,maxsplit=1,flags=re.I)
        exp=parts[0].strip();notes=parts[1].strip() if len(parts)>1 else ''
    return dict(stem=o['stem'],options=[x['text'] for x in o['options']],
                key=[x['id'] for x in o['options'] if x['correct']],
                category_labels=meta.get('category_labels',['Benar','Salah']) if o['format']=='KATEGORI' else None,
                explanation=exp,additional_notes=notes)


def compare(source,target):
    return dict(stem_equal=normalize(source['stem'])==normalize(target['stem']),
        options_equal=[normalize(x) for x in source['options']]==[normalize(x) for x in target['options']],
        key_equal=source['key'] is not None and source['key']==target['key'],
        category_labels_equal=source.get('category_labels')==target.get('category_labels'),
        additional_notes_equal=normalize(source.get('additional_notes',''))==normalize(target.get('additional_notes','')),
        explanation_equal=None if target['explanation'] is None or source['explanation'] is None else normalize(source['explanation'])==normalize(target['explanation']))


def verify_generators(originals):
    from config_store import ConfigStore,validate_config
    from lint import reproduce_original
    from engine import generate,GenerationError
    store=ConfigStore(VG/'configs'); rows={}
    for o in originals:
        qid=o['id']; versions=store.versions(qid)
        row=dict(question_id=qid,original_version=o['version'],original_hash=o['hash'],
                 original_content_sha256=hashlib.sha256(json.dumps(o,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
                 generation_status=o.get('metadata',{}).get('generation_status','ACTIVE'),available_versions=versions)
        if not versions:row['status']='ABSENT'
        else:
            cfg,h=store.load(qid); path=VG/'configs'/qid/f"v{cfg['config_version']}.json"
            row.update(config_version=cfg['config_version'],config_hash=h,config_sha256=digest(path),config_path=path.relative_to(ROOT).as_posix())
            errors=validate_config(cfg,o); reproduction=reproduce_original(o,cfg)
            row.update(validation_errors=errors,reproduction_errors=reproduction[0],reproduction_warnings=reproduction[1],
                       smoke_attempts=[])
            for seed in range(1,11):
                try:
                    a=generate(o,cfg,seed,[]);b=generate(o,cfg,seed,[])
                    deterministic=(a.cand,a.values,a.draws_used)==(b.cand,b.values,b.draws_used)
                    row['smoke_attempts'].append(dict(seed=seed,result='PASS' if deterministic else 'NONDETERMINISTIC',
                        candidate_sha256=hashlib.sha256(json.dumps(a.cand,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),draws=a.draws_used))
                    break
                except GenerationError as e:row['smoke_attempts'].append(dict(seed=seed,result='REJECTED',reason=str(e)))
            row['status']='VERIFIED' if not errors and not reproduction[0] and row['smoke_attempts'][-1]['result']=='PASS' else 'FAILED'
        rows[qid]=row
    return rows


def run():
    from bank import load_workspace_bank
    bank=load_workspace_bank(VG/'data/q0_bank.csv')
    originals=[bank.get(qid) for qid in bank.ids() if bank.get(qid).get('classification',{}).get('activity')=='DRILL']
    entries=[q for folder in sorted((ROOT/'docs/sources/incoming').glob('2026-10-19-indikator-*')) for q in source_entries(folder)]
    write(OUT/'source-structure.json',entries)
    generators=verify_generators(originals);write(OUT/'generator-verification.json',generators)
    print(f'Parsed {len(entries)} review units; generators {dict(Counter(g["status"] for g in generators.values()))}',flush=True)


if __name__=='__main__':run()
