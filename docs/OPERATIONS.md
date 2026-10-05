# Panduan penggunaan

Perintah dari root `Numora-ai-service`; setup Python/venv pada [README](../readme.md). Gunakan store dan salinan config sendiri untuk eksperimen.

## Workbench

```powershell
python -B variant_gen/webui.py
```

Default http://127.0.0.1:8765; bind `127.0.0.1`. Argumen: `--port`, `--bank`, `--configs`, `--store`. Path default mengacu folder modul; path custom relatif mengacu current directory.

```powershell
# Store terpisah; editor masih menulis config default.
python -B variant_gen/webui.py --port 8766 --store scratch/variants.jsonl
# Pisahkan config juga jika akan memakai Simpan versi baru.
New-Item -ItemType Directory -Path scratch -Force
Copy-Item variant_gen/configs scratch/configs -Recurse
python -B variant_gen/webui.py --port 8766 --configs scratch/configs --store scratch/variants.jsonl
```

Tab **Service AI** bekerja pada bank/config/store lokal. **DB Utama** membaca PostgreSQL; tidak ada sinkronisasi otomatis. Berpindah tab mempertahankan draft config.

1. Pilih aktivitas/paket. Drill difilter per indikator, level sumber dan format; Tryout per bab dan format. Level Drill 4–5 tersedia pada indikator 11–15; indikator 6–10,16–23 dan Pretest masih kosong.
2. Pilih soal/seed positif. **Lihat** membaca snapshot. Original seed 0 selalu di kiri; varian yang belum dibuat belum tampil.
3. **Generate** membuat varian seed baru atau membaca hasil existing.
4. **Regen** menambah versi. Isi **Alasan regen** bila config sama; config versi lebih tinggi tidak memerlukan alasan manual.
5. **Atur config → Validasi** memeriksa draft tanpa menulis. **Simpan versi baru** membuat versi berikutnya setelah struktur, reproduksi original dan probe lima seed lulus. Editor usang ditolak; muat ulang sebelum retry.

Draft belum disimpan menonaktifkan Generate/Regen/generasi paket. Perpindahan soal/filter meminta keputusan membuang draft. `HOLD_SOURCE` dan `DEFERRED_CONCEPTUAL` terlihat dengan alasan; generator/editor disabled. Drill tanpa config tetap dapat menampilkan original; template baru memerlukan desain konten. Indikator20–23 menampilkan nomor soal dokumen dan kategori sumber; kunci HOLD berlabel belum disahkan.

## CLI per soal

```powershell
python -B variant_gen/cli.py view pg-18-3-1 s0
python -B variant_gen/cli.py hash pg-18-3-1
python -B variant_gen/cli.py lint pg-18-3-1 --n 20
python -B variant_gen/cli.py gen pg-18-3-1 s5 --store scratch/variants.jsonl --json
python -B variant_gen/cli.py regen pg-18-3-1 s5 --store scratch/variants.jsonl --reason "Ulang angka"
python -B variant_gen/cli.py view pg-18-3-1 s5 v1 --store scratch/variants.jsonl --json
```

`s5`, `seed5`, `5` diterima. `gen` menerima `s1-20`, maksimal 1.000 seed per panggilan; command lain membutuhkan satu seed. UI/paket membatasi seed positif sampai 1.000.000.000. CLI `gen`/`view s0` menampilkan original; `regen s0` ditolak.

`gen` seed existing tidak memakai config terbaru atau menambah record. `regen` memakai config terbaru lalu append versi berikutnya. `view` tanpa `vN` membaca versi terbaru. `--json` mengubah output record; lint/hash tetap teks. Rentang seed menghasilkan beberapa objek JSON berturut-turut, bukan array; sebagian seed dapat berhasil sebelum lainnya gagal. Lihat CLI/subcommand `--help` untuk argumen.

## Paket Tryout

UI: **Tryout → Tryout 1**, isi seed, **Generate paket Tryout**. Preview 27 varian + 3 original ditunda; **Unduh preview JSON** mengambil manifest. Filter bab/format tidak mengurangi isi paket lengkap.

```powershell
python -B variant_gen/cli.py package-gen tryout-1 s5 --store scratch/variants.jsonl --output scratch/tryout-1-s5.json
python -B variant_gen/cli.py package-export scratch/tryout-1-s5.json --output scratch/tryout-1-s5-preview.json
```

Manifest mem-pin record/version saat paket pertama dibuat. Snapshot seed existing dipakai kembali; yang belum ada digenerasikan. Regen soal individual tidak mengubah paket existing. Gunakan **seed baru** untuk paket baru. Identitas paket/seed berbeda untuk output existing ditolak. Revisi original konseptual setelah manifest dibuat membuat manifest lama ditolak, bukan diganti diam-diam.

UI menyimpan `<folder-store>/packages/<package_id>-s<seed>.json`; CLI memakai `--output`. `package-export` tidak menimpa destination existing. Status **LOCAL_PREVIEW** belum merupakan paket canonical Numora. Ekspor individual dengan mapping pada [arsitektur](ARCHITECTURE.md#ekspor-ke-numora).

Kandidat baru divalidasi sebelum append. Jika append sebagian gagal, record yang ditulis tetap ada; ulang command dengan identitas sama untuk melanjutkan. Manifest ditulis melalui file sementara dan rename setelah lengkap. Tidak ada rollback transaksi atau pemulihan JSONL rusak otomatis.

## Database dan VPS

Generator tidak memerlukan `DATABASE_URL`. Untuk tab DB, isi `.env` root repo mengikuti [.env.example](../.env.example); pertahankan file existing. Environment proses mengalahkan `.env`; restart UI setelah perubahan.

```dotenv
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/postgres?sslmode=require
```

URL-encode karakter khusus kredensial. Backend membaca kredensial; Git mengabaikan `.env`. Hak akses mengikuti akun/RLS. Query read-only, timeout lima detik, TLS remote; [schema dan batas](ARCHITECTURE.md#browser-database).

Pada VPS AI, jalankan Python melalui venv repo, akses dengan tunnel:

```sh
ssh -L 8765:127.0.0.1:8765 USER@AI_VPS
```

Buka localhost 8765 di komputer operator. Workbench belum memiliki autentikasi operator/API produksi; pertahankan akses localhost melalui tunnel.

## Pengujian

```powershell
python -B -m unittest discover -s variant_gen/tests -v
```

Suite memakai fixture/temp stores, tidak membutuhkan DB Numora. Meliputi bank/catalog, evaluator, config, original reconstruction, regen/history, ekspor, pinning/crash retry, HTTP, query DB dengan mock.

Browser helpers membutuhkan Playwright CLI dan server port 8766:

```powershell
npx --yes --package @playwright/cli playwright-cli open http://127.0.0.1:8766
npx --yes --package @playwright/cli playwright-cli run-code --filename variant_gen/tests/check_tryout_browser.js
npx --yes --package @playwright/cli playwright-cli close
```

Start server dengan config/store sementara: helper Tryout melakukan generate/regen. `check_webui_browser.js` memakai respons DB fixture. Helper SQL opsional memerlukan binary PostgreSQL lokal:

```powershell
python -B variant_gen/tests/check_database_postgres.py
```

Helper membuat dan menghapus cluster sementara; tidak memakai `.env` atau `DATABASE_URL` pengguna.

Audit matematika indikator 11–15 dapat diulang tanpa menulis store:

```powershell
python -B variant_gen/tests/audit_drill_11_15.py --output output/drill-11-15/audit.json
```

Perintah ini juga menulis `examples.json` di folder output. Target default 20 variant unik dengan batas 200 seed; enam generator memiliki hasil sampling di bawah target. Suite memutar ulang seed berhasil dari audit bank dan memeriksa hash config. Audit 6–10 dan20–23 tersedia di `docs/audits/`; browser helper masing-masing adalah `check_drill_6_10_browser.js` dan `check_drill_20_23_browser.js`, dengan server/config/store sementara.

## Pemecahan masalah

| Gejala | Tindakan |
|---|---|
| `ModuleNotFoundError: dotenv/psycopg` | Aktifkan venv; install requirements. |
| Indikator baru belum muncul | Pastikan server menjalankan checkout terbaru, restart server, lalu refresh halaman. |
| Port dipakai | Hentikan server lama atau pilih `--port` lain. |
| `no config found` | Periksa ID, `--configs`, status soal tanpa generator. |
| Config edited after generation | Pulihkan versi lama; buat versi berikutnya. |
| `original_hash does not match` | Review original/revisi, sesuaikan template dan versi; jangan sekadar ganti hash. |
| Regen perlu alasan | Isi alasan atau gunakan config versi lebih tinggi. |
| `no acceptable variant within ... draws` | Tinjau rejection/domain/constraints; max_draws bukan bukti stok habis. |
| Pinned snapshot missing/changed | Gunakan store asli; jangan edit manifest; seed baru bila original ditunda direvisi. |
| DB belum terbaca | Periksa environment/.env, restart, jaringan/TLS, schema/izin SELECT. |
| Snapshot lama tanpa pembahasan | Regen ke config baru; pertahankan snapshot lama. |

Sistem belum mencatat kapasitas finite exact atau otomatis reuse saat stok habis. Kegagalan dilaporkan kepada operator.

Indikator 11–15 dimuat otomatis dari bank lokal oleh UI/CLI. Jika server sudah berjalan sebelum integrasi bank, restart `python -B variant_gen/webui.py`, lalu refresh halaman. [Audit generator](audits/2026-10-05-drill-11-15-generator-audit.md).
