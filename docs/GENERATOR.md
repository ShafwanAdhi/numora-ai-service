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

`OriginalBank(path)` membaca satu bank. CLI/UI memakai `load_workspace_bank`: path default Drill menggabungkan Tryout bila tersedia; `--bank` custom tetap standalone. API Python menerima `additional_paths` eksplisit; ID duplikat ditolak. Katalog/metadata/ledger harus di samping CSV. CSV tanpa katalog unclassified; paket custom membutuhkan katalog Tryout.

ID Drill `pg-16-1-3`: format PG, indikator 16, level sumber 1, soal 3. ID Tryout `tryout-1-b2-q04`: paket 1, bab 2, soal 4. ID lokal bukan UUID canonical database. Level sumber berbeda dari difficulty, cognitive level dan parameter IRT.

Ledger menjaga row source/replacement dan versi berurutan; loader memvalidasi identitas/hash lalu mengekspos original efektif. Salin ledger bersama CSV; CSV saja menunjukkan source sebelum koreksi. Klasifikasi tidak masuk hash konten original.

## Config

Lokasi `variant_gen/configs/<question_id>/v<N>.json`. Folder/file harus sesuai `question_id`/`config_version`. CLI generate/regen memakai versi terbaru; UI dapat melihat config historis.

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
- Duplicate check: versi terbaru seed lain + seluruh versi seed yang sedang dibuat ulang; urutan opsi diabaikan. Bukan seluruh versi historis setiap seed.

RNG memakai question ID, seed, draw, nama variabel. Draw yang sama deterministik; kandidat akhir bergantung stok/penolakan. Snapshot tersimpan menjadi acuan, bukan replay dengan stok/config terbaru.

`lint` memeriksa schema/hash, reproduksi stem/opsi/kunci original dengan normalisasi whitespace, probe N seed unik di memori. Pembahasan tidak dibandingkan terhadap source. Warning stok tidak otomatis gagal bila masih ada kandidat valid; sampel bukan kapasitas exact.

## Menambah atau merevisi soal

1. Tetapkan aktivitas/paket/indikator+level atau bab, ID, format, kompetensi, stimulus, opsi, kunci, pembahasan, sumber.
2. Tambahkan original baru dan membership katalog. Koreksi existing melalui ledger row/versi/hash yang tepat.
3. Buat config versi baru; derive jawaban/distractor dari input; jaga domain/constraints agar tugas akademik sesuai.
4. Jalankan hash/lint, review reproduksi original, matematika dan kunci dengan oracle independen.
5. Probe store sementara, run suite, review kurikulum sebelum publikasi. Jangan melonggarkan validator global demi satu soal.

Config yang sudah menghasilkan snapshot dilindungi hash. Editing in-place menolak generasi berikutnya; buat `v<N+1>.json`. Perubahan config tidak memigrasi snapshot existing.

## Cakupan dan koreksi

Drill: 110/120 config, seluruh indikator 18–19 tercakup. [Review skip](../variant_gen/soalskip.md) mencatat 12 soal awal: dua mendapat config, sepuluh memerlukan desain/policy konseptual.

Tryout: 27/30 aktif; deferred `tryout-1-b1-q07` (alasan operasi), `tryout-1-b4-q02` (satu mata dadu), `tryout-1-b4-q06` (bias survei). `DEFERRED_CONCEPTUAL` menolak generasi walaupun config disuplai.

| Original efektif v2 | Koreksi lokal |
|---|---|
| `pg-16-3-5` | Segitiga siku-siku 3–4–5; dua alas 12 cm², luas prisma 132 cm² |
| `mcma-19-3-6` | Benda terpisah; limas 15 cm tidak muat dalam kubus 10 cm |
| `tryout-1-b2-q04` | 11.000 + 5.000 = 16.000; kunci C |
| `tryout-1-b4-q04` | Bandingkan rentang, jangan simpulkan varians dari rentang |

Normalisasi source dicatat dalam metadata. q06 deferred: jumlah sampel sama per kelas belum tentu proporsional. Kebenaran teknis tidak menggantikan approval kurikulum atau kalibrasi empiris.
