# Implementasi gambar varian Tryout — tahap 1 dan 2

**Terbaru:** seluruh tahap lokal 1-5 selesai. [Preview paket, pengujian dan handoff](STAGE_5.md).

**Pembaruan:** tahap 3-4 juga selesai. [Hasil sudut dan limas](STAGES_3_4.md). Uraian di bawah adalah snapshot tahap 1-2.

Tanggal: 27 Oktober 2026. **ENGINEERING DECISION — instruksi pengguna:**
“gas implementasi tahap 1 dan 2”. Kedua tahap dikerjakan dalam sesi yang sama;
tahap 3–5 tidak dijalankan.

## Hasil

- Fondasi renderer lokal dan tiga template siap: dadu, taman, tangki.
- Nilai gambar memakai `Result.values` yang sama dengan kandidat generator.
  Tidak ada pengacakan ulang, pembacaan nilai dari stem, atau pembekuan domain.
- Dadu: jumlah percobaan pada kartu dan keterangan berubah bersama.
- Taman: panjang dan lebar sesuai nilai generator, lebar=2×radius.
- Tangki: radius kubah/tabung sama, diameter=2×radius, tinggi tabung mengambil
  `h`, sedangkan tinggi balok mengambil `t`. Semua label source telah dibersihkan.
- Template mempertahankan piksel original di luar region penghapusan tulisan.
  Panah, ilustrasi, wajah dadu dan judul/caption tetap dipertahankan.
- PNG final tetap berukuran 292×255, 489×240, 646×318, semuanya di bawah 5 MiB.
- Renderer menghasilkan byte di memori. Tidak mengubah CLI/workbench, menulis
  DB/R2, mengimpor varian, atau mempublikasikan paket.

## Contoh untuk diperiksa

| Soal | Contoh varian | Perbandingan source/template/varian |
|---|---|---|
| Dadu | [612 percobaan](stage-1/dice-seed-1.png) | [Contact sheet](stage-1/dice-contact-sheet.png) |
| Taman | [56 m × 14 m](stage-2/garden-seed-1.png) | [Contact sheet](stage-2/garden-contact-sheet.png) |
| Tangki | [r=14; tinggi tabung 15; balok 14×27×30](stage-2/tank-seed-1.png) | [Contact sheet](stage-2/tank-contact-sheet.png) |

`examples.json` memuat 67 PNG review (60 kandidat seed 1–20, tiga render
original-values, empat contoh jumlah percobaan dadu), binding/scene/provenance,
versi/hash original dan config. Tiga contact sheet diperiksa langsung secara
visual, termasuk original-values, seed 1 dan seed 20. Ini bukan klaim bahwa
seluruh domain generator telah diaudit visual.

## Pengujian

**35 tes PASS:**

| Suite | Jumlah |
|---|---:|
| `test_image_variants_core.py` | 8 |
| `test_image_variants_dice.py` | 3 |
| `test_image_variants_dimensions.py` | 7 |
| `test_tryout.py` | 8 |
| `test_stateless.py` | 3 |
| `test_tryout_conceptual_stock.py` | 6 |

Tes baru diawali kegagalan karena fitur/template belum tersedia. Pemeriksaan
baru mencakup binding berulang, label dimensi ekstrem, integritas base/font,
penolakan binding tidak eksak, overflow, batas kanvas, perubahan piksel yang
terlokalisasi, determinisme PNG, dan identitas environment/formatter/template.
Jalur existing tetap stateless. Bukti hash input dan artefak ada di
`verification.json`; sumber bank/config/arsip tetap sama.

Perintah dari root repo AI:

```powershell
python -m unittest discover -s variant_gen/tests -p 'test_image_variants_*.py' -v
python -m unittest discover -s variant_gen/tests -p 'test_tryout.py' -q
python -m unittest discover -s variant_gen/tests -p 'test_stateless.py' -q
python -m unittest discover -s variant_gen/tests -p 'test_tryout_conceptual_stock.py' -q
python docs/audits/2026-10-27-tryout-image-variants/render_examples.py
```

## Review independen dan perbaikan

Satu reviewer terpisah memeriksa kode dan gambar. Tidak ada Critical; tiga
Important ditutup dalam satu rangkaian perbaikan, masing-masing dengan regresi:

1. **Tulisan lama pada tangki.** Region awal tidak mencakup seluruh unit diameter
   dan salah menempatkan label panjang. Uji penghapusan/preservasi caption gagal,
   lalu lulus setelah region diperbaiki. Gambar bukti digenerate ulang dan
   diperiksa kembali.
2. **Definisi efektif template.** Perubahan label melalui `dataclasses.replace`
   semula dapat memakai hash template lama. Tes perubahan label yang tetap muat
   gagal terlebih dahulu; verifikasi fingerprint seluruh definisi efektif kini
   menolak perubahan tersebut.
3. **Identitas renderer.** Kini mencakup hash formatter `expr.py`, versi zlib,
   build/platform dan hash binary Pillow/FreeType, serta hash PNG. Tes pin identitas
   gagal sebelum perbaikan dan lulus sesudahnya.

**Minor ditunda:** `RenderedImage.provenance` masih dictionary yang dapat
dimutasi pemanggil, meskipun model hasil dibekukan. Pada tahap lokal ini status
tersebut bukan otorisasi atau receipt R2. Pemanggil harus memperlakukannya
read-only; integrasi berikutnya wajib memvalidasi ulang manifest/hash/receipt,
tidak mempercayai status metadata dari klien. Belum ada konsumen produksi media
yang diaktifkan. Ini tidak memengaruhi byte gambar yang sudah dihasilkan.

## Keputusan pelaksanaan

- Worktree terisolasi membawa salinan kondisi lokal pengguna tanpa commit,
  lalu hanya delta milik tahap 1–2 disalin kembali. Tujuannya menjaga perubahan
  pengguna; jika pemilihan delta keliru, perubahan lain dapat tertimpa, sehingga
  penyalinan dibatasi pada file fitur dan dokumentasi plan yang diperiksa.
- Instruksi terbaru mengizinkan tahap 1 **dan** 2, sehingga checkpoint setelah
  tahap 1 tidak dipakai untuk meminta izin ulang. Batas setelah tahap 2 tetap.
- Hasil pembersihan imagegen dipakai hanya pada region tulisan, lalu dikomposit
  dengan source original. Ini menjaga ilustrasi di luar tulisan. Risiko salah
  region dibatasi oleh tes piksel/preservasi dan review visual di atas.
- Tidak commit/push; ledger lokal dipertahankan karena tidak ada riwayat commit
  task yang dapat menggantikannya. Baseline pengguna tidak dijadikan commit baru.
- Git checkout sempat mengubah line ending CSV pada worktree, tanpa mengubah
  bank pada checkout pengguna. Byte CSV worktree dikembalikan dari salinan sumber
  yang hash-nya sudah dipin; pemeriksaan akhir membandingkan byte, bukan hanya isi
  teks yang sudah dinormalisasi. Ini menghindari klaim hash sama yang keliru.

## Pembersihan gambar

Menggunakan **built-in imagegen**, tiga panggilan edit, bukan CLI/API fallback.
Prompt lengkap ada di `image-edit-prompts.json`. File final yang dipakai renderer
adalah `variant_gen/image_templates/<question_id>/v1/base.png`, dengan metadata
dan hash di `template.json`. Font/lisensi dibundel di `image_templates/fonts/`.

Tahap berikutnya sesuai plan adalah **tahap 3: ekspresi sudut**. Integrasi paket
dan R2 belum termasuk hasil tahap 1–2 ini.
