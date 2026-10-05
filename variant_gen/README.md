# Generator varian Numora

Panduan aktif dipusatkan di root repo dan docs:

- [Setup dan status bank](../readme.md)
- [UI/CLI, seed, regen dan paket](../docs/OPERATIONS.md)
- [Config, bank, validator dan penambahan soal](../docs/GENERATOR.md)
- [Arsitektur, ekspor dan database](../docs/ARCHITECTURE.md)
- [Indeks arsip desain/audit](../docs/README.md)

Dari folder ini, jalankan `python -B webui.py` untuk UI atau `python -B cli.py --help` untuk CLI. Perintah panduan utama memakai path `variant_gen/...` dari root repo.

[Review soal skip](soalskip.md) mencatat 95 soal tanpa config beserta alasannya. Workspace default berisi 670 original dan 575 soal dengan config. Generator memakai config JSON; komputasi IRT belum diimplementasikan.

Drill Paket 1 indikator 6–10: 150 original, 129 generator aktif, 12 HOLD, 9 ditunda. [Audit dan batas stok](../docs/audits/2026-10-05-drill-6-10-generator-audit.md). Level 4–5 kosong sesuai sumber. Default UI/CLI memuat bank ini; hasil berupa snapshot lokal.

```powershell
python -B variant_gen/cli.py gen pg-6-1-1 s1 --store output/drill-6-10.jsonl
python -B variant_gen/cli.py view pg-6-1-1 s1 --store output/drill-6-10.jsonl
python -B variant_gen/cli.py regen pg-6-1-1 s1 --reason "review angka" --store output/drill-6-10.jsonl
```

Perintah di atas dijalankan dari root repo; `--store` memisahkan hasil percobaan dari snapshot pengguna.

Drill Paket 1 indikator 11–15: 250 original, 223 generator aktif, 5 HOLD_SOURCE dan 22 DEFERRED_CONCEPTUAL. Level 1–5 tersedia di UI. [Audit](../docs/audits/2026-10-05-drill-11-15-generator-audit.md) dan [15 contoh hasil](data/drill-1-indicators-11-15/examples.json) tersimpan; [manifest audit](data/drill-1-indicators-11-15/audit.json) memuat hash config dan seed.

Drill Paket1 indikator20–23: [audit 120 sumber dan 86 generator aktif](../docs/audits/2026-10-05-drill-20-23-generator-audit.md). Sebelas sumber HOLD dan 23 template konseptual belum dapat digenerate; alasan terlihat di UI. Bank baru terpisah, default workspace memuatnya bersama bank sebelumnya. Semua hasil tetap snapshot lokal.
