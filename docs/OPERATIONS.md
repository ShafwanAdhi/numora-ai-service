# Panduan penggunaan

Generate mengembalikan JSON tanpa menyimpan varian, cache, riwayat, atau manifest paket. Original dan versi config tetap disimpan. Database Numora belum menerima hasil generate.

## Workbench

```powershell
python -B variant_gen/webui.py
```

Buka http://127.0.0.1:8765. Argumen: `--port`, `--bank`, `--configs`. `--store` lama diterima tetapi diabaikan; tidak membaca/menulis file. Gunakan salinan config jika ingin bereksperimen dengan editor.

1. Pilih aktivitas > paket > indikator/bab > level > soal.
2. Atur seed positif. **Lihat** memuat original/config dan mengosongkan hasil sebelumnya.
3. **Generate** menghitung hasil memakai config terbaru; respons langsung tampil di kanan. Dapat diulang tanpa batas stok. Seed/config sama menghasilkan konten sama; seed berbeda masih dapat menghasilkan konten yang pernah muncul.
4. **Atur config > Validasi** memeriksa draft. **Simpan versi baru** menulis config berikutnya; hasil varian tidak ikut disimpan. Draft belum disimpan menonaktifkan generate/paket. Editor usang ditolak.

Tombol Regen, versi/riwayat varian, dan unduh preview paket sudah dihapus. Hasil hanya berada dalam respons dan tampilan halaman; refresh/pergantian soal mengosongkan hasil. Soal HOLD_SOURCE/DEFERRED_CONCEPTUAL tetap menampilkan original dan alasan, dengan generate/editor dinonaktifkan.

Jumlah panggilan tidak dibatasi stok. Validasi akademik dan batas `max_draws` per panggilan tetap berlaku; config yang tidak menghasilkan kandidat sah tetap melaporkan kegagalan. Sistem tidak menjamin varian unik tanpa batas.

Tab **DB Utama** tetap membaca PostgreSQL secara terpisah; generate tidak mengakses database. Endpoint service-to-service dan penyimpanan hasil oleh service utama belum diimplementasikan.

## CLI per soal

```powershell
python -B variant_gen/cli.py view pg-18-3-1 s0
python -B variant_gen/cli.py hash pg-18-3-1
python -B variant_gen/cli.py lint pg-18-3-1 --n 20
python -B variant_gen/cli.py gen pg-18-3-1 s5 --json
python -B variant_gen/cli.py view pg-18-3-1 s5 --json
```

`gen`/`view` menghitung preview baru; seed 0 menampilkan original. `regen`, pemilihan `vN` varian, `package-export`, dan `--output` paket dihapus. `s5`, `seed5`, `5` diterima. `gen` menerima rentang `s1-20`, maksimal 1.000 seed per panggilan. Rentang menghasilkan objek JSON berturut-turut, bukan array; hasil hanya dicetak ke stdout. UI/paket menerima seed 1 sampai 1.000.000.000.

## Paket Tryout

UI: **Tryout > Tryout 1 > Generate paket Tryout**. Setiap panggilan menghasilkan 27 varian + 3 original ditunda dalam satu respons; tidak menulis file. Filter bab/format tidak mengurangi isi paket lengkap.

```powershell
python -B variant_gen/cli.py package-gen tryout-1 s5
```

Status **LOCAL_PREVIEW** tetap menandai paket belum canonical Numora. Ekspor individual dengan mapping menghasilkan envelope di stdout, tanpa insert/upload: lihat [arsitektur](ARCHITECTURE.md#ekspor-ke-numora).

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

Suite memeriksa matematika, bank/config, respons tanpa penyimpanan, generate berulang, paket lengkap, config versioning, ekspor, serta validasi HTTP. Tidak memerlukan DB Numora.

```powershell
npx --yes --package @playwright/cli playwright-cli open http://127.0.0.1:8766
npx --yes --package @playwright/cli playwright-cli run-code --filename variant_gen/tests/check_tryout_browser.js
npx --yes --package @playwright/cli playwright-cli close
```

Server browser test: `python -B variant_gen/webui.py --port 8766`; gunakan config sementara jika helper menguji penyimpanan config. Audit matematika boleh menulis laporan ringkas berisi hash/seed/status, tetapi tidak menyimpan teks varian/contoh hasil.

## Pemecahan masalah

| Gejala | Tindakan |
|---|---|
| Indikator/perubahan belum muncul | Restart server checkout terbaru dan refresh halaman. |
| Port dipakai | Hentikan server lama atau pilih `--port` lain. |
| `no config found` | Periksa ID, path config, dan status penundaan soal. |
| `original_hash does not match` | Periksa sumber/revisi dan config; line ending CRLF/LF sudah dinormalisasi untuk hash. |
| `no acceptable variant within ... draws` | Periksa domain, constraints, dan rejection; bukan tanda stok tersimpan habis. |
| Soal sama muncul kembali | Wajar: tidak ada riwayat deduplikasi; ubah seed/config untuk mencoba variasi. |
| DB belum terbaca | Periksa environment, jaringan/TLS, schema/izin SELECT. |
