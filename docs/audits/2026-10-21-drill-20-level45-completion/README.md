# Penyelesaian 13 generator indikator 20 level 4–5

**ENGINEERING DECISION — instruksi pengguna, 21 Oktober 2026:** kerjakan 13 soal indikator 20 level 4–5 yang sudah dimuat tetapi belum memiliki generator.

**13 generator config v1 sudah tersedia pada bank runtime.** Indikator 20 level 4–5 kini memiliki 20 generator untuk 20 original. Total indikator 20: **50 original, 41 generator dan 9 original dengan stok konseptual**, tanpa HOLD atau original yang belum terlayani.

## Cakupan

| Level | Nomor dalam level | Nomor sumber DOCX | Jenis keluarga |
|---|---|---|---|
| 4 | 1, 4, 6, 10 | 31, 34, 36, 40 | Konseptual: hubungan variabel, pertanyaan menggiring, pengukuran kebiasaan, pemisahan aspek |
| 4 | 5, 8 | 35, 38 | Data tabel dan sampel: generalisasi serta keterwakilan |
| 5 | 1, 6, 9 | 41, 46, 49 | Konseptual: skala kepuasan, rancangan survei dan integritas penyajian |
| 5 | 2, 3, 4, 8 | 42, 43, 44, 48 | Data kategori, sebab-akibat, bias sampel dan proporsi |

Semua tetap pada `DRILL / drill-1`, dengan nomor sumber asli 31–50. Tidak ada original baru atau revisi isi sumber. CSV original, opsi, kunci, versi v1, pembahasan sumber, serta arsip DOCX tetap sama.

## Perilaku generator

- Enam keluarga mengubah data tabel/jumlah sampel dan menghitung ulang total, jumlah pengamatan atau proporsi yang dirujuk pada opsi dan pembahasan. Evaluasi tetap membedakan fakta sampel dari generalisasi populasi dan sebab-akibat.
- Tujuh keluarga konseptual menyusun skenario dengan kombinasi sasaran penelitian, populasi, objek kepuasan, aspek pertanyaan atau periode pengukuran. Pertanyaan tentang membaca, olahraga, gawai, perpustakaan, sarapan dan perjalanan memakai kalimat khusus sesuai perilaku yang diukur.
- Konteks pada stimulus dan opsi saling terikat. Pemeriksa menolak pasangan variabel, layanan, aspek, sasaran perilaku, sasaran survei atau sasaran diagram yang tidak sesuai.
- Domain setiap config adalah `k=0..24`. Nilai 0 mereproduksi stimulus, opsi dan kunci original; nilai 1–24 menghasilkan **24 varian efektif per keluarga**, total 312. Ini kapasitas berhingga per keluarga, bukan 312 original tambahan.
- Engine/config existing digunakan tanpa evaluator baru, panggilan LLM, perubahan API atau penulisan hasil runtime ke file/database. Seed sama menghasilkan varian yang sama; seed berbeda belum tentu unik.

## Bukti pemeriksaan

- **325 kasus input** diperiksa menyeluruh: seluruh opsi/kunci, perhitungan data, dan alasan konseptual dalam keluarga yang didukung.
- **260 sampel unik** melalui jalur generate runtime dan **130 panggilan seed tambahan** untuk pemeriksaan determinisme.
- 7 tes baru lulus, termasuk seluruh domain, mutasi kunci/angka/klaim, integritas aset dan generate HTTP untuk semua 13 ID tanpa koneksi database atau penyimpanan hasil.
- 11 tes impor dan generator level 4–5 indikator 20–23 sebelumnya tetap lulus.
- 14 tes service lulus; 11 tes PostgreSQL dilewati karena cluster uji tidak dijalankan.
- Seluruh 1.078 generator workspace diperiksa validasi config, reproduksi original dan satu pemanggilan seed tetap tanpa error. Pemeriksaan global ini bukan enumerasi ulang seluruh parameter atau audit akademik ulang seluruh bank.
- Hash **1.372 aset sebelumnya** tetap sama. Satu berkas metadata bersama diperbarui hanya pada 13 ID: `generator_status`, jenis keluarga dan tautan audit; seluruh metadata sumber dan entri lain dipertahankan.
- Review terpisah menemukan dan menutup masalah kalimat pertanyaan kebiasaan serta pengikatan sasaran penelitian; tes regresi menolak kasus-kasus yang dilaporkan.

## Persetujuan dan batas

**PROPOSED:** keluarga/rentang varian baru belum merupakan persetujuan Kurikulum, publikasi atau kesetaraan kesulitan/IRT. `approval_status=NOT_CURRICULUM_APPROVED` dan `self_adjustment_enabled=false` tetap dipertahankan. Perubahan konteks maupun angka tidak dinyatakan meningkatkan/menurunkan kesulitan. Tidak memperluas rentang generator lama.

Laporan sebelum pekerjaan ini adalah snapshot historis. Kini tidak ada lagi original berstatus unavailable dalam katalog runtime; 16 HOLD kelompok lain tetap tidak diubah. Inventaris global: 1.180 original, 1.078 generator, 86 original konseptual dan 16 HOLD.

## Reproduksi

```powershell
python -B -m unittest discover -s variant_gen/tests -p "test_drill_20_level45*.py" -v
python -B -m unittest discover -s variant_gen/tests -p "test_drill_20_23_level45*.py" -v
python -B -m unittest discover -s tests/service -v
python -B variant_gen/cli.py gen pg-20-4-1 s1
```

Builder offline: `variant_gen/tests/build_drill_20_level45_completion.py`. Config existing yang berbeda ditolak, bukan ditimpa. Revisi berikutnya terhadap konten yang sudah dipakai harus membuat versi baru. Restart proses service/workbench lokal yang sudah berjalan untuk memuat config tambahan.

[JSON lengkap, hash, domain dan sampel](evidence.json) · [Daftar 13 generator](entries.csv) · [Manifest sebelum perubahan](prior-assets-baseline.json) · [Hasil verifikasi](verification.json).
