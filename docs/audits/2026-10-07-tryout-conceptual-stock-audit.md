# Stok konseptual Tryout 1

7 Oktober 2026. Tiga soal Tryout tanpa generator kini memiliki **sembilan stok manual VERIFIED**, masing-masing tiga. Tidak mengubah original, config, katalog, ledger, atau 206 stok Drill existing. Metadata hanya memperbarui alasan ketersediaan pada tiga ID tersebut. Tidak mengakses database atau commit/push.

| Original | Format/kognitif | Variasi substantif | Kunci stok 1 / 2 / 3 |
|---|---|---|---|
| `tryout-1-b1-q07` | MCMA / C5 | Dua bentuk setara melalui distributif; tanda negatif sebelum kurung; kurung pada pembagi. Masing-masing dua penyelesaian dan empat klaim, dua benar. | A,C / B,D / A,D |
| `tryout-1-b4-q02` | PG / C3 | Empat sektor sama luas; dadu delapan sisi fair; dua bola merah di antara enam bola sama mungkin. Satu langkah rasio kejadian terhadap ruang sampel. | A / C / D |
| `tryout-1-b4-q06` | KATEGORI / C4 | Kelas sama besar dengan alokasi proporsional; kelas berbeda besar dengan alokasi sama yang tidak proporsional; pertanyaan netral dan variabel durasi kontinu. Tiga klaim, dua benar. | 1,2 / 1,3 / 2,3 |

Asset pada `variant_gen/data/conceptual_stock.json` memakai ID stabil `:stock-01` sampai `:stock-03`, versi stok1, hash/versi original yang tepat. Status VERIFIED berarti review teknis isi, kunci, dan profil; tidak menyatakan persetujuan tim kurikulum atau kesetaraan IRT empiris. Review terpisah mengonfirmasi sembilan kunci dan semua klaim, termasuk batas proporsional sampling.

Stok dapat dipilih berulang melalui **Service AI > Tryout > Tryout 1 > bab > soal > Varian stok**. Mulai ulang UI untuk memuat asset baru. Tidak menggunakan seed, tidak mencatat pemakaian, tidak habis. CLI: `python -B variant_gen/cli.py stock tryout-1-b1-q07 --variant 2 --json`.

**Generate paket Tryout tetap memakai original** untuk tiga soal ini (`ORIGINAL_ONLY`). Pekerjaan ini menambah stok dan akses per soal pada UI/CLI existing; tidak mengubah kontrak respons atau pemilihan konten paket. Generator otomatis tetap ditunda.

Total repository tetap820 original/746 generator. Stok kini **70 original / 215 varian VERIFIED**: Drill67/206; Tryout3/9. Empat Drill HOLD masih tanpa generator maupun stok.

Verifikasi: tes `test_tryout_conceptual_stock.py` memeriksa format/profil/provenance, aritmetika kedua penyelesaian, semua opsi peluang, klaim sampling, CLI berulang, dan HTTP UI untuk seluruh sembilan stok tanpa DB/penulisan. Inventaris lengkap loader mencakup70 ID; 206 record Drill existing tetap sama.

Suite lengkap: `python -B -m unittest discover -s variant_gen/tests -v` — **178 tes lulus dalam104,724 detik**. Browser memeriksa pemilihan stok1–3 dan pemakaian ulang stok1 pada ketiga ID. Snapshot799 asset/config existing:797 tetap identik, hanya asset stok dan metadata ketersediaan Tryout berubah. Rekonstruksi206 record lama cocok dengan SHA-256 sebelum penambahan; semua original/config/ledger/katalog tetap identik. `git diff --check` lulus.
