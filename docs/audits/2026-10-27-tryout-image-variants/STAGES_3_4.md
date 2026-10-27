# Hasil tahap 3 dan 4 — sudut dan limas

Tanggal: 27 Oktober 2026. **ENGINEERING DECISION — instruksi pengguna:**
“lanjutkan step 3 dan 4”. Kedua tahap selesai lokal; tahap 5 belum dijalankan.

Kelima template Tryout kini tersedia. Dua tambahan pada tahap ini:

- **Sudut:** empat label numerik/ekspresi mengikuti nilai generator, termasuk
  ekspresi yang berulang di dua tempat. Huruf titik/garis, tanda sejajar, dan
  tanda tanya merah dipertahankan. Nilai x dan jawaban sudut C tidak dicetak.
- **Limas:** dua label rusuk, tinggi total, pecahan, permukaan air dan isi air
  mengikuti kandidat yang sama. Rasio 1/3 dan 2/3 memberi permukaan berbeda.
  Pecahan memakai `Fraction` eksak, bukan float hasil ekspor yang dibulatkan.

## Contoh

| Contoh | File |
|---|---|
| Sudut, seed 1 | [Gambar](stage-3/angles-seed-1.png) |
| Ekspresi panjang | [Gambar](stage-3/angles-long-expression.png) |
| Limas, air 1/3 | [Gambar](stage-4/pyramid-water-1-3.png) |
| Limas, air 2/3, ukuran wadah sama | [Gambar](stage-4/pyramid-water-2-3.png) |
| Perbandingan sudut | [Contact sheet](stage-3/angles-contact-sheet.png) |
| Perbandingan limas | [Contact sheet](stage-4/pyramid-contact-sheet.png) |

48 PNG review tersimpan: 40 keluaran generator seed 1–20 dan delapan fixture
original/batas/rasio. `examples-stage34.json` mengikat gambar dengan raw values,
scene, config/original dan provenance renderer. Bukti tahap 1–2 dipertahankan;
hash renderer pada laporan lama adalah snapshot versi sebelumnya.

## Pemeriksaan

**48 tes PASS:** 31 tes renderer gambar (8 core, 3 dadu, 7 dimensi, 4 sudut,
9 limas), ditambah 8 Tryout, 3 stateless, dan 6 stok konseptual Tryout.

- Semua string label yang mungkin dari kombinasi masukan sudut yang memenuhi
  constraints diperiksa terhadap kotak/layout, termasuk minus Unicode dan derajat.
  Pemeriksaan ini adalah cakupan layout, bukan audit akademik baru seluruh soal.
- Seluruh 234 kombinasi masukan dasar limas diperiksa: 138 memenuhi constraints
  generator dan dirender; 96 ditolak oleh constraints existing. Ini mencakup
  original/fixture, bukan klaim 138 varian unik yang lolos seluruh validator.
- Geometri air diperiksa independen dengan W=P+r(V−P), rasio luas proyeksi,
  posisi di dalam wadah, arah perubahan tinggi, dan perubahan piksel isi air.
- Rumus independen untuk contoh original memberi tinggi air 12, sisi air 8,
  volume 256; contoh seed 1 memberi 9, 3, 27. Jawaban tidak dimasukkan ke gambar.
- Rasio tidak sah, float yang dibulatkan, template dengan rim bersilangan/
  degenerat, dan scene geometri yang dimodifikasi ditolak.
- Kasus glyph lama yang tertinggal pada baseline label sudut ditangkap tes gagal,
  diperbaiki pada region cleanup, lalu lulus. Perbandingan visual akhir diperiksa.
- Sumber original, arsip, config, kunci, pembahasan, dan rentang generator tetap.

Perintah dari root repo AI:

```powershell
python -m unittest discover -s variant_gen/tests -p 'test_image_variants_*.py' -q
python -m unittest discover -s variant_gen/tests -p 'test_tryout.py' -q
python -m unittest discover -s variant_gen/tests -p 'test_stateless.py' -q
python -m unittest discover -s variant_gen/tests -p 'test_tryout_conceptual_stock.py' -q
python docs/audits/2026-10-27-tryout-image-variants/render_stage34_examples.py
```

## Keputusan dan review

Worktree tahap sebelumnya dipakai ulang setelah sinkronisasi diperiksa. Hanya
delta tahap 3–4 disalin kembali; tidak ada commit/push atau write DB/R2.

Sudut dibersihkan sekali menggunakan built-in imagegen, lalu patch region label
dikomposit dengan original. Prompt dicatat di `image-edit-prompts-stage34.json`.
Limas digambar dengan kode geometri, sesuai opsi redraw pada plan; proyeksi dan
kanvas mengikuti sumber. Ini mengganti lapisan wadah/air, bukan mengubah PNG
arsip original. Pendekatan tersebut mencegah air lama 2/3 tertinggal. Jika
proyeksi/urutan layer keliru, gambar bisa menyesatkan; tes geometri dan review
visual dipakai untuk memeriksanya. Bentuk tetap dinyatakan skematis.

Review kode terpisah tidak menemukan Critical atau Important. Dua minor dicatat:

1. Domain pada tes cakupan penuh ditulis eksplisit dan sesuai config saat ini;
   perubahan domain di masa depan perlu memperbarui atau mem-pin tes tersebut.
   Hash config saat pemeriksaan dicatat dalam bukti, sehingga cakupan tidak
   diklaim berlaku untuk versi config yang belum diperiksa.
2. Metadata provenance hasil masih dictionary mutable, seperti catatan tahap
   1–2. Konsumen lokal memperlakukannya read-only; status lokal bukan receipt
   VERIFIED/otorisasi. Integrasi produksi kelak harus memvalidasi ulang.

Renderer tetap menghasilkan byte di memori dan tidak memanggil AI per varian.
CLI/workbench belum otomatis memasang gambar; paket, callback, dan handoff
integrasi adalah tahap 5. Tidak ada klaim approval akademik, Publish, atau IRT.
