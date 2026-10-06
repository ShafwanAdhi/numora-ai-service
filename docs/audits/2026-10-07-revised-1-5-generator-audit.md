# Generator revisi Drill Paket 1 indikator 1–5

7 Oktober 2026. Empat puluh original v2 hasil [impor kurikulum](2026-10-07-drill-1-5-source-revision.md) kini memakai generator config v1. Generator existing, stok konseptual, sumber CSV/DOCX, katalog, dan ledger revisi dipertahankan. Tidak mengakses database, tidak commit/push. Hasil generate hanya berada pada respons/tampilan.

## Cakupan

| Indikator | Original level 1–3 | Generator baru | Total ACTIVE | Konseptual dengan stok | HOLD_SOURCE |
|---|---:|---:|---:|---:|---:|
| 1 | 30 | 6 | 24 | 5 | 1 |
| 2 | 30 | 10 | 26 | 4 | 0 |
| 3 | 30 | 10 | 30 | 0 | 0 |
| 4 | 30 | 13 | 30 | 0 | 0 |
| 5 | 30 | 1 | 28 | 1 | 1 |
| Total | 150 | 40 | 138 | 10 | 2 |

Bank 1–2: 50 ACTIVE, 9 DEFERRED_CONCEPTUAL, 1 HOLD_SOURCE. Bank 3–5: 88 ACTIVE, 1 DEFERRED_CONCEPTUAL, 1 HOLD_SOURCE. Seluruh Drill: **719 generator + 67 original dengan stok + 4 HOLD = 790 original**. Bersama Tryout: **746 config / 820 original**. Level tambahan dalam DOCX revisi tetap hanya diarsipkan, tidak ditambahkan ke bank runtime.

Tetap ditahan:

- `pg-1-2-1`: kunci D sudah benar, tetapi pembahasan sumber masih menulis −58% = 0,58%; seharusnya −0,58.
- `pg-5-3-3`: header B menyebut 24 liter/menit, opsi B/pembahasan menyebut selisih 4 liter/menit.

## Perilaku dan domain

Config menggunakan evaluator dan engine existing. Perubahan runtime satu pola placeholder untuk mempertahankan literal LaTeX `\text{C}` pada satuan suhu. Tes regresi memastikan variabel biasa tetap dirender.

Urutan bilangan negatif dan analisis operasi/kalender memiliki jawaban substantif berbeda: posisi pengukuran atau isi analisis berubah, bukan sekadar shuffle opsi. Penyederhanaan eksponen mengubah nilai benar/salah pernyataan dengan jumlah kunci MCMA tetap sama. FPB/KPK memakai kuantitas integer; pilihan basis prima dibatasi oleh constraint ke daftar yang sudah diperiksa, termasuk penolakan faktor yang bertabrakan dengan faktor prima lainnya.

Pembulatan menggunakan aturan sumber secara eksplisit: harga satuan sebelum hasil akhir, kedua operand sebelum perkalian, atau pembulatan ke atas sesuai ID. Kalender dihitung 60 hari setelah tanggal awal, tanpa menghitung tanggal awal dua kali. Efisiensi bensin dibatasi 30–50 km/liter.

Enam catatan alasan distraktor pada sumber (`pg-2-1-1`, `pg-2-1-5`, `pg-2-2-1`, `pg-3-1-3`, `pg-3-1-5`, `pg-3-2-3`) tetap tersimpan sebagai provenance. Pembahasan generator menghitung saldo/kembalian/estimasi yang benar, menjelaskan aturan pembulatan dan membandingkan opsi, tanpa menyalin penjelasan distraktor yang salah.

Default memakai satu input integer atau pilihan basis prima. **Kapasitas unik default 25–40 varian per soal**, dihitung dengan enumerasi seluruh domain dan validator existing. Daftar domain, kapasitas unik tepat, versi, dan ID tersedia di [laporan JSON](2026-10-07-revised-1-5-generator-audit.json); laporan tidak menyimpan teks soal varian. Rentang ini disengaja, dapat diperluas setelah pemeriksaan matematika dan kesulitan. Tidak ada penyesuaian otomatis atau kalibrasi IRT.

Generate dapat dipanggil berulang tanpa batas stok. Seed sama menghasilkan konten sama; seed berbeda dapat menghasilkan konten sama. Tidak ada pencatatan keunikan lintas request atau penyimpanan hasil. Config tetap berversi dan dapat ditinjau melalui editor existing.

## Verifikasi

- Semua 40 config mereproduksi stimulus, seluruh opsi dan kunci original v2 tepat.
- Oracle independen membaca teks hasil render; memeriksa setiap opsi, kunci, hasil pembulatan, persamaan, dan tanggal. Seluruh domain default diperiksa, termasuk nilai yang kemudian ditolak karena sama dengan original.
- Masing-masing generator menghasilkan 20 varian unik dengan pembanding sementara di memori: total 800; seed 201–250 menambah 2.000 pemeriksaan tanpa menyimpan hasil.
- Mutasi kunci/pembahasan, integer di luar batas, serta basis prima yang belum disahkan ditolak oleh tes.
- Browser memeriksa seluruh 40 ID: Generate aktif, config tampil, seed berulang konsisten, dua HOLD diblokir, tanpa Regen. Database diputus pada server pemeriksaan; request tab database dimock.
- Snapshot 759 berkas existing: 757 identik; hanya dua metadata bank berubah. Semua 706 config existing, stok manual, CSV, DOCX, katalog, dan ledger tetap identik.
- Review terpisah tidak menemukan kesalahan matematika/kunci. Script authoring sekali pakai menolak menimpa config existing; audit impor ditandai sebagai snapshot historis.

Pemeriksaan runnable: `python -B -m unittest discover -s variant_gen/tests -p test_drill_1_5_revised_generators.py -v` — 6 tes lulus. Suite lengkap setelah guard basis tambahan: `python -B -m unittest discover -s variant_gen/tests -v` — **172 tes lulus dalam 100,233 detik**. `git diff --check` lulus.

Di UI pilih **Service AI > Drill > Paket 1 > indikator > level > soal**. Mulai ulang proses UI existing untuk memuat metadata baru. CLI: `python -B variant_gen/cli.py gen pg-1-1-5 s11 --json`.
