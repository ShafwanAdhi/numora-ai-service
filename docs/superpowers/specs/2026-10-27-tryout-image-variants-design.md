# Generator gambar varian Tryout

Tanggal: 27 Oktober 2026. Status: seluruh tahap 1-5 lokal selesai atas instruksi pengguna; integrasi produksi tetap rencana.

## Maksud pengguna dan batas pekerjaan

**ENGINEERING DECISION — klarifikasi pengguna:** bentuk dasar gambar boleh
dipertahankan, sedangkan angka, variabel, konstanta, dan ekspresi pada gambar
diganti mengikuti hasil generator soal. Kelima soal bergambar Tryout termasuk
cakupan. Pengguna meminta plan terlebih dahulu.

**PROPOSED:** renderer deterministik berbasis template; empat gambar memakai
label dinamis dan limas juga memakai permukaan air dinamis. Tidak membekukan
parameter soal untuk mempertahankan tulisan original, tidak memperluas domain
angka, dan tidak mengganti pola akademik soal menjadi pertanyaan pembesaran.

**PRD RULE — rujukan layanan utama:** konten dan hasil historis memakai versi
yang dipin; DRAFT/preview bukan publikasi. Implementasi gambar tidak memberi
persetujuan akademik, kesetaraan kesulitan, IRT, atau izin Publish.

Target pertama adalah generator gambar **lokal yang dapat direview** pada
repo `Numora-ai-service`, berikut bundel serah-terima untuk integrasi. Penyajian
gambar varian melalui compute service/R2 adalah tahap integrasi berikutnya,
bukan kemampuan yang dianggap otomatis tersedia setelah PNG berhasil dibuat.

## Dasar pemeriksaan

- Bank `variant_gen/data/tryout-1/`: 30 original, 27 generator, 3 konseptual.
- Lima gambar dan hash sumber:
  `docs/sources/incoming/2026-10-26-tryout-images/image-manifest.json`.
- Audit `docs/audits/2026-10-27-tryout-image-compatibility/`: binding label,
  versi/hash, dan 540 sampel keluaran generator. Rekomendasi mempertahankan
  seluruh tulisan gambar pada audit tersebut adalah alternatif historis;
  klarifikasi terbaru pengguna memilih penggantian tulisan.
- `engine.generate` mengembalikan `Result.values` beserta kandidat yang diterima.
  `engine.assemble` membuat teks/opsi/pembahasan dari nilai tersebut.
- Ekspor `values_used` mengubah pecahan menjadi angka JSON yang dapat dibulatkan;
  ini tidak boleh menjadi sumber perhitungan geometri atau label eksak.
- `cli.preview`/`tryout.generate_package` bersifat stateless. Generasi biasa tidak
  boleh tiba-tiba menulis PNG atau paket ke disk.
- `numora_service/content.py` dan kontrak generator-service-v1 saat ini menolak
  media aktif (`MEDIA_NOT_SUPPORTED`, `media=[]`). Jangan menambahkan marker lalu
  menghapus penolakan ini tanpa kontrak dan validasi end-to-end baru.
- Numora mempunyai upload receipt VERIFIED, importer DRAFT, dan akses media
  berbasis versi soal/attempt. Rujukan: repo utama
  `docs/superpowers/specs/2026-10-26-tryout-r2-database-sync-design.md`,
  `docs/api/CONTENT_MEDIA_UPLOADS.md`, dan ADR-008.

## Pendekatan

1. **Template dengan label dinamis — pilihan utama.** Bersihkan tulisan satu
   kali, simpan template, kemudian isi label dengan program. Mempertahankan
   ilustrasi existing dan menghasilkan keluaran yang dapat direproduksi.
2. **Menggambar ulang seluruh diagram secara parametrik.** Berguna jika struktur
   gambar harus berubah; dipakai terbatas pada lapisan geometri limas/air.
   Menggambar ulang taman dan ilustrasi dadu memberi pekerjaan tambahan yang
   tidak diperlukan untuk cakupan ini.
3. **Mengedit seluruh gambar dengan AI setiap kali generate.** Tidak dipilih:
   penempatan label dan geometri perlu terikat secara teruji pada nilai soal.

Pembersihan raster, bila dibutuhkan, dilakukan sekali pada salinan menggunakan
alat pengeditan gambar, kemudian hasilnya ditinjau dan dibekukan. Tidak ada
panggilan AI pada saat menghasilkan setiap varian. Label, garis, panah, dan
arsiran asli tidak boleh tertutup sisa penghapusan atau angka lama.

## Cakupan lima template

| Soal / ukuran kanvas original | Binding yang wajib | Perubahan bentuk |
|---|---|---|
| `tryout-1-b4-q05`, 292×255 | `times` pada kartu dan keterangan `n`; keduanya sama | Tidak ada; wajah dadu tetap ilustrasi |
| `tryout-1-b3-q02`, 489×240 | panjang `p`, lebar `width=2*r` | Bentuk taman tetap skematis |
| `tryout-1-b3-q06`, 646×318 | radius `r` di dua tempat, diameter `2*r`, tinggi tabung `h`, balok `p,l,t` | Bentuk tangki tetap skematis; label `t` tabung pada sumber dipetakan ke variabel generator `h`, bukan `t` balok |
| `tryout-1-b3-q03`, 648×318 | `({a}x+{b})°` di dua tempat, `({c}x−{offset})°`, `{other}°` | Garis sejajar/segitiga tetap skematis; A/B/C, g/h/t dan tanda tanya tetap |
| `tryout-1-b3-q04`, 653×313 | `{s} cm` di dua rusuk, tinggi `{h} cm`, pecahan `{ratio}` | Permukaan dan isi air mengikuti `p/q`, bukan hanya label pecahannya |

`threshold` pada dadu/tangki tidak dipaksakan menjadi label baru karena memang
tidak ada pada gambar sumber. Nilai yang ditanyakan tidak dibocorkan: tanda `?`
pada sudut C tetap, volume/luas/jawaban tidak dimasukkan ke gambar atau alt text.

Gambar geometri diberi keterangan kecil **“Gambar skematis, tidak berskala.”**
sebagai bagian presentasi template, tanpa mengubah teks akademik bank. Toleransi
ini mencakup proporsi sisi/kemiringan yang tidak presisi, bukan label salah,
hubungan sejajar yang rusak, atau tinggi air yang bertentangan dengan pecahan.

## Renderer dan kontrak internal

**PROPOSED stack:** Python 3.11+, Pillow 12.1.0 (versi yang terpasang saat
pemeriksaan), font DejaVu Sans yang dibundel bersama lisensi dan SHA-256.
Dependency renderer dipisahkan dalam `requirements-image.txt`; core generator
tanpa fitur gambar tidak bergantung pada impor Pillow. Versi dependency/font
dibekukan dalam identitas renderer; jangan memakai font OS sebagai fallback.

Pillow menyediakan pengukuran batas teks dan penggambaran poligon yang diperlukan
untuk label serta bidang air: [dokumentasi ImageDraw resmi](https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html).

Fungsi inti yang direncanakan:

```python
load_template(question_id: str, version: int | None = None) -> ImageTemplate
build_scene(template: ImageTemplate, values: dict) -> ImageScene
render_scene(template: ImageTemplate, scene: ImageScene) -> RenderedImage
```

- `ImageTemplate`: ID/versi, ID soal, hash sumber/base/font, kanvas, region label,
  urutan layer, renderer yang diizinkan, serta kontrak nama/jenis variabel.
- `ImageScene`: daftar label terformat, binding eksak tiap label, bounding box,
  geometri dan alt text. Scene adalah bukti yang dapat diperiksa selain piksel.
- `RenderedImage`: `png_bytes`, SHA-256, ukuran byte, dimensi, scene, dan provenance
  template/renderer. Byte hanya ditulis oleh eksportir yang diminta eksplisit.
- Template lokal merupakan input terkontrol: tidak menerima URL, path arbitrer,
  font eksternal, atau kode Python dari JSON. Binding memakai formatter/ekspresi
  aman existing, tanpa `eval` atau OCR pada saat generate.

Renderer menerima **`Result.values` dari kandidat yang sudah diterima**. Tidak
mengacak ulang, memanggil generator kedua kali, atau mengekstrak nilai dari teks.
Format angka/satuan/pecahan mengikuti formatter generator; binding eksak disimpan
sebagai integer atau pasangan pembilang/penyebut, tidak melalui float dibulatkan.

Render memakai koordinat kanvas original, menggambar pada skala internal 2×,
lalu mengekspor PNG pada dimensi kanvas di tabel. Label memiliki kotak, anchor,
padding dan rentang font yang ditetapkan template. Label panjang diukur sebelum
digambar; kecilkan sampai batas minimum yang direview, lalu gagal jika tetap
tidak muat. Jangan memotong teks atau mengubah nilainya agar muat.

Jika label/geometri gagal, keluaran media untuk soal itu gagal dan bundel lengkap
tidak diterbitkan. Jangan diam-diam memakai gambar original dengan angka salah,
atau menarik nilai baru sehingga teks yang sudah diterima berubah.

## Geometri air limas

Kanvas mempertahankan proyeksi wadah yang direview. Template menyimpan titik
puncak bawah P dan empat titik rusuk atas V_i. Dengan rasio eksak `r=p/q`:

`W_i = P + r × (V_i − P)`

Empat W_i menentukan bidang air; bagian berisi air adalah limas bawah dengan
puncak P. Koordinat dihitung eksak sebelum konversi ke piksel. `r=1/3` dan `2/3`
harus memberi bidang air berbeda dan terletak di dalam wadah. Urutan layer:
latar, struktur belakang, isi air, bidang permukaan, garis depan, lalu label.
Pembersihan template harus menghapus **seluruh air lama**, bukan hanya label 2/3.

Volume tidak dihitung ulang dengan rumus terpisah untuk label gambar. Uji
independen memastikan scene konsisten dengan `hw=h*p/q`, `sw=s*p/q`, dan
`water=(s*s*h/3)*(p/q)^3` dari kandidat yang sama. Bentuk wadah boleh skematis;
perbandingan posisi air terhadap wadah tetap mengikuti rasio.

## Integrasi lokal dan identitas artefak

Tambahkan callback internal opsional `on_generated(original, config, result,
record)` pada `cli.preview` dan `tryout.generate_package`. Callback membaca hasil
generasi yang sama, tanpa mengubah record. Pemanggil existing tanpa callback
mendapat perilaku/JSON yang sama dan tidak menghasilkan berkas.

Jalur baru `package-media tryout-1 sN --output <directory>` menghasilkan bundel
lokal terpisah, bukan mengubah schema manifest existing secara diam-diam:

```text
<directory>/
  questions.json       # manifest 30 soal existing, hasil generate satu kali
  media-manifest.json  # 5 aset, binding, hash, provenance, placement STEM
  images/<sha256>.png
  preview.html         # review lokal kelima gambar + soal terkait
```

22 generator tanpa gambar dan 3 original konseptual tetap pada urutan roster
existing; tidak dipasangi gambar baru. `preview.html` menggunakan gambar lokal
bundel, melakukan escaping teks, tidak membawa token atau signed URL. Ini
artefak review, bukan perubahan UI aplikasi utama/workbench pada tahap ini.

Setiap aset mengikat `question_id`, seed, versi/hash original dan config,
fingerprint konten record (tidak termasuk timestamp operasional), hash binding
eksak, ID/versi/hash template, hash font, renderer/environment ID, dan hash PNG.
`record_id` saja tidak cukup karena rerender dengan template baru bisa memiliki
seed/ID record sama. Identitas artefak dihitung dari semua input tersebut.
Identitas byte gambar terpisah sehingga nilai berbeda yang tidak muncul pada
gambar dapat memakai PNG identik, tetapi referensi per soal tetap terlacak.

Reproduksibilitas byte dijamin pada environment renderer yang dipin. FreeType,
Pillow, font, opsi PNG, dan dependency terkait dicatat; tidak ada timestamp acak
pada PNG. Perubahan environment/template membuat identitas artefak baru.

Exporter menulis ke direktori sementara pada parent output yang sama, memvalidasi
seluruh bundel, lalu memindahkan ke target baru. Target nonkosong yang berbeda
ditolak. Retry input identik memverifikasi dan memakai bundel yang sama; tidak
menimpa artefak berbeda atau meninggalkan manifest final yang setengah lengkap.

## Batas integrasi R2 dan service utama

**PROPOSED, tahap lanjutan:** gambar dibuat saat persiapan varian, diunggah melalui
reservasi/completion NestJS, lalu reference VERIFIED dipin bersama versi konten
varian sebelum varian dapat dipakai dalam paket. Tidak merender saat siswa GET.
Output PNG mengikuti batas MIME/5 MiB existing; key immutable memakai hash baru.
Database tidak menyimpan PNG/base64 atau signed URL permanen.

Kontrak bundel lokal membedakan `LOCAL_RENDERED` dari `R2_VERIFIED`. Bundel lokal
tidak boleh mengarang bucket/object key/receipt atau diklaim siap disajikan oleh
service. Persetujuan upload lima **original** pada pekerjaan sebelumnya tidak
dianggap persetujuan upload semua gambar varian baru.

Sebelum aktivasi compute bermedia, rencana integrasi terpisah harus mencakup:
kontrak versi/capability media di kedua repo; ownership upload oleh NestJS;
receipt versi yang tepat; hash canonical termasuk media; marker/placement;
pin UUID versi di paket/attempt; authorization WORK/REVIEW; retry/idempotensi;
dan penyimpanan hasil generasi varian pada keluarga yang benar. Importer
original tidak boleh dipakai untuk menyamarkan varian sebagai original baru.
Jangan mengubah `media=[]` menjadi permisif atau menonaktifkan guard existing
sebagai jalan pintas. Handoff tahap lokal menyertakan daftar gap ini.

## Pengerjaan bertahap dan penerimaan

Lima tahap lokal dikerjakan satu per satu sesuai instruksi lanjutan pengguna:

1. Fondasi renderer dan pilot dadu: dua label berubah bersama.
2. Taman dan tangki: seluruh ukuran, satuan, serta label radius/diameter konsisten.
3. Sudut: ekspresi panjang dan label berulang benar tanpa membocorkan jawaban.
4. Limas: semua label dan posisi air mengikuti kandidat yang sama.
5. Integrasi bundel 30 soal, preview, regresi, dan handoff R2/service.

Setiap tahap menghasilkan contoh original-values, seed 1, dan kasus batas untuk
direview. Berhenti setelah laporan tahap; tahap berikutnya menunggu instruksi.
Tidak menjalankan kelima tahap hanya karena plan ini tersedia.

Kriteria akhir lokal: lima template lolos pemeriksaan binding dan layout;
pecahan/derajat/superskrip terbaca; tidak ada label original tertinggal; satu
hasil generate dipakai untuk teks dan gambar; bundel memiliki 30 soal/5 gambar;
retry konsisten; input sumber/config tetap; generasi existing stateless tetap
lulus. Review visual melengkapi tes scene/piksel dan bukan digantikan oleh tes
yang hanya membaca ulang label yang baru ditulis program.
