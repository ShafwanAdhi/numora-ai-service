# Tahap 2 gambar numerik Drill

**ENGINEERING DECISION - instruksi pengguna:** lanjut satu tahap dari rencana
yang disetujui. Tahap ini mencakup lima keluarga numerik saja. Empat keluarga
konseptual, integrasi interface, dan exporter Drill tetap menunggu tahap 3-5.

## Hasil

Kelima template v1 memakai canvas 960 x 640 dan renderer/font existing.
Adapter baru berada di `variant_gen/drill_images`; modul generator, config,
bank, core image_variants, template Tryout dan workbench existing tidak diedit.

| Keluarga | Gambar | Ukuran original | Domain varian |
|---|---|---|---|
| pg-16-4-1 | Net tabung baru | r=7, tinggi=10 | r=7(k+1), tinggi=10(k+1) |
| pg-16-4-3 | Net kerucut baru | r=14, s=20 | r=14(k+1), s=20(k+1); sudut geometri 252 derajat |
| pg-16-4-4 | Net limas baru yang konsisten | sisi=12, tinggi segitiga=10 | sisi=12(k+1), tinggi segitiga=10(k+1) |
| pg-16-5-3 | Ilustrasi sumber, label s diganti | s=12, sudut=150 | s=12(k+1); sudut tetap 150 |
| pg-16-5-5 | Ilustrasi sumber, label ukuran diganti | sisi=10, tinggi segitiga=13 | sisi=10(k+1), tinggi segitiga=13(k+1) |

k=1..30 sesuai penyaringan existing. k=0 hanya acuan dimensi original, bukan
varian yang dipaksa melewati filter. Seed berbeda dapat menghasilkan k sama.
Net kerucut pg-16-4-3 memakai sudut geometris yang benar tanpa menambahkan label
sudut hasil hitungan pada soal. Demikian pula label panjang selimut tabung
bersifat simbolis, tidak menyisipkan jawaban luas permukaan.

Kunci pg-16-5-5 tetap D pada original dan C pada varian. Tinggi segitiga pada
gambar adalah 13(k+1), tidak mengambil klaim tinggi limas dari v9. Alt text
mendeskripsikan data gambar tanpa menyatakan benar/salahnya pernyataan soal.

## Penggunaan dan review

- [Preview 155 gambar beserta soal](stage-2/review/preview.html).
- [Record dan provenance lengkap](stage-2/review/review.json).
- [Bukti cakupan seed/domain dan hash hasil](stage-2/domain-verification.json).
- [API Python dan contoh penggunaan](../../../variant_gen/drill_images/README.md).

Preview ini adalah artefak audit statis, bukan endpoint/workbench baru. Halaman
`/image-variants` existing masih melayani lima soal Tryout sampai tahap 4.
Gambar tersimpan bersama preview pada folder images, sehingga HTML bisa dibuka
langsung dengan seluruh folder tetap bersama.

Untuk membuat ulang audit di lokasi baru dari root repo:

```powershell
python -B tools/audit_drill_numeric_images.py --output .scratch/drill-image-stage2-review
python -B -m unittest discover -s variant_gen/tests -p test_drill_image_numeric.py -q
```

Audit menolak menimpa direktori output existing. Ini utilitas review khusus
tahap 2, bukan exporter umum/paket Drill yang dijadwalkan untuk tahap 5.

## Penyiapan aset

Tiga net dibuat sebagai geometri kode deterministik: dua lingkaran dan persegi
panjang, lingkaran/juring yang busurnya cocok, serta persegi dan empat segitiga
kongruen dengan tinggi yang benar. Dua ilustrasi lain dibersihkan melalui
**built-in image_gen edit**, kemudian disusun sebagai template statis. Model
gambar tidak dipanggil ketika menghasilkan soal atau varian.

Seluruh pixel asli di luar masker pembersihan dipertahankan sebelum penempatan
di canvas. Label tinggi segitiga pg-16-5-5 diarahkan ke garis tinggi horizontal,
bukan garis ukuran miring pada ilustrasi sumber. Semua gambar diberi keterangan
skematis/tidak berskala; perubahan ukuran di domain ini berupa kesebangunan.

Input edit, masker, hash, dan prompt tersimpan di
[asset-preparation](stage-2/asset-preparation/preparation.json). Skrip penyiapan
`tools/prepare_drill_numeric_templates.py` hanya untuk build aset eksplisit dan
menolak menimpa template existing; bukan bagian dari runtime.

## Verifikasi dan batas

Audit mencakup **5 original dan 150 varian dari seed nyata**. Semua k=1..30
tercakup untuk setiap keluarga; tidak hanya sampling. Setiap hasil diperiksa
dengan rumus matematika independen, nilai/kunci existing, konsistensi geometri,
layout label, SHA-256 PNG, dan record sebelum/sesudah penambahan gambar.

Pin template bersifat eksternal melalui registry, bukan hanya hash diri dari
JSON yang sedang dibaca. Perubahan template, original/config lengkap, byte
config, font, atau build renderer ditolak sebelum menggambar. Tes juga memblokir
socket, koneksi database, dan mode penulisan berkas saat preview berjalan.

[verification-stage2.json](verification-stage2.json) mencatat hasil tes,
review kode, dan perbandingan 1.265 berkas sebelum tahap 2. Bukti Tahap 1
tetap disimpan sebagai snapshot historis; tambahan template baru pada tahap ini
tidak ditulis kembali ke baseline lama.

Tidak ada perubahan angka/rentang/distribusi/filter/opsi/kunci/pembahasan,
status approval/self-adjustment, akses DB/R2, publikasi, atau aktivasi siswa.
Pemeriksaan matematika ini merupakan bukti engineering lokal dan tidak
menggantikan persetujuan kurikulum atau kesetaraan kesulitan/IRT.
