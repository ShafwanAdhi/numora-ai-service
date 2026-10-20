# Sumber masuk indikator 20 sampai 23

## Pembaruan 21 Oktober 2026

80 soal level4-5 telah diaudit dan diimpor ke bank lokal:67 ACTIVE,13 HOLD_SOURCE. [Laporan](../../../audits/2026-10-21-drill-20-23-level45-import/README.md). DOCX, ekstraksi, indeks dan manifest intake tetap sebagai arsip19 Oktober; status STAGED_ONLY di bawah dan manifest adalah snapshot saat penerimaan. Level1-3 dokumen ini belum direkonsiliasi ulang dengan bank existing.

## Snapshot penerimaan 19 Oktober 2026

**ENGINEERING DECISION — instruksi pengguna, 19 Oktober 2026:** simpan dokumen original baru dan ekstraknya terlebih dahulu. Analisis perubahan, pencocokan ID existing, impor ke bank aktif, dan pembuatan/perubahan generator menunggu instruksi berikutnya.

Dokumen yang diterima adalah `indikator 20-23.docx`. Arsip ini terpisah dari bank aktif indikator 20–23. Loader runtime tidak membaca folder ini.

## Isi arsip

| Berkas | Kegunaan |
|---|---|
| [source.docx](source.docx) | Salinan byte demi byte dokumen pengguna, sebagai acuan sumber asli. |
| [extracted.md](extracted.md) | Seluruh isi utama menurut urutan dokumen, termasuk tabel dan notasi matematika yang ditulis sebagai teks. |
| [extracted.json](extracted.json) | Struktur paragraf dan sel/baris tabel, termasuk informasi penggabungan sel. |
| [question-index.json](question-index.json) | Indeks 200 soal dengan nomor asli, heading indikator/level, posisi sumber dan isi lengkap. ID runtime belum dipetakan. |
| [manifest.json](manifest.json) | Status intake, hash sumber/hasil ekstraksi, jumlah elemen dan cakupan setiap indikator/level. |

## Cakupan yang terdeteksi

- 200 judul soal unik: indikator 20–23, masing-masing level 1–5, sepuluh soal per level.
- Penomoran sumber berlanjut **1–50 pada setiap indikator**, bukan diulang 1–10 pada setiap level. Nomor tersebut dipertahankan tanpa normalisasi ke ID bank aktif.
- 3.064 paragraf isi utama dan 64 tabel.
- Tidak ada objek persamaan Word OMML atau gambar tertanam. Notasi/perhitungan yang ditulis sebagai teks tetap disimpan sebagai teks.
- Tidak ada bagian header/footer, komentar, atau catatan kaki/akhir dalam arsip DOCX ini.
- SHA-256 sumber: `74a6f81a2c65ed9f11fc824f1f999c13fb79faa2887cf5db9311df9b85a19e57`.

Heading level memiliki beberapa bentuk, misalnya `LEVEL 1 — C3`, `Level 4 (C4–C5)`, dan `B. LEVEL 5 (C5)`. Heading level 1 indikator 21 mendahului heading indikatornya. Judul bagian 23 berbentuk `23. peluang dan frekuensi relatif dari kejadian tunggal`. Indeks mempertahankan teks heading asli agar penempatan setiap soal bisa diperiksa kembali.

Inventaris struktur ini bukan penilaian kebenaran soal. Kunci, pembahasan, label dan redaksi tetap sebagaimana diberikan, tanpa perbandingan atau koreksi. Isi dokumen diperlakukan sebagai data sumber, bukan instruksi operasional.

## Status dan batas ekstraksi

`STAGED_ONLY`; analisis belum dimulai, bank aktif belum diperbarui, dan generator tidak diubah. Tidak ada revisi ledger, ID runtime baru, publikasi atau penulisan database.

Markdown merupakan alat baca, bukan replika layout Word. JSON mempertahankan struktur logis tabel; DOCX tetap menjadi acuan tampilan. Indeks hanya membagi soal menurut heading, tanpa menormalisasi opsi, kunci atau rubrik menjadi kontrak bank aktif.

Integritas sumber/salinan, cakupan paragraf/tabel, keunikan indeks soal dan penempatan 20 kelompok indikator/level diperiksa saat intake. Sebanyak 812 asset data/config/service existing serta 41 berkas dari empat arsip sebelumnya tetap memiliki hash yang sama. Analisis dan generator menunggu instruksi berikutnya.
