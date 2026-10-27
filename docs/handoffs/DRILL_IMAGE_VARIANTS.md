# Handoff gambar varian Drill indikator 16-19

Tahap 1-5 lokal selesai. Buka http://127.0.0.1:8765/image-variants dan pilih
Aktivitas Drill. Jika server belum berjalan, jalankan dari Numora-ai-service:

```powershell
python -B variant_gen/webui.py --port 8765
```

Sembilan keluarga soal mencakup lima generator numerik dan empat keluarga stok.
Mode Original tidak mengundi angka; mode Generator memakai hasil accepted
generator existing; mode Stok mengikuti stock_variant_id. Angka pada gambar
berasal dari nilai yang sama dengan soal. Tidak ada aturan generator yang diubah.

Semua diagram DOCX indikator 16-19 berada di indikator 16. Aset di indikator
lain berupa rumus/simbol, bukan diagram terpisah yang hilang dari interface.

Ekspor review dan perintah verifikasi, tabel cakupan 167 pilihan interface,
hash, batas implementasi, serta contoh gambar tersedia di
[laporan Tahap 5](../audits/2026-10-27-drill-image-variants/STAGE_5.md).

Ekspor bersifat lokal/LOCAL_RENDERED, bukan receipt R2 atau publikasi. Tidak ada
integrasi baru ke DB/compute/student runtime, perubahan konten aktif, approval,
atau IRT. Original, config, stok dan template dipin; perubahannya memerlukan
review/versi yang sesuai. Jangan memperbarui pin otomatis agar error menghilang.
