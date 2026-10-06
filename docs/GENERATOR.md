# Referensi generator

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
| `data/drill-1-indicators-1-2/` |60 original level1–3,34 config, katalog6 grup, metadata dan DOCX provenance |
| `data/drill-1-indicators-3-5/` |90 original level1–3,64 config,9 grup, metadata/DOCX provenance |
| `data/drill-1-indicators-6-10/` | 150 original, katalog, metadata, source DOCX |
| `data/drill-1-indicators-11-15/` | 250 original, katalog, metadata, source DOCX dan audit.json |
| `data/drill-1-indicators-20-23/` | 120 original Drill tambahan, katalog, metadata, source DOCX; ledger kosong karena belum ada koreksi disetujui |

`OriginalBank(path)` membaca satu bank. CLI/UI memakai `load_workspace_bank`: path default Drill menggabungkan Tryout dan Drill indikator1–2,3–5,6–10,11–15,20–23 bila tersedia; `--bank` custom tetap standalone. API Python menerima `additional_paths` eksplisit; ID duplikat ditolak. Katalog/metadata/ledger harus di samping CSV. CSV tanpa katalog unclassified; paket custom membutuhkan katalog sesuai aktivitasnya.

ID Drill `pg-16-1-3`: format PG, indikator 16, level sumber 1, soal 3. ID Tryout `tryout-1-b2-q04`: paket 1, bab 2, soal 4. ID lokal bukan UUID canonical database. Level sumber berbeda dari difficulty, cognitive level dan parameter IRT.

Ledger menjaga row source/replacement dan versi berurutan; loader memvalidasi identitas/hash lalu mengekspos original efektif. Salin ledger bersama CSV; CSV saja menunjukkan source sebelum koreksi. Klasifikasi tidak masuk hash konten original.

Metadata status: `ACTIVE`, `HOLD_SOURCE`, `DEFERRED_CONCEPTUAL`; non-ACTIVE wajib alasan dan menolak generate/lint/config save. `category_labels` opsional: dua label unik nonempty, hanya KATEGORI. Key CSV memilih kategori pertama, bukan selalu kebenaran. Label nondefault masuk hash original; respons memuat `answer_categories` seluruh pernyataan. UI membaca label respons; ekspor kontrak boolean menolak kategori berlabel khusus.

## Stok konseptual manual

Cakupan lengkap: 67 original Drill/206 stok VERIFIED, masing-masing2–4. Review tugas aktual dan perubahan per varian tercatat pada [audit kesulitan](audits/2026-10-06-conceptual-stock-audit.md). Pewarisan label kognitif tidak membuktikan kesetaraan kesulitan.

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

Drill indikator16–19: 110/120 config, seluruh indikator18–19 tercakup. [Review skip](../variant_gen/soalskip.md) mencatat 12 soal awal: dua mendapat config, sepuluh memerlukan desain/policy konseptual. Indikator20–23: 86/120 aktif, 11 HOLD_SOURCE, 23 DEFERRED_CONCEPTUAL; [audit](audits/2026-10-05-drill-20-23-generator-audit.md) memuat stok20 unik per ACTIVE dan semua alasan penundaan. Subtotal indikator16–23: 196 config/240 original.

Drill indikator 6–10: 129/150 aktif, 12 HOLD_SOURCE, 9 DEFERRED_CONCEPTUAL. Subtotal indikator6–10 dan16–23: 325 config/390 original. [Audit](audits/2026-10-05-drill-6-10-generator-audit.md) mencatat pemeriksaan setiap opsi, stok teramati, serta batas recipe. Bank `variant_gen/data/drill-1-indicators-6-10` dimuat otomatis oleh UI/CLI; level 4–5 kosong sesuai sumber. Contoh: `python -B variant_gen/cli.py gen pg-6-1-1 s1 --json`. Kunci PG sumber yang kosong tetap HOLD, tampil “Belum tersedia”.

Tryout: 27/30 aktif; deferred `tryout-1-b1-q07` (alasan operasi), `tryout-1-b4-q02` (satu mata dadu), `tryout-1-b4-q06` (bias survei). `DEFERRED_CONCEPTUAL` menolak generasi walaupun config disuplai.

| Original efektif v2 | Koreksi lokal |
|---|---|
| `pg-16-3-5` | Segitiga siku-siku 3–4–5; dua alas 12 cm², luas prisma 132 cm² |
| `mcma-19-3-6` | Benda terpisah; limas 15 cm tidak muat dalam kubus 10 cm |
| `tryout-1-b2-q04` | 11.000 + 5.000 = 16.000; kunci C |
| `tryout-1-b4-q04` | Bandingkan rentang, jangan simpulkan varians dari rentang |

Normalisasi source dicatat dalam metadata. q06 deferred: jumlah sampel sama per kelas belum tentu proporsional. Kebenaran teknis tidak menggantikan approval kurikulum atau kalibrasi empiris.

Drill indikator11–15: 223/250 generator aktif, 5 HOLD_SOURCE dan 22 DEFERRED_CONCEPTUAL, tersedia level1–5. [Audit](audits/2026-10-05-drill-11-15-generator-audit.md) dan contoh hasil berada di bank `variant_gen/data/drill-1-indicators-11-15/`. Indikator1–2 menambah34 config/60 original level1–3. Total Drill:646 config/790 original; bersama Tryout:673 config/820 original. Ekspor kanonik mensyaratkan satu label kognitif C1–C6; label sumber gabungan tetap disimpan lokal.

Indikator3–5:64 config/90 original;25 HOLD_SOURCE/1 DEFERRED_CONCEPTUAL. [Audit](audits/2026-10-06-drill-3-5-generator-audit.md).
