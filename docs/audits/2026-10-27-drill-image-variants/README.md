# Inventaris gambar Drill indikator 16-19

**Status akhir: tahap 1-5 lokal selesai.** Seluruh 167 kombinasi dari sembilan
soal Drill bergambar telah diuji melalui interface `/image-variants`.
[Laporan akhir dan cara mencoba](STAGE_5.md) memuat ekspor review lengkap,
bukti matematika, hasil browser, dan batas penggunaan lokal.

Bagian tahap sebelumnya di bawah merupakan catatan checkpoint historis.

**Update Tahap 3-4:** 12 skenario konseptual selesai dan 14 soal bergambar
Tryout/Drill tersedia pada `/image-variants` melalui mode Original/Generator/Stok.
[Laporan tahap 3-4](STAGES_3_4.md). Tahap 5 belum dikerjakan.

**Update Tahap 2:** lima template numerik dan adapter lokal selesai.
[Laporan Tahap 2](STAGE_2.md) memuat preview lima original dan seluruh 150 varian.
Interface, diagram konseptual, dan exporter umum belum dikerjakan.

**Tahap 1 selesai: arsip dan pemetaan saja.** Renderer, adapter, endpoint, UI,
dan ekspor gambar Drill belum dibuat pada checkpoint Tahap 1. Bagian di bawah
mempertahankan bukti checkpoint tersebut; status terbaru ada pada laporan Tahap 2.

**ENGINEERING DECISION - rencana pengguna:** sembilan keluarga soal dikerjakan
dengan pendekatan gabungan. Bank aktif/revisi existing tetap acuan; tidak ada
perubahan aturan generator, angka, domain, filter, opsi, kunci atau pembahasan.

## Arsip dan bukti

- [DOCX final verbatim](../../sources/incoming/2026-10-27-indikator-16-19-final-images/source.docx).
- [Inventaris lengkap dan pin konten JSON](../../sources/incoming/2026-10-27-indikator-16-19-final-images/image-inventory.json).
- [Pemetaan CSV](../../sources/incoming/2026-10-27-indikator-16-19-final-images/image-map.csv).
- [Manifest hash arsip](../../sources/incoming/2026-10-27-indikator-16-19-final-images/manifest.json).
- [Desain](../../superpowers/specs/2026-10-27-drill-image-variants-design.md) dan [rencana bertahap](../../superpowers/plans/2026-10-27-drill-image-variants.md).
- [Verifikasi Tahap 1](verification-stage1.json), [hash sebelum](protected-before.json), [hash sesudah](protected-after.json).

SHA-256 DOCX final:
`9e837e8631aafccd8cfa2f152f311ef430f7d4b4f9235e43790ec9b191a5bb6c`.

Seluruh teks/persamaan dan gambar sama dengan arsip 19 Oktober (hash DOCX lama
`8182d606d4a27e6ab3c80834a36648796d395ee8f66a5ef7b90a3c88587cd232`).
DOCX bukan identik byte: XML hubungan dan penamaan aset berubah. Semua 14
penempatan terverifikasi melalui byte gambar dan paragraf yang sama.

Indeks paragraf nol berbasis mencakup paragraf dalam tabel; body block mengikuti
arsip ekstraksi lama. XML paragraf penempatan serta semua XML/relationship Word
disimpan agar tabel, OMML, dan konteks asli dapat ditelusuri.

## Cakupan diagram

| ID soal | Media final | Media arsip lama | Original aktif | Mode |
|---|---|---|---|---|
| pg-16-4-1 | image1.jpg | image4.jpg | v2 | config v1 |
| pg-16-4-2 | image3.png | image10.png | v1 | dua stok |
| pg-16-4-3 | image13.png | image14.png | v2 | config v1 |
| pg-16-4-4 | image8.jpg | image1.jpg | v2 | config v1 |
| mcma-16-4-6 | image11.png | image9.png | v2 | dua stok |
| mcma-16-4-7 | image12.png | image12.png | v2 | dua stok |
| pg-16-5-1 | image10.jpg | image2.jpg | v2 | dua stok |
| pg-16-5-3 | image6.png | image7.png | v1 | config v1 |
| pg-16-5-5 | image14.jpg | image3.jpg | v1 | config v1 |

Untuk empat keluarga konseptual, empat original dan delapan stok memerlukan
12 skenario gambar. Ini tidak berarti ada empat generator numerik yang hilang.
Gambar stok akan mengikuti stock_variant_id dan versi/hash kontennya.

## Rumus dan simbol yang bukan diagram

| ID soal | Media final | Isi |
|---|---|---|
| kategori-16-2-10 | image2.png | 6 x 4 x 4 |
| kategori-17-1-10 | image7.png | simbol O |
| kategori-17-2-9 | image9.png | y = x |
| mcma-18-2-7 | image4.png | 2 |
| mcma-19-1-7 | image5.png | 3 |

Aset ini tetap diarsipkan sebagai sumber; tidak dibuatkan generator diagram.

## Pin dan batas pemeriksaan

Ledger menyimpan snapshot original lengkap, termasuk metadata/pembahasan,
original_version/hash, SHA-256 snapshot, config_version/hash beserta SHA-256
berkas, dan snapshot delapan stok. Hash original existing tidak mencakup
pembahasan; SHA-256 snapshot lengkap tidak menggantikannya dalam kontrak runtime.
Status approval dan self-adjustment yang tercatat disalin apa adanya.

Kelima config numerik tetap k=0..30. Pemeriksaan melalui build_values/assemble
dan filter existing menerima k=1..30 untuk setiap config: 150 kombinasi varian.
k=0 ditolak sebagai kandidat; original harus dibaca melalui jalur original.
Ini pemeriksaan domain/filter, **bukan audit akademik baru atau bukti render**.

Pada pg-16-5-5, v9 adalah klaim tinggi limas. Binding tinggi segitiga harus
13*(k+1), bukan v9. Kunci original D dan varian C tetap sesuai config existing.
Pada pg-16-5-3, radius alas yang ditanyakan tidak boleh dimunculkan pada gambar.

Pemetaan SOURCE_TO_ACTIVE_FAMILY tidak mengklaim konten source identik dengan
original aktif yang sudah direvisi. Bagan keliru di sumber tidak mengembalikan
soal aktif ke versi lama. Tidak ada approval kurikulum/IRT baru atau publikasi.

## Verifikasi ulang

Dari root Numora-ai-service:

```powershell
python -B -m unittest discover -s tools -p test_drill_image_inventory.py -q
python -B tools/drill_image_inventory.py --verify
```

Verifikasi memeriksa roster/hash arsip, merekonstruksi ledger dari DOCX dan
konten runtime saat ini, mencocokkan CSV/JSON, serta membandingkan 1.265 berkas
protected. Cakupannya data bank/revisi/stok, seluruh config, template/font
Tryout, renderer/runtime existing, dan arsip sumber lama. Tidak memuat .env.

Jika config atau bank sengaja diubah pada pekerjaan mendatang, verifier akan
menolak pin lama; pertahankan bukti historis dan buat snapshot tahap baru,
bukan menulis ulang bukti Tahap 1 agar cocok.

Belum ada akses DB/R2 maupun perubahan pada workbench atau layanan siswa.
