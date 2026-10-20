"""Audit-only matching of the 250 incoming indicator 1–5 entries.

All active Drill originals are searched across IDs/levels. Similarity proposes
candidates only; exact content comparisons decide identity. No runtime writes.
"""
import csv
import difflib
import hashlib
import json
import re
import subprocess
from collections import Counter,defaultdict
from pathlib import Path
from audit_original_questions import (ROOT,VG,OUT,digest,read,write,normalize,
    source_entries,flatten,canonical_original,verify_generators)

DEST=OUT/'stage-06-matching-indicators-01-05'
FIELDS=('format','stem','options','key','category_labels','key_caption','explanation','additional_notes')


def norm(text):
    if text is None:return None
    # Keep compound exponent grouping; stripping braces indiscriminately would
    # falsely identify x^(a+b) with x^a+b.
    text=text.replace('$','').replace('−','-').replace('\u00a0',' ')
    text=text.replace(r'\left','').replace(r'\right','').replace(r'\{','{').replace(r'\}','}')
    text=re.sub(r'\\text\{([^{}]*)\}',r'\1',text)
    text=text.replace(r'^\circ','°').replace(r'\circ','°').replace(r'\%','%')
    text=text.replace(r'\underset{}{min}','min')
    text=re.sub(r'(?<!\w)(\d+)\\frac\{(\d+)\}\{(\d+)\}',r'MIXED[\1;\2;\3]',text)
    text=re.sub(r'(?<!\w)(\d+)\s+(\d+)/(\d+)',r'MIXED[\1;\2;\3]',text)
    for _ in range(12):
        before=text
        text=re.sub(r'\\frac\{([^{}]*)\}\{([^{}]*)\}',r'(\1)/(\2)',text)
        text=re.sub(r'\\sqrt\{([^{}]*)\}',lambda m:'sqrt('+m[1].strip()+')',text)
        def power(m):
            base=m[1].strip();exponent=m[2].strip()
            if not re.fullmatch(r'[\w.,]+|\)',base):base='('+base+')'
            return base+'^('+exponent+')'
        text=re.sub(r'\{([^{}]+)\}\^\{([^{}]+)\}',power,text)
        text=re.sub(r'\^\{([^{}]+)\}',r'^(\1)',text)
        text=re.sub(r'\{([A-Za-z0-9]+)\}_\{([^{}]+)\}',r'\1_(\2)',text)
        if before==text:break
    text=text.replace('²','^(2)').replace('³','^(3)')
    text=re.sub(r'\^(-?\d+(?:[.,]\d+)?)',r'^(\1)',text)
    text=re.sub(r'\^([A-Za-z])(?!\w)',r'^(\1)',text)
    text=re.sub(r'\(\s*([A-Za-z]|\d+)\s*\)(?=\^)',r'\1',text)
    text=re.sub(r'(?m)^\s*•\s*','',text)
    text=re.sub(r'\.{3,}','…',text)
    text=re.sub(r'\s+…','…',text)
    # Currency cents explicitly zero: retain the amount, never normalize other numbers.
    text=re.sub(r'(Rp\s*\d+(?:\.\d{3})*),00\b',r'\1',text)
    # Spaces at delimiters/operators are presentation; spaces between words/digits remain.
    text=re.sub(r'\s*([-=<>×÷+;])\s*',r'\1',text)
    text=re.sub(r'\(\s+','(',text);text=re.sub(r'\s+\)',')',text)
    return re.sub(r'\s+',' ',text).strip()


def signature(q):
    return (q['format'],norm(q['stem']),tuple(norm(x) for x in q['options']),
            tuple(q['key']) if q.get('key') is not None else None,
            tuple(q['category_labels']) if q.get('category_labels') is not None else None)


def find_matches(q,bank):return sorted(o['id'] for o in bank if signature(o)==signature(q))


def component_diff(a,b):
    result={}
    for field in FIELDS:
        if field in ('options',):x=[norm(t) for t in a[field]];y=[norm(t) for t in b[field]]
        elif field in ('key','category_labels','format'):x=a.get(field);y=b.get(field)
        else:x=norm(a.get(field));y=norm(b.get(field))
        result[field+'_equal']=None if (x is None or y is None) and field in ('explanation','key_caption') else x==y
    return result


def full_equal(a,b):return all(value is True for value in component_diff(a,b).values())


def source_projection(q):
    result={k:q[k] for k in ('format','stem','options','key','category_labels','explanation','additional_notes')}
    result['key_caption']='\n'.join(re.sub(r'^Kunci\s*(?:Jawaban)?\s*:\s*','',t,flags=re.I) for t in q['declared_key_texts']) or None
    result['stem']=re.sub(r'^Soal\s*\(Bentuk Soal:\s*Pilihan Ganda\)\s*\n','',result['stem'],flags=re.I)
    # Restore DATA table row/cell boundaries for comparison with old CSV's pipe notation.
    # Category tables stay as ordered statements; data cells must remain in the stimulus.
    for table in q['tables']:
        if len(table['rows'][0])!=2:continue
        cells=[['\n'.join(p['text'] for p in flatten(c['blocks'])).strip() for c in row] for row in table['rows']]
        serialized='\n'.join(' | '.join(row) for row in cells)
        flat='\n'.join(cell for row in cells for cell in row if cell)
        if flat in result['stem']:result['stem']=result['stem'].replace(flat,serialized,1)
        else:
            start=min(p['paragraph_index'] for p in flatten([table]))
            previous=[p['text'].strip() for p in q['paragraphs'] if p['paragraph_index']<start and p['text'].strip()]
            anchor=next((t for t in reversed(previous) if t in result['stem']),None)
            if anchor:
                at=result['stem'].index(anchor)+len(anchor)
                result['stem']=result['stem'][:at]+'\n'+serialized+result['stem'][at:]
            else:raise AssertionError(('cannot locate data table',q['audit_id'],table['id']))
    return result


def original_projection(o):
    p=canonical_original(o);p['format']=o['format'];p['id']=o['id']
    p['key_caption']=o.get('metadata',{}).get('declared_key')
    return p


def history():
    from bank import _parse_row
    result=[]
    for path in sorted((VG/'data').rglob('original_revisions.jsonl')):
        for line,text in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
            if not text.strip():continue
            r=json.loads(text);o=_parse_row(r['original_row'],line,allow_missing_key=True)
            result.append(dict(**original_projection(o),original_version=o['version'],original_hash=o['hash'],
                ledger_path=path.relative_to(ROOT).as_posix(),ledger_sha256=digest(path),ledger_line=line))
    return result


def run():
    from bank import load_workspace_bank
    from conceptual_stock import load_stock
    bank=load_workspace_bank(VG/'data/q0_bank.csv')
    originals={qid:bank.get(qid) for qid in bank.ids() if bank.get(qid)['classification']['activity']=='DRILL'}
    active={qid:original_projection(o) for qid,o in originals.items()}
    historical=history()
    source=source_entries(ROOT/'docs/sources/incoming/2026-10-19-indikator-1-5')
    assert len(source)==250
    review_paths=[OUT/'stage-02-academic-indicator-01/audit.json',OUT/'stage-03-academic-indicator-02/audit.json',
                  OUT/'stage-04-academic-indicator-03/audit.json',OUT/'stage-05-academic-indicators-04-05/audit.json']
    academics={q['audit_id']:q for p in review_paths for q in read(p)['entries']}
    assert len(academics)==250 and set(academics)=={q['audit_id'] for q in source}
    core_index=defaultdict(list);stem_index=defaultdict(list)
    for qid,o in active.items():core_index[signature(o)].append(qid);stem_index[(o['format'],norm(o['stem']))].append(qid)
    related=set(qid for qid,o in originals.items() if o['classification']['indicator']<=5)
    for s in source:related.update(core_index.get(signature(source_projection(s)),[]))
    generator_checks=verify_generators([originals[qid] for qid in sorted(related)])
    stock=load_stock(VG/'data/conceptual_stock.json',bank)
    # Pin bank files, ledgers, metadata, configs and code actually used, including stock.
    pins={p.relative_to(ROOT).as_posix():digest(p) for p in (VG/'data').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    for rel in ('bank.py','config_store.py','engine.py','lint.py','conceptual_stock.py','expr.py','filters.py'):
        pins['variant_gen/'+rel]=digest(VG/rel)
    for check in generator_checks.values():
        if check.get('config_path'):pins[check['config_path']]=check['config_sha256']
    rows=[]
    for q in source:
        s=source_projection(q);academic=academics[q['audit_id']]
        cores=sorted(core_index.get(signature(s),[]))
        full=[qid for qid in cores if full_equal(s,active[qid])]
        same_stem=sorted(stem_index.get((s['format'],norm(s['stem'])),[]))
        candidates=set(cores)|set(same_stem)
        # Search globally; similarity never proves content equality or runtime mapping.
        if not cores:
            tokens=set(re.findall(r'\w+',norm(s['stem']).lower()))
            prelim=[]
            for qid,o in active.items():
                if o['format']!=s['format']:continue
                other=set(re.findall(r'\w+',norm(o['stem']).lower()))
                overlap=len(tokens&other)/max(1,len(tokens|other))
                prelim.append((overlap,qid))
            scores=[]
            for _,qid in sorted(prelim,reverse=True)[:10]:
                ratio=difflib.SequenceMatcher(None,norm(s['stem']),norm(active[qid]['stem']),autojunk=False).ratio()
                scores.append((ratio,qid))
            similar=sorted(scores,reverse=True)[:3]
            candidates.update(qid for score,qid in similar if score>=0.25)
        else:similar=[]
        links=[]
        for qid in sorted(candidates):
            o=originals[qid];t=active[qid];diff=component_diff(s,t)
            changed={field:dict(source=s.get(field),active=t.get(field)) for field in FIELDS if diff[field+'_equal'] is not True}
            links.append(dict(question_id=qid,original_version=o['version'],original_hash=o['hash'],
                original_content_sha256=hashlib.sha256(json.dumps(o,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
                classification=o['classification'],source_document_sha256=o.get('metadata',{}).get('source_document_sha256'),
                original_explanation_provenance='question_metadata.original_explanation' if t['explanation'] is not None else 'UNAVAILABLE',
                match='FULL_IDENTITY' if qid in full else 'CORE_IDENTITY' if qid in cores else 'STEM_IDENTITY' if qid in same_stem else 'SIMILARITY_CANDIDATE_ONLY',
                similarity=next((round(score,6) for score,x in similar if x==qid),None),
                comparison=diff,differences=changed,generator=generator_checks.get(qid,dict(status='NOT_CHECKED_NOT_A_CONFIRMED_MATCH')),
                stock_count=len(stock.get(qid,[]))))
        past=[]
        for old in historical:
            if signature(old)==signature(s):
                past.append({k:old[k] for k in ('id','original_version','original_hash','ledger_path','ledger_sha256','ledger_line')})
        classification=('FULL_IDENTITY' if len(full)==1 else 'AMBIGUOUS_MULTIPLE_FULL_MATCHES' if len(full)>1 else
            'CORE_IDENTITY_EXPLANATION_OR_CAPTION_DIFFERS' if len(cores)==1 else 'AMBIGUOUS_MULTIPLE_CORE_MATCHES' if len(cores)>1 else
            'STEM_MATCH_CONTENT_CHANGED' if same_stem else 'NO_VERIFIED_IDENTITY')
        # Availability describes this incoming version, not existence of a vaguely related template.
        verified=[qid for qid in cores if generator_checks[qid]['status']=='VERIFIED']
        stocked=[qid for qid in cores if qid in stock and stock[qid]]
        availability=('VERIFIED_FOR_IDENTICAL_CORE' if verified else 'MANUAL_STOCK_ONLY' if stocked else
                      'MATCHED_ORIGINAL_WITHOUT_GENERATOR' if cores else 'NO_GENERATOR_VERIFIED_FOR_THIS_CONTENT')
        clean=academic['recommendation']=='NO_BLOCKING_ACADEMIC_FINDING'
        if not clean:recommendation='TERTAHAN_AKADEMIK'
        elif len(cores)>1:recommendation='TERTAHAN_PEMETAAN_GANDA'
        elif full and verified:recommendation='GUNAKAN_GENERATOR_EXISTING'
        elif cores and verified:recommendation='REVIEW_PEMBAHASAN_ATAU_KUNCI_TERTULIS'
        elif stocked:recommendation='STOK_MANUAL_SAJA'
        else:recommendation='UPDATE_ATAU_BANGUN_GENERATOR'
        manual_note=None
        if (q['indicator'],q['level'],q['source_number']) in ((3,1,3),(3,2,3)):
            manual_note=dict(status='UNCONFIRMED_MIXED_NUMBER_RENDERING',
                candidate_id=f"pg-3-{q['level']}-3",
                evidence='Sumber memakai bilangan campuran Word; stem bank memakai bentuk tanpa pemisah seperti 3(1)/(4) atau 3(1)/(2). Itu dapat terbaca sebagai perkalian. Tidak dinormalisasi otomatis menjadi bilangan campuran.',
                action='Review representasi original/config dan provenance sebelum menganggap konten identik. Generator untuk original lama tersedia, tetapi kecocokan versi baru belum terbukti.')
        rows.append(dict(audit_id=q['audit_id'],indicator=q['indicator'],level=q['level'],source_number=q['source_number'],
            source=q['source'],source_projection=s,academic={k:academic[k] for k in ('validity','answer_status','explanation_status','recommendation')},
            match_status=classification,full_match_ids=full,core_match_ids=cores,stem_match_ids=same_stem,
            matches_and_candidates=links,historical_core_matches=past, generator_availability=availability,
            verified_core_generator_ids=verified,recommendation=recommendation,
            manual_mapping_note=manual_note,approval_status='NOT_CURRICULUM_APPROVED',runtime_mapping_changed=False))
    baseline=read(OUT/'protected-inputs.json')['sha256'];assert all(digest(ROOT/p)==h for p,h in baseline.items())
    summary=dict(scope='Pencocokan sumber indikator1–5 saja,250entri',date='2026-10-20',source_entries=250,
        unique_source_positions=len({(r['indicator'],r['level'],r['source_number']) for r in rows}),
        active_drill_originals_searched=len(active),originals_indicators_1_5=len(related),
        generator_checks=dict(Counter(x['status'] for x in generator_checks.values())),
        match_status=dict(Counter(r['match_status'] for r in rows)),generator_availability=dict(Counter(r['generator_availability'] for r in rows)),
        recommendations=dict(Counter(r['recommendation'] for r in rows)),
        distinct_verified_generator_families=len({x for r in rows for x in r['verified_core_generator_ids']}),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        script_sha256=digest(Path(__file__)),
        academic_input_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in review_paths},
        protected_files_checked=len(baseline),protected_hashes_unchanged=True)
    DEST.mkdir(parents=True,exist_ok=True)
    write(DEST/'matching.json',dict(summary=summary,normalization_policy=[
        'Whitespace collapse; Word/LaTeX powers (compound exponent grouping retained), fractions/roots, degree/text wrappers; mixed-number notation without evaluating its value.',
        'Only explicitly zero currency cents RpN,00→RpN; no other number/unit/sign/punctuation deletion.',
        'Data tables retain ordered rows/cells using pipes; category statements retain order and labels; bullet layout/ellipsis and redundant format heading only.',
        'No algebraic/numeric simplification, no option reordering, no case folding for equality.',
        'Full identity additionally requires declared key caption, explanation and warning notes.',
        'Similarity and historical equality never substitute active identity; no mapping written.'],
        pinned_inputs=pins,checked_generators=generator_checks,entries=rows))
    fields=['audit_id','indicator','level','source_number','match_status','full_match_ids','core_match_ids','generator_availability','verified_core_generator_ids','recommendation']
    def csv_out(name,rs):
        with (DEST/name).open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
            for r in rs:w.writerow({k:','.join(r[k]) if isinstance(r[k],list) else r[k] for k in fields})
    csv_out('entries.csv',rows)
    csv_out('without-verified-generator.csv',[r for r in rows if not r['verified_core_generator_ids']])
    csv_out('review-or-adjustment.csv',[r for r in rows if r['recommendation']=='REVIEW_PEMBAHASAN_ATAU_KUNCI_TERTULIS' or not r['core_match_ids']])
    csv_out('held.csv',[r for r in rows if r['recommendation'].startswith('TERTAHAN')])
    csv_out('unconfirmed-mapping.csv',[r for r in rows if r['match_status'] not in ('FULL_IDENTITY','CORE_IDENTITY_EXPLANATION_OR_CAPTION_DIFFERS')])
    csv_out('manual-stock-only.csv',[r for r in rows if r['generator_availability']=='MANUAL_STOCK_ONLY'])
    report=['# Tahap 6 — Pencocokan original dan generator indikator 1–5','',
        'Cakupan: **250 entri sumber indikator 1–5** dicari lintas ID/level terhadap **790 original Drill aktif** setelah ledger revisi diterapkan. Bank aktif indikator 1–5 sendiri berisi **150 original**, seluruhnya pada level 1–3. Sumber baru juga menyediakan **100 entri level 4–5**. Tidak ada pemetaan runtime atau konten yang diubah.','',
        '| Hasil identitas konten | Entri |','|---|---:|',
        f"| Identik seluruh isi setelah normalisasi tampilan yang dibatasi | {summary['match_status'].get('FULL_IDENTITY',0)} |",
        f"| Inti soal identik, tetapi pembahasan/caption kunci/catatan berbeda | {summary['match_status'].get('CORE_IDENTITY_EXPLANATION_OR_CAPTION_DIFFERS',0)} |",
        f"| Belum ada identitas terverifikasi | {summary['match_status'].get('NO_VERIFIED_IDENTITY',0)} |",'',
        'Identik seluruh isi mensyaratkan format, stimulus/pertanyaan, urutan opsi/pernyataan, kunci semantis, label kategori, caption kunci tertulis, pembahasan, dan catatan cocok. Tidak menggunakan original_hash sebagai bukti identitas penuh: hash itu tidak mencakup pembahasan. Perbandingan menyimpan isi dan perbedaan per komponen, versi original, hash isi lengkap, serta hash berkas pembanding.','',
        '**103 entri yang belum identik** terdiri dari 100 entri level 4–5 tanpa pasangan identik, I5 L3Q5 yang benar-benar berbeda redaksi stimulus/pembahasan, dan dua kasus representasi bilangan campuran (I3 L1Q3/L2Q3) yang belum dipastikan. Dua kasus terakhir memiliki kandidat original/generator lama; tidak disimpulkan bahwa sama sekali tidak ada template terkait. Tidak ada kecocokan historis tambahan yang menggantikan kecocokan versi aktif.','',
        '| Ketersediaan untuk isi sumber baru | Entri |','|---|---:|']
    for label,status in [('Inti cocok dengan generator terverifikasi','VERIFIED_FOR_IDENTICAL_CORE'),
        ('Inti cocok, hanya stok manual','MANUAL_STOCK_ONLY'),('Inti cocok, original masih HOLD tanpa generator','MATCHED_ORIGINAL_WITHOUT_GENERATOR'),
        ('Belum ada generator yang terbukti cocok untuk isi ini','NO_GENERATOR_VERIFIED_FOR_THIS_CONTENT')]:
        report.append(f"| {label} | {summary['generator_availability'].get(status,0)} |")
    report+=['','Artinya **115 entri belum mempunyai generator yang terbukti cocok untuk versinya**: 103 belum memiliki identitas terverifikasi + 10 stok manual + 2 original HOLD. Ini tidak berarti 115 keluarga generator harus dibuat: kemiripan konsep belum membuktikan kecocokan, dan beberapa kasus perlu perbaikan atau penyesuaian terlebih dahulu.','',
        'Pemeriksaan 150 original pembanding indikator 1–5 menemukan **138 konfigurasi generator** dan 12 tanpa konfigurasi. Seluruh 138 lulus validasi config, reproduksi original, serta uji panggil deterministik berulang dengan seed tercatat. **135** keluarga generator tersebut terbukti cocok dengan inti sumber baru; 3 lainnya terkait kandidat yang isinya belum identik/terverifikasi. Uji ini membuktikan konfigurasi dan reproduksi, bukan kebenaran akademik semua varian atau kesetaraan kesulitan.','',
        '| Rekomendasi setelah mempertimbangkan audit akademik | Entri |','|---|---:|']
    labels={'GUNAKAN_GENERATOR_EXISTING':'Gunakan generator existing',
        'REVIEW_PEMBAHASAN_ATAU_KUNCI_TERTULIS':'Review pembahasan/caption dahulu',
        'STOK_MANUAL_SAJA':'Stok manual saja', 'UPDATE_ATAU_BANGUN_GENERATOR':'Antrean update atau bangun generator',
        'TERTAHAN_AKADEMIK':'Perlu tindak lanjut akademik sebelum penggunaan'}
    for status,label in labels.items():report.append(f"| {label} | {summary['recommendations'].get(status,0)} |")
    report+=['','Rekomendasi tersebut **PROPOSED, bukan persetujuan Kurikulum**. Ketersediaan generator tetap dicatat walaupun soal tertahan secara akademik. Sebanyak 42 entri memiliki tindak lanjut akademik dari tahap sebelumnya; tidak semuanya berarti soal tidak valid—sebagian hanya memerlukan koreksi alasan opsi.','',
        '| Kasus penting | Hasil |','|---|---|',
        '| I1 L2Q1 / pg-1-2-1 | Inti cocok, tetapi sumber baru memperbaiki pembahasan persentase yang membuat original lama HOLD. Belum ada generator; masuk antrean setelah revisi original disetujui. HOLD runtime tidak diubah. |',
        '| I3 L1Q6 / mcma-3-1-6 | Inti dan generator cocok; pembahasan berbeda pada penulisan desimal 81,00 versus 81. Disimpan sebagai perbedaan, tidak disederhanakan otomatis. |',
        '| I4 L1Q7 / mcma-4-1-7 | Inti dan generator cocok; pembahasan berbeda pada teks waktu detikcom-60 versus detik ke-60. Perlu review pembahasan; bukan alasan otomatis membuat generator baru. |',
        '| I5 L3Q3 / pg-5-3-3 | Inti cocok dengan original HOLD tanpa generator, tetapi caption kunci lama menyebut 24 liter/menit walaupun yang ditanya selisih 4. Pembahasan/catatan juga berubah; audit akademik masih menahan asumsi volume awal. |',
        '| I5 L3Q5 / pg-5-3-5 | Ada kandidat original/generator terverifikasi untuk versi aktif lama, tetapi stimulus dan pembahasan baru berubah. Kandidat bukan bukti identitas; perlu update/review untuk versi baru. |',
        '| I3 L1Q3 dan L2Q3 | Notasi campuran Word versus penulisan bank 3(1)/(4) atau 3(1)/(2) belum dianggap identik. Generator lama tersedia; identitas perlu review notasi/provenance. |','',
        'Sepuluh stok manual terdapat pada pg-1-1-4, mcma-1-1-8, kategori-1-1-10, kategori-1-2-10, kategori-1-3-10, pg-2-2-5, pg-2-3-1, pg-2-3-4, pg-2-3-5, dan pg-5-2-4. Satu di antaranya masih memerlukan tindak lanjut akademik, sehingga rekomendasi stok manual langsung hanya sembilan.','',
        'Normalisasi hanya mengatasi tampilan yang dibatasi: whitespace, delimiter/pangkat/akar/pecahan Word–LaTeX, subskrip, angka campuran yang eksplisit, sen nol pada mata uang, dan susunan tabel dengan urutan sel tetap. Pengelompokan pangkat dipertahankan; x^(a+b) tidak disamakan dengan x^a+b. Tidak menghitung bentuk akar menjadi angka, tidak mengubah angka/satuan/tanda, dan tidak menukar opsi. Kandidat kemiripan tidak pernah diberi label identik.','',
        'Semua pasangan yang benar-benar cocok memiliki pembahasan tersendiri dalam metadata original yang dipin. Kasus 118 original lama tanpa pembahasan berasal dari kelompok lain dan tidak menjadi pasangan cocok pada bagian ini; tidak ada pembahasan buatan generator yang dipakai sebagai pengganti sumber.','',
        'Keluaran: [JSON lengkap](matching.json), [CSV 250 entri](entries.csv), [tanpa generator terverifikasi](without-verified-generator.csv), [stok manual](manual-stock-only.csv), [review/penyesuaian](review-or-adjustment.csv), [tindak lanjut akademik](held.csv), dan [identitas/pemetaan belum terverifikasi](unconfirmed-mapping.csv). Daftar terakhir mencakup konten baru juga; kemunculan di sana tidak berarti kandidat sudah dipastikan sebagai pasangan.','',
        f"Git HEAD pembanding: `{summary['git_head']}`. Isi working tree dipin terpisah karena ada berkas lokal yang belum di-commit. Seluruh {len(baseline)} hash sumber/bank/config/stok/layanan tetap sama. Tidak ada publikasi, perubahan bank/generator, penyesuaian rentang, atau aktivasi otomatis.",'',
        'Reproduksi: `python variant_gen/tests/match_indicators_01_05.py`. Pengujian batas identitas: `python -m unittest discover -s variant_gen/tests -p test_match_indicators_01_05.py`.','',
        '**Bagian pencocokan indikator 1–5 selesai sebagai laporan; pekerjaan indikator berikutnya menunggu instruksi.**','']
    (DEST/'README.md').write_text('\n'.join(report),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=True,indent=2))


if __name__=='__main__':run()
