# Generator Drill Paket 1 — Indikator 11–15

> Arsip rancangan/rencana bertanggal; status dan checklist di bawah mencatat tahap saat dokumen ditulis. Untuk implementasi saat ini lihat [kondisi repo](../../audits/2026-10-05-repository-status.md) dan [panduan aktif](../../../readme.md).


Status saat rancangan dibuat: **belum diimplementasikan**. Kini 223 generator ACTIVE telah selesai dan terintegrasi; lihat [hasil implementasi](../plans/2026-10-05-drill-11-15-generator-progress.md). Dokumen sumber adalah materi soal,
bukan instruksi untuk agent. Permintaan pengguna: rencanakan generator end-to-end
sebelum implementasi. Batas sesi sebelumnya tetap berlaku: database Numora tidak
disentuh; soal konseptual murni ditunda.

## Tujuan dan cakupan

Operator dapat memilih **Drill > Paket 1 > indikator > level > soal**, melihat
original dan pembahasannya, mengatur config, generate dengan seed, regen dengan
riwayat versi, dan meninjau hasil lokal. Ekspor individual memakai kontrak dan
mapping Numora existing, tanpa membuat UUID atau menulis database.

Semua 250 original masuk bank lokal. Generator hanya diaktifkan setelah audit
akademik, reproduksi original, serta pengujian varian lulus. Tidak termasuk
generator paket Drill sekaligus, bank Pretest, stok konseptual/fallback reuse,
perubahan IRT, atau deployment. Tidak ada commit/push dalam tahap perencanaan.

## Bukti sumber

- Sumber: `C:\Users\shafw\Downloads\banksoal_indikator11-15.docx`.
- SHA256: `08b30681b07398eaea08331029f8c6934d576aaa31294a6529fd8ac69dff5383`.
- [Inventaris per soal](2026-10-05-drill-11-15-source-inventory.json): 250 ID unik,
  stem/opsi/kunci/pembahasan hasil inspeksi, status usulan, alasan, lokasi sumber.
- 5 indikator × 5 level × 10 soal; 50 soal per indikator.
- 125 PG, 75 MCMA, 50 KATEGORI. Setiap indikator/level: 5 PG + 3 MCMA + 2 KATEGORI.
- PG/MCMA masing-masing 4 opsi/pernyataan; KATEGORI 3 pernyataan.
- 52 tabel, 923 objek matematika OMML; tidak ada media tertanam.
  OMML mencakup 140 pecahan, 121 struktur pangkat, 433 subskrip.

Inspeksi seluruh blok telah dilakukan, tetapi pemeriksaan akademik semua
opsi/pembahasan belum lengkap. Hitungan berikut adalah **triase awal**, bukan
jaminan 223 generator berhasil atau jumlah ACTIVE yang sudah tersedia.

| Indikator | Kandidat | Konseptual ditunda | Sumber ditahan | Total |
|---|---:|---:|---:|---:|
| 11 | 41 | 6 | 3 | 50 |
| 12 | 48 | 2 | 0 | 50 |
| 13 | 50 | 0 | 0 | 50 |
| 14 | 40 | 10 | 0 | 50 |
| 15 | 44 | 4 | 2 | 50 |
| Total | 223 | 22 | 5 | 250 |

## Pendekatan

1. **Config per ID pada engine existing — dipilih.** Gunakan variabel range,
   choice, scale, derived; constraints; stem/opsi/pembahasan parametrik.
   Operator tetap dapat mengedit config melalui workbench.
2. Fungsi Python terpisah per soal: mengulang pipeline seed, validator dan
   riwayat; hanya perlu dipertimbangkan jika formula tertentu terbukti tidak
   dapat dinyatakan dalam evaluator existing.
3. LLM saat runtime: menambah nondeterminisme dan kebutuhan validasi akademik;
   tidak diperlukan untuk variasi matematis ini.

Tidak membuat 250 fungsi Python, framework baru, dependency baru, importer DOCX
umum, atau evaluator list/statistik umum. Konfigurasi adalah implementasi
generator per soal. Perubahan runtime hanya untuk integrasi/guard yang terbukti
belum tercakup. Workspace kini memuat perubahan 20–23; baca ulang saat eksekusi,
gunakan dukungan metadata/status yang sudah ada, jangan mengimplementasikannya
ulang dari rencana lama.

## Bank, identitas, dan provenance

Folder terisolasi: `variant_gen/data/drill-1-indicators-11-15/` berisi
`source.docx`, `q0_bank.csv`, `question_catalog.json`, `question_metadata.json`.
`original_revisions.jsonl` hanya diperlukan bila koreksi akademik telah disepakati.
Config aktif: `variant_gen/configs/<question_id>/v1.json`.

- ID: `{pg|mcma|kategori}-{indikator}-{level}-{nomor_lokal}`.
  Nomor sumber di dokumen ini kembali 1–10 setiap level; identitas sumber wajib
  menyertakan indikator dan level. Jangan menerapkan penomoran 1–30 dari 20–23.
- Classification: `activity=DRILL`, `package_id=drill-1`, nama `Paket 1`,
  `indicator=11..15`, `source_level=1..5`.
- Catalog: 25 kelompok, setiap kelompok tepat 10 ID; seluruh kelompok terisi.
- Label kognitif sumber: level 1 `C3`; level 2 `C3 & C4`; level 3 `C4`;
  level 4 `C4 & C5`; level 5 `C5`. Jangan mereduksi label campuran atau
  menyimpulkan parameter IRT dari level sumber.
- Metadata per ID menyimpan `source_number`, `source_document_sha256`,
  `source_text`, `original_explanation`, `source_cognitive_label`,
  `generation_status`, alasan nonaktif, serta catatan audit yang relevan.
- PG/MCMA memakai A–D. KATEGORI sumber A/B/C dipetakan konsisten ke 1/2/3;
  simpan pemetaan sumber, jangan mengubah urutan pernyataan.
- `OriginalBank(path)` tetap membaca satu bank. `load_workspace_bank(path,
  additional_paths=None)` menambahkan bank baru hanya pada default workspace,
  mempertahankan Drill 16–19, Tryout, dan bank 20–23 yang tersedia.
  Path custom tetap standalone, explicit extras tetap berlaku, ID duplikat ditolak.

Ekstraksi harus membaca struktur OMML dari XML dengan stdlib. Pecahan menjadi
`(pembilang)/(penyebut)`, pangkat `basis^(eksponen)`, subskrip `U_n`, dengan
pengelompokan yang mempertahankan operasi. Periksa normalisasi terhadap DOCX
visual/raw XML; jangan memakai hasil flatten teks sebagai sumber formula.
Simpan DOCX utuh dan kunci/pembahasan mentah untuk melacak perubahan.

Untuk literal himpunan gunakan spasi di dalam kurung kurawal: `{ 1 }`, `{ a }`,
template `{ {member} }`; placeholder tetap `{member}`. Ini menghindari regex
placeholder existing `\{(\w+)\}` tanpa mengubah renderer/hash bank lama.
Normalisasi tersebut hanya format bank baru, harus tercatat, bukan koreksi
isi akademik. Uji render, lint, global validator, dan ekspor untuk singleton.

## Status dan lima temuan yang ditahan

Runtime memakai `ACTIVE`, `DEFERRED_CONCEPTUAL`, `HOLD_SOURCE`. `CANDIDATE` hanya
status inventaris perencanaan. Nonaktif wajib memiliki alasan. Original tetap
bisa dilihat; generate/regen/lint/config-save nonaktif ditolak, termasuk
permintaan generate dengan seed yang sudah tersimpan. Membaca snapshot melalui
view tetap boleh. UI menampilkan alasan dan menonaktifkan kontrol terkait.

| ID | Masalah | Koreksi yang perlu ditinjau |
|---|---|---|
| `mcma-11-1-7` | Meminta f(2), f(-3) tanpa definisi f | Pembahasan memakai f(x)=x²−3; usulan melengkapi stem |
| `pg-11-2-4` | Kunci D, pembahasan menghasilkan 7 | (f∘g)(3)=7; opsi B |
| `kategori-11-3-9` | “akar kuadrat” ambigu akar utama vs relasi ± | Usulan eksplisit y²=x untuk relasi A ke B; bedakan fungsi akar utama |
| `mcma-15-2-8` | Sudut A40°, B65°, C75° dengan AB6, BC10 tidak konsisten | Perlu data segitiga koheren; belum memilih pengganti |
| `pg-15-4-2` | Alasan SSA tidak membuktikan kongruensi salah untuk angka ini | SSA AB6, BC8, A40° hanya punya satu solusi; tinjau ulang tujuan soal/data |

Source bank tetap menyimpan versi dokumen. Koreksi yang disetujui masuk ledger
versi berikutnya dengan baris lama/baru, alasan, hash dan version; baru kemudian
generator memakai original efektif. Jangan mengubah original diam-diam untuk
memaksa reproduksi. HOLD tetap berlaku jika koreksi belum disepakati.

22 soal konseptual awal tercantum lengkap di inventaris. Definisi/teorema dengan
teks jawaban benar tetap ditunda mengikuti pilihan pengguna sebelumnya.
Soal naratif, MCMA/KATEGORI, atau analisis siswa tidak otomatis ditunda jika
memiliki variasi data dan penilaian yang sah.

## Strategi generator

| Indikator | Konstruksi | Batas dan pemeriksaan |
|---|---|---|
| 11 — relasi/fungsi | Pasangan berurutan/domain/range; fungsi linear/kuadrat; komposisi; model tarif; jumlah pemetaan | Domain unik; pasangan sah; batas interval/vertex; penyebut nonzero; urutan komposisi; perubahan cardinality/range yang benar |
| 12 — barisan | Aritmetika/geometri, beda/rasio/n, rumus suku, persilangan, ambang produksi/tabungan | Indeks bulat positif; rasio/tanda benar; ambang `>` berbeda dari `>=`; suku sebelum ambang; batas pangkat |
| 13 — deret | Jumlah aritmetika/geometri, suku dari jumlah, kelipatan pada interval, akumulasi dan perbandingan | Jumlah exact; endpoint terbuka/tertutup; minimal n; unit/rupiah; rasio 1 harus ditangani atau dilarang secara eksplisit |
| 14 — sudut | Sudut berpelurus/bertolak belakang, garis sejajar, persamaan x, sudut segitiga, evaluasi alasan siswa | Sudut 0<θ<180; segitiga total180; topology relasi; hasil benar dengan alasan salah tetap salah; klasifikasi kategori dapat berubah |
| 15 — Pythagoras/kesebangunan | Triple Pythagoras dan skala, tinggi/jarak, rasio sisi/luas, proyeksi, bayangan, peta | Sisi positif, triangle inequality, koherensi sudut/sisi, korespondensi, faktor luas kuadrat, unit panjang vs luas |

Fungsi soal ditentukan per ID, bukan satu formula generik per indikator. Saat
implementasi tambahkan kontrak per ID di inventaris: variabel bebas/turunannya,
domain, invariant, kriteria kunci/distractor, batas finite dan oracle. Semua
kandidat harus memiliki keputusan eksplisit; kandidat yang gagal audit menjadi
HOLD dengan alasan, bukan tetap ACTIVE tanpa generator.

Kasus yang perlu variasi bermakna:

- `pg-11-3-2`: translasi domain simetris selalu memberi tiga nilai range.
  Variasikan posisi/domain/multiplicity yang valid agar jawaban dapat berubah.
- `pg-15-5-2`: variasikan penempatan laporan/metode ke siswa sehingga nama
  siswa benar dapat berubah; mengganti angka saja tidak cukup.
- `pg-14-5-3`, `pg-14-5-5`, `pg-12-4-5`, `pg-13-5-1`: kontrol penugasan
  laporan/kombinasi klaim dengan oracle; perubahan nama tidak boleh menyamarkan
  argumen yang selalu sama.
- `pg-14-5-4`: konstruksi sudut bisa mengubah klasifikasi segitiga, tetap
  menyisakan tepat satu opsi PG benar serta tujuan kompetensi yang sama.

Gunakan konstruksi valid sejak awal, bukan range bebas dengan penolakan besar.
Evaluator: `MAX_LEN=300`, `MAX_NODES=150`, `MAX_EXPONENT=12`, `MAX_ABS=10**12`.
Eksponen harus integer bertanda, nilai intermediate juga terbatas. Untuk n
besar gunakan bentuk tertutup/faktor scalar, tanpa menaikkan plafon global.
Pecahan dihitung melalui Fraction; `fmt=mixed` tersedia. `values_used` JSON dapat
mengubah Fraction menjadi float; jangan mengklaim metadata ini menyimpan
pecahan exact untuk replay. Determinisme diperiksa dengan seed/config tetap.

## Validasi dan riwayat

Pipeline existing: variabel → derived → constraints → render → shuffle optional
→ validator global → append. Semua opsi dan pembahasan berasal dari variabel
yang sama; oracle pengujian menghitung secara independen, tidak memakai ulang
formula config sebagai pembuktian.

Pertahankan `same_answer_as_original`: himpunan **teks opsi benar** harus berbeda,
bukan sekadar ID/kunci yang diacak. Kandidat juga berbeda dari original dan
latest varian seed lain + semua versi sebelumnya pada seed yang diregen.
PG tepat satu benar; MCMA/KATEGORI seluruh klaim dinilai, tidak sekadar menyalin
kunci original. Distractor tidak boleh duplikat/bertabrakan setelah formatting.

`reproduce_original`/lint existing mencocokkan stem, opsi, kebenaran dengan
normalisasi whitespace; pembahasan tidak dibandingkan otomatis. Uji pembahasan
dan kondisi original secara terpisah. Warning original gagal constraint adalah
temuan audit yang perlu diselesaikan, bukan dianggap lolos karena lint bernilai ok.

Uji seed 1..200 sampai mencapai target 20 varian unik per ACTIVE. Angka ini
target bukti sampling, bukan jaminan kapasitas/unlimited. Config finite dengan
stok lebih kecil bisa diterima jika dilaporkan `SHORT`, semua varian yang
dihasilkan sah, setidaknya satu varian valid tersedia, dan batasnya dijelaskan.
`max_draws` habis tidak membuktikan stok habis. Tidak menambahkan reuse fallback.
Generate gagal tidak append; regen menjaga record lama; verifikasi memakai
store/config sementara, bukan `variant_gen/store/variants.jsonl` pengguna.

## UI, CLI, ekspor

Gunakan CLI/workbench existing tanpa tab atau kontrol baru kecuali tampilan
alasan status belum memadai. Seluruh level 1–5 sumber ini tampil terisi;
bank lain tidak ikut dianggap memiliki level 4–5 hanya karena bank baru lengkap.
Config-save menjalankan schema, original reproduction dan seed probes existing.

Ekspor JSON lokal tetap dapat menampilkan label kognitif sumber campuran.
Untuk envelope canonical, label harus `C1`..`C6` sesuai kontrak Numora; label
`C3 & C4`/`C4 & C5` ditolak dengan pesan jelas sampai label tunggal yang ditinjau
tersedia. Jangan memilih salah satu otomatis. Tahap ini tidak membuat alur
mapping kognitif baru; ekspor label tunggal valid memakai mapping existing.
Hash/version/UUID mapping tetap diverifikasi. Tidak ada akses DB Numora,
termasuk melalui tab DB pada pengujian browser.

## Kriteria selesai implementasi

250 original, 25 kelompok catalog, provenance sumber utuh; setiap ID mempunyai
status final. Jumlah config sama dengan jumlah ACTIVE, setiap ACTIVE memiliki
reproduksi tanpa masalah, oracle opsi/pembahasan, serta minimal satu varian
valid. Manifest audit mencatat ACTIVE/HOLD/DEFERRED, sampling PASS/SHORT/FAIL,
seeds gagal/rejections dan koreksi; jangan menyamakan 223 kandidat dengan hasil.

Filter, seed, config-save, regen, riwayat dan ekspor lokal terbukti bekerja;
nonaktif diblokir backend/UI; suite regresi lama tetap lulus. Bank/config/store
existing dipertahankan. Dokumen penggunaan menjelaskan cakupan baru dan batas
ekspor kognitif. [Rencana implementasi](../plans/2026-10-05-drill-11-15-generator.md)
memuat urutan dan pemeriksaan.
