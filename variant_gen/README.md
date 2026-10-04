# Generator varian Numora

Panduan aktif dipusatkan di root repo dan docs:

- [Setup dan status bank](../readme.md)
- [UI/CLI, seed, regen dan paket](../docs/OPERATIONS.md)
- [Config, bank, validator dan penambahan soal](../docs/GENERATOR.md)
- [Arsitektur, ekspor dan database](../docs/ARCHITECTURE.md)
- [Indeks arsip desain/audit](../docs/README.md)

Dari folder ini, jalankan `python -B webui.py` untuk UI atau `python -B cli.py --help` untuk CLI. Perintah panduan utama memakai path `variant_gen/...` dari root repo.

[Review soal skip](soalskip.md) tetap mencatat alasan sepuluh Drill tanpa config. Generator memakai config JSON; komputasi IRT belum diimplementasikan.
