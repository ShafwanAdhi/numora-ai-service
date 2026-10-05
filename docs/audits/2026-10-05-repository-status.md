# Kondisi repo Numora AI Service — 5 Oktober 2026

Laporan ini menjadi acuan inventaris checkout `main`. Dokumen desain dan
rencana bertanggal mempertahankan keputusan awal; checklist dan jumlah tes
di dalamnya adalah catatan sesi, bukan status keseluruhan repo sekarang.

## Inventaris lokal

| Bank | Original | Soal dengan config | HOLD_SOURCE | DEFERRED_CONCEPTUAL | Tanpa config lainnya |
|---|---:|---:|---:|---:|---:|
| Drill 6–10 | 150 | 129 | 12 | 9 | 0 |
| Drill 11–15 | 250 | 223 | 5 | 22 | 0 |
| Drill 16–19 | 120 | 110 | 0 | 0 | 10 |
| Drill 20–23 | 120 | 86 | 11 | 23 | 0 |
| Tryout 1 | 30 | 27 | 0 | 3 | 0 |
| Total | **670** | **575** | **28** | **57** | **10** |

Sepuluh soal bank dasar 16–19 belum memiliki status metadata eksplisit;
loader memperlakukannya sebagai ACTIVE, tetapi tidak ada config. Jangan
menyamakan default status tersebut dengan generator yang siap dipakai.
[Daftar seluruh 95 soal tanpa generator](../../variant_gen/soalskip.md).

Drill berisi 640 original dan 548 soal dengan config. Indikator 11–15
memiliki level 1–5; indikator 6–10 dan16–23 memiliki level 1–3. Sebanyak
260 soal level 4–5 pada kelompok lain belum tersedia. Tryout memiliki
empat bab; Pretest belum memiliki bank. Workspace berisi 94 kelompok
katalog, termasuk kelompok kosong.

## Implementasi yang tersedia

- UI/CLI memuat kelima bank secara otomatis pada path bank default.
  `--bank` custom membaca bank tersebut secara standalone.
- Seluruh 223 generator aktif 11–15 terintegrasi ke interface bersama
  129 generator 6–10, 110 generator 16–19 dan86 generator 20–23.
- Generate, regenerate dengan alasan, history, config berversi, stale hash,
  original seed 0, lint, dan manifest Tryout yang mem-pin snapshot tersedia.
- HOLD_SOURCE dan DEFERRED_CONCEPTUAL menolak generate/regen/lint/save,
  termasuk reuse snapshot melalui CLI; original dan alasan tetap terbaca.
- Label kategori khusus disimpan pada snapshot. Ekspor kanonik menerima
  kategori boolean Benar/Salah dan satu label kognitif C1–C6. Label sumber
  gabungan tetap lokal sampai klasifikasinya disahkan.
- Tab DB Utama membaca PostgreSQL; generator bekerja pada bank/config/store
  lokal dan tidak mengimpor atau memublikasikan hasil ke database.

Original berada di CSV beserta ledger/catalog/metadata. Config di
`variant_gen/configs/<id>/v<N>.json`; snapshot operator di
`variant_gen/store/variants.jsonl`. Snapshot existing disertakan sebagai
riwayat lokal, bukan inventaris soal pada database produksi.

## Audit dan contoh hasil

- [Audit 6–10](2026-10-05-drill-6-10-generator-audit.md): 129 generator,
  oracle seluruh opsi dan stok sampling; konteks berat manusia pada tiga
  generator masih memerlukan kurasi.
- [Audit 11–15](2026-10-05-drill-11-15-generator-audit.md): 217 PASS,
  6 SHORT, 0 FAIL, 27 SKIP; 4.436 variant unik tervalidasi saat sampling.
  [Manifest per soal](../../variant_gen/data/drill-1-indicators-11-15/audit.json)
  menyimpan hash config dan seed; [15 contoh hasil](../../variant_gen/data/drill-1-indicators-11-15/examples.json)
  mencakup tiga format pada lima indikator.
- [Audit 20–23](2026-10-05-drill-20-23-generator-audit.md): 86 generator
  mencapai target sampling 20 variant unik; semua opsi diuji independen.

Stok sampling bukan kapasitas domain exact. Enam SHORT pada 11–15 tetap
memiliki generator valid; aturan jawaban unik dipertahankan. Pembahasan dan
variasi belum merupakan approval kurikulum atau kalibrasi kesulitan IRT.

## Verifikasi dan batas implementasi

Perintah dari root repo:

```powershell
python -B -m unittest discover -s variant_gen/tests -v
python -B variant_gen/tests/audit_drill_11_15.py --output output/drill-11-15/audit.json
git diff --check
```

Verifikasi checkout `main` sebelum publikasi meluluskan **97 tes** dalam
86,950 detik, exit code 0. Pengujian menggunakan fixture/store sementara dan
mock database. Pemeriksaan
integrasi memastikan 377 file bank/config/store existing dipertahankan.
Browser setelah restart menampilkan indikator 6–23 dan level 1–5 pada11–15,
dengan nol error/warning konsol. Server lokal berada di localhost:8765;
refresh halaman setelah restart untuk membaca katalog terbaru.

IRT compute worker, API produksi service-to-service, generation LLM,
self-adjusting soal, penulisan/publikasi database dan kapasitas exact belum
diimplementasikan. Satu writer diperlukan untuk store/config yang sama.
Bytecode Python dan scratch diabaikan Git; config, source, bank, snapshot,
audit, contoh hasil dan tes merupakan artefak repo.
