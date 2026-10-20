# Sumber masuk indikator 16 sampai 19

**ENGINEERING DECISION — instruksi pengguna, 19 Oktober 2026:** simpan dokumen original baru dan ekstraknya terlebih dahulu. Analisis perubahan, pemilihan versi sumber, pencocokan ID existing, impor ke bank aktif, dan pembuatan/perubahan generator menunggu instruksi berikutnya.

Dokumen yang diterima adalah `indikator 16-19.docx`. Arsip ini terpisah dari bank aktif indikator 16–19. Loader runtime tidak membaca folder ini.

## Isi arsip

| Berkas | Kegunaan |
|---|---|
| [source.docx](source.docx) | Salinan byte demi byte dokumen pengguna, sebagai acuan sumber asli. |
| [extracted.md](extracted.md) | Isi utama menurut urutan dokumen, termasuk tabel, persamaan LaTeX untuk dibaca, dan tautan gambar pada posisi sumber. |
| [extracted.json](extracted.json) | Paragraf, struktur tabel, persamaan beserta XML Word OMML asli, posisi/referensi gambar, relationship dan bookmark sumber. |
| [question-index.json](question-index.json) | Indeks setiap kemunculan heading soal beserta posisi dan isi lengkap. ID runtime belum dipetakan; nomor berulang memiliki `source_occurrence` berbeda. |
| [media](media/) | Empat belas gambar asli, disalin tanpa perubahan atau OCR. |
| [source-parts](source-parts/) | XML header/footer dan relationship dokumen; tautan eksternal tidak diakses. |
| [manifest.json](manifest.json) | Status intake, hash sumber/berkas ekstraksi, inventaris elemen dan nomor sumber berulang. |

## Cakupan yang terdeteksi

- Indikator 16–19, masing-masing level 1–5: 20 kelompok sumber.
- **201 kemunculan heading soal dengan 200 kombinasi indikator/level/nomor unik.** Indikator 17 level 2 memuat dua bagian bernomor Soal 10; keduanya disimpan, tanpa memilih atau menggabungkan versi. Kelompok itu mempunyai 11 kemunculan heading; kelompok lain masing-masing sepuluh.
- 2.650 paragraf isi utama, 41 tabel, 731 persamaan Word dengan 3.636 elemen teks matematika, serta 14 gambar tertanam.
- Header dan footer tersedia tanpa teks literal; XML aslinya tetap diarsipkan. Tidak ada bagian komentar atau catatan kaki/akhir.
- SHA-256 sumber: `8182d606d4a27e6ab3c80834a36648796d395ee8f66a5ef7b90a3c88587cd232`.

Inventaris ini bukan penilaian kebenaran atau keputusan versi soal yang akan dipakai. Kunci, pembahasan, label kognitif dan redaksi tetap sebagaimana diberikan. Isi dokumen diperlakukan sebagai data sumber, bukan instruksi operasional.

## Status dan batas ekstraksi

`STAGED_ONLY`; analisis belum dimulai, bank aktif belum diperbarui, dan generator tidak diubah. Tidak ada revisi ledger, ID runtime baru, publikasi atau penulisan database.

Markdown/LaTeX merupakan alat baca, bukan replika layout Word. JSON mempertahankan struktur tabel dan OMML asli, termasuk pecahan, akar, pangkat, subskrip dan gabungan subskrip/pangkat. Gambar tetap berupa berkas asli; tidak ditafsirkan atau ditranskripsikan. DOCX menjadi acuan layout dan penempatan visual. Indeks membagi soal menurut heading tanpa menormalisasi opsi, kunci, rubrik, atau nomor berulang menjadi kontrak bank aktif.

Integritas sumber/salinan, struktur seluruh persamaan, cakupan paragraf/tabel, referensi gambar dan nomor kemunculan soal diperiksa saat intake. Sebanyak 812 asset data/config/service existing serta 18 berkas dari tiga arsip sebelumnya tetap memiliki hash yang sama. Analisis dan generator menunggu instruksi berikutnya.
