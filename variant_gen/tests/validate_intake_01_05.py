"""Stage 1 only: verify faithful intake structure, without academic/generator audit."""
import csv
import json
import re
import zipfile
from collections import Counter
import xml.etree.ElementTree as ET
from audit_original_questions import ROOT, OUT, W, digest, read, write, flatten, source_entries

M='{http://schemas.openxmlformats.org/officeDocument/2006/math}'
FOLDER=ROOT/'docs/sources/incoming/2026-10-19-indikator-1-5'
DEST=OUT/'stage-01-extraction-01-05'


def tree_signature(node):
    return (node.tag, sorted(node.attrib.items()), node.text or '',
            tuple(tree_signature(c) for c in node))


def native_projection(node, math_map):
    if node.tag==M+'oMath':return '$'+math_map[id(node)]['latex']+'$'
    name=node.tag.rsplit('}',1)[-1]
    if name.endswith('Pr'):return ''
    if node.tag==W+'t':return node.text or ''
    if node.tag==W+'tab':return '\t'
    if node.tag in (W+'br',W+'cr'):return '\n'
    result=''.join(native_projection(c,math_map) for c in node)
    if node.tag==W+'r':
        alignment=node.find(W+'rPr/'+W+'vertAlign')
        if alignment is not None and result:
            result=('^' if alignment.get(W+'val')=='superscript' else '_')+'{'+result+'}'
    return result


def run():
    protected=read(OUT/'protected-inputs.json')['sha256']
    # Freeze current protected assets too, so prior baselines cannot conceal additions.
    before={p.relative_to(ROOT).as_posix():digest(p)
            for folder in ('variant_gen/data','variant_gen/configs','numora_service','docs/sources/incoming')
            for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    manifest=read(FOLDER/'manifest.json');doc=read(FOLDER/'extracted.json')
    index=read(FOLDER/'question-index.json')['questions']
    assert digest(FOLDER/'source.docx')==manifest['source_sha256']
    with zipfile.ZipFile(FOLDER/'source.docx') as z:
        native=ET.fromstring(z.read('word/document.xml'))
        media=[name for name in z.namelist() if name.startswith('word/media/') and not name.endswith('/')]
    equations=list(native.iter(M+'oMath'))
    assert len(equations)==len(doc['equations'])==4019
    for n,e in zip(equations,doc['equations']):
        assert tree_signature(n)==tree_signature(ET.fromstring(e['ooxml'])),e['id']
    math_map={id(n):e for n,e in zip(equations,doc['equations'])}
    paragraphs=list(flatten(doc['blocks']));native_p=list(native.iter(W+'p'))
    assert len(paragraphs)==len(native_p)==10092
    for n,p in zip(native_p,paragraphs):
        assert native_projection(n,math_map)==p['text'],p['paragraph_index']
        assert [math_map[id(m)]['id'] for m in n.iter(M+'oMath')]==p['math_ids']
    def check_blocks(nodes,blocks):
        nodes=[n for n in nodes if n.tag in (W+'p',W+'tbl')]
        assert len(nodes)==len(blocks)
        for n,b in zip(nodes,blocks):
            if n.tag==W+'p':assert b['type']=='paragraph';continue
            assert b['type']=='table'
            rows=n.findall(W+'tr');assert len(rows)==len(b['rows'])
            for nr,br in zip(rows,b['rows']):
                cells=nr.findall(W+'tc');assert len(cells)==len(br)
                for nc,bc in zip(cells,br):
                    span=nc.find(W+'tcPr/'+W+'gridSpan');merge=nc.find(W+'tcPr/'+W+'vMerge')
                    assert bc['col_span']==(int(span.get(W+'val','1')) if span is not None else 1)
                    assert bc['vertical_merge']==(merge.get(W+'val','continue') if merge is not None else None)
                    check_blocks(list(nc),bc['blocks'])
    check_blocks(list(native.find(W+'body')),doc['blocks'])
    assert len(list(native.iter(W+'tbl')))==55 and not media
    entries=source_entries(FOLDER)
    assert len(entries)==len(index)==250
    positions={(q['indicator'],q['level'],q['source_number']) for q in entries}
    assert positions=={(i,l,n) for i in range(1,6) for l in range(1,6) for n in range(1,11)}
    for q in index:
        first=doc['blocks'][q['body_block_start_index']]
        assert first['paragraph_index']==q['paragraph_start_index']
        assert first['text'].strip()==q['source_heading']
    # Do not pick between competing drafts in the source.
    holds={(1,5,2):'Beberapa definisi a dan dua rangkaian evaluasi berada dalam satu entri; batas versi tidak eksplisit.',
           (3,5,7):'Dua rangkaian opsi A–D dan kunci tambahan berada dalam satu entri; tidak dipilih otomatis.'}
    rows=[]
    for q in entries:
        pos=(q['indicator'],q['level'],q['source_number'])
        native_labels=[dict(paragraph=p['paragraph_index'],label=p['native_label'],text=p['text'])
                       for p in q['paragraphs'] if p.get('native_label')]
        review=holds.get(pos)
        assert not q['parse_flags'],(pos,q['parse_flags'])
        if not review:assert len(q['options'])==(3 if q['format']=='KATEGORI' else 4),pos
        assert q['key'] is not None and q['explanation'] is not None,pos
        rows.append(dict(audit_id=q['audit_id'],indicator=q['indicator'],level=q['level'],source_number=q['source_number'],
            source=q['source'],format=q['format'],structural_status='REVIEW_REQUIRED' if review else 'STRUCTURE_VERIFIED',
            caveat=review,stem=q['stem'],options=q['options'],declared_key_texts=q['declared_key_texts'],
            parsed_key=q['key'],explanation=q['explanation'],additional_notes=q['additional_notes'],
            tables=q['tables'],native_numbering=native_labels,
            paragraph_count=len(q['paragraphs']),math_ids=[m for p in q['paragraphs'] for m in p['math_ids']],
            academic_status='NOT_EVALUATED_IN_THIS_STAGE',generator_matching_status='NOT_EVALUATED_IN_THIS_STAGE'))
    after={path:digest(ROOT/path) for path in before}
    assert before==after
    assert all(digest(ROOT/p)==h for p,h in protected.items())
    DEST.mkdir(parents=True,exist_ok=True)
    summary=dict(stage='01',scope='Validasi ekstraksi indikator 1–5 saja',source_sha256=manifest['source_sha256'],
        source_entries=250,unique_positions=250,paragraphs_checked=10092,tables_checked=55,
        question_tables=53,preface_tables=2,omml_equations_checked=4019,embedded_media=0,
        formats=dict(Counter(q['format'] for q in rows)),
        structural_status=dict(Counter(q['structural_status'] for q in rows)),
        native_numbered_paragraphs=sum(bool(p.get('native_label')) for q in entries for p in q['paragraphs']),
        protected_files_checked=len(before),protected_hashes_unchanged=True,
        limitation='Kesetiaan teks dan OMML diperiksa; kebenaran akademik dan bentuk visual persamaan belum disertifikasi.')
    write(DEST/'validation.json',dict(summary=summary,entries=rows))
    with (DEST/'entries.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['audit_id','indicator','level','source_number','format','structural_status','caveat','paragraph_count','option_count','math_count','source_paragraph_start','source_paragraph_end']
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for q in rows:
            writer.writerow({**{k:q[k] for k in fields if k in q},'option_count':len(q['options']),
                'math_count':len(q['math_ids']),'source_paragraph_start':q['source']['paragraph_start'],
                'source_paragraph_end':q['source']['paragraph_end']})
    report=f'''# Tahap 1 — Validasi ekstraksi indikator 1–5

**Cakupan disetujui:** struktur ekstraksi saja. Audit akademik dan pencocokan generator menunggu instruksi terpisah. Artefak audit lain di direktori induk masih hasil sementara, bukan laporan final.

Arsip: `docs/sources/incoming/2026-10-19-indikator-1-5/source.docx`  
SHA-256: `{manifest['source_sha256']}`

| Pemeriksaan | Hasil |
|---|---:|
| Entri / posisi unik | 250 / 250 |
| Cakupan | 5 indikator × 5 level × 10 soal |
| PG / MCMA / Kategori | 125 / 75 / 50 |
| Paragraf dibandingkan dengan XML Word | 10.092 |
| Tabel diperiksa, termasuk span dan merge | 55 (53 dalam soal, 2 pengantar) |
| Persamaan OMML dibandingkan dengan XML arsip | 4.019 |
| Gambar tertanam | 0 |
| Struktur dapat dipisahkan / perlu review batas versi | 248 / 2 |

Seluruh teks paragraf cocok dengan proyeksi XML Word menggunakan representasi LaTeX intake; seluruh XML OMML tersimpan cocok dengan arsip. Penomoran otomatis dipulihkan dari numbering/styles Word dan disimpan bersama lokasi paragraf; teks intake asli tetap dipertahankan. Tabel, label kategori, dan posisi sumber tidak diratakan atau dihapus dari bukti JSON. Tidak ada posisi soal yang hilang atau berulang pada kelompok ini.

**Dua batas versi belum dapat diputuskan:**

- I1 level 5 soal 2: beberapa definisi `a` dan dua rangkaian evaluasi bercampur dalam satu entri (termasuk catatan `eh wait`). Semua teks dipertahankan, tidak dipilih versi akhir.
- I3 level 5 soal 7: dua rangkaian A–D serta kunci tambahan bercampur. Delapan teks opsi tersimpan sebagai bukti dua rangkaian, bukan dianggap satu soal delapan opsi yang siap digunakan.

**Catatan pemisahan sumber:** I1 level 2 soal 1 memuat catatan koreksi opsi dalam pembahasan; I2 level 4 soal 9 memuat catatan koreksi kunci; I4 level 4 soal 5 memuat deskripsi panjang setelah huruf kunci. Teks-teks tersebut dipertahankan pada bagiannya dan perlu dinilai pada audit akademik. Belum ada keputusan kebenaran kunci atau pembahasan.

Pemeriksaan ini membuktikan kesetiaan struktur/teks, bukan kebenaran matematika atau ketepatan tampilan visual setiap persamaan. Label `STRUCTURE_VERIFIED` tidak berarti soal valid secara akademik.

Keluaran: [CSV 250 entri](entries.csv), [JSON komponen dan bukti](validation.json). Reproduksi: `python variant_gen/tests/validate_intake_01_05.py`.

Seluruh {len(before)} berkas sumber/bank/config/stok/layanan yang dibekukan tetap memiliki hash yang sama; tidak ada perubahan runtime. **Tahap berikutnya belum dikerjakan dalam bagian ini.**
'''
    (DEST/'README.md').write_text(report,encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=True,indent=2))


if __name__=='__main__':run()
