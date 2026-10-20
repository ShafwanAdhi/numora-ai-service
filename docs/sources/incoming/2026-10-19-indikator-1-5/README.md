# Sumber masuk indikator 1 sampai 5

**ENGINEERING DECISION — instruksi pengguna, 19 Oktober 2026:** simpan dokumen original baru dan ekstraknya di repo AI terlebih dahulu. Analisis perubahan, pencocokan dengan ID existing, impor ke bank aktif, dan pembuatan/perubahan generator menunggu instruksi berikutnya.

Dokumen yang diterima adalah `indikator 1-5.docx`. Repo sudah mempunyai bank original aktif indikator 1–5; paket ini merupakan arsip sumber masuk yang terpisah, bukan pengganti otomatis bank tersebut. Loader runtime tidak membaca folder ini.

## Isi arsip

| Berkas | Kegunaan |
|---|---|
| [source.docx](source.docx) | Salinan byte demi byte dokumen pengguna; acuan sumber asli. |
| [extracted.md](extracted.md) | Seluruh isi utama menurut urutan dokumen, termasuk tabel dan persamaan dalam notasi LaTeX untuk dibaca. |
| [extracted.json](extracted.json) | Paragraf, sel/baris tabel beserta informasi penggabungan sel, referensi persamaan, serta LaTeX dan XML Word OMML asli setiap persamaan. |
| [question-index.json](question-index.json) | Indeks 250 soal berdasarkan indikator, level, nomor sumber, posisi blok/paragraf dan teks lengkapnya. ID runtime sengaja belum dipetakan. |
| [manifest.json](manifest.json) | Status intake, hash sumber/hasil ekstraksi, jumlah elemen dan cakupan per indikator/level. |

## Cakupan yang terdeteksi

- 250 judul soal unik: indikator 1–5, masing-masing level 1–5, sepuluh soal per level.
- 10.092 paragraf, 55 tabel, dan 4.019 persamaan Word yang memuat 9.827 elemen teks matematika.
- Tidak terdapat gambar/media tertanam, header/footer, catatan kaki/akhir, atau komentar dalam arsip DOCX ini.
- SHA-256 sumber: `0e868995fdeb3fe035b625c3bb8252424a2be7dea4dfe48413af79ede18f1147`.

Jumlah tersebut merupakan inventaris struktur dokumen, bukan hasil penilaian kebenaran soal. Kunci, pembahasan, label kognitif, dan redaksi sumber disimpan sebagaimana diberikan; belum dibandingkan atau dikoreksi. Isi dokumen diperlakukan sebagai data sumber, bukan instruksi operasional.

## Status dan batas ekstraksi

`STAGED_ONLY`; analisis belum dimulai, bank aktif belum diperbarui, dan generator tidak diubah. Belum ada revisi ledger, ID runtime baru, publikasi atau penulisan database.

Markdown dan LaTeX adalah alat baca, bukan replika layout Word. JSON mempertahankan struktur logis tabel dan OMML asli agar pecahan, akar, pangkat, subskrip, limit dan delimiter dapat diperiksa tanpa mengandalkan teks datar. Dokumen DOCX tetap menjadi acuan untuk tampilan/layout sumber. Indeks hanya membagi soal berdasarkan heading; belum menormalisasi format, opsi, kunci atau rubrik menjadi kontrak bank aktif.

Integritas sumber/salinan, jumlah paragraf/tabel/persamaan, cakupan seluruh teks OMML, keunikan 250 indeks soal, dan hash 812 asset data/config/service existing telah diperiksa saat intake. Analisis dan generator dilakukan hanya setelah instruksi pengguna berikutnya.
