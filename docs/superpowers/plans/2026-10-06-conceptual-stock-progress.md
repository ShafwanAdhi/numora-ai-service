# Progress — 2026-10-06-conceptual-variant-stock.md

Plan: [Stok konseptual](2026-10-06-conceptual-variant-stock.md).

## Batas tahap pertama

Instruksi pengguna: laksanakan sampai sekitar 50% dahulu, report bertahap. Tahap pertama = 34/67 original (50,7%), maksimal 136 varian; tahap kedua belum dikerjakan.

Cakupan: semua 19 original indikator 1–10; lima original indikator 11 (selain `mcma-11-5-6`); dua indikator 12; `pg-14-1-1`, `mcma-14-1-6`, `kategori-14-1-9`; `pg-16-3-2`; `kategori-20-1-9`, `kategori-20-2-10`; `pg-23-1-1`, `pg-23-1-2`. Enam original percontohan rencana termasuk di dalamnya.

## Keputusan eksekusi

- Ruling: gunakan branch `feat/conceptual-stock` pada checkout session existing, tanpa checkout tambahan — hasil tetap terlihat pada workspace/UI pengguna, perubahan terpisah dari main, tanpa commit/merge.
- Ruling: ledger memakai Markdown native Windows, scratch `.scratch/conceptual-stock` — skrip workspace skill berbasis Bash; format kemajuan tetap dipertahankan.
- Ruling: sumber kebutuhan adalah instruksi pengguna dan keputusan pada plan yang disetujui, tanpa spec terpisah — tidak menduplikasi dokumen untuk perubahan terbatas ini.
- Ruling: ganti `mcma-11-5-6` dan `pg-14-2-1` pada cakupan awal fase dengan dua KATEGORI indikator 20 — kedua label custom diuji pada stok nyata dan seluruh percontohan plan tetap masuk; kedua ID yang diganti menunggu tahap kedua, jumlah fase tetap 34.
- Pre-flight Task 2 → 3: schema dan validator dibagi; jumlah akhir dihitung dari VERIFIED, bukan rancangan.
- Pre-flight Task 2 → 4: stock_record memberi seed/config null; renderer wajib memakai source_kind, bukan menganggap semuanya generator.
- Pre-flight Task 3 → 5: batas fase 34 keluarga; audit harus mencatat 33 keluarga tahap kedua tanpa menandainya selesai.

## Task

- Task 1: complete — 67 original diidentifikasi pada plan; tahap pertama memilih 34.
- Task 2: core complete — 709 file baseline dilindungi; baseline 126 tests PASS; validator dan pengecualian scoped lolos tes RED→GREEN.
- Task 3: complete untuk fase pertama — 136 kandidat direview; 15 kandidat redundan disisihkan; 121 VERIFIED untuk 34 original. 33 original tahap kedua belum dikerjakan.
- Task 4: complete — CLI/HTTP akses baca dan selector UI lolos tes serta smoke browser dengan asset produksi 121 item.
- Task 5: complete untuk fase pertama — audit 67 ID, alasan sepuluh keluarga terbatas, soalskip dan panduan diperbarui; preservasi, suite dan browser diverifikasi.

## Report

| Batch | Ditulis | VERIFIED | Ditahan | Status |
|---|---:|---:|---:|---|
| Semua kandidat tahap pertama | 136 | 121 | 15 | Kandidat redundan dihapus; bukan DRAFT tersedia |

Percontohan merupakan subset tahap pertama, bukan penambahan di luar target 136. Cakupan 34/67 = 50,7%; jumlah varian 121/268 = 45,1% dari maksimum keseluruhan. 24 keluarga memiliki empat varian, lima memiliki tiga, lima memiliki dua.

## Review dan verifikasi akhir

- Reviewer independen membaca seluruh 136 kandidat/34 original beserta perubahan runtime. Tidak menemukan Critical atau kunci matematika salah; pengulangan tugas konseptual diperbaiki dalam satu pass, tanpa review independen kedua.
- Ruling: asumsi tarif upah tetap dinyatakan sebagai perbaikan substansial agar hubungan proporsional sah. Argumen rasional, ekuivalensi distributif dan konstruksi tabung diperjelas; 15 kandidat redundan dihapus sebelum publikasi.
- Tes targeted RED→GREEN: sembilan tes lulus setelah seleksi/promosi 121 item. Suite lengkap terbaru: **135 tes lulus dalam 88,154 detik**; log lokal `.scratch/conceptual-stock/full-tests.log`.
- Browser nyata port 8771 memakai asset produksi default: PG/MCMA/KATEGORI, label Kuantitatif/Kualitatif dan Sesuai/Tidak Sesuai, profil semua benar, selector 2/3/4, pembacaan ulang, kembali ke generator numerik, HOLD dan dua tab lolos; tanpa page error. Permintaan DB dimock; tidak menguji koneksi database aktual.
- SHA-256 seluruh **709 file** baseline original, metadata, katalog, revisi, source dan config tetap sama. `git diff --check` tanpa error whitespace.
- Numora, DB, `.env`, IRT dan config existing tidak diubah; tidak ada commit/push. Server/browser pengujian sementara ditutup.
- [Audit lengkap](../../audits/2026-10-06-conceptual-stock-audit.md). Tahap kedua **33 original** menunggu instruksi berikutnya.

## Tahap kedua — diizinkan pengguna

Instruksi terbaru: lanjutkan 33 original tersisa, cross-check seluruh stok agar variasi mempertahankan tingkat kesulitan, kemudian perbarui dokumentasi Markdown.

- Task 3: in progress — 101 kandidat manual DRAFT untuk seluruh 33 original tersisa ditulis; total 222 kandidat pada 67 keluarga. Stok tahap pertama belum dianggap otomatis lolos review kesulitan baru.
- Task 5: in progress — review independen seluruh 67 original/222 kandidat dan runtime sedang berlangsung. Pemeriksaan matematis stdlib terhadap statistik yang dicetak dan komposisi refleksi lulus; tes cakupan/promosi tetap RED sampai selesai review.
- Ruling: gunakan tugas aktual original sebagai baseline kesulitan, bukan label kognitif saja — label diwariskan, tetapi soal sumber berlabel C4 dapat sebenarnya hanya meminta pengenalan konsep; menaikkan tuntutan demi menyesuaikan label akan melanggar permintaan pengguna. Biaya jika salah: kesulitan konten tidak setara walaupun metadata sama.
- Ruling: tidak mengklaim kesetaraan parameter IRT — pemeriksaan isi mencakup prasyarat, langkah inferensi, beban hitung, bacaan dan pengecoh; kesetaraan empiris membutuhkan respons siswa. Biaya jika diabaikan: klaim psikometrik tanpa data.
- Baseline preservasi sebelum review: 709 file original/config tetap sama.

## Hasil akhir dua tahap

- Task 1–5: **complete** untuk cakupan67 original. Hasil akhir **206 VERIFIED**, tanpa DRAFT; 20 keluarga memiliki4, 32 memiliki3, 15 memiliki2. Tahap pertama setelah cross-check114 stok, tahap kedua92 stok.
- Reviewer fresh-context membaca67 original/222 kandidat dan runtime: tidak menemukan kunci matematika salah, PG berkunci ganda, profil kunci berubah atau defect runtime penting. Ditemukan30 kelompok Important: D01–D15 kesulitan, V01–V15 variasi. Semua masuk satu pass perbaikan;16 kandidat dihapus, lainnya direvisi. Perbaikan terakhir self-review, tanpa reviewer kedua.
- Re-grade catatan kualitatif sebagai Important tambahan: kategori-1-3-10 stok04 memberi petunjuk pecahan terlalu mudah; kategori-6-3-9 stok03 kehilangan komponen tarif per jam; pg-12-2-4 stok01 memberi pola yang seharusnya diinferensi; mcma-20-3-8 hanya mengganti objek kepuasan. Argumen pertama dan pengecoh kepuasan ditulis ulang; dua kandidat yang mengurangi beban dibuang.
- RED→GREEN: tes cakupan gagal34≠67 sebelum penulisan; tes regresi gagal19 kasus sebelum pemulihan beban;10 tes stok lulus setelah perbaikan. Pemeriksaan statistik memakai mean/median/modus/jangkauan dari angka stimulus; komposisi refleksi diverifikasi pada beberapa titik; persamaan I/II dan identitas aljabar diuji independen.
- Suite awal fase kedua menemukan satu ekspektasi usang pada `test_webui`: pg-16-1-1 tanpa config kini memiliki stok, sehingga variant tidak lagi null. Tes diperbarui untuk membaca stok tanpa generate serta tetap mengecek Tryout tanpa config/stok. Suite final **136/136 PASS,71,431 detik**; log `.scratch/conceptual-stock/full-tests-final.log`.
- Browser actual asset final8771 PASS:67 keluarga/206 stok,11 soal representatif PG/MCMA/KATEGORI, dua kategori custom, selector2/3/4, membaca ulang, kembali ke numeric, HOLD, dua tab; tidak ada page error. DB dimock. Server/browser test milik session ditutup.
- Dokumen aktif README root/folder, GENERATOR, OPERATIONS, ARCHITECTURE, indeks docs, soalskip, plan, ledger dan audit diperbarui. Audit menyertakan67 baseline keluarga,206 catatan varian final dan16 kandidat lama yang dihapus.
- Preservasi final:709 file baseline original/source/metadata/katalog/revisi/config sama SHA-256; Numora/.env/DB/IRT tidak diubah. Tidak ada commit/push/merge.

## Keputusan review dan catatan batas

- Final: Ruling: kesetaraan empiris/IRT tidak dinilai — tidak ada data respons siswa; hasil adalah review kualitatif tugas dan prasyarat. Biaya jika salah dipahami: menganggap stok telah dikalibrasi padahal belum.
- Final: Ruling: koreksi source dan deployment Numora/DB di luar cakupan — original serta database tetap utuh; stok dibaca lokal. Biaya: source lain yang masih bermasalah tetap perlu review terpisah, tidak otomatis dibenahi oleh fitur stok.
- Final: Ruling: slot stok dirapatkan setelah seleksi agar selector1–N valid; stock_version dinaikkan saat konten slot tahap pertama berubah — ID+versi digunakan untuk mengidentifikasi revisi. Biaya jika konsumen hanya menyimpan ID: konten revisi bisa dianggap identik dengan konten lama.
- Final: minor (deferred): variasi kecil bacaan atau prasyarat representasi tetap ada, misalnya refleksi diagonal, representasi desimal versus penutupan operasi, serta faktor luar ekspansi. Diterima dalam review kualitatif; ukur dari respons siswa sebelum menyatakan kesulitan persis sama. Tidak ada perbaikan runtime minor yang ditunda.
- Ruling: branch `feat/conceptual-stock` tetap lokal tanpa commit/merge sesuai batas plan — pengguna tetap dapat meninjau perubahan workspace. Biaya: perubahan masih belum tersimpan sebagai commit.
