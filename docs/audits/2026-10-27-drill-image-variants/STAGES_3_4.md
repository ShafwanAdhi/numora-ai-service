# Tahap 3 dan 4 gambar Drill

**ENGINEERING DECISION - instruksi pengguna:** lanjut sampai tahap 4. Diagram
konseptual dan interface lokal selesai; exporter umum/paket review akhir tahap 5
belum dikerjakan. Tidak ada publikasi, akses DB/R2, atau perubahan generator soal.

## Diagram konseptual

Empat keluarga memiliki 12 skenario: empat original dan delapan stok existing.
Ada delapan PNG unik; gambar yang sama boleh dipakai ulang ketika geometrinya
memang sama, dengan identitas/provenance record yang tetap berbeda.

| Keluarga | Original | Stok 1 | Stok 2 |
|---|---|---|---|
| pg-16-4-2 | Diagram sumber empat panel dipertahankan | Kubus, prisma, limas dengan tiga segitiga, kerucut | Tabung, limas lengkap, prisma, kerucut dengan busur pendek |
| mcma-16-4-6 | Net empat segitiga dan tetrahedron terlipat | Geometri yang sama sesuai stok | Geometri yang sama sesuai stok |
| mcma-16-4-7 | Net tabung tertutup | Net tabung tanpa tutup: satu lingkaran | Net tabung tertutup: dua lingkaran |
| pg-16-5-1 | Panel A-D disertai ukuran 7/44, 7/20, dan 7/44 sesuai record aktif | Panel dengan kecocokan tepi/busur sesuai stok | Satu net tabung dengan ukuran simbolis r, h, p |

Stok terakhir pg-16-5-1 tidak menampilkan rumus p=2*pi*r karena kondisi panjang
selimut itulah yang ditanyakan. Pada semua gambar, alt text menjelaskan data
yang terlihat, bukan menyimpulkan pilihan benar/salah.

PNG dibuat dari geometri deterministik saat penyiapan aset, bukan generator
angka baru. Model gambar tidak dipakai pada tahap ini. Pemilihan skenario
berdasarkan question_id dan stock_variant_id; seed tidak memilih stok.

Pin diperiksa terhadap snapshot original lengkap, versi/hash stok lengkap,
template byte yang diizinkan registry eksternal, sumber, font, dan build renderer.
Semua preview konseptual mengembalikan original_record/stock_record existing
tanpa mengubah stem, opsi, kunci, pembahasan, atau status approval.

[Preview 12 skenario](stage-34/conceptual/preview.html) dan
[record, geometri, provenance](stage-34/conceptual/review.json) tersedia untuk review.
Utilitas penyiapan eksplisit: `tools/prepare_drill_concept_images.py`; menolak
menimpa aset existing dan tidak dipanggil saat mengakses soal.

## Interface lokal

Jalankan dari Numora-ai-service:

```powershell
python -B variant_gen/webui.py --port 8765
```

Buka http://127.0.0.1:8765/image-variants. Pilih aktivitas Tryout/Drill, soal,
dan mode yang tersedia. Katalog berisi lima Tryout dan sembilan Drill.

- **Generator:** masukkan seed positif. Teks dan gambar memakai satu accepted
  Result; peraturan pengundian/penyaringan tidak diubah.
- **Original:** baca versi original aktif; tidak memanggil RNG atau menerima
  kandidat k=0 yang sebelumnya ditolak.
- **Stok:** pilih salah satu ID stok existing; kontrol seed disembunyikan dan
  dinonaktifkan. Gambar mengikuti isi stok, bukan gambar original secara otomatis.

Halaman menampilkan gambar, teks/opsi, kunci/pembahasan, provenance dan unduhan
PNG. Nama file unduhan membedakan original, seed varian, atau indeks/versi stok.
Semua hasil tetap sementara di memori browser/server; tidak ada cache disk otomatis.

## API lokal dan kompatibilitas

- GET `/api/image-variants` tetap memberikan `id` dan `stem`, ditambah `activity`,
  `modes`, dan daftar `stocks` beserta variant_id/index/version.
- POST `/api/image-variants/generate` mempertahankan request Tryout lama
  `{question_id, seed}`. Mode default numerik tetap generator.
- Request baru: `{question_id, mode:"original"}`; seed jika disertakan harus 0.
  Stok: `{question_id, mode:"stock", stock_variant_id}` tanpa seed.
- Respons `record` dan `image` tetap, ditambah `mode` dan `source`. PNG base64
  hanya transport HTTP lokal; tidak mengubah kontrak manifest DB/R2.
- `/image-variants.js` merupakan aset statis tetap, bukan file server arbitrer.
  Guard Host/Origin dan batas body JSON existing tetap berlaku.

Route gambar konseptual dapat membaca original/stok DEFERRED_CONCEPTUAL, tetapi
tidak mengaktifkan `/api/generate` untuk soal tersebut. Business API NestJS,
compute API, database, dan kontrak paket Tryout tidak berubah.

## Bukti pengujian

**94 tes terkait lulus:** 15 numerik Drill, 7 konseptual, 7 mode HTTP, 3 workbench
gambar existing, 44 image/bundle Tryout, 14 Tryout/stock, dan 4 stateless.
Review independen tidak menemukan masalah correctness/security pada tahap 3-4.

Pemeriksaan browser desktop 1600x900 dan mobile 390x844 mencakup unduhan PNG
dengan SHA-256 sesuai metadata, kontrol per mode, respons lama setelah pilihan
diganti, katalog tertunda, gagal/retry, dan teks sumber yang menyerupai HTML.
Tidak ada overflow horizontal; data sumber ditampilkan melalui textContent.

```powershell
python -B -m unittest discover -s variant_gen/tests -p test_drill_concept_images.py -q
python -B -m unittest discover -s variant_gen/tests -p test_image_workbench_modes.py -q
node --check variant_gen/image_variants.js
# Setelah membuka halaman dengan playwright-cli:
# playwright-cli run-code --filename tools/check_image_workbench_browser.js
```

[verification-stage34.json](verification-stage34.json) memuat hash/hasil dan
daftar perubahan yang diizinkan. Berkas sumber, bank/revisi, seluruh config dan
stok, template numerik tahap 2, serta core/template Tryout tetap identik.
Dokumentasi tahap 1-2 dipertahankan sebagai bukti historis.

Tahap 5 (exporter umum Drill dan penutupan review akhir) menunggu instruksi
selanjutnya. Hasil ini tidak menyatakan persetujuan kurikulum/IRT atau publikasi.
