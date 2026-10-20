# Validasi audit dan impor original indikator 16?19 level 4?5

Tanggal: 21 Oktober 2026. Cakupan: Drill Paket 1, 80 original; tanpa generator, stok baru, database atau publikasi.

**Hasil: 80 original diimpor, 66 ACTIVE, 14 HOLD_SOURCE.** ACTIVE berarti sumber lolos pemeriksaan ini; bukan approval kurikulum, kalibrasi IRT, atau generator sudah tersedia. Nomor sumber, redaksi, opsi, kunci, pembahasan dan label kategori dipertahankan. Tidak ada koreksi sumber diam-diam.

| Indikator | Impor | ACTIVE | HOLD_SOURCE |
|---|---:|---:|---:|
| 16 | 20 | 13 | 7 |
| 17 | 20 | 14 | 6 |
| 18 | 20 | 20 | 0 |
| 19 | 20 | 19 | 1 |

## Bukti dan batas validasi

- SHA-256 DOCX diperiksa terhadap manifest intake: `8182d606d4a27e6ab3c80834a36648796d395ee8f66a5ef7b90a3c88587cd232`.
- Seluruh 80 proyeksi diekstrak ulang dari arsip dengan penomoran Word, lalu dibandingkan tepat dengan source-structure audit lama. Tidak perlu menjalankan ulang ekstraksi DOCX awal.
- Kunci, setiap opsi/pernyataan, perhitungan, domain, pembahasan dan gambar ditinjau ulang. Derivasi independen per soal tercatat di bawah dan pada audit.json bank.
- Sembilan referensi gambar dipastikan tersedia dan ditinjau visual; contact sheet tersedia sebagai [bukti visual](media-contact-sheet.png). Ukuran ilustrasi tanpa label tidak diasumsikan sebagai data numerik.
- Empat soal sudah ditandai bermasalah oleh audit lama. Pemeriksaan ini mempertahankan keempatnya dan menambahkan sepuluh HOLD; penalaran lama yang sekadar mengutip pembahasan tidak dianggap bukti independen.
- Koordinat rusak dipertahankan persis dari proyeksi arsip, tidak ditebak atau diperbaiki. Soal tersebut ditahan.
- Kasus 16/L4/Q6: klaim empat titik sudut bangun terlipat tidak identik dengan klaim empat titik sudut jaring-jaring; kunci final belum ditentukan.
- Kasus 19/L5/Q5: hasil tepat sisa kapasitas 2512/3 cm?, opsi A merupakan pembulatan dua desimal; ini dicatat sebagai presisi pembulatan, bukan konflik kunci.
- Gambar asli tetap di arsip sumber; metadata `source_media` menyimpan path repo dan hash. Tidak ditambahkan renderer gambar ke UI.
- Label kategori `Tabung`/`Kerucut` pada kategori-16-4-10 dipertahankan; tidak dikonversi menjadi Benar/Salah.

## Soal yang ditahan

| ID | Alasan |
|---|---|
| `pg-16-4-1` | MEDIA_MISMATCH: image4.jpg adalah tabung utuh, stem menyebut gambar jaring-jaring. |
| `pg-16-4-3` | MEDIA_MISMATCH: image14.png adalah kerucut utuh, bukan jaring-jaring; perhitungan busur tetap benar. |
| `pg-16-4-4` | INCONSISTENT_DIMENSIONS: image1.jpg menandai alas segitiga12, sisi miring10 dan tinggi10 sekaligus; seharusnya tinggi8 bila kedua sisi10. Kunci384 hanya berlaku jika tinggi10 diprioritaskan. |
| `mcma-16-4-6` | KEY_AND_MEDIA: kunci A,B,D memilih klaim lima titik sudut yang salah. Gambar image9.png menunjukkan limas utuh, bukan net. Opsi C menyebut titik sudut net, sementara pembahasan menghitung titik sudut limas; perlu perjelas sebelum menentukan kunci final. |
| `mcma-16-4-7` | MEDIA_MISMATCH: image12.png tabung utuh, bukan jaring-jaring yang diminta. |
| `kategori-16-4-9` | DOMAIN_AMBIGUITY: limas segi-n tidak selalu mempunyai tepat n bidang segitiga total; n=3 mempunyai4 termasuk alas. Ubah menjadi n sisi tegak segitiga jika itu maksudnya. |
| `pg-16-5-1` | INSUFFICIENT_METRIC_DATA: gambar C tampak tidak proporsional tetapi tidak memiliki ukuran; tidak cukup membuktikan panjang selimut tidak sama dengan keliling alas. |
| `mcma-17-4-6` | MALFORMED_EXPLANATION: koordinat A(-,25), hasil(-,2-5), dan rumus(-y,yx) rusak; kunci A,B,C benar untuk stem. |
| `kategori-17-4-9` | MALFORMED_OPTION: vektor opsi A ditulis T(-,25), bukan pasangan koordinat valid; pembahasan bermaksud T(-2,5). |
| `pg-17-5-1` | MULTIPLE_PG_ANSWERS: stem menanyakan faktor yang mungkin; 3 pada opsi A juga mungkin, sedangkan C memuat3 atau-3. Perlu meminta semua kemungkinan. |
| `pg-17-5-3` | UNDERDETERMINED_TRANSFORMATION: satu pasangan titik juga cocok dengan translasi(-6,0); tidak membuktikan refleksiY maupun sifat seluruh bangun. |
| `kategori-17-5-9` | MALFORMED_OPTIONS_AND_EXPLANATION: opsi A(-,2-2), D(-,102) dan pembahasan tidak membentuk pasangan koordinat yang jelas. |
| `kategori-17-5-10` | ORIENTATION_AMBIGUITY: opsi C menyatakan rotasi mengubah orientasi; rotasi mempertahankan orientasi matematis, tetapi mengubah arah gambar. Kunci123 tidak aman tanpa definisi orientasi. |
| `kategori-19-5-10` | MISSING_DOMAIN: tinggi awal tidak diketahui; pengurangan5cm memerlukan t>5 agar tetap prisma. Contoh alas200cm2 memberi t=3cm dari V600 sehingga operasi tidak valid. |

## Derivasi per soal

Jawaban pada soal HOLD bersifat bersyarat/usulan analisis; kunci sumber di bank tidak diubah.

| ID | Hasil independen | Derivasi / evaluasi opsi |
|---|---|---|
| `pg-16-4-1` | D | 2*(22/7)*7*(7+10)=748; opsi 440,594,616 salah. |
| `pg-16-4-2` | C | Gambar C mempunyai persegi dan lima segitiga; limas segiempat hanya empat sisi tegak. A empat segitiga, B prisma segitiga, D kerucut. |
| `pg-16-4-3` | B | Busur selimut=keliling alas=2*(22/7)*14=88; s=20 tidak mengubah keliling alas. |
| `pg-16-4-4` | C | Jika tinggi segitiga benar 10 dan alas 12: 12^2+4*(12*10/2)=384. Label gambar tidak konsisten, sehingga hasil bersyarat. |
| `pg-16-4-5` | B | Dua segitiga 6-8-10 dan persegi panjang 6x15,8x15,10x15; ketiganya berbeda ukuran. |
| `mcma-16-4-6` | A,B | Tetrahedron mempunyai F=4,E=6,V=4. Namun opsi C membahas titik sudut jaring-jaring, bukan bangun terlipat; tidak boleh disamakan. Opsi D=5 salah. |
| `mcma-16-4-7` | A,C,D | Tabung tertutup: dua lingkaran dan satu persegi panjang; panjang=2*pi*r, lebar=t, luas=2*pi*r^2+2*pi*r*t. |
| `mcma-16-4-8` | A,B,D | Limas persegi: empat segitiga tegak, E=4+4=8, V=4+1=5. Bukan lima sisi tegak. |
| `kategori-16-4-9` | 1,4 | Prisma mempunyai dua alas kongruen. Klaim tepat n segitiga gagal untuk n=3: alas limas juga segitiga, total empat. Enam persegi berbeda ukuran tidak membentuk balok. Puncak di atas sudut alas memungkinkan empat sisi tegak siku-siku. |
| `kategori-16-4-10` | 1,4 | Kategori pertama Tabung: dua lingkaran+satu persegi panjang dan tiga sisi. Kerucut: satu lingkaran+satu juring dengan busur=keliling alas. |
| `pg-16-5-1` | C | C dimaksudkan sebagai selimut terlalu pendek; tanpa panjang/diameter, proporsi ilustrasi bukan bukti metrik. A juga tidak diberi ukuran, sehingga keunikan C tidak terjamin. |
| `pg-16-5-2` | B | r menjadi r/2 dan t menjadi 2t: luas baru=pi*r^2/2+2*pi*r*t, lebih kecil dari 2*pi*r^2+2*pi*r*t untuk r>0. |
| `pg-16-5-3` | A | Busur=(150/360)*2*pi*12=10*pi; 2*pi*r=10*pi memberi r=5. B,C salah; D hanya berlaku jika sudut=180, bukan 150. |
| `pg-16-5-4` | B | 412/2=96+(12+8)t; t=(206-96)/20=5.5. |
| `pg-16-5-5` | D | Alas=10^2=100; tiap segitiga=10*13/2=65; luas total=100+4*65=360. Tinggi limas=sqrt(13^2-5^2)=12, bukan13. |
| `mcma-16-5-6` | A,B,D | Faktor panjang3 memberi faktor luas9 dan volume27; jumlah bidang persegi tetap6. |
| `mcma-16-5-7` | A,C,D | Tanpa tutup: pi*r^2+2*pi*r*t. Persegi memerlukan t=2*pi*r, bukan2r. r digandakan pada t tetap memberi selimut dua kali. |
| `mcma-16-5-8` | A,B,C | Prisma segitiga lima bidang; limas segienam satu alas+enam segitiga; lima panjang sisi alas berbeda memberi lima persegi panjang berbeda. Limas persegi dengan rusuk tegak=sisi alas dapat memiliki segitiga sama sisi. |
| `kategori-16-5-9` | 1,3,4 | Luas net=permukaan; 6s^2=150 memberi s=5,V=125 bukan155. Vtabung=pi*r^2*t. Luas limas=64+4*40=224. |
| `kategori-16-5-10` | 1,4 | Busur=14*pi; sudut=360*7/14=180 bukan90; tinggi=sqrt(14^2-7^2)=7sqrt(3), bukan14; luas=pi*7*(7+14)=147*pi. |
| `pg-17-4-1` | C | Rotasi90 searah: (x,y)->(y,-x); (-3,4)->(4,3). |
| `pg-17-4-2` | A | Substitusi x=X-1,y=Y+2: 2X+3Y=6+2-6=2. |
| `pg-17-4-3` | C | Luas=6*4*(-2)^2=96. |
| `pg-17-4-4` | C | Refleksi y=x memberi (b,a)=(4,-3); a+b=1. |
| `pg-17-4-5` | A | Vektor=(-3-2,1-(-5))=(-5,6); Q menjadi(-6,10). |
| `mcma-17-4-6` | A,B,C | A(-2,5): refleksiX=(-2,-5); tukar=(5,-2); rotasiCCW=(-5,-2); dilatasi-2=(4,-10), bukan(-4,10). Pembahasan sumber rusak. |
| `mcma-17-4-7` | A,B,C | Translasi garis: y=2x+(-1+1-2*3)=2x-6; refleksiX=-2x+1; refleksiY=-2x-1; dilatasi2 memberi2x-2 bukan2x-4. |
| `mcma-17-4-8` | A,B,C | B=(-6,8)/(-2)=(3,-4); jumlah=-1,kuadranIV,refleksiY=(-3,-4),rotasi180=(-3,4) bukan(3,4). |
| `kategori-17-4-9` | 1,2,3 | Jika translasi dimaksud(-2,5), hasil(2,2). RefleksiX=(4,3); refleksi y=-x=(3,-4); CCW90=(3,4) bukan(3,-4). Vektor opsi A rusak. |
| `kategori-17-4-10` | 1,2,3 | Isometri menjaga luas12; dilatasi3 memberi108; dilatasi-2 memberi48 bukan24. |
| `pg-17-5-1` | A,C | k^2=90/10=9 memberi k=+3 atau-3. Opsi A=3 juga faktor yang mungkin, sehingga A dan C sama-sama memenuhi stem PG. |
| `pg-17-5-2` | A | (-y,x)=(-4,5) memberi x=5,y=4. |
| `pg-17-5-3` | B | RefleksiY bisa memetakan(3,-2) ke(-3,-2), tetapi translasi(-6,0) juga bisa. Satu pasangan titik tidak menentukan sifat transformasi seluruh bangun. |
| `pg-17-5-4` | A | Refleksi y=-x: x=-Y,y=-X; 2(-Y)-(-X)+3=0 memberi X-2Y+3=0. |
| `pg-17-5-5` | A | -3*k=12 memberi k=-4; komponen x=-3*2=-6 cocok. |
| `mcma-17-5-6` | A,B,C | P(-3,4): refleksiX=(-3,-4),rotasi180=(3,-4),translasi(4,-2)=(1,2),dilatasi2=(-6,8) bukan(-6,-8). |
| `mcma-17-5-7` | A,B,D | Dilatasi memberi luas k^2*L. Refleksi menjaga K; rotasi menjaga L, bukan2L; translasi menjaga L. |
| `mcma-17-5-8` | A,B,D | B(4,-2): tukar=(-2,4),refleksi y=-x=(2,-4),CW90=(-2,-4) bukan(2,-4),dilatasi-3=(-12,6). |
| `kategori-17-5-9` | 1,2,3 | D(-5,2): translasi(3,-4)=(-2,-2); refleksiY=(5,2); rotasi180=(5,-2); dilatasi2=(-10,4), bukan(-10,2). Opsi A/D rusak. |
| `kategori-17-5-10` | 1,2 | Refleksi/translasi menjaga luas20. Rotasi180 menjaga orientasi dalam arti handedness, meskipun arah gambar berubah; klaim C ambigu. Dilatasi3 memberi180 bukan60. |
| `pg-18-4-1` | B | (22/7)*14^2-14^2=616-196=420. |
| `pg-18-4-2` | B | Diameter lingkaran terbesar=min(24,14)=14; 24*14-(22/7)*7^2=182. |
| `pg-18-4-3` | C | Keliling linear terhadap r: faktor3; luas kuadrat: faktor9. |
| `pg-18-4-4` | C | Keliling luar=2*10+7+(22/7)*7/2=38; sisi sambungan bukan keliling luar. |
| `pg-18-4-5` | B | K44 memberi persegi sisi11,luas121; lingkaran r7,luas154; selisih33. |
| `mcma-18-4-6` | A,B,C | Persegi196; seperempat lingkaran154; sisa42; keliling sisa=14+14+22=50 bukan72. |
| `mcma-18-4-7` | A,C,D | Lingkaran616; diagonal persegi28 bukan14; persegi=28^2/2=392; sisa224. |
| `mcma-18-4-8` | A,B,C | Luas awal200; luar24*14=336; jalan136. Lebar1 memberi22*12-200=64 bukan68. |
| `kategori-18-4-9` | 1,2,3 | Persegi panjang98; dua setengah lingkaran luas38.5; total136.5; keliling28+22=50; r3.5 bukan7. |
| `kategori-18-4-10` | 1,2,3 | r14,luas616,R17.5; jalan=(22/7)*(17.5^2-14^2)=346.5 bukan462. |
| `pg-18-5-1` | B | K88: persegi22^2=484; lingkaran r14 luas616; selisih132. |
| `pg-18-5-2` | C | Dua potongan setengah lingkaran r7 tidak berimpit pada panjang20; 280-154=126. |
| `pg-18-5-3` | A | Luas196+77=273; keliling3*14+22=64; keduanya benar. |
| `pg-18-5-4` | D | Jalan=(22/7)*(17.5^2-14^2)=346.5; biaya=34650000. |
| `pg-18-5-5` | B | Busur seperempat lingkaran22; keliling14+14+22=50; biaya7500000; kurang500000. |
| `mcma-18-5-6` | A,B,C | Persegi196; setengah lingkaran77; keliling64; total273 bukan300. |
| `mcma-18-5-7` | A,B,D | Lingkaran616; R17.5; jalan346.5 bukan462; keliling taman88. |
| `mcma-18-5-8` | A,C,D | Luas16*12/2=96; sisi=sqrt(8^2+6^2)=10 bukan14; keliling40; sqrt96=4sqrt6. |
| `kategori-18-5-9` | 1,2,3 | Lantai150m2; keramik0.5^2=0.25m2; jumlah600; dus600/4=150 bukan200. |
| `kategori-18-5-10` | 1,2,3 | Karton280; potongan77; sisa203; keliling20+20+14+22=76 bukan88. |
| `pg-19-4-1` | C | Volume faktor2^3: 36*pi*8=288*pi. |
| `pg-19-4-2` | B | Alas6*8/2=24; tinggi240/24=10. |
| `pg-19-4-3` | D | Tinggi3*160/(8*6)=10. |
| `pg-19-4-4` | A | Kubus1000; bola r5 volumenya500*pi/3; kosong1000-500*pi/3. |
| `pg-19-4-5` | B | VolumeA=6^2*8/3=96; B=12^2*16/3=768; rasio8. |
| `mcma-19-4-6` | A,B,C | Alas3*4/2=6; volume60; tinggi20 memberi120; semua sisi alas digandakan memberi faktor4, bukan2. |
| `mcma-19-4-7` | A,B,C | Bola=4*6^3*pi/3=288*pi; limas12^2*8/3=384; rasio limas:bola=4:3pi; bola r12 volumenya2304pi>384. |
| `mcma-19-4-8` | A,B,D | Prisma=3*limas pada alas/tinggi sama; rasio bola1:27; bola pi*d^3/6 tidak sama dengan limas d^3/3; rumus diameter benar. |
| `kategori-19-4-9` | 1,2,3 | Alas8*6/2=24; volume360; tinggi30 memberi720; alas12 pada tinggi15 memberi180 bukan200. |
| `kategori-19-4-10` | 1,2,3 | Bola r10=4000pi/3; r20 faktor8; r5=500pi/3; diameter20 tetap r10 sehingga volume tetap. |
| `pg-19-5-1` | A | Air limas10^2*12/3=400; prisma40*15=600; sisa200. |
| `pg-19-5-2` | C | Bola288pi; tiap limas12^2*2pi/3=96pi; tepat3 limas. |
| `pg-19-5-3` | B | Volume1=12^2*10/3=480; alas2=8*18=144; tinggi3*480/144=10. |
| `pg-19-5-4` | D | Alas belahketupat12*16/2=96; tinggi960/96=10. |
| `pg-19-5-5` | A | Air=(10*12/2)*20/2=600; bola=4*(22/7)*7^3/3=4312/3; sisa2512/3=837.333..., dibulatkan dua desimal837.33. |
| `mcma-19-5-6` | A,B,C | Vprisma=A*t; Vlimas=A*t/3. Rasio3:1 tetap saat t keduanya digandakan. tprisma=3*tlimas memberi rasio9:1 bukan1:1. |
| `mcma-19-5-7` | A,B,C | Vlimas=(2r)^2*r/3=4r^3/3; Vbola=pi*Vlimas>Vlimas untuk r>0; rbola digandakan memberi8pi*Vlimas bukan2. |
| `mcma-19-5-8` | A,B,C | Kubus1000; limas1000/3; kosong2000/3; rasio limas:kosong1:2 bukan1:3. |
| `kategori-19-5-9` | 1,2,3 | Rusuk3 memberi volume27; rsetengah memberi1/8; tinggi2 memberi2; bola diameterd=pi*d^3/6 dan limas=d^3/6, rasio pi bukan4. |
| `kategori-19-5-10` | 1,2,3 | Tinggi2 memberi1200; alas3 memberi1800; mengurangi tinggi5 hanya membentuk prisma valid bila t>5. Semua rusuk2 memberi8*600=4800 bukan1200. |

## Pemakaian dan verifikasi

Bank baru: `variant_gen/data/drill-1-indicators-16-19-levels-4-5/`. Loader default memuatnya otomatis. Bank eksplisit/custom tetap terisolasi. Restart proses UI/API yang sudah berjalan untuk memuat tambahan.

Cakupan indikator 16?19 kini 200 original: 112 generator existing, 8 original konseptual dengan 22 stok existing, 66 original baru tanpa generator, 14 HOLD_SOURCE. Semua indikator memiliki level1?5 masing-masing10 soal.

Perintah reproduksi (menolak menimpa berkas output yang sudah diedit):

```powershell
python -B variant_gen/tests/import_drill_16_19_level45.py
python -B -m unittest discover -s variant_gen/tests -p test_drill_16_19_level45_import.py
```

Tes khusus: 3 lulus, mencakup 80 identitas/provenance, status HOLD, kategori khusus, pemuatan bank default dan lima HTTP GET representatif tanpa akses database/penyimpanan varian.

Validasi regresi tambahan: `test_catalog.py` 2 lulus, `test_bank_coverage.py` 9 lulus, `test_webui.py` 17 lulus. Total bersama tes impor: **31 tes lulus**. `git diff --check` lulus. Builder dijalankan ulang dan menghasilkan output identik.
