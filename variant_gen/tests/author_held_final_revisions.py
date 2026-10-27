"""Offline authoring for the 16 audited curriculum revisions; no database access."""
import copy
import hashlib
import importlib.util
import json
import re
from pathlib import Path

from build_drill_1_5_level45_batch1 import Author, ROOT, REPO
from bank import OriginalBank, load_workspace_bank
from test_held_final_revisions import KEYS

SOURCE=REPO/'docs/sources/incoming/2026-10-22-held-revisions'
AUDIT=REPO/'docs/audits/2026-10-22-held-final-revisions'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'


def render(node):
    if node.nodeType == node.TEXT_NODE: return node.data
    tag=node.localName
    if tag and tag.endswith('Pr'): return ''
    if tag=='f':
        parts={n.localName:render(n) for n in node.childNodes if n.nodeType==n.ELEMENT_NODE}
        return '('+parts['num']+')/('+parts['den']+')'
    if tag=='br': return '\n'
    return ''.join(render(c) for c in node.childNodes)


def projections():
    spec=importlib.util.spec_from_file_location('held_extract',SOURCE/'extract.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    manifest=json.loads((SOURCE/'manifest.json').read_text(encoding='utf8'))
    result={}
    for file in manifest['files']:
        _,body=module.document(SOURCE/file['extracted']);chunks=[]
        for node in body.childNodes:
            if node.nodeType!=node.ELEMENT_NODE or node.localName=='sectPr': continue
            if re.match(r'^soal\s*\d+\b',render(node).strip(),re.I): chunks.append([])
            assert chunks
            chunks[-1].append(node)
        assert len(chunks)==len(file['questions'])
        for item,nodes in zip(file['questions'],chunks):
            q=item['id'];fmt=q.split('-')[0].upper();stem=[];options=[];explanation=[];raw=[];exp=False
            for node in nodes[1:]:
                value=render(node).strip()
                if not value: continue
                raw.append(value)
                if re.match(r'^pembahasan\b',value,re.I): exp=True
                if exp: explanation.append(value);continue
                if node.localName=='tbl':
                    for row in node.getElementsByTagNameNS(W,'tr')[1:]:
                        cells=row.getElementsByTagNameNS(W,'tc')
                        options.append(re.sub(r'^[A-E]\.\s*','',render(cells[0]).strip()))
                    continue
                if re.match(r'^(?:level kognitif|kunci jawaban)\s*:',value,re.I) or value.lower()=='soal':continue
                option=re.match(r'^(?:\[\s*\]\s*)?([A-E])\.\s*(.*)',value,re.S)
                if option: options.append(option[2]);continue
                if not options: stem.append(value)
            assert len(options) in (4,5),(q,options)
            result[q]=dict(format=fmt,stem='\n'.join(stem),options=options,key=list(KEYS[q]),
                           explanation='\n'.join(explanation),raw='\n'.join(raw),
                           source=file['extracted'],source_sha256=hashlib.sha256((SOURCE/file['extracted']).read_bytes()).hexdigest(),
                           original_document_sha256=file['source_sha256'])
    assert set(result)==set(KEYS)
    return result


def correction(q,p):
    p=copy.deepcopy(p);notes=[]
    if q=='kategori-21-4-9':
        notes.append('Kunci B Benar: median25. Pembahasan yang menyebut B Salah diganti sesuai hitungan.')
        p['explanation']='Rerata=140/5=28; median=25; modus=25; jangkauan=40-20=20. Semua pernyataan benar.'
    elif q=='kategori-21-4-10':
        notes.append('Kunci awal A,B Tepat dikoreksi menjadi Tidak tepat; hanya D Tepat.')
        p['explanation']='Rerata A=B=3; median A=2 dan B=3; jangkauan A=6 dan B=2. Hanya D tepat.'
    elif q=='pg-22-4-3':
        notes.append('Opsi C: lebih tinggi diganti lebih rendah; hanya D benar. Disetujui pengguna22 Oktober2026.')
        p['options'][2]=p['options'][2].replace('lebih tinggi','lebih rendah')
    elif q=='mcma-23-4-7':
        notes.append('Pembulatan B dinyatakan eksplisit: sekitar0,4667; angka eksak28/60.')
        p['options'][1]=p['options'][1].replace('adalah 0,4667','adalah sekitar 0,4667')
    elif q=='pg-23-5-3':
        notes.append('Dua lemparan koin ditegaskan independen, sesuai ruang sampel pada pembahasan.')
        p['stem']=p['stem'].replace('dilempar dua kali','dilempar dua kali secara independen')
    elif q=='mcma-23-5-8':
        notes.append('Pengambilan acak ditegaskan seragam: setiap bola memiliki peluang terambil sama.')
        p['stem']=p['stem'].replace('secara acak,','secara acak (setiap bola memiliki peluang terambil yang sama),')
    return p,notes


def author(q,p,o):
    _,i,l,n=q.split('-');a=Author(dict(indicator=int(i),level=int(l),source_number=int(n),source_projection=p))
    def exp(s):a.exp=a.explanation(s)
    def ratio(num,den,literal):
        return a.var(num,literal)+a.var("'/'",'')+a.var(den,'')
    if q=='pg-1-2-1':
        # ponytail: 30 audited positive scales; extend after reviewing loss bounds.
        a.stem=a.stem.replace('-(3)/(5)', '-'+a.var('60+k','(3)/(5)')+a.var("'%'",''))
        a.stem=a.stem.replace('-0,55','-'+a.var('55+k','0,55')+a.var("'%'",''))
        a.stem=a.stem.replace('58%',a.var('58+k','58')+'%')
        a.stem=a.stem.replace('-0,62','-'+a.var('62+k','0,62')+a.var("'%'",''))
        exp('Kerugian dalam persen: Pak Dimas[[60+k]], Kelompok1[[55+k]], Kelompok2[[58+k]], Kelompok3[[62+k]]. Nilai bertanda negatif terkecil adalah milik Kelompok3; D benar.')
    elif q=='pg-5-3-3':
        a.stem=a.nums(a.stem,{'300':'300*(k+1)','480':'480*(k+1)'})
        a.options=[a.nums(t,{str(x):f'{x}*(k+1)' for x in (2,4,6,8)}) for t in a.options]
        exp('Debit P=[[20*(k+1)]] liter/menit; Q=[[24*(k+1)]] liter/menit. Selisih=[[4*(k+1)]] liter/menit. Hanya B benar.')
    elif q=='mcma-6-3-7':
        a.stem=a.nums(a.stem,{'6':'6*(k+1)','4':'4*(k+1)'})
        a.options[1]=a.nums(a.options[1],{'10':'10*(k+1)'})
        a.options[2]=a.options[2].replace('2 anggota',a.var('2*(k+1)','2')+' anggota')
        exp('Persediaan awal masing-masing=[[60*(k+1)]] porsi. Gabungan=[[120*(k+1)]] porsi untuk[[10*(k+1)]] siswa:12hari. Setelah2hari, sisa=[[48*(k+1)]] porsi untuk[[8*(k+1)]] siswa:6hari. A,B,C benar; D salah karena porsi harian sama.')
    elif int(i) in (21,22):
        mapping={m[0]:f"({m[0].replace(',','.')})*(k+1)" for text in [a.stem,*a.options]
                 for m in re.finditer(r'(?<!\w)\d+(?:,\d+)?',text)}
        a.allnums(mapping)
        explanations={
            'kategori-21-4-9':'Rerata=[[28*(k+1)]], median dan modus=[[25*(k+1)]], jangkauan=[[20*(k+1)]]. Semua benar.',
            'kategori-21-4-10':'Rerata kedua kelompok=[[3*(k+1)]]. Median A=[[2*(k+1)]], B=[[3*(k+1)]]. Jangkauan A=[[6*(k+1)]], B=[[2*(k+1)]]. Hanya D tepat.',
            'mcma-21-5-6':'Median=[[75*(k+1)]], rerata=[[80*(k+1)]], jangkauan=[[45*(k+1)]]. Nilai ekstrem[[110*(k+1)]] memengaruhi rerata; tidak ada modus. A,B,C,D benar.',
            'mcma-21-5-7':'Rerata dan median kedua kelompok=[[80*(k+1)]]. Modus A=[[70*(k+1)]] dan[[80*(k+1)]]. Kedua jangkauan=[[30*(k+1)]]. A,B,E benar.',
            'pg-22-4-3':'Rerata A=B=[[4*(k+1)]]. Median A=[[3*(k+1)]], B=[[4*(k+1)]]. Jangkauan A=[[6*(k+1)]], B=[[3*(k+1)]]. Hanya D benar.',
            'mcma-22-4-7':'Rerata dan median kedua kelompok=[[5*(k+1)]]. Jangkauan P=0, Q=[[4*(k+1)]]. Semua nilai Q berbeda; tidak ada modus. A,B,D benar.',
            'kategori-22-4-9':'Median dan rerata kedua kelompok=[[20*(k+1)]]. Jangkauan A=[[20*(k+1)]], B=[[10*(k+1)]]. Tidak ada modus. Pernyataan1,3 benar.'}
        exp(explanations[q])
    elif q=='pg-23-4-5':
        a.stem=a.nums(a.stem,{'40':'40*(k+1)','26':'26*(k+1)'})
        exp('Frekuensi relatif=26/40=0,65. Koin seimbang memberi peluang teoretis1/2=0,5, sehingga C benar. Jumlah lemparan=[[40*(k+1)]].')
    elif q=='mcma-23-4-7':
        a.stem=a.nums(a.stem,{'60':'60*(k+1)','32':'32*(k+1)','28':'28*(k+1)'})
        a.options[0]='Frekuensi relatif sisi angka adalah '+ratio('32*(k+1)','60*(k+1)','0,53\u0305')+'.'
        a.options[1]='Frekuensi relatif sisi gambar adalah '+ratio('28*(k+1)','60*(k+1)','sekitar 0,4667 atau sekitar 0,47')+'.'
        a.options[3]=a.options[3].replace('32/60',ratio('32*(k+1)','60*(k+1)','32/60'))
        exp('Frekuensi angka=[[32*(k+1)]]/[[60*(k+1)]]=8/15; gambar=[[28*(k+1)]]/[[60*(k+1)]]=7/15. Jumlah=1. Peluang teoretis koin seimbang1/2. A,B,C benar; D,E salah.')
    elif q=='pg-23-5-3':
        a.variables['k']['range']=[0,8]
        a.stem=a.stem.replace('dua kali',a.var('2+k','dua')+' kali')
        # Exactly one picture among n independent tosses: n/2**n.
        a.options=[ratio('1','2**(2+k)','1/4'),ratio('1','2**(2+k)-1','1/3'),
                   ratio('2+k','2**(2+k)','1/2'),ratio('2**(2+k)-1','2**(2+k)','3/4'),'1']
        exp('Ada[[2**(2+k)]] hasil sama mungkin dari[[2+k]] lemparan independen koin seimbang. Tepat satu gambar dapat berada pada[[2+k]] posisi. Peluang=[[2+k]]/[[2**(2+k)]]. Hanya C benar.')
    elif q=='pg-23-5-4':
        a.stem=a.nums(a.stem,{'300':'300*(k+1)','162':'162*(k+1)'})
        exp('Frekuensi relatif=162/300=0,54. Pada dadu seimbang, ada3angka genap dari6sisi; peluang teoretis=1/2=0,5. C benar. Jumlah lemparan=[[300*(k+1)]].')
    elif q=='mcma-23-5-7':
        a.stem=a.nums(a.stem,{'80':'80*(k+1)','46':'46*(k+1)','34':'34*(k+1)'})
        exp('Frekuensi gambar=46/80=0,575; angka=34/80=0,425; jumlah=1. Peluang teoretis koin seimbang=0,5, bukan frekuensi empiris. A,B,C benar. Jumlah lemparan=[[80*(k+1)]].')
    elif q=='mcma-23-5-8':
        a.stem=a.nums(a.stem,{'4':'4*(k+1)','6':'6*(k+1)','100':'100*(k+1)','38':'38*(k+1)'})
        exp('Pengambilan acak seragam dengan pengembalian: P(merah)=4/10=0,4. Frekuensi relatif merah=38/100=0,38; biru=62/100=0,62. Frekuensi tidak membuktikan peluang teoretis atau menjamin hasil berikutnya. A,B,C benar. Total bola=[[10*(k+1)]].')
    else: raise AssertionError(q)
    # The shared validator requires changed answer content, not only new data.
    details={
        'pg-1-2-1':(3,'62+k','% kerugian'),
        'kategori-21-4-10':(3,'6*(k+1)',' jam, jangkauan A'),
        'pg-22-4-3':(3,'4*(k+1)',' buku, rerata kedua kelompok'),
        'mcma-22-4-7':(0,'5*(k+1)',' poin, rerata kedua kelompok'),
        'kategori-22-4-9':(0,'20*(k+1)',' median kedua kelompok'),
        'pg-23-4-5':(2,'40*(k+1)',' kali percobaan'),
        'pg-23-5-4':(2,'300*(k+1)',' kali percobaan'),
        'mcma-23-5-7':(2,'80*(k+1)',' kali percobaan'),
        'mcma-23-5-8':(0,'10*(k+1)',' bola dalam kantong')}
    if q in details:a.answer_value(*details[q])
    return a.config(o)


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--configs-only',action='store_true')
    args=parser.parse_args()
    from config_store import validate_config
    from lint import reproduce_original
    bank=load_workspace_bank(ROOT/'data/q0_bank.csv');audit=[]
    projections_by_id=projections()
    if not args.configs_only:
        assert not any((ROOT/'configs'/q/'v1.json').exists() for q in KEYS), 'Already applied; use --configs-only'
    locations={q:p for p in (ROOT/'data').rglob('q0_bank.csv')
               for q in OriginalBank(p).ids() if q in KEYS}
    assert len(locations)==16
    for q,source in projections_by_id.items():
        p,notes=correction(q,source);old=bank.get(q);path=locations[q];meta_path=path.with_name('question_metadata.json')
        if args.configs_only:
            cfg=author(q,p,old)
            assert validate_config(cfg,old)==[],q
            assert reproduce_original(old,cfg)==([],[]),q
            (ROOT/'configs'/q/'v1.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
            continue
        metadata=json.loads(meta_path.read_text(encoding='utf8'));oldmeta=metadata[q]
        newmeta=copy.deepcopy(oldmeta)
        newmeta.update(generation_status='ACTIVE',generator_status='IMPLEMENTED',reason='',
                       source_document=(SOURCE/source['source']).relative_to(REPO).as_posix(),source_document_sha256=source['source_sha256'],
                       source_original_document_sha256=source['original_document_sha256'],
                       source_text=source['raw'],original_explanation=p['explanation'],
                       source_review_status='AUDITED_CURRICULUM_REVISION',
                       source_review=dict(date='2026-10-22',issues=[],original_unchanged=False,
                                          local_corrections=notes,audit='docs/audits/2026-10-22-held-final-revisions/README.md'),
                       audit='Audit revisi final dan generator selesai; tanpa perubahan database.',
                       declared_key='; '.join(line for line in source['raw'].splitlines() if re.match(r'^kunci jawaban\s*:',line,re.I)),
                       local_corrections=notes,approval_status='NOT_CURRICULUM_APPROVED',self_adjustment_enabled=False,
                       source_projection={k:p[k] for k in ('format','stem','options','key','explanation')})
        row=lambda o:dict(id=q,format=o['format'],cognitive_level=o['cognitive_level'],stem=o['stem'],
                         options_json=json.dumps([x['text'] for x in o['options']],ensure_ascii=False),
                         key=','.join(x['id'] for x in o['options'] if x['correct']),version=o['version'])
        before=row(old);after=dict(before,stem=p['stem'],options_json=json.dumps(p['options'],ensure_ascii=False),
                                  key=','.join(p['key']),version=old['version']+1)
        revision=dict(question_id=q,original_version=old['version'],original_row=before,
                      replacement_version=after['version'],replacement_row=after,
                      original_metadata=oldmeta,replacement_metadata=newmeta,
                      source_document=source['source'],source_document_sha256=source['source_sha256'],
                      reason='Revisi final kurikulum22 Oktober2026; audit dan koreksi lokal minimum disetujui pengguna.')
        revisions=path.with_name('original_revisions.jsonl')
        with revisions.open('a',encoding='utf8') as stream:stream.write(json.dumps(revision,ensure_ascii=False)+'\n')
        metadata[q]=newmeta;meta_path.write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        original=OriginalBank(path).get(q);cfg=author(q,p,original)
        assert validate_config(cfg,original)==[],q
        assert reproduce_original(original,cfg)==([],[]),(q,reproduce_original(original,cfg))
        dest=ROOT/'configs'/q/'v1.json';assert not dest.exists(),q
        dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        audit.append(dict(question_id=q,status='ACTIVE',key=p['key'],local_corrections=notes,
                          original_version=original['version'],source=source['source'],source_sha256=source['source_sha256']))
        print(q,'ACTIVE',','.join(p['key']))
    if args.configs_only:return
    AUDIT.mkdir(exist_ok=True)
    (AUDIT/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


if __name__=='__main__':main()
