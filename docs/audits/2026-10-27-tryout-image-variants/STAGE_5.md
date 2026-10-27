# Tahap 5 — bundel lokal 30 soal dan lima gambar

Tanggal: 27 Oktober 2026. **ENGINEERING DECISION — instruksi pengguna:**
“lanjut ke tahap 5”. Tahap 5 selesai lokal; tidak ada upload R2/write database.

## Hasil yang bisa dibuka

- [Preview 30 soal dengan lima gambar](stage-5/bundle-s1/preview.html).
- [Manifest pertanyaan](stage-5/bundle-s1/questions.json).
- [Manifest media dan identitas aset](stage-5/bundle-s1/media-manifest.json).
- [Bukti uji 20 seed](stage-5/seed-audit.json).
- [Handoff integrasi R2/service](../../handoffs/TRYOUT_IMAGE_VARIANTS.md).

Jalankan dari root AI:

```powershell
python -B variant_gen/cli.py package-media tryout-1 s1 --output .scratch/tryout-media-s1
```

Bundel memiliki roster 8/8/7/7. Dua puluh tujuh soal memakai generator, tiga
konseptual memakai original. Lima gambar menerima `Result.values` dari hasil
generate yang sama dengan teks. Collector tidak melakukan generasi tambahan.
Jalur CLI/workbench existing tetap stateless dan tidak otomatis menulis gambar.

Ekspor menyimpan PNG dengan nama hash, versi/hash sumber/config/template/font,
binding eksak, scene, dan identitas konten. Retry identik memakai ulang snapshot
yang sudah diverifikasi; output berbeda atau rusak ditolak. Kegagalan render
atau tulis disk tidak menyisakan direktori final setengah jadi.

## Verifikasi

**71 tes PASS:** 44 tes image-variant (31 tahap sebelumnya + 13 bundel), 14
Tryout/stok, 4 stateless, dan 9 service content. Tes service membuktikan penolakan
media aktif pada kontrak v1 tetap berlaku.

Audit 20 seed menghasilkan 20 bundel, 600 kemunculan soal, 540 panggilan engine
dan pemeriksaan matematika independen, serta 100 kemunculan aset gambar yang
cocok dengan nilai kandidat. Ini bukan klaim 100 PNG unik atau kesetaraan
kesulitan. Seed 1 disimpan sebagai contoh dalam docs; seed lain berada pada
`.scratch/tryout-image-variants/stage5-seeds/` sebagai artefak lokal.

```powershell
python -m unittest discover -s variant_gen/tests -p 'test_image_variants_*.py' -q
python -m unittest discover -s variant_gen/tests -p 'test_tryout*.py' -q
python -m unittest discover -s variant_gen/tests -p 'test_stateless.py' -q
python -m unittest discover -s tests/service -p 'test_content.py' -q
python docs/audits/2026-10-27-tryout-image-variants/audit_stage5.py
```

Preview diperiksa melalui browser pada server loopback: 30 section, lima gambar
berhasil dimuat dengan dimensi benar. Lebar desktop 1600 dan mobile 390 tidak
memerlukan perubahan aset; pada mobile tidak ada overflow horizontal. Screenshot
limas: [desktop](stage-5/preview-pyramid.png),
[mobile](stage-5/preview-pyramid-mobile.png). Satu 404 favicon dari server lokal
tidak terkait konten/gambar. Tool browser memblokir protokol file, sehingga
verifikasi browser dilakukan melalui HTTP loopback, bukan klaim uji file-URL.

Hash seluruh bank/config/arsip Tryout dipertahankan. Tidak ada perubahan API
produksi, kontrak compute, scoring/IRT, atau histori paket/attempt.

## Review dan keputusan

Satu reviewer kode independen tidak menemukan Critical/Important. Minor ditunda:

- Callback equality belum membedakan integer dari float yang nilainya sama.
  Collector renderer internal menerima raw values tanpa mutasi; ini tidak
  mengubah hasil pengujian same-result/single-generate. Integrasi callback baru
  tidak boleh mengandalkan guard ini sebagai security boundary.
- Tes filesystem junction/symlink/race belum mencakup semua cabang. Windows
  menolak pembuatan symlink (1314) saat review; implementasi tetap memeriksa
  reparse point, file roster, hash, dan batas direktori staging.

Keputusan implementasi:

- Perakitan bundel dan penulisan filesystem dipisah menjadi `tryout_media.py`
  dan `tryout_media_io.py` agar dapat diuji terpisah, dengan signature publik plan
  tetap. Risiko salahnya adalah batas validasi tidak konsisten; tes ekspor/
  retry/korupsi/disk failure memeriksa batas tersebut.
- Timestamp operasional created_at tidak menjadi identitas konten. Retry
  menyimpan timestamp ekspor pertama, bukan menimpa artefak karena waktu baru.
- Worktree existing dipakai, hanya delta task disalin kembali; perubahan lain
  dilindungi snapshot hash. Tidak ada merge, commit, atau push otomatis.
- Status LOCAL_RENDERED sengaja dipisahkan dari receipt VERIFIED. Jalur upload,
  mapping canonical, penyimpanan versi varian dan publish belum diaktifkan.

Seluruh lima tahap plan lokal kini terpenuhi. Pekerjaan berikutnya adalah
integrasi canonical/R2 yang dijelaskan pada handoff, dengan instruksi terpisah.
