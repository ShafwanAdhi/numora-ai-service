"""Repeatable source-only import; independent review, no configs/variants/database writes."""
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path

from audit_original_questions import ROOT, source_entries

SOURCE = ROOT/'docs/sources/incoming/2026-10-19-indikator-16-19'
DATA = ROOT/'variant_gen/data/drill-1-indicators-16-19-levels-4-5'
REPORT = ROOT/'docs/audits/2026-10-21-drill-16-19-level45-import'

# Independent derivations from the question data, not the previous review's verdict.
# Each row covers Q1..Q10; option letters refer to source order.
REVIEW = {
 (16,4): [
 ('D','2*(22/7)*7*(7+10)=748; opsi 440,594,616 salah.'),
 ('C','Gambar C mempunyai persegi dan lima segitiga; limas segiempat hanya empat sisi tegak. A empat segitiga, B prisma segitiga, D kerucut.'),
 ('B','Busur selimut=keliling alas=2*(22/7)*14=88; s=20 tidak mengubah keliling alas.'),
 ('C','Jika tinggi segitiga benar 10 dan alas 12: 12^2+4*(12*10/2)=384. Label gambar tidak konsisten, sehingga hasil bersyarat.'),
 ('B','Dua segitiga 6-8-10 dan persegi panjang 6x15,8x15,10x15; ketiganya berbeda ukuran.'),
 ('AB','Tetrahedron mempunyai F=4,E=6,V=4. Namun opsi C membahas titik sudut jaring-jaring, bukan bangun terlipat; tidak boleh disamakan. Opsi D=5 salah.'),
 ('ACD','Tabung tertutup: dua lingkaran dan satu persegi panjang; panjang=2*pi*r, lebar=t, luas=2*pi*r^2+2*pi*r*t.'),
 ('ABD','Limas persegi: empat segitiga tegak, E=4+4=8, V=4+1=5. Bukan lima sisi tegak.'),
 ('14','Prisma mempunyai dua alas kongruen. Klaim tepat n segitiga gagal untuk n=3: alas limas juga segitiga, total empat. Enam persegi berbeda ukuran tidak membentuk balok. Puncak di atas sudut alas memungkinkan empat sisi tegak siku-siku.'),
 ('14','Kategori pertama Tabung: dua lingkaran+satu persegi panjang dan tiga sisi. Kerucut: satu lingkaran+satu juring dengan busur=keliling alas.'),
 ],
 (16,5): [
 ('C','C dimaksudkan sebagai selimut terlalu pendek; tanpa panjang/diameter, proporsi ilustrasi bukan bukti metrik. A juga tidak diberi ukuran, sehingga keunikan C tidak terjamin.'),
 ('B','r menjadi r/2 dan t menjadi 2t: luas baru=pi*r^2/2+2*pi*r*t, lebih kecil dari 2*pi*r^2+2*pi*r*t untuk r>0.'),
 ('A','Busur=(150/360)*2*pi*12=10*pi; 2*pi*r=10*pi memberi r=5. B,C salah; D hanya berlaku jika sudut=180, bukan 150.'),
 ('B','412/2=96+(12+8)t; t=(206-96)/20=5.5.'),
 ('D','Alas=10^2=100; tiap segitiga=10*13/2=65; luas total=100+4*65=360. Tinggi limas=sqrt(13^2-5^2)=12, bukan13.'),
 ('ABD','Faktor panjang3 memberi faktor luas9 dan volume27; jumlah bidang persegi tetap6.'),
 ('ACD','Tanpa tutup: pi*r^2+2*pi*r*t. Persegi memerlukan t=2*pi*r, bukan2r. r digandakan pada t tetap memberi selimut dua kali.'),
 ('ABC','Prisma segitiga lima bidang; limas segienam satu alas+enam segitiga; lima panjang sisi alas berbeda memberi lima persegi panjang berbeda. Limas persegi dengan rusuk tegak=sisi alas dapat memiliki segitiga sama sisi.'),
 ('134','Luas net=permukaan; 6s^2=150 memberi s=5,V=125 bukan155. Vtabung=pi*r^2*t. Luas limas=64+4*40=224.'),
 ('14','Busur=14*pi; sudut=360*7/14=180 bukan90; tinggi=sqrt(14^2-7^2)=7sqrt(3), bukan14; luas=pi*7*(7+14)=147*pi.'),
 ],
 (17,4): [
 ('C','Rotasi90 searah: (x,y)->(y,-x); (-3,4)->(4,3).'),
 ('A','Substitusi x=X-1,y=Y+2: 2X+3Y=6+2-6=2.'),
 ('C','Luas=6*4*(-2)^2=96.'),
 ('C','Refleksi y=x memberi (b,a)=(4,-3); a+b=1.'),
 ('A','Vektor=(-3-2,1-(-5))=(-5,6); Q menjadi(-6,10).'),
 ('ABC','A(-2,5): refleksiX=(-2,-5); tukar=(5,-2); rotasiCCW=(-5,-2); dilatasi-2=(4,-10), bukan(-4,10). Pembahasan sumber rusak.'),
 ('ABC','Translasi garis: y=2x+(-1+1-2*3)=2x-6; refleksiX=-2x+1; refleksiY=-2x-1; dilatasi2 memberi2x-2 bukan2x-4.'),
 ('ABC','B=(-6,8)/(-2)=(3,-4); jumlah=-1,kuadranIV,refleksiY=(-3,-4),rotasi180=(-3,4) bukan(3,4).'),
 ('123','Jika translasi dimaksud(-2,5), hasil(2,2). RefleksiX=(4,3); refleksi y=-x=(3,-4); CCW90=(3,4) bukan(3,-4). Vektor opsi A rusak.'),
 ('123','Isometri menjaga luas12; dilatasi3 memberi108; dilatasi-2 memberi48 bukan24.'),
 ],
 (17,5): [
 ('AC','k^2=90/10=9 memberi k=+3 atau-3. Opsi A=3 juga faktor yang mungkin, sehingga A dan C sama-sama memenuhi stem PG.'),
 ('A','(-y,x)=(-4,5) memberi x=5,y=4.'),
 ('B','RefleksiY bisa memetakan(3,-2) ke(-3,-2), tetapi translasi(-6,0) juga bisa. Satu pasangan titik tidak menentukan sifat transformasi seluruh bangun.'),
 ('A','Refleksi y=-x: x=-Y,y=-X; 2(-Y)-(-X)+3=0 memberi X-2Y+3=0.'),
 ('A','-3*k=12 memberi k=-4; komponen x=-3*2=-6 cocok.'),
 ('ABC','P(-3,4): refleksiX=(-3,-4),rotasi180=(3,-4),translasi(4,-2)=(1,2),dilatasi2=(-6,8) bukan(-6,-8).'),
 ('ABD','Dilatasi memberi luas k^2*L. Refleksi menjaga K; rotasi menjaga L, bukan2L; translasi menjaga L.'),
 ('ABD','B(4,-2): tukar=(-2,4),refleksi y=-x=(2,-4),CW90=(-2,-4) bukan(2,-4),dilatasi-3=(-12,6).'),
 ('123','D(-5,2): translasi(3,-4)=(-2,-2); refleksiY=(5,2); rotasi180=(5,-2); dilatasi2=(-10,4), bukan(-10,2). Opsi A/D rusak.'),
 ('12','Refleksi/translasi menjaga luas20. Rotasi180 menjaga orientasi dalam arti handedness, meskipun arah gambar berubah; klaim C ambigu. Dilatasi3 memberi180 bukan60.'),
 ],
 (18,4): [
 ('B','(22/7)*14^2-14^2=616-196=420.'),
 ('B','Diameter lingkaran terbesar=min(24,14)=14; 24*14-(22/7)*7^2=182.'),
 ('C','Keliling linear terhadap r: faktor3; luas kuadrat: faktor9.'),
 ('C','Keliling luar=2*10+7+(22/7)*7/2=38; sisi sambungan bukan keliling luar.'),
 ('B','K44 memberi persegi sisi11,luas121; lingkaran r7,luas154; selisih33.'),
 ('ABC','Persegi196; seperempat lingkaran154; sisa42; keliling sisa=14+14+22=50 bukan72.'),
 ('ACD','Lingkaran616; diagonal persegi28 bukan14; persegi=28^2/2=392; sisa224.'),
 ('ABC','Luas awal200; luar24*14=336; jalan136. Lebar1 memberi22*12-200=64 bukan68.'),
 ('123','Persegi panjang98; dua setengah lingkaran luas38.5; total136.5; keliling28+22=50; r3.5 bukan7.'),
 ('123','r14,luas616,R17.5; jalan=(22/7)*(17.5^2-14^2)=346.5 bukan462.'),
 ],
 (18,5): [
 ('B','K88: persegi22^2=484; lingkaran r14 luas616; selisih132.'),
 ('C','Dua potongan setengah lingkaran r7 tidak berimpit pada panjang20; 280-154=126.'),
 ('A','Luas196+77=273; keliling3*14+22=64; keduanya benar.'),
 ('D','Jalan=(22/7)*(17.5^2-14^2)=346.5; biaya=34650000.'),
 ('B','Busur seperempat lingkaran22; keliling14+14+22=50; biaya7500000; kurang500000.'),
 ('ABC','Persegi196; setengah lingkaran77; keliling64; total273 bukan300.'),
 ('ABD','Lingkaran616; R17.5; jalan346.5 bukan462; keliling taman88.'),
 ('ACD','Luas16*12/2=96; sisi=sqrt(8^2+6^2)=10 bukan14; keliling40; sqrt96=4sqrt6.'),
 ('123','Lantai150m2; keramik0.5^2=0.25m2; jumlah600; dus600/4=150 bukan200.'),
 ('123','Karton280; potongan77; sisa203; keliling20+20+14+22=76 bukan88.'),
 ],
 (19,4): [
 ('C','Volume faktor2^3: 36*pi*8=288*pi.'),
 ('B','Alas6*8/2=24; tinggi240/24=10.'),
 ('D','Tinggi3*160/(8*6)=10.'),
 ('A','Kubus1000; bola r5 volumenya500*pi/3; kosong1000-500*pi/3.'),
 ('B','VolumeA=6^2*8/3=96; B=12^2*16/3=768; rasio8.'),
 ('ABC','Alas3*4/2=6; volume60; tinggi20 memberi120; semua sisi alas digandakan memberi faktor4, bukan2.'),
 ('ABC','Bola=4*6^3*pi/3=288*pi; limas12^2*8/3=384; rasio limas:bola=4:3pi; bola r12 volumenya2304pi>384.'),
 ('ABD','Prisma=3*limas pada alas/tinggi sama; rasio bola1:27; bola pi*d^3/6 tidak sama dengan limas d^3/3; rumus diameter benar.'),
 ('123','Alas8*6/2=24; volume360; tinggi30 memberi720; alas12 pada tinggi15 memberi180 bukan200.'),
 ('123','Bola r10=4000pi/3; r20 faktor8; r5=500pi/3; diameter20 tetap r10 sehingga volume tetap.'),
 ],
 (19,5): [
 ('A','Air limas10^2*12/3=400; prisma40*15=600; sisa200.'),
 ('C','Bola288pi; tiap limas12^2*2pi/3=96pi; tepat3 limas.'),
 ('B','Volume1=12^2*10/3=480; alas2=8*18=144; tinggi3*480/144=10.'),
 ('D','Alas belahketupat12*16/2=96; tinggi960/96=10.'),
 ('A','Air=(10*12/2)*20/2=600; bola=4*(22/7)*7^3/3=4312/3; sisa2512/3=837.333..., dibulatkan dua desimal837.33.'),
 ('ABC','Vprisma=A*t; Vlimas=A*t/3. Rasio3:1 tetap saat t keduanya digandakan. tprisma=3*tlimas memberi rasio9:1 bukan1:1.'),
 ('ABC','Vlimas=(2r)^2*r/3=4r^3/3; Vbola=pi*Vlimas>Vlimas untuk r>0; rbola digandakan memberi8pi*Vlimas bukan2.'),
 ('ABC','Kubus1000; limas1000/3; kosong2000/3; rasio limas:kosong1:2 bukan1:3.'),
 ('123','Rusuk3 memberi volume27; rsetengah memberi1/8; tinggi2 memberi2; bola diameterd=pi*d^3/6 dan limas=d^3/6, rasio pi bukan4.'),
 ('123','Tinggi2 memberi1200; alas3 memberi1800; mengurangi tinggi5 hanya membentuk prisma valid bila t>5. Semua rusuk2 memberi8*600=4800 bukan1200.'),
 ],
}

ISSUES = {
 (16,4,1): 'MEDIA_MISMATCH: image4.jpg adalah tabung utuh, stem menyebut gambar jaring-jaring.',
 (16,4,3): 'MEDIA_MISMATCH: image14.png adalah kerucut utuh, bukan jaring-jaring; perhitungan busur tetap benar.',
 (16,4,4): 'INCONSISTENT_DIMENSIONS: image1.jpg menandai alas segitiga12, sisi miring10 dan tinggi10 sekaligus; seharusnya tinggi8 bila kedua sisi10. Kunci384 hanya berlaku jika tinggi10 diprioritaskan.',
 (16,4,6): 'KEY_AND_MEDIA: kunci A,B,D memilih klaim lima titik sudut yang salah. Gambar image9.png menunjukkan limas utuh, bukan net. Opsi C menyebut titik sudut net, sementara pembahasan menghitung titik sudut limas; perlu perjelas sebelum menentukan kunci final.',
 (16,4,7): 'MEDIA_MISMATCH: image12.png tabung utuh, bukan jaring-jaring yang diminta.',
 (16,4,9): 'DOMAIN_AMBIGUITY: limas segi-n tidak selalu mempunyai tepat n bidang segitiga total; n=3 mempunyai4 termasuk alas. Ubah menjadi n sisi tegak segitiga jika itu maksudnya.',
 (16,5,1): 'INSUFFICIENT_METRIC_DATA: gambar C tampak tidak proporsional tetapi tidak memiliki ukuran; tidak cukup membuktikan panjang selimut tidak sama dengan keliling alas.',
 (17,4,6): 'MALFORMED_EXPLANATION: koordinat A(-,25), hasil(-,2-5), dan rumus(-y,yx) rusak; kunci A,B,C benar untuk stem.',
 (17,4,9): 'MALFORMED_OPTION: vektor opsi A ditulis T(-,25), bukan pasangan koordinat valid; pembahasan bermaksud T(-2,5).',
 (17,5,1): 'MULTIPLE_PG_ANSWERS: stem menanyakan faktor yang mungkin; 3 pada opsi A juga mungkin, sedangkan C memuat3 atau-3. Perlu meminta semua kemungkinan.',
 (17,5,3): 'UNDERDETERMINED_TRANSFORMATION: satu pasangan titik juga cocok dengan translasi(-6,0); tidak membuktikan refleksiY maupun sifat seluruh bangun.',
 (17,5,9): 'MALFORMED_OPTIONS_AND_EXPLANATION: opsi A(-,2-2), D(-,102) dan pembahasan tidak membentuk pasangan koordinat yang jelas.',
 (17,5,10): 'ORIENTATION_AMBIGUITY: opsi C menyatakan rotasi mengubah orientasi; rotasi mempertahankan orientasi matematis, tetapi mengubah arah gambar. Kunci123 tidak aman tanpa definisi orientasi.',
 (19,5,10): 'MISSING_DOMAIN: tinggi awal tidak diketahui; pengurangan5cm memerlukan t>5 agar tetap prisma. Contoh alas200cm2 memberi t=3cm dari V600 sehingga operasi tidak valid.',
}


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2)+'\n'


def main():
    entries = [e for e in source_entries(SOURCE) if e['level'] in (4,5)]
    assert len(entries)==80
    assert Counter((e['indicator'],e['level']) for e in entries)==Counter({(i,l):10 for i in range(16,20) for l in (4,5)})
    previous = json.loads((ROOT/'docs/audits/2026-10-19-original-question-audit/reviews/16-19.json').read_text(encoding='utf8'))['reviews']
    old = {(e['indicator'],e['level'],e['source_number'],e['occurrence'],e['fragment']):e for e in previous}
    archived = json.loads((ROOT/'docs/audits/2026-10-19-original-question-audit/source-structure.json').read_text(encoding='utf8'))
    archived = {e['audit_id']:e for e in archived}
    index = json.loads((SOURCE/'question-index.json').read_text(encoding='utf8'))['questions']
    rows, metadata, groups, reviews = [], {}, {}, []
    for e in entries:
        i,l,n=e['indicator'],e['level'],e['source_number']; identity=(i,l,n)
        assert e==archived[e['audit_id']], f'Source extraction drift: {identity}'
        assert not e['parse_flags'] and len(e['options'])==4 and e['key'] is not None, identity
        answer, reasoning=REVIEW[i,l][n-1]
        expected=list(answer)
        issues=[ISSUES[identity]] if identity in ISSUES else []
        # No clean verdict can hide an independently detected key mismatch.
        if expected!=e['key'] and not issues:
            raise AssertionError((identity,expected,e['key']))
        qid=f"{e['format'].lower()}-{i}-{l}-{n}"
        raw=next(q['extracted_content'] for q in index if (q['source_indicator'],q['source_level'],q['source_question_number'])==identity)
        cognitive=re.search(r'Level\s+Kognitif\s*:\s*\(?\s*(C[1-6])',raw,re.I)
        assert cognitive, identity
        projection={k:e[k] for k in ('format','stem','options','key','explanation','additional_notes','category_labels')}
        status='HOLD_SOURCE' if issues else 'ACTIVE'
        review=dict(question_id=qid,audit_id=e['audit_id'],indicator=i,level=l,source_number=n,
                    source_projection=projection,independent_answer=expected,independent_reasoning=reasoning,
                    answer_is_conditional=bool(issues),issues=issues,
                    previous_review=old[i,l,n,e['occurrence'],e['fragment']],generation_status=status)
        reviews.append(review)
        rows.append(dict(id=qid,format=e['format'],cognitive_level=cognitive[1],stem=e['stem'],
                         options_json=json.dumps(e['options'],ensure_ascii=False),key=','.join(e['key']),version=1))
        media={p['target'] for paragraph in e['paragraphs'] for p in paragraph.get('images',[])}
        for target in media:
            assert target.startswith('media/') and (SOURCE/target).is_file(), target
        metadata[qid]=dict(generation_status=status,reason='; '.join(issues),generator_status='NOT_IMPLEMENTED',
            source_number=n,source_document=e['source']['path'],source_document_sha256=e['source']['sha256'],
            source_location=e['source'],source_text=raw,source_projection=projection,
            original_explanation=e['explanation'],source_additional_notes=e['additional_notes'],
            source_media=[dict(path=(SOURCE/t).relative_to(ROOT).as_posix(),sha256=hashlib.sha256((SOURCE/t).read_bytes()).hexdigest()) for t in sorted(media)],
            approval_status='NOT_CURRICULUM_APPROVED',self_adjustment_enabled=False,
            source_review=dict(date='2026-10-21',audit_id=e['audit_id'],issues=issues,
                               independent_reasoning=reasoning,original_unchanged=True),
            batch='2026-10-21-indicators16-19-level45-source-only')
        if e['category_labels']: metadata[qid]['category_labels']=e['category_labels']
        if (ROOT/'variant_gen/configs'/qid/'v1.json').exists():
            metadata[qid]['generator_status']='IMPLEMENTED'
        groups.setdefault((i,l),[]).append(qid)
    counts=dict(originals=80,active=sum(not e['issues'] for e in reviews),hold=sum(bool(e['issues']) for e in reviews),generators_added=0,stocks_added=0)
    report=dict(date='2026-10-21',source_sha256=entries[0]['source']['sha256'],counts=counts,entries=reviews)
    out=io.StringIO(newline=''); w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    files={DATA/'q0_bank.csv':out.getvalue(),DATA/'question_metadata.json':encoded(metadata),
           DATA/'question_catalog.json':encoded([dict(activity='DRILL',package_id='drill-1',indicator=i,source_level=l,question_ids=qs) for (i,l),qs in groups.items()]),
           DATA/'audit.json':encoded(report)}
    # Validate every existing output before any write; never overwrite later edits.
    for path,value in files.items():
        if path.exists(): assert path.read_bytes()==value.encode('utf8'), f'Refusing overwrite: {path}'
    DATA.mkdir(parents=True,exist_ok=True)
    for path,value in files.items():
        if not path.exists(): path.write_bytes(value.encode('utf8'))
    print(json.dumps(counts))


if __name__=='__main__':
    main()
