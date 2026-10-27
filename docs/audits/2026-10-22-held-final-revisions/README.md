# Audit 16 revisi HOLD — 22 Oktober 2026

Seluruh 16 original kini ACTIVE lokal, masing-masing mempunyai konfigurasi generator v1. Jumlah original tetap; revisi diterapkan melalui `original_revisions.jsonl`, tanpa menimpa CSV sumber. DOCX hasil seleksi dan manifest ekstraksi tetap utuh. Status ACTIVE tidak menyatakan persetujuan publikasi kurikulum atau kalibrasi IRT.

| ID | Hasil audit / tindakan | Kunci aktif |
|---|---|---|
| pg-1-2-1 | Revisi memperbaiki −58%=−0,58; −0,62 paling kecil. Original v3. | D |
| pg-5-3-3 | Debit P=300/15=20, Q=480/20=24; selisih4 liter/menit. Header24 yang konflik sudah tidak ada. Original v2. | B |
| mcma-6-3-7 | Revisi menyebut setelah2hari: sisa60−12=48porsi; 48/8=6hari. Original v3. | ABC |
| kategori-21-4-9 | Median25 membuat B benar. Kunci dan pembahasan lokal diperbaiki; semua pernyataan benar. | 1234 |
| kategori-21-4-10 | Kedua rerata3; median2 dan3; jangkauan6 dan2. Kunci lokal hanya D Tepat. | 4 |
| mcma-21-5-6 | Revisi konsisten: median75, rerata80, jangkauan45; nilai110 memengaruhi rerata. | ABCD |
| mcma-21-5-7 | Revisi konsisten: kedua rerata80, median80, jangkauan30; modus A70 dan80. | ABE |
| pg-22-4-3 | Sumber masih memiliki dua jawaban benar C,D. Opsi C diubah lokal menjadi median B lebih rendah; C salah, D benar. | D |
| mcma-22-4-7 | Revisi konsisten: kedua rerata/median5; jangkauan P0,Q4; Q tidak memiliki modus. | ABD |
| kategori-22-4-9 | Revisi konsisten: kedua rerata/median20; jangkauan20 dan10; tanpa modus. | 13 |
| pg-23-4-5 | Revisi menetapkan koin seimbang: peluang teoretis0,5; frekuensi empiris26/40=0,65. | C |
| mcma-23-4-7 | 32/60=8/15; 28/60=7/15; jumlah1. Frasa B diperjelas menjadi sekitar0,4667; varian memakai pecahan eksak. | ABC |
| pg-23-5-3 | Koin seimbang telah disebut; independensi ditegaskan lokal sesuai model pada pembahasan. Peluang tepat1gambar dari n lemparan=n/2^n. | C |
| pg-23-5-4 | Revisi menetapkan dadu seimbang: peluang genap3/6=0,5, bukan frekuensi162/300=0,54. | C |
| mcma-23-5-7 | Revisi menetapkan koin seimbang: frekuensi46/80=0,575 dan34/80=0,425; total1. | ABC |
| mcma-23-5-8 | Sumber menyebut acak; peluang sama untuk setiap bola ditegaskan lokal. Peluang4/10=0,4; frekuensi38/100=0,38. | ABC |

Koreksi minimum konflik kunci/opsi disetujui pengguna pada sesi ini. Pembulatan dan asumsi model dicatat terbuka di metadata `local_corrections`; sumber asli tidak diubah. Original yang sebelumnya v1 menjadi v2; dua original yang sebelumnya v2 menjadi v3. Jumlah jawaban benar per format dipertahankan terhadap original revisi.

## Generator dan verifikasi

Generator memakai bahasa konfigurasi dan pipeline yang sudah tersedia; API dan engine tidak berubah. Parameter `k=0` mereproduksi original aktif. Lima belas generator memiliki 30 kasus tambahan; `pg-23-5-3` memiliki delapan kasus tambahan untuk3–10lemparan. Domain sengaja terbatas; penambahan domain membutuhkan pemeriksaan matematika kembali. Seed identik memberi hasil identik; hasil generate tidak disimpan.

- `python variant_gen/tests/test_held_final_revisions.py`: reproduksi16original, pemeriksaan aritmetika seluruh domain, variasi dengan pembanding sementara, seed deterministik, serta32request HTTP untuk16soal tanpa DB/filevarian.
- `python variant_gen/tests/audit_held_final_progress.py`: inventaris dari loader aktual, validasi konfigurasi seluruh generator, validasi stok konseptual dan struktur115level ×10soal.
- `python docs/sources/incoming/2026-10-22-held-revisions/extract.py --check`: membandingkan XML hasil seleksi dengan DOCX sumber lokal, termasuk tabel dan rumus.

Hasil: suite296tes menghasilkan289lulus dan7ekspektasi historis yang perlu diperbarui. Setelah pembaruan, seluruh21tes pada dua modul terkait lulus (17interface,4regresi sumber); dua tes khusus16generator juga lulus pada pemeriksaan terakhir. Tidak ada perubahan engine untuk meloloskan tes. Perbandingan loader dengan HEAD membuktikan tepat16original berubah dan1.164original lainnya tetap identik; seluruh konfigurasi generator dan248stok tervalidasi.

[Audit terstruktur](audit.json) · [Inventaris terbaru](progress.json) · [Progres per indikator](indicators.csv) · [Ringkasan](../../PROGRESS.md)

Database, repository Numora, stok konseptual dan snapshot audit lama tidak berubah. Tidak commit atau push.
