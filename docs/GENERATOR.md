# Referensi generator

## Kondisi terbaru indikator 1-5 setelah persetujuan pengguna

**ENGINEERING DECISION - instruksi pengguna:** 28 koreksi dan aktivasi generator lokal telah disetujui. Indikator 1-5 kini memuat **250 original**, dengan **100 generator level 4-5**. Total indikator 1-5: 238 generator, 10 original konseptual dengan stok manual, dan 2 HOLD lama pada level 1-3.

Bank tambahan `variant_gen/data/drill-1-indicators-1-5-levels-4-5-approved/` mempertahankan original v2/config v1 yang sama dengan draf yang direview. Persetujuan dicatat sebagai `USER_APPROVED_CORRECTION`; arsip draf tetap utuh. Penyesuaian otomatis, publikasi database, dan persetujuan kesetaraan kesulitan tidak diaktifkan.

[Laporan aktivasi dan catatan persetujuan](audits/2026-10-21-drill-1-5-level45-approved/README.md). Angka dan status draf pada laporan tahap sebelumnya merupakan snapshot sebelum persetujuan ini. Restart proses lokal yang sudah berjalan untuk memuat bank/config tambahan.

## Status terbaru 21 Oktober 2026: batch kedua generator indikator 20-23

Tambahan **27 generator** (indikator 20=4, 21=8, 22=11, 23=4). Total **54/80 original baru (67,5%)** sudah memiliki generator; tersisa **13 menunggu generator/stok + 13 HOLD**. Seluruh indikator 20-23: **200 original, 156 generator, 18 konseptual/50 stok**. Batch ini lolos 837 input dan regresi 50 tes. Original serta stok tetap; hasil runtime tidak disimpan, database tidak diubah. Pembaruan sebelumnya merupakan snapshot historis.

[Daftar generator dan validasi](audits/2026-10-21-drill-20-23-level45-batch2/README.md).

## Status terbaru 21 Oktober 2026: 27 generator indikator 20-23 level 4-5

Tahap pertama **27/80 soal (33,75%)** selesai: indikator20=3,21=8,22=6,23=10. Seluruh837 input diuji;810 varian unik valid. Total indikator20-23: **200 original,129 generator,18 konseptual/50 stok,40 menunggu generator/stok,13 HOLD**. Original tidak direvisi, hasil runtime tidak disimpan, database utama tidak diubah. Angka pada pembaruan sebelumnya merupakan snapshot historis.

[Daftar generator dan validasi](audits/2026-10-21-drill-20-23-level45-batch1/README.md).

## Status terbaru 21 Oktober 2026: impor original indikator 20-23 level 4-5

80 original selesai diaudit dan masuk bank lokal: **67 ACTIVE, 13 HOLD_SOURCE**. Indikator20-23 kini lengkap **200 original**, lima level x sepuluh soal per indikator. Tambahan ini belum mempunyai generator/stok; bank lama tetap102 generator dan18 konseptual/50 stok. Kunci primer serta sumber mentah dipertahankan; database utama tidak diubah. Pembaruan bertanggal sebelumnya merupakan snapshot historis.

[Audit per soal dan daftar HOLD](audits/2026-10-21-drill-20-23-level45-import/README.md).

## Status terbaru 21 Oktober 2026: indikator 16-19 lengkap

Seluruh 80 original level 4-5 kini terlayani: **65 generator + 15 konseptual dengan 30 stok**, 0 HOLD. Tambahan tahap akhir: 38 generator dan 30 stok; 14 original direvisi lokal v2 dengan sumber mentah tetap tersimpan. Total indikator 16-19: **200 original, 177 generator, 23 konseptual/52 stok**. Generate runtime tidak disimpan; database utama tidak diubah. Angka pada pembaruan sebelumnya merupakan snapshot historis.

[Laporan dan bukti validasi](audits/2026-10-21-drill-16-19-level45-completion/README.md).

## Indikator 16?19 level 4?5: 27 generator pertama (21 Oktober 2026)

27 dari80 original baru sudah mempunyai config v1 (33,75%): indikator16=2,17=8,18=9,19=8. Seluruh837 input diuji; masing-masing30 varian unik valid. Total indikator16?19 kini139 generator/200 original,8 konseptual/22 stok existing,39 menunggu generator/stok,14 HOLD. Original tidak direvisi, metadata generator_status diperbarui. Hasil runtime tidak disimpan. [Laporan dan bukti](audits/2026-10-21-drill-16-19-level45-batch1/README.md).

## Impor original indikator 16?19 level 4?5 (21 Oktober 2026)

Loader default kini memuat `data/drill-1-indicators-16-19-levels-4-5/q0_bank.csv`: 80 original tambahan, 66 ACTIVE dan 14 HOLD_SOURCE. Seluruhnya belum memiliki config maupun stok; generator_status NOT_IMPLEMENTED. Total indikator16?19: 200 original,112 generator existing,8 konseptual/22 stok existing,66 menunggu generator,14 HOLD. Revisi sumber tidak dilakukan. [Validasi per soal](audits/2026-10-21-drill-16-19-level45-import/README.md).

Generator per soal berupa JSON; engine Python dipakai bersama. Tambahkan config sebelum custom function Python. Tidak ada LLM atau `eval` dalam pipeline.

## Bank dan katalog

| File dalam `variant_gen/` | Isi |
|---|---|
| `data/q0_bank.csv` | 120 original Drill |
| `data/question_catalog.json` | Paket, indikator, level sumber, membership termasuk level kosong |
| `data/original_revisions.jsonl` | Revisi original Drill setelah CSV dibaca |
| `data/tryout-1/q0_bank.csv` | 30 original Tryout |
| `data/tryout-1/question_catalog.json` | Paket/bab dan urutan soal |
| `data/tryout-1/question_metadata.json` | Nomor sumber, difficulty, status/alasan, notes, teks/pembahasan sumber |
| `data/tryout-1/original_revisions.jsonl` | Koreksi original Tryout |
| `data/tryout-1/source.docx` | Source verbatim |
| `data/drill-1-indicators-1-2/` |60 original level1–3,50 config, katalog6 grup, metadata dan DOCX provenance |
| `data/drill-1-indicators-3-5/` |90 original level1–3,88 config,9 grup, metadata/DOCX provenance |
| `data/drill-1-indicators-6-10/` | 150 original, katalog, metadata, source DOCX |
| `data/drill-1-indicators-11-15/` | 250 original, katalog, metadata, source DOCX dan audit.json |
| `data/drill-1-indicators-20-23/` | 120 original Drill tambahan, katalog, metadata, source DOCX; ledger kosong karena belum ada koreksi disetujui |

`OriginalBank(path)` membaca satu bank. CLI/UI memakai `load_workspace_bank`: path default Drill menggabungkan Tryout dan Drill indikator1–2,3–5,6–10,11–15,20–23 bila tersedia; `--bank` custom tetap standalone. API Python menerima `additional_paths` eksplisit; ID duplikat ditolak. Katalog/metadata/ledger harus di samping CSV. CSV tanpa katalog unclassified; paket custom membutuhkan katalog sesuai aktivitasnya.

ID Drill `pg-16-1-3`: format PG, indikator 16, level sumber 1, soal 3. ID Tryout `tryout-1-b2-q04`: paket 1, bab 2, soal 4. ID lokal bukan UUID canonical database. Level sumber berbeda dari difficulty, cognitive level dan parameter IRT.

Ledger menjaga row source/replacement dan versi berurutan; loader memvalidasi identitas/hash lalu mengekspos original efektif. Salin ledger bersama CSV; CSV saja menunjukkan source sebelum koreksi. Klasifikasi tidak masuk hash konten original.

Metadata status: `ACTIVE`, `HOLD_SOURCE`, `DEFERRED_CONCEPTUAL`; non-ACTIVE wajib alasan dan menolak generate/lint/config save. `category_labels` opsional: dua label unik nonempty, hanya KATEGORI. Key CSV memilih kategori pertama, bukan selalu kebenaran. Label nondefault masuk hash original; respons memuat `answer_categories` seluruh pernyataan. UI membaca label respons; ekspor kontrak boolean menolak kategori berlabel khusus.

## Stok konseptual manual

Cakupan lengkap: **70 original/215 stok VERIFIED**: Drill67/206, masing-masing2–4; Tryout3/9, masing-masing3. Review tugas aktual pada [audit Drill](audits/2026-10-06-conceptual-stock-audit.md) dan [audit Tryout](audits/2026-10-07-tryout-conceptual-stock-audit.md). Pewarisan label kognitif tidak membuktikan kesetaraan kesulitan.

`variant_gen/data/conceptual_stock.json` menyimpan konten lengkap yang ditulis offline: maksimum empat varian tambahan per original. Tidak memakai generator/config/seed. `conceptual_stock.py` memvalidasi schema, hash/versi original, opsi, kunci, indeks dan duplikasi; hanya VERIFIED dilayani. DRAFT tetap divalidasi tetapi tidak tersedia. `same_answer_as_original` dikecualikan hanya untuk stok, aturan numerik tetap berlaku.

Respons memakai `source_kind: conceptual_stock`, `stock_index`, ID stabil dan versi stok; seed/config null. Label KATEGORI custom tetap diwariskan. Asset dibaca saat server mulai; restart setelah perubahan asset. Tidak ada pencatatan pemakaian atau penulisan asset oleh runtime. Saat konten slot berubah, naikkan stock_version; saat original berubah, provenance stok harus direview ulang. ID+versi mengidentifikasi revisi, bukan nomor selector saja. [Audit cakupan](audits/2026-10-06-conceptual-stock-audit.md).

## Config

Lokasi `variant_gen/configs/<question_id>/v<N>.json`. Folder/file harus sesuai `question_id`/`config_version`. CLI generate memakai versi terbaru; UI dapat melihat config historis.

| Field | Aturan |
|---|---|
| `question_id`, `config_version` | Identitas soal/versi config |
| `original_hash` | Hash original efektif dari command hash |
| `original_values` | Nilai input non-derived untuk mereproduksi original |
| `variables` | Berurutan; formula mengacu variabel sebelumnya |
| `constraints` | Ekspresi boolean wajib benar |
| `stem` | Template soal |
| `options` | List `{id,text,correct}`; correct boolean/formula |
| `explanation` | Template pembahasan wajib tidak kosong |
| `shuffle` | Default false; acak/label ulang opsi, kunci mengikuti |
| `max_draws` | Default 200; integer 1–10.000; batas pencarian kandidat |

Referensi config nyata: [suhu Tryout](../variant_gen/configs/tryout-1-b1-q01/v1.json), [volume Drill](../variant_gen/configs/pg-18-3-1/v1.json). Jangan mengedit versi yang sudah dipakai.

### Variabel dan ekspresi

| `gen` | Contoh spec | Perilaku |
|---|---|---|
| `range` | `{"gen":"range","range":[7,35],"step":7}` | Kelipatan step dalam rentang inklusif; default 1 |
| `choice` | `{"gen":"choice","values":[2,3,5]}` | Pilih satu angka/teks |
| `scale` | `{"gen":"scale","base":12,"factor":[0.75,1.5],"step":1}` | Base × faktor acak, dibulatkan ke step |
| `derived` | `{"gen":"derived","expr":"a+b"}` | Hitung dari variabel sebelumnya |

Spec mendukung `filters`, `min`, `max`, `step`, `fmt`, `decimals`. Filter: `nominus`, `positive`, `nozero`, `nodec`, `step100` atau `step<N>` positif. `step` juga membatasi validitas nilai. Key custom `unit`/`role` belum didukung.

Placeholder `{name}` memakai nilai variabel. Angka literal/pi/fakta bangun tetap konstanta template, bukan otomatis parameter bebas untuk di-adjust.

| `fmt` | Tampilan |
|---|---|
| `id` default | `1.570`, `3,14`; decimals default 2 |
| `raw` | Tanpa pemisah ribuan; formatter angka existing |
| `mixed` | Pecahan exact reduced: 13/3 menjadi `4 1/3`, −13/3 menjadi `-4 1/3` |

Operasi `+ - * / // % **`, perbandingan, `and/or/not`, conditional `a if cond else b`. Fungsi `abs min max round floor ceil sqrt gcd`. Evaluator AST membatasi ekspresi; atribut/import/I/O/kode Python bebas ditolak. Rasional memakai `Fraction`, rounding half-up. `values_used` pecahan menjadi float JSON; metadata ini tidak selalu exact untuk replay.

## Validator dan determinisme

Pipeline: input/derived → filter variabel → constraints → render → shuffle opsional → validator global. Draw ditolak dicoba ulang sampai max_draws.

- Jumlah opsi sama original; teks tidak kosong/duplikat, placeholder tuntas.
- PG tepat satu benar; MCMA minimal satu dan jumlah benar sama original; KATEGORI jumlah benar sama original, termasuk nol/semua benar.
- Kandidat tidak sama original; himpunan **teks jawaban benar** berbeda. `same_answer_as_original` membandingkan teks, bukan huruf kunci; shuffle saja tidak cukup.
- Duplicate check memakai perbandingan in-memory yang diberikan pemanggil; generate numerik stateless tidak membaca riwayat seed. Loader stok membandingkan semua item dalam satu keluarga, termasuk DRAFT; urutan opsi diabaikan.

RNG memakai question ID, seed, draw, nama variabel. Config dan seed sama memberi konten sama. Tidak ada snapshot/riwayat hasil generator; seed lain tidak menjamin konten unik.

`lint` memeriksa schema/hash, reproduksi stem/opsi/kunci original dengan normalisasi whitespace, probe N seed unik di memori. Pembahasan tidak dibandingkan terhadap source. Warning stok tidak otomatis gagal bila masih ada kandidat valid; sampel bukan kapasitas exact.

## Menambah atau merevisi soal

1. Tetapkan aktivitas/paket/indikator+level atau bab, ID, format, kompetensi, stimulus, opsi, kunci, pembahasan, sumber.
2. Tambahkan original baru dan membership katalog. Koreksi existing melalui ledger row/versi/hash yang tepat.
3. Buat config versi baru; derive jawaban/distractor dari input; jaga domain/constraints agar tugas akademik sesuai.
4. Jalankan hash/lint, review reproduksi original, matematika dan kunci dengan oracle independen.
5. Probe respons tanpa penyimpanan, run suite, review kurikulum sebelum publikasi. Jangan melonggarkan validator global demi satu soal.

Config tetap berversi; editor membuat `v<N+1>.json`. Setiap generate membaca config terbaru dan menyertakan hash. Tidak ada snapshot/riwayat varian untuk mendeteksi perubahan config setelah dipakai.

## Cakupan dan koreksi

Drill indikator16–19: 112/120 config, seluruh indikator18–19 tercakup. [Review skip](../variant_gen/soalskip.md) mencatat 12 soal awal: empat mendapat config, delapan tersedia melalui stok manual. Indikator20–23: 102/120 aktif, 0 HOLD_SOURCE, 18 DEFERRED_CONCEPTUAL; [audit revisi](audits/2026-10-07-revised-20-23-generator-audit.md) memuat 20 kandidat unik per generator baru. Audit 5 Oktober merekam kondisi sebelum revisi. Subtotal indikator16–23: 214 config/240 original.

Drill indikator 6–10: 140/150 aktif, 1 HOLD_SOURCE, 9 DEFERRED_CONCEPTUAL dengan stok manual. Sebelas original v2 hasil revisi kini mempunyai config v1; `mcma-6-3-7` tetap ditahan. [Audit revisi](audits/2026-10-07-revised-6-10-generator-audit.md) mencatat pemeriksaan setiap opsi dan batas parameter. Bank `variant_gen/data/drill-1-indicators-6-10` dimuat otomatis oleh UI/CLI; level 4–5 kosong sesuai sumber. Contoh: `python -B variant_gen/cli.py gen pg-6-1-5 s1 --json`. Hasil tidak disimpan; proses UI yang sudah berjalan perlu dimulai ulang untuk memuat metadata baru.

Tryout:27/30 generator aktif; `tryout-1-b1-q07` (alasan operasi), `tryout-1-b4-q02` (peluang), `tryout-1-b4-q06` (bias/sampling/jenis data) masing-masing memiliki3 stok manual VERIFIED. UI/CLI per soal dapat memilih stok berulang; generate paket tetap memakai original untuk ketiganya. [Audit stok](audits/2026-10-07-tryout-conceptual-stock-audit.md). `DEFERRED_CONCEPTUAL` tetap menolak generator/config.

| Original efektif v2 | Koreksi lokal |
|---|---|
| `pg-16-3-5` | Segitiga siku-siku 3–4–5; dua alas 12 cm², luas prisma 132 cm² |
| `mcma-19-3-6` | Benda terpisah; limas 15 cm tidak muat dalam kubus 10 cm |
| `tryout-1-b2-q04` | 11.000 + 5.000 = 16.000; kunci C |
| `tryout-1-b4-q04` | Bandingkan rentang, jangan simpulkan varians dari rentang |

Normalisasi source dicatat dalam metadata. q06 deferred: jumlah sampel sama per kelas belum tentu proporsional. Kebenaran teknis tidak menggantikan approval kurikulum atau kalibrasi empiris.

Drill indikator11–15: 227/250 generator aktif, tersedia level1–5. [Impor revisi 7 Oktober](audits/2026-10-07-drill-11-15-source-revision.md) memperbarui lima soal menjadi original v2; [empat generator revisi](audits/2026-10-07-revised-11-15-generator-audit.md) kini aktif dan menghasilkan masing-masing 20 varian unik teruji. Satu soal tetap HOLD_SOURCE karena panjang sisi belum cocok dengan sudut; 22 soal tanpa generator memakai stok manual. Status bank saat ini 227 ACTIVE, 1 HOLD_SOURCE, dan 22 DEFERRED_CONCEPTUAL. Penyesuaian otomatis belum aktif; batas angka tidak diperluas otomatis. [Audit awal](audits/2026-10-05-drill-11-15-generator-audit.md) tetap merekam versi sebelum revisi. Indikator1–2 mempunyai50 config/60 original level1–3. Penghitungan repo lokal 7 Oktober:719 config Drill/790 original; bersama Tryout:746 config/820 original, termasuk pembaruan indikator lain yang tersedia. Ekspor kanonik mensyaratkan satu label kognitif C1–C6; label sumber gabungan tetap disimpan lokal.

Indikator1–2:50 config/60 original;50 ACTIVE,9 DEFERRED_CONCEPTUAL,1 HOLD_SOURCE. Indikator3–5:88 config/90 original;88 ACTIVE,1 DEFERRED_CONCEPTUAL,1 HOLD_SOURCE. [Audit generator revisi 7 Oktober](audits/2026-10-07-revised-1-5-generator-audit.md) mengaktifkan40 config v1 untuk original v2. Kapasitas unik default25–40 per soal; pemanggilan Generate dapat diulang tanpa batas stok. `pg-1-2-1` dan `pg-5-3-3` masih HOLD_SOURCE. Sepuluh soal konseptual memakai stok manual. [Snapshot impor](audits/2026-10-07-drill-1-5-source-revision.md) dan [audit awal indikator3–5](audits/2026-10-06-drill-3-5-generator-audit.md) merekam kondisi sebelum aktivasi.


## Penambahan indikator 1-5 level 4-5, tahap 1 (20 Oktober 2026)

**ENGINEERING DECISION - instruksi pengguna:** implementasi 33 dari 100 soal sumber baru; menggantikan batas level 1-3 historis hanya untuk 33 ID yang disetujui. Bank tambahan `variant_gen/data/drill-1-indicators-1-5-levels-4-5-batch1/` dimuat eksplisit oleh `load_workspace_bank` pada path default. `OriginalBank` dan custom `--bank` tetap membaca bank tunggal. Katalog tambahan berisi sepuluh kelompok parsial dalam `drill-1`; `source_number` tidak dipadatkan. Tidak mengimpor 67 soal antrean ke bank runtime.

Config memakai bahasa/engine yang sama, tanpa dependensi atau evaluator baru. Parameter `k` dibatasi dalam setiap config; setelah constraints dan validator global, kapasitas dihitung dengan enumerasi seluruh input, bukan jumlah seed. Dua config dengan jawaban berupa alasan kualitatif menyertakan hasil perhitungan pada opsi varian; label evaluasi dan status pernyataan lain mengikuti klaim yang benar. Tidak melonggarkan `same_answer_as_original`, jumlah opsi benar, atau guard hash.

Reproduksi memeriksa stimulus, seluruh opsi dan kunci dengan nilai original. Pembahasan original tersedia verbatim di metadata; pembahasan varian ditulis sebagai penjelasan parametrik tersendiri dan dihitung ulang. Pecahan simbolik LaTeX `a/b` pada satu opsi disajikan sebagai `(a)/(b)` untuk menghindari salah tafsir sebagai placeholder; sumber mentah, kunci tertulis dan catatan tetap disimpan.

**PROPOSED / belum disetujui Kurikulum:** rentang angka dan keluarga varian baru belum merupakan approval publikasi atau kesetaraan kesulitan. `approval_status=NOT_CURRICULUM_APPROVED` dan `self_adjustment_enabled=false`. Beberapa perubahan angka dapat mengubah beban hitung; tidak ada janji bahwa varian setara secara IRT. Rentang lama dan kebijakan penyesuaian otomatis tidak disentuh.

Reproduksi: `python -B variant_gen/tests/build_drill_1_5_level45_batch1.py` (penyusunan asset offline), `python -B variant_gen/tests/audit_drill_1_5_level45_batch1.py` (bukti), dan `python -B -m unittest discover -s variant_gen/tests -p test_drill_1_5_level45_batch1.py -v`. Builder hanya untuk asset v1 batch ini yang belum dirilis; setelah digunakan/dirilis, perubahan isi harus memakai versi baru. [Laporan](audits/2026-10-20-drill-1-5-level45-batch1/README.md).


## Indikator 6-10 level 4-5: tahap 1 (20 Oktober 2026)

20 dari 100 soal ditambahkan ke Drill paket 1: setiap indikator memiliki dua soal level 4 dan dua soal level 5. Bank tambahan dimuat oleh load_workspace_bank; custom bank tetap terpisah. Original, sumber, pembahasan, serta nomor soal dipertahankan.

Generator memakai engine yang ada. Hasil varian hanya dikembalikan dalam respons; tidak ditulis ke file atau database. Seluruh domain parameter, reproduksi original, seed, katalog service, dan workbench diuji. Rentang belum dikalibrasi IRT; self-adjustment tetap nonaktif.

[Laporan dan 80 soal antrean](audits/2026-10-20-drill-6-10-level45-batch1/README.md). Uji: python -B -m unittest discover -s variant_gen/tests -p test_drill_6_10_level45_batch1.py


## Indikator 6-10 level 4-5: tahap 2 (20 Oktober 2026)

Tambahan 20 generator membawa cakupan menjadi 40/100. Batch kedua memilih soal tanpa temuan audit: indikator 6 (2), 7 (6), 8 (4), 9 (4), 10 (4). Soal yang memerlukan revisi sumber tetap tertahan. Katalog paket Drill 1 menggabungkan kedua batch dengan nomor soal asli.

Original dan konfigurasi batch pertama tidak berubah. Hasil varian tetap hanya di respons; tidak disimpan ke lokal atau database. Rentang numerik belum dikalibrasi IRT. [Laporan tahap kedua dan 60 soal tersisa](audits/2026-10-20-drill-6-10-level45-batch2/README.md).

Uji kedua batch: python -B -m unittest discover -s variant_gen/tests -p test_drill_6_10_level45_batch*.py


## Indikator 6-10 level 4-5: tahap 3 (20 Oktober 2026)

Tambahan 10 generator membawa cakupan menjadi 50/100. Tahap ini memuat indikator 7 (1), 8 (7), 9 (1), 10 (1), dipilih dari soal tanpa temuan audit. Katalog Drill paket 1 tetap memakai nomor asli. Original/konfigurasi lama dilindungi hash; hasil varian tetap hanya dalam respons. Database tidak diubah.

[Laporan tahap ketiga dan 50 soal tersisa](audits/2026-10-20-drill-6-10-level45-batch3/README.md). Uji: python -B -m unittest discover -s variant_gen/tests -p test_drill_6_10_level45_batch3.py

## Indikator 6-10 level 4-5: tahap 4 (21 Oktober 2026)

Tambahan 25 generator membawa cakupan menjadi 75/100. Stimulus dan kunci terpilih valid menurut audit akademik; temuan pembahasan, presisi, domain, dan proyeksi ditinjau eksplisit. Proyeksi mentah serta pembahasan original dipertahankan dalam metadata; pembahasan varian memperbaiki temuan tersebut. Deklarasi kunci yang bocor ke stimulus dinormalisasi dengan jejak review.

Setiap generator menghasilkan 30 varian unik valid dalam domain yang diperiksa. Hasil hanya dikembalikan melalui respons API/workbench, tanpa penyimpanan varian atau perubahan database. Self-adjustment tetap nonaktif; rentang belum disetujui kurikulum atau dikalibrasi IRT. [Laporan, tinjauan sumber, dan 25 soal tersisa](audits/2026-10-21-drill-6-10-level45-batch4/README.md).

Uji seluruh tahap: `python -B -m unittest discover -s variant_gen/tests -p 'test_drill_6_10_level45_batch*.py'`.

## Indikator 6-10 level 4-5: tahap 5, koreksi kunci (21 Oktober 2026)

Tujuh generator tambahan membawa cakupan menjadi 82/100. Ketujuh soal mempunyai stimulus valid dan kesalahan kunci yang dapat dibuktikan dari hitungan; stimulus serta opsi original dipertahankan. Kunci lokal dikoreksi dengan jejak review, sumber mentah dan pembahasan original tetap dalam metadata. Pembahasan varian dihitung ulang. Tiap keluarga menyediakan 30 varian unik valid; hasil runtime tidak disimpan.

Sisa 18 belum diaktifkan: 17 memerlukan keputusan revisi sumber, satu soal klasifikasi konseptual memerlukan keputusan stok. [Usulan revisi per soal](audits/2026-10-21-drill-6-10-level45-batch5-source-proposal.md) dan [laporan pengujian](audits/2026-10-21-drill-6-10-level45-batch5/README.md). Status belum disetujui kurikulum; self-adjustment tetap nonaktif.

## Indikator 6-10 level 4-5: selesai (21 Oktober 2026)

Setelah persetujuan revisi lokal minimum, seluruh 100 soal paket 1 tersedia: **99 generator + 1 soal konseptual dengan 3 stok berulang**. Tahap terakhir menambahkan 17 generator. Tiap indikator mempunyai 5 level; level 4 dan 5 kini masing-masing lengkap 10 soal. Indikator 7 memuat stok `mcma-7-5-6`; empat indikator lain masing-masing mempunyai 20 generator level 4-5.

Naskah lokal menampilkan revisi yang konsisten. DOCX, proyeksi mentah, pembahasan sumber, temuan audit dan perubahan sebelum/sesudah tetap terlacak. Seluruh 527 input tahap terakhir diperiksa dari hasil render; tiap generator baru menghasilkan 30 varian unik valid. Stok ditulis offline sebagai inventaris editorial; hasil generate runtime tidak disimpan, tidak ada penghitung pemakaian persisten. Self-adjustment nonaktif; belum approval kurikulum atau kalibrasi IRT.

[Laporan final dan rincian revisi](audits/2026-10-21-drill-6-10-level45-batch6/README.md). Generate melalui API/workbench; stok melalui pemilih varian atau `python -B variant_gen/cli.py stock mcma-7-5-6 --variant 1 --json`. Mulai ulang workbench yang sudah berjalan untuk memuat bank terbaru.


## Indikator 11?15: generator nonkonseptual lengkap (21 Oktober 2026)

Cakupan kini **228/250 generator**, 22 konseptual ditunda, 0 HOLD. `mcma-15-2-8` memakai original lokal v3: panjang BC yang bertentangan dengan sudut dihapus; opsi B memakai rasio QR/BC. Generator v1 mempunyai 30 varian unik valid dari 31 input termasuk original. Riwayat v1/v2 dan DOCX dipertahankan; revisi belum disetujui kurikulum, self-adjustment nonaktif. Hasil runtime tidak disimpan. [Audit dan validasi](audits/2026-10-21-mcma-15-2-8-generator.md).
## Penyelesaian indikator 1–5 level 4–5, 21 Oktober 2026

**ENGINEERING DECISION — instruksi pengguna:** lanjutkan 67 soal tersisa dan pisahkan 28 soal yang membutuhkan koreksi akademik sebagai draf review belum aktif. Bank `variant_gen/data/drill-1-indicators-1-5-levels-4-5-batch2/` menambah 39 original v1/config v1. `load_workspace_bank` menggabungkan keanggotaan katalog berdasarkan paket, indikator, dan level lalu mengurutkan nomor sumber; isi bank tahap pertama tetap dipertahankan. Cakupan 100 keluarga menjadi 72 generator lokal dan 28 generator draf.

**PROPOSED:** `variant_gen/drafts/2026-10-20-level45-academic/` menyimpan 28 usulan original v2, config v1, sumber sebelum koreksi dan perubahan per komponen. `HOLD_SOURCE`, `review_only=true`, `PROPOSED_NOT_APPROVED`; bank dan config default tidak memuatnya. Audit memeriksa salinan sandbox dalam memori tanpa mengaktifkan aset draf. Jangan memindahkan config draf ke direktori runtime sebelum ada persetujuan.

Semua keluarga baru memakai domain eksplisit `k=0..24`; nilai original mereproduksi stimulus, opsi, dan kunci. Setelah validator, kapasitas efektif masing-masing 24 varian. Pembahasan parametrik dihitung terpisah dari pembahasan sumber. Angka FPB/KPK di dalam fungsi, penyebutan satuan waktu, radikan berbeda, langkah perhitungan, dan jawaban diperiksa dari teks hasil render. Rentang baru belum disetujui untuk publikasi atau kesetaraan kesulitan; `self_adjustment_enabled=false`.

[Audit lengkap, CSV dan cara reproduksi](audits/2026-10-20-drill-1-5-level45-completion/README.md). Laporan tahap pertama tetap merupakan snapshot historis. Perubahan versi setelah digunakan harus menambah versi, bukan menimpa aset yang sudah dipakai.
