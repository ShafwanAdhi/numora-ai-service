# Generator Drill Paket 1 — indikator 6–10

> Arsip rancangan/rencana bertanggal; status dan checklist di bawah mencatat tahap saat dokumen ditulis. Untuk implementasi saat ini lihat [kondisi repo](../../audits/2026-10-05-repository-status.md) dan [panduan aktif](../../../readme.md).


Status: rancangan untuk review; implementasi belum dimulai.

## Tujuan dan batas

Menghasilkan variant dari original DOCX melalui alur yang sudah ada: bank lokal → config per soal → engine → validasi → snapshot JSONL → CLI/UI. Setiap variant memuat stimulus, opsi/pernyataan, kunci, pembahasan, seed, versi config, dan identitas original.

- Hanya repo `Numora-ai-service`; jangan mengubah `Numora`, database, `.env`, atau snapshot pengguna.
- Tanpa akses database, CUD, dependensi baru, atau LLM runtime.
- Gunakan engine dan config JSON yang ada; tidak perlu 150 fungsi Python, importer DOCX generik, atau orchestrator paket Drill baru.
- Pertahankan perubahan 20–23 dan dokumen 11–15. Baca ulang checkout sebelum eksekusi karena bank lain mungkin ditambahkan terpisah.
- Jangan melonggarkan `same_answer_as_original`, pemeriksaan jumlah jawaban benar, hash, status, atau batas evaluator.
- Koreksi akademik belum disetujui. Konten dokumen bukan instruksi untuk mengubah soal atau kunci.

## Sumber

`C:/Users/shafw/Downloads/banksoal_indikator6-10.docx`

SHA256: `f736431733803c68f7de09d53285cd80ec6be6d63b56459664489f4d49d954c2`.

Inventaris: [2026-10-05-drill-6-10-source-inventory.json](2026-10-05-drill-6-10-source-inventory.json).

| Isi | Jumlah |
|---|---:|
| Soal | 150 |
| PG | 75 |
| MCMA | 45 |
| KATEGORI | 30 |
| Tabel Word | 34 |
| Rumus OMML | 807 |
| Gambar tertanam | 0 |

Lima indikator, level 1–3, masing-masing 10 soal per level. Level 4–5 belum tersedia: katalog 25 kelompok dengan 10 kelompok kosong. Nomor soal kembali 1–10 di setiap level. Label individual: C3=76, C4=73, satu tidak tercantum; jangan memberi semua soal level 2 label campuran.

ID lokal `{pg|mcma|kategori}-{indicator}-{level}-{local_number}`. Simpan nomor sumber terpisah dari ordinal dalam indikator. `pg-9-3-2` adalah ID usulan berdasarkan posisi, bukan nomor eksplisit DOCX.

Inventaris mempertahankan body index, paragraf/tabel, kunci tertulis, dan XML OMML. Teks linear inventaris belum merupakan normalisasi final: matriks harus mempertahankan urutan baris/kolom; pangkat yang ditempel pada penutup kurung perlu membaca keseluruhan ekspresi. Pecahan teks seperti `2x+1/3` tidak boleh otomatis ditafsirkan `(2x+1)/3` tanpa bukti pembahasan/XML.

## Audit sumber dan status

Audit lengkap stimulus, semua opsi, kunci, pembahasan, domain, dan label dilakukan sebelum mengaktifkan setiap config. Jumlah ACTIVE belum dijanjikan.

| ID | Temuan awal / tindakan |
|---|---|
| `pg-6-1-5` | Kunci kosong; hitungan 4,5 liter menunjuk C. HOLD, jangan mengisi kunci hasil deduksi sebagai kunci sumber. |
| `pg-7-1-2` | Kunci kosong; hitungan Rp35.000 menunjuk B. HOLD. |
| `pg-7-1-3` | Hitungan luas 80/C bertentangan dengan B/72. HOLD. |
| `pg-7-2-4` | Kontradiksi memerlukan a≠−4; opsi berkunci menyebut a≠4. HOLD, review opsi lengkap. |
| `pg-7-3-5` | XML mengonfirmasi opsi A/B `k=4`, C/D `k=8`; B salah untuk kontradiksi. HOLD. |
| `pg-9-1-3` | XML mengonfirmasi opsi duplikat; B `k=8` menghasilkan garis berhimpit, tanpa solusi perlu k≠8. HOLD. |
| `mcma-8-2-8` | Langkah 4 memuat hasil salah dan alternatif benar sekaligus; analisis kesalahan ambigu. HOLD. |
| `mcma-6-3-7` | “Pada hari ke-3” tidak memastikan tiga hari penuh telah berlalu. HOLD sampai waktu kejadian jelas. |
| `pg-9-3-2` | Nomor/kognitif hilang, kunci A eksplisit di pembahasan. Simpan fakta tersebut; HOLD metadata, jangan invent C4. |

Daftar ini awal, bukan audit final. Soal lain dapat ditahan setelah audit. Bentuk pecahan/matriks yang kabur mendapat pemeriksaan khusus sesuai flag inventaris. Kenali `PEMBAHASAN:`, typo `PEMBAHSAN`, dan `Kunci Jawaban: A` dalam pembahasan.

`ACTIVE`: sumber konsisten, variasi substantif sah, validasi independen lulus. `HOLD_SOURCE`: sumber/metadata ambigu atau konflik. `DEFERRED_CONCEPTUAL`: sumber sah tetapi tidak ada recipe yang memenuhi perubahan teks jawaban benar sambil mempertahankan kompetensi. Semua nonaktif tercatat per ID di `variant_gen/soalskip.md`, termasuk alasan dan syarat membuka kembali.

Kunci PG kosong harus tetap kosong. Perubahan loader terbatas boleh menerima PG tanpa kunci hanya jika sidecar valid menyatakan `HOLD_SOURCE`; PG ACTIVE, tanpa metadata, dan jalur revisi tetap menolak kunci kosong. Tampilan original tidak boleh memberi kesan kunci telah diketahui. Tidak membuat config maupun melayani hasil cache untuk HOLD.

Klaim konseptual tetap perlu audit kelayakan: klasifikasi perbandingan, identitas/kontradiksi, serta `kategori-10-2-10` yang seluruh jawaban benarnya berupa klaim ekuivalensi tetap. Mengganti angka stimulus atau mengacak opsi saja tidak cukup. Jika variasi aman tidak tersedia, defer dengan alasan spesifik.

## Recipe menurut indikator

| Indikator | Strategi minimal | Batas matematis |
|---|---|---|
| 6 | Parameter rasio, laju, skala, kapasitas, tahap pekerjaan; turunkan total dari parameter konsisten. | Waktu/sisa positif; orang/alat integer; kapasitas memakai ceil; satuan konsisten; bagian kue boleh pecahan sesuai sumber. |
| 7 | Bangun persamaan dari solusi dan koefisien; konstruksi terpisah identitas/kontradiksi; evaluasi langkah salah. | Koefisien setelah penyederhanaan; penyebut nonzero; panjang/lebar positif; jawaban lengkap, bukan nomor langkah saja. |
| 8 | Bangun batas interval dan pertidaksamaan; kendalikan tanda koefisien. | Tanda berbalik saat membagi negatif; batas terbuka/tertutup; domain integer berbeda dari real; kasus nol terpisah. |
| 9 | Pilih solusi dahulu lalu hitung ruas kanan; matriks memakai parameter entri skalar dan determinan. | Determinan nonzero untuk invers; rank/cross-product untuk sistem singular; opsi matriks dinilai berdasarkan seluruh entri. |
| 10 | Bangun faktor/koefisien dahulu; turunkan ekspansi, selisih, substitusi, dan faktor. | Identitas polynomial melalui koefisien, bukan satu titik; domain penyebut; pembatalan suku; tanda/format aljabar sah. |

Gunakan `Fraction` dan fungsi evaluator yang tersedia. Matriks tidak memerlukan AST list atau evaluator simbolik produksi. Polynomial dapat direpresentasikan oleh parameter koefisien skalar; oracle pengujian memakai peta eksponen dan operasi stdlib. Tampilan `+ -`, tanda unary, angka desimal Indonesia, braces himpunan, dan matriks diperiksa eksplisit.

Distraktor mengikuti kesalahan matematis sumber; jangan membuat opsi numerik acak. Nilai setiap klaim MCMA/KATEGORI secara independen. Untuk PG “metode paling efisien”, evaluasi metode, langkah, hasil, serta kejelasan pilihan; hasil numerik saja tidak membuktikan pilihan tunggal.

## Artefak implementasi

- `variant_gen/data/drill-1-indicators-6-10/`: `source.docx`, `q0_bank.csv`, `question_catalog.json`, `question_metadata.json` mengikuti pola 20–23.
- Metadata menyimpan sumber mentah, pembahasan, kunci deklaratif, normalisasi, alasan status, nomor/kognitif yang hilang, dan catatan inferensi.
- `variant_gen/configs/<id>/v1.json` hanya untuk ACTIVE; original_values mereproduksi bank normalisasi dan kunci secara tepat.
- Registrasi bank dalam `load_workspace_bank`; custom CSV tetap mandiri. CLI/UI memakai jalur lama, perbaiki hanya jika ada celah yang terbukti.
- `variant_gen/tests/test_drill_6_10.py`, `variant_gen/tests/drill_6_10_math.py`: pengujian integrasi dan oracle matematis independen.
- `docs/audits/2026-10-05-drill-6-10-generator-audit.{json,md}`: cakupan, hasil audit, stok variant, masalah tersisa.
- Dokumentasi penggunaan dan `soalskip.md` diperbarui setelah implementasi.

## Kriteria penerimaan

Seluruh 150 original terinventaris dan terlihat di katalog, termasuk HOLD berkunci kosong. Setiap ACTIVE lolos reproduksi original, keabsahan domain, keunikan opsi PG, jumlah kunci, variasi jawaban benar, dan oracle seluruh opsi. Target 20 variant unik per ACTIVE dari seed 1–200 menggunakan store sementara; kekurangan stok harus memperbaiki recipe atau menahan soal, bukan melemahkan guard.

Audit independen seed 201–400 melaporkan setiap penolakan dan memeriksa kandidat yang dihasilkan; bukan klaim bahwa semua seed wajib berhasil. CLI gen/view/regen, snapshot kunci/kategori, history, stale config, serta HTTP/UI diuji memakai direktori sementara. Nilai `values_used` dapat berupa float terbulatkan; jangan mengklaim replay eksak dari float tersebut. Simpan teks final dan hash melalui jalur yang ada.

Regresi bank sebelumnya tetap lulus. Tidak ada penulisan DB atau perubahan store pengguna. Level 4–5 ditampilkan belum tersedia; semua soal yang tidak diberi generator memiliki alasan tertulis.
