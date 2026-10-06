# Numora AI Service

Service terpisah untuk membuat dan meninjau varian soal Numora. Implementasi saat ini: generator deterministik berbasis config JSON, stok konseptual manual, CLI, workbench lokal, dan browser database read-only. Generasi tidak memanggil model AI/LLM. Komputasi IRT belum diimplementasikan di repo ini.

Numora menjalankan aplikasi utama pada VPS utama; repo ini ditujukan untuk VPS AI terpisah. Workbench merupakan alat operator di localhost, belum API produksi untuk aplikasi Numora.

## Mulai

Semua perintah dokumentasi dijalankan dari root **Numora-ai-service**, kecuali disebut lain. Gunakan Python 3.11 atau lebih baru.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -B variant_gen/webui.py
```

Buka http://127.0.0.1:8765. Pada soal berstok, pilih Varian1–N; seed/Generate/editor disembunyikan. Restart workbench setelah asset stok berubah. Tab **Service AI** berjalan tanpa database. UI membutuhkan `python-dotenv` dan `psycopg`; engine/CLI generator memakai stdlib. Di Linux, aktivasi venv memakai `source .venv/bin/activate`.

## Status bank lokal

Inventaris kode/data per **6 Oktober 2026**:

| Aktivitas | Paket | Original | Soal dengan config | Struktur |
|---|---|---:|---:|---|
| Drill & Practice | `drill-1` / Paket 1 | 790 | 646 | Paket > indikator1–23 > level sumber > soal |
| Tryout | `tryout-1` / Tryout 1 | 30 | 27 | Paket > bab 1–4 > soal |
| Pretest | Belum tersedia | 0 | 0 | Belum memiliki bank lokal |
| Total | | 820 | 673 | |

Paket Drill menargetkan 5 level × 10 soal per indikator. Indikator 11–15 memiliki level 1–5; indikator 6–10 dan 16–23 memiliki level 1–3. Total790 original; indikator1–2 dibatasi level1–3 sesuai scope, indikator3–5 level1–3 sudah tersedia. Seluruh 60 soal indikator 18–19 memiliki config. Config tersedia bukan approval kurikulum atau bukti kesetaraan IRT.

**Stok konseptual lengkap: 67 original Drill, 206 varian VERIFIED, masing-masing2–4.** Generator646 + stok67 + review sumber77 =790 Drill. Metadata DEFERRED_CONCEPTUAL pada sumber tetap historis; stok dapat dibaca walaupun generator belum ada. [Audit variasi dan kesulitan per ID](docs/audits/2026-10-06-conceptual-stock-audit.md).

Indikator **1–2**:60 original level1–3, **34 generator aktif**,17 HOLD_SOURCE,9 DEFERRED_CONCEPTUAL. Indikator3–5 tersedia, lihat audit berikut. [Audit](docs/audits/2026-10-05-drill-1-2-generator-audit.md).

Indikator **3–5**:90 original level1–3,**64 aktif**,25 HOLD_SOURCE,1 DEFERRED_CONCEPTUAL. [Audit](docs/audits/2026-10-06-drill-3-5-generator-audit.md).

Indikator **6–10**: 150 original, **129 generator aktif**, 12 HOLD_SOURCE dan 9 DEFERRED_CONCEPTUAL. Level 1–3 tersedia; level 4–5 belum memiliki sumber. [Laporan audit](docs/audits/2026-10-05-drill-6-10-generator-audit.md).

Indikator **11–15**: 250 original, **223 generator aktif**, 5 HOLD_SOURCE dan 22 DEFERRED_CONCEPTUAL. Bank dan config sudah terintegrasi ke checkout ini; pilih Service AI > Drill > Paket 1 > indikator 11–15 > level 1–5. [Laporan audit dan contoh hasil](docs/audits/2026-10-05-drill-11-15-generator-audit.md).

Indikator **20–23**: 120 original, **86 generator aktif**, **11 HOLD_SOURCE** (konflik opsi/kunci/stem), **23 DEFERRED_CONCEPTUAL** (template setara/aturan penilaian perlu review). Semua 86 aktif diuji masing-masing 20 varian unik, dengan oracle matematika independen. Tidak ada koreksi akademik pada sumber yang diterapkan. [Audit per soal](docs/audits/2026-10-05-drill-20-23-generator-audit.md) memuat alasan setiap soal tertahan. Sepuluh Drill indikator16–19 dan tiga Tryout tetap tanpa generator.

Di tab **Service AI**, pilih Drill > Paket 1 > indikator20–23 > level > soal. Generate menampilkan respons tanpa penyimpanan lokal. Tidak ada Regen atau riwayat varian; generate dapat diulang tanpa batas stok. Seed sama menghasilkan soal sama, seed lain belum tentu unik. Nomor dokumen dan status review ditampilkan; kunci HOLD belum disahkan. Kategori Kuantitatif/Kualitatif dan Sesuai/Tidak Sesuai mempertahankan label sumber. Level4–5 tersedia pada indikator 11–15; kelompok lainnya masih kosong.

```powershell
python -B variant_gen/cli.py gen pg-21-1-1 s1-20
python -B variant_gen/cli.py view pg-21-1-1 s1
```

Bank tambahan disimpan di `variant_gen/data/drill-1-indicators-{1-2,3-5,6-10,11-15,20-23}/` dan dimuat bersama bank dasar; bank/config dipertahankan. Generator memakai engine deterministik dan mengembalikan hasil tanpa menyimpannya. Ekspor kontrak kategori boolean menolak label kategori khusus; tidak mengakses atau menulis database Numora.

Original disimpan sebagai CSV dengan ledger revisi. Hasil generator numerik hanya berada dalam respons/tampilan; stok konseptual adalah asset JSON offline yang dibaca ulang tanpa habis. Jumlah ini **bukan inventaris database Numora**. Tab **DB Utama** membaca database bila `DATABASE_URL` dikonfigurasi; generator tidak mengimpor/memublikasikan hasil ke database tersebut.

## Dokumentasi

- [Panduan penggunaan](docs/OPERATIONS.md): UI, CLI, seed, generate, paket, tes, troubleshooting.
- [Referensi generator](docs/GENERATOR.md): bank, config, variabel, validator, versi, penambahan soal.
- [Arsitektur dan integrasi](docs/ARCHITECTURE.md): modul, alur data, ekspor Numora, akses DB, batas implementasi.
- [Indeks dan arsip](docs/README.md): desain, audit, progres, sumber akademik.

## Verifikasi

```powershell
python -B -m unittest discover -s variant_gen/tests -v
```

Verifikasi gabungan dicatat pada [laporan kondisi repo](docs/audits/2026-10-06-repository-status.md). Tes memakai fixture sementara dan memeriksa generate tanpa penyimpanan. Editor config tetap memerlukan satu writer untuk folder config yang sama.
