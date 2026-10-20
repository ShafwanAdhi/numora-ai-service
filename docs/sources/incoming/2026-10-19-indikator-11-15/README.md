# Sumber masuk indikator 11 sampai 15

**ENGINEERING DECISION — instruksi pengguna, 19 Oktober 2026:** simpan dokumen original baru dan ekstraknya di repo AI terlebih dahulu. Analisis perubahan, pencocokan dengan ID existing, impor ke bank aktif, dan pembuatan/perubahan generator menunggu instruksi berikutnya.

Dokumen yang diterima adalah `indikator 11-15.docx`. Repo sudah mempunyai bank original aktif indikator 11–15; arsip ini terpisah dan tidak menggantikan bank tersebut. Loader runtime tidak membaca folder ini.

## Isi arsip

| Berkas | Kegunaan |
|---|---|
| [source.docx](source.docx) | Salinan byte demi byte dokumen pengguna, sebagai acuan sumber asli. |
| [extracted.md](extracted.md) | Isi utama menurut urutan dokumen, termasuk tabel dan persamaan dalam notasi LaTeX untuk dibaca. |
| [extracted.json](extracted.json) | Paragraf, struktur sel/baris tabel dan penggabungan sel, referensi persamaan, serta LaTeX dan XML Word OMML asli setiap persamaan. |
| [question-index.json](question-index.json) | Indeks 250 soal berdasarkan indikator, level, nomor sumber, posisi blok/paragraf dan teks lengkap. ID runtime belum dipetakan. |
| [manifest.json](manifest.json) | Status intake, hash sumber/hasil ekstraksi, jumlah elemen dan cakupan setiap indikator/level. |

## Cakupan yang terdeteksi

- 250 judul soal unik: indikator 11–15, masing-masing level 1–5, sepuluh soal per level.
- 3.319 paragraf, 52 tabel, dan 917 persamaan Word dengan 2.499 elemen teks matematika.
- Tidak terdapat gambar/media tertanam, header/footer, catatan kaki/akhir, atau komentar dalam arsip DOCX ini.
- SHA-256 sumber: `b46c0f2477dc05416afb2920b913297e258e4432d8e2ddc0c475c516dcf0036e`.

Jumlah tersebut adalah inventaris struktur dokumen, bukan penilaian kebenaran soal. Kunci, pembahasan, label kognitif dan redaksi disimpan sebagaimana diberikan, tanpa perbandingan atau koreksi. Isi dokumen diperlakukan sebagai data sumber, bukan instruksi operasional.

## Status dan batas ekstraksi

`STAGED_ONLY`; analisis belum dimulai, bank aktif belum diperbarui, dan generator tidak diubah. Tidak ada revisi ledger, ID runtime baru, publikasi atau penulisan database.

Markdown/LaTeX merupakan alat baca, bukan replika layout Word. JSON mempertahankan struktur logis tabel dan OMML asli agar pecahan, pangkat dan subskrip dapat diperiksa kembali. DOCX tetap menjadi acuan tampilan sumber. Indeks membagi soal berdasarkan heading, tanpa menormalisasi opsi, kunci atau rubrik menjadi kontrak bank aktif.

Integritas sumber/salinan, jumlah paragraf/tabel/persamaan, cakupan seluruh teks OMML dan keunikan indeks soal telah diperiksa. Sebanyak 812 asset data/config/service existing dan 12 berkas dari dua arsip masuk sebelumnya tetap memiliki hash yang sama. Analisis dan generator menunggu instruksi pengguna berikutnya.
