# Numora AI Service

Service terpisah untuk membuat dan meninjau varian soal Numora. Implementasi saat ini: generator deterministik berbasis config JSON, CLI, workbench lokal, dan browser database read-only. Generasi tidak memanggil model AI/LLM. Komputasi IRT belum diimplementasikan di repo ini.

Numora menjalankan aplikasi utama pada VPS utama; repo ini ditujukan untuk VPS AI terpisah. Workbench merupakan alat operator di localhost, belum API produksi untuk aplikasi Numora.

## Mulai

Semua perintah dokumentasi dijalankan dari root **Numora-ai-service**, kecuali disebut lain. Gunakan Python 3.11 atau lebih baru.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -B variant_gen/webui.py
```

Buka http://127.0.0.1:8765. Tab **Service AI** berjalan tanpa database. UI membutuhkan `python-dotenv` dan `psycopg`; engine/CLI generator memakai stdlib. Di Linux, aktivasi venv memakai `source .venv/bin/activate`.

## Status bank lokal

Inventaris kode/data per **5 Oktober 2026**:

| Aktivitas | Paket | Original | Soal dengan config | Struktur |
|---|---|---:|---:|---|
| Drill & Practice | `drill-1` / Paket 1 | 120 | 110 | Paket > indikator 16–19 > level sumber > soal |
| Tryout | `tryout-1` / Tryout 1 | 30 | 27 | Paket > bab 1–4 > soal |
| Pretest | Belum tersedia | 0 | 0 | Belum memiliki bank lokal |
| Total | | 150 | 137 | |

Paket Drill menargetkan 5 level × 10 soal per indikator. Data baru level 1–3: 120 dari target 200 original; 80 soal level 4–5 belum tersedia. Seluruh 60 soal indikator 18–19 memiliki config. Sepuluh Drill dan tiga Tryout konseptual belum memiliki generator. Config tersedia bukan approval kurikulum atau bukti kesetaraan IRT.

Original disimpan sebagai CSV dengan ledger revisi; varian sebagai JSONL. Jumlah ini **bukan inventaris database Numora**. Tab **DB Utama** membaca database bila `DATABASE_URL` dikonfigurasi; generator tidak mengimpor/memublikasikan hasil ke database tersebut.

## Dokumentasi

- [Panduan penggunaan](docs/OPERATIONS.md): UI, CLI, seed, regen, paket, tes, troubleshooting.
- [Referensi generator](docs/GENERATOR.md): bank, config, variabel, validator, versi, penambahan soal.
- [Arsitektur dan integrasi](docs/ARCHITECTURE.md): modul, alur data, ekspor Numora, akses DB, batas implementasi.
- [Indeks dan arsip](docs/README.md): desain, audit, progres, sumber akademik.

## Verifikasi

```powershell
python -B -m unittest discover -s variant_gen/tests -v
```

Tes memakai fixture/store sementara. Jalankan satu writer untuk config/store yang sama; JSONL belum mendukung transaksi atau koordinasi writer lintas proses.
