# Tryout Image Variants Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Pengguna meminta pekerjaan bertahap; berhenti setelah setiap Task dan tunggu instruksi untuk tahap berikutnya.

**Goal:** Menghasilkan lima gambar varian Tryout dari nilai generator yang sama dengan teks, beserta bundel lokal 30 soal yang dapat direview.

**Architecture:** Template raster yang dibersihkan sekali menerima label dari `Result.values`; limas memakai lapisan air parametrik. Renderer tidak mengacak nilai atau mengubah domain config. Ekspor bundel lokal bersifat opt-in; aktivasi compute bermedia/R2 tidak termasuk implementasi lokal ini.

**Tech Stack:** Python 3.11+, Pillow 12.1.0, DejaVu Sans terbundel/lisensi/hash, unittest, PNG dan JSON manifest. Paket renderer dipisahkan dari dependency core/service existing.

**Spec:** [2026-10-27-tryout-image-variants-design.md](../specs/2026-10-27-tryout-image-variants-design.md).

**Status 27 Oktober 2026:** seluruh tahap 1-5 selesai lokal. [Bukti tahap 5](../../audits/2026-10-27-tryout-image-variants/STAGE_5.md). Upload R2/DB/publikasi tidak dijalankan.

## Global Constraints

- Cakupan hanya `tryout-1-b3-q02/q03/q04/q06` dan `tryout-1-b4-q05` dalam paket `tryout-1`.
- Template/renderer menerima `Result.values` dari kandidat yang sama; dilarang regenerate, parse angka dari stem, atau menghitung dari float ekspor `values_used`.
- Original, arsip DOCX/PNG, config generator, domain angka, kunci dan pembahasan tidak diubah oleh pekerjaan gambar.
- Empat gambar mempertahankan bentuk skematis; limas menyesuaikan permukaan/isi air dengan `p/q`.
- Kelima dimensi kanvas mengikuti spec; PNG maksimum 5 MiB. Font/renderer/template dipin dan memiliki hash.
- Tidak ada render AI per varian, fallback angka lama, pemotongan label, atau pengungkapan jawaban di gambar/alt text.
- Core CLI/package-gen/workbench tetap stateless. Hanya command ekspor baru menulis ke direktori output eksplisit.
- Tidak ada upload R2, write DB, migrasi, Publish, deployment, atau perubahan kontrak generator-service-v1 dalam lima Task lokal.
- Gunakan branch deskriptif tanpa awalan `codex`; lindungi perubahan pengguna yang sudah ada. Worktree untuk implementasi mengikuti skill using-git-worktrees.
- Tidak commit/push otomatis dari plan ini; siapkan diff dan laporan per tahap. Eksekusi tahap berikutnya memerlukan instruksi lanjutan pengguna.

## Review Focus

1. Label berulang tertinggal: kedua angka 180, kedua ekspresi sudut, kedua radius, dan diameter harus mengikuti satu nilai. Tes pada Task 1–3.
2. Binding salah karena nama sama: `h` generator adalah tinggi tabung yang dilabeli `t` pada ilustrasi, sedangkan `t` generator adalah tinggi balok. Tes pada Task 2.
3. Label ekstrem/Unicode: ekspresi sudut panjang, minus, derajat, pecahan, dan unit tidak terpotong atau keluar kotak. Tes pada Task 1/3/4.
4. Identitas stale: seed sama dengan config/template/font berbeda tidak boleh memakai artefak lama; media tidak boleh cocok hanya berdasarkan `record_id`. Tes pada Task 1/5.
5. Kegagalan dan boundary produksi: satu render gagal tidak menghasilkan bundel final parsial; ekspor lokal tidak boleh lolos sebagai media VERIFIED atau melewati penolakan compute v1. Tes pada Task 5.

## Peta file

Seluruh path berikut relatif terhadap root **Numora-ai-service**. Path yang
ditandai Create belum ada; nama/antarmukanya ditetapkan plan ini.

| File | Tanggung jawab |
|---|---|
| Create `requirements-image.txt` | Pin dependency renderer lokal |
| Create `variant_gen/image_variants/{__init__,models,templates,scene,renderer,geometry}.py` | Kontrak data, loader template, binding/layout, rasterisasi, geometri air |
| Create `variant_gen/image_templates/fonts/DejaVuSans.ttf`, `LICENSE.txt`, `manifest.json` | Font redistributable dan pin hash/lisensi |
| Create `variant_gen/image_templates/<question_id>/v1/{template.json,base.png}` | Lima template versioned; limas dapat menambah layer PNG terpisah dalam folder ini |
| Create `variant_gen/tryout_media.py` | Capture hasil generasi dan susun bundel tanpa DB/R2 |
| Modify `variant_gen/cli.py` | Callback opsional dan command `package-media` |
| Modify `variant_gen/tryout.py` | Teruskan callback; schema/perilaku existing dipertahankan |
| Create `variant_gen/tests/test_image_variants_{core,dice,dimensions,angles,pyramid,bundle}.py` | Pengujian renderer/template/bundel |
| Modify `variant_gen/tests/test_stateless.py` | Regresi tidak ada efek tulis pada jalur existing |
| Create `docs/audits/2026-10-27-tryout-image-variants/stage-N/` | Bukti visual, hashes, hasil uji masing-masing tahap; tanggal implementasi dicatat dalam laporan |
| Create `docs/handoffs/TRYOUT_IMAGE_VARIANTS.md` | Kontrak bundel dan gap integrasi compute/R2 |
| Modify `variant_gen/README.md` | Perintah penggunaan dan batas local-only |

Implementasi font/base diambil dari sumber yang lisensinya dapat dibuktikan;
arsip original tetap di `docs/sources/incoming/2026-10-26-tryout-images/`.
Pembersihan gambar raster menggunakan alat image editing sesuai skill yang
berlaku, lalu hasilnya diperiksa visual sebelum menjadi template versioned.

---

### Task 1: Fondasi dan pilot dadu

**Files:** Create dependency, package renderer kecuali geometri air, font, template `tryout-1-b4-q05/v1/`, `test_image_variants_core.py`, `test_image_variants_dice.py`.

**Interfaces:**
- Consumes: original/config hasil loader existing; `Result.values`; lima hash sumber dalam manifest incoming.
- Produces: dataclass `ImageTemplate`, `ImageScene`, `RenderedImage`; `load_template(question_id: str, version: int | None = None) -> ImageTemplate`; `build_scene(template: ImageTemplate, values: dict) -> ImageScene`; `render_scene(template: ImageTemplate, scene: ImageScene) -> RenderedImage`.
- `RenderedImage` memiliki `png_bytes: bytes`, `sha256: str`, `byte_length: int`, `width: int`, `height: int`, `scene: ImageScene`, `provenance: dict`.

- [x] **Step 1 — Tulis tes gagal.** `test_repeated_dice_labels_bind_times` memeriksa nilai 72,180,612,720 di kedua lokasi. `test_threshold_does_not_change_dice_pixels` memeriksa nilai `times` sama dengan threshold berbeda. `test_missing_binding_and_unknown_template_fail` menolak binding hilang, jenis salah, path traversal/URL dan ID selain allowlist.
- [x] **Step 2 — Jalankan tes merah.** `python -m unittest discover -s variant_gen/tests -p 'test_image_variants_core.py' -v` serta pola `test_image_variants_dice.py`; harus gagal karena modul/template belum ada.
- [x] **Step 3 — Siapkan template dan renderer minimal.** Bersihkan kedua angka pada salinan gambar dadu, bundel font beserta lisensi/hash, buat region label/anchor dan formatter bersama. Gambar kartu/ilustrasi tetap; tidak menjalankan pengeditan AI saat render.
- [x] **Step 4 — Tambah tes determinisme dan layout.** PNG dapat didecode sebagai 292×255, ukuran <5 MiB, label muat, hash berulang identik pada environment dipin; font/base hash salah ditolak; teks yang tetap tidak muat pada font minimum gagal eksplisit. `test_pinned_environment_and_template_change_identity` membedakan versi template/font/rendering options.
- [x] **Step 5 — Jalankan kedua suite sampai PASS dan review gambar.** Buat contact sheet original, template bersih, dan empat nilai `times` di atas. Inspeksi sisa angka 180, glyph satuan dan tepi kartu; uji pixel-region membuktikan perubahan terlokalisasi ke region label yang diizinkan.
- [x] **Step 6 — Laporkan Task 1 dan berhenti.** Simpan bukti/hash/command uji di `stage-1/`; tampilkan contoh pilot untuk review pengguna. Tunggu instruksi Task 2.

### Task 2: Taman dan tangki

**Files:** Create template `tryout-1-b3-q02/v1/`, `tryout-1-b3-q06/v1/`, `test_image_variants_dimensions.py`; extend `scene.py` bila diperlukan untuk label diameter memakai evaluator aman existing.

**Interfaces:** Consumes tiga fungsi Task 1. Produces dua template dengan output 489×240 dan 646×318; tidak menambah API renderer baru.

- [x] **Step 1 — Tulis tes gagal.** `test_garden_width_is_twice_radius`: original 20×14 dan seed-1 56×14; radius 7/14/21/28. `test_tank_labels_do_not_swap_cylinder_and_box_height`: r=14,h=15,p=14,l=27,t=30 harus memberi radius 14 dua kali, diameter 28, tinggi tabung 15 dan tinggi balok 30. `test_threshold_does_not_change_tank_pixels` memastikan threshold tidak menjadi label.
- [x] **Step 2 — Jalankan tes merah.** `python -m unittest discover -s variant_gen/tests -p 'test_image_variants_dimensions.py' -v`; template belum ada sehingga FAIL.
- [x] **Step 3 — Bersihkan dan ikat seluruh label.** Template mempertahankan garis ukuran/struktur/ilustrasi; label generator `h` ditempatkan di tinggi tabung walaupun sumber menyebutnya `t`. Tambahkan keterangan skematis pada area template yang tidak menutupi data.
- [x] **Step 4 — Tambah tes batas visual.** Gunakan kandidat yang diterima generator untuk ukuran ekstrem yang mungkin; uji kotak label terhadap kanvas/region terlarang. Periksa bahwa radius kubah/tabung sama dan diameter=2r melalui scene witness dan rumus independen.
- [x] **Step 5 — Jalankan suite dimensions dan core/dice sampai PASS.** Review contact sheet original-values, seed 1, serta label terpanjang; pastikan label 20/14/7/10/15/12 original tidak tertinggal pada varian yang mengubahnya.
- [x] **Step 6 — Laporkan Task 2 dan berhenti.** Simpan `stage-2/` beserta hash sumber yang tetap; tunggu instruksi Task 3.

### Task 3: Ekspresi sudut

**Files:** Create template `tryout-1-b3-q03/v1/`, `test_image_variants_angles.py`; extend format/layout di `scene.py` bila dibutuhkan.

**Interfaces:** Consumes renderer Task 1. Produces template 648×318 dengan empat label dinamis (ekspresi pertama berulang), simbol tetap, dan keterangan skematis.

- [x] **Step 1 — Tulis tes gagal.** `test_angle_labels_repeat_expression_without_leaking_answer`: seed 1 memuat `(4x+17)°` dua kali, `(8x−51)°`, `70°`; tanda C tetap `?`, tanpa `25°` di label jawaban. `test_original_expression_can_render_even_if_outside_random_draw_domain` memberi original-values c=5 untuk review, tanpa mengubah domain generasi c=6–9.
- [x] **Step 2 — Jalankan tes merah.** `python -m unittest discover -s variant_gen/tests -p 'test_image_variants_angles.py' -v`.
- [x] **Step 3 — Siapkan template dan binding ekspresi.** Pertahankan hubungan garis sejajar dan posisi label; gunakan minus/derajat yang didukung font. Tidak menggambar angka x hasil penyelesaian ataupun jawaban sudut C.
- [x] **Step 4 — Tambah tes ekspresi panjang dan glyph.** Enumerasi domain masukan sudut yang berukuran kecil, saring dengan constraints existing, kemudian ukur setiap label; ekspresi yang valid harus muat pada region yang disediakan. Uji label panjang tidak menabrak garis/label tetangga dan label lama tidak tersisa.
- [x] **Step 5 — Jalankan suite angles dan core sampai PASS.** Review original-values, seed 1, serta contoh sudut lancip/tumpul dan ekspresi terpanjang; sketsa tidak digunakan untuk pengukuran piksel.
- [x] **Step 6 — Laporkan Task 3 dan berhenti.** Simpan `stage-3/`; tunggu instruksi Task 4.

### Task 4: Limas dan air parametrik

**Files:** Create `geometry.py`, template/layer `tryout-1-b3-q04/v1/`, `test_image_variants_pyramid.py`; extend renderer untuk layer poligon.

**Interfaces:** Consumes renderer dan `ImageScene`. Produces `pyramid_water_vertices(apex: tuple, rim: tuple, ratio: Fraction) -> tuple` pada `geometry.py`; scene memuat permukaan/isi air dan binding dua rusuk, tinggi, rasio.

- [x] **Step 1 — Tulis tes gagal.** `test_water_vertices_interpolate_exact_fraction` memeriksa W=P+r(V−P) untuk 1/3 dan 2/3; `test_water_stays_inside_vessel_and_moves_monotonically` memeriksa posisi bidang air. `test_same_dimensions_different_ratio_changes_fill_and_label` memastikan perubahan bukan hanya tulisan.
- [x] **Step 2 — Jalankan tes merah.** `python -m unittest discover -s variant_gen/tests -p 'test_image_variants_pyramid.py' -v`.
- [x] **Step 3 — Siapkan wadah tanpa air lama.** Pisahkan latar/garis/air; gambar ulang lapisan wadah bila perlu untuk mempertahankan garis yang sebelumnya tertutup air. Tetapkan apex/rim yang direview dalam template. Isi/permukaan air mengikuti ratio eksak; layer garis depan tetap terbaca.
- [x] **Step 4 — Tambah tes silang matematika dan layer.** Original s=12,h=18,p=2,q=3 memberi hw=12,sw=8,water=256; seed 1 s=9,h=27,p=1,q=3 memberi hw=9,sw=3,water=27. Angka ini diperiksa terhadap oracle terpisah, tidak dicetak sebagai jawaban pada gambar. Uji rasio di luar (0,1) ditolak, dan label pecahan tidak memakai 0,33 yang dibulatkan.
- [x] **Step 5 — Jalankan suite pyramid dan core sampai PASS.** Periksa seluruh 234 kombinasi masukan dasar limas setelah constraints existing; render kombinasi yang valid tanpa melonggarkan syarat. Review dua rasio pada dimensi sama dan contoh dimensi ekstrem untuk mengonfirmasi arsiran, perspektif dan label.
- [x] **Step 6 — Laporkan Task 4 dan berhenti.** Simpan `stage-4/`; tunggu instruksi Task 5.

### Task 5: Bundel Tryout, review lokal, dan handoff

**Files:** Create `tryout_media.py`, `test_image_variants_bundle.py`, `docs/handoffs/TRYOUT_IMAGE_VARIANTS.md`; modify `cli.py`, `tryout.py`, `test_stateless.py`, `variant_gen/README.md`.

**Interfaces:**
- Extend `cli.preview(bank, configs, qid, seed, *, on_generated=None)`; callback `(original, config, result, record)` dipanggil setelah make_record, tidak memutasi record.
- Extend `tryout.generate_package(bank, configs, package_id, seed, *, on_generated=None)` untuk meneruskan callback pada 27 soal generatif; signature positional existing tetap berlaku.
- Create `generate_media_bundle(bank, configs, package_id: str, seed: int) -> MediaBundle` dan `write_media_bundle(bundle: MediaBundle, output: Path) -> Path` di `tryout_media.py`.
- `MediaBundle` memuat manifest existing, lima `RenderedImage`, dan manifest media/provenance. `write_media_bundle` satu-satunya fungsi baru yang menulis output.

- [x] **Step 1 — Tulis tes gagal integrasi.** `test_bundle_has_30_questions_and_5_images` menjaga roster 8/8/7/7 dan tiga original konseptual. `test_renderer_receives_same_accepted_result_without_second_generate` menghitung tepat 27 panggilan engine dan memeriksa object nilai yang diterima callback. `test_existing_preview_and_package_json_unchanged_without_callback` membandingkan keluaran existing.
- [x] **Step 2 — Jalankan tes merah.** `python -m unittest discover -s variant_gen/tests -p 'test_image_variants_bundle.py' -v`.
- [x] **Step 3 — Implementasikan capture dan bundel opt-in.** Tambahkan command `python -B variant_gen/cli.py package-media tryout-1 s1 --output .scratch/tryout-media-s1`. Simpan `questions.json`, `media-manifest.json`, `images/<sha256>.png`, `preview.html` sesuai spec. Callback tetap murni; rendering tanpa ekspor tidak menulis cache.
- [x] **Step 4 — Tambah tes identitas, retry, dan kegagalan.** `test_changed_template_cannot_reuse_stale_asset`; `test_same_seed_changed_config_cannot_reuse_stale_asset`; `test_missing_image_or_failed_render_leaves_no_final_bundle`; `test_output_reuse_checks_all_hashes_and_rejects_different_content`; `test_bundle_paths_cannot_escape_root`; `test_preview_escapes_untrusted_text`. ID pertanyaan terikat fingerprint konten dan binding eksak, bukan seed saja.
- [x] **Step 5 — Tambah tes batas serah-terima.** `test_local_manifest_does_not_claim_r2_verified_or_contain_signed_urls` memastikan status LOCAL_RENDERED; existing tes service tetap menolak media aktif v1. Jangan mengubah `handoff.export_record` agar membuang media diam-diam; dokumentasikan bundle lokal sebagai jalur terpisah sampai kontrak produksi mendukungnya.
- [x] **Step 6 — Jalankan regresi lokal.** Dari root AI: `python -m unittest discover -s variant_gen/tests -p 'test_image_variants_*.py' -v`, lalu pola `test_tryout.py`, `test_stateless.py`, dan `test_tryout_conceptual_stock.py`. Jalankan juga `python -m unittest discover -s tests/service -p 'test_content.py' -v` untuk memastikan boundary media v1 tetap berlaku. Jika runner existing memakai perintah berbeda, ikuti README suite tersebut dan catat command sebenarnya.
- [x] **Step 7 — Uji artefak dan review.** Buat bundel seed 1 serta 20 seed untuk lima gambar (100 gambar); verifikasi label terhadap raw accepted values, hash PNG, tidak ada jawaban bocor, layout dan dimensi. Inspeksi visual contoh original-values/seed 1/batas, bukan mengklaim semua 100 sudah direview hanya karena render sukses. Pastikan hash semua original/config/arsip sama sebelum-sesudah.
- [x] **Step 8 — Tulis handoff dan laporan akhir lokal.** Jelaskan kontrak LOCAL_RENDERED, marker `[[asset:diagram-1]]`/placement yang kelak dibentuk adapter, kebutuhan receipt VERIFIED yang cocok versi, ownership NestJS, pin versi/asset, serta alasan compute v1 belum boleh menerima media. Rencana integrasi lanjutan harus dibuat sebelum aktivasi; bukan pekerjaan terselip pada Task 5.
- [x] **Step 9 — Laporkan Task 5 dan berhenti.** Serahkan bundel, contoh lima gambar, bukti tes, dan daftar gap R2/service. Tidak upload, impor DB, atau Publish. Minta instruksi terpisah jika pengguna ingin melanjutkan integrasi tersebut.

## Kriteria selesai plan lokal

- Lima template siap dan labelnya mengikuti hasil generator yang sama.
- Limas mendukung kedua rasio air existing tanpa mengganti nilai generator.
- Paket review berisi 30 soal dan tepat lima aset dengan provenance yang dapat diverifikasi.
- Tidak ada perubahan domain soal, kunci, pembahasan, atau perilaku generasi stateless existing.
- Pembuktian lokal dibedakan dari integrasi production: tidak mengklaim aktif di R2/compute/student flow.

## Pemeriksaan plan sebelum serah-terima

- Kontrak tipe/fungsi antara Task 1–5 memakai nama yang sama.
- Seluruh binding pada lima gambar memiliki task dan tes spesifik.
- Lima Review Focus dipetakan ke tes di atas.
- Tidak ada Task yang membutuhkan write R2/DB atau mengubah kontrak service diam-diam.
- Pelaksanaan satu per satu dipertahankan; plan ini belum merupakan instruksi menjalankan implementasi.
