# Generator mcma-15-2-8 ? 21 Oktober 2026

Dari 23 soal indikator 11?15 tanpa generator, 22 konseptual ditunda sesuai instruksi. Satu soal nonkonseptual kini aktif. Total: 228 generator / 250 original; 22 DEFERRED_CONCEPTUAL, 0 HOLD_SOURCE.

## Revisi minimum original

Original lokal v2 mencantumkan sudut A=75?, B=65?, AB=6 cm, BC=9 cm. Panjang BC tersebut bertentangan dengan sudut (seharusnya sekitar 9,0163 cm). Original v3 menghapus informasi BC=9 cm; opsi B menjadi ?Panjang QR adalah 1,5 kali panjang BC.? Kunci B,D dipertahankan. Tidak perlu trigonometri dalam soal siswa.

CSV sumber, DOCX dan rekaman v1?v2 dipertahankan. Ledger menambahkan v2?v3 beserta metadata lama. Status revisi NOT_CURRICULUM_APPROVED; self-adjustment nonaktif.

## Generator dan pemeriksaan

Config v1 memakai k=0..30, PQ=9+3k dan faktor kesebangunan (3+k)/2. Rasio luas dihitung sebagai kuadrat faktor. Seluruh 31 input diperiksa melalui teks hasil render, kunci, opsi, pembahasan dan filter; k=0 mereproduksi original, k=1..30 menghasilkan 30 varian unik valid. Pemeriksaan korupsi menolak kunci, rasio dan pembahasan salah. Seed deterministik; generate melalui HTTP tidak mengakses database atau menulis hasil.

Perintah ulang:

```powershell
python -B variant_gen/tests/build_mcma_15_2_8.py
python -B -m unittest discover -s variant_gen/tests -p test_mcma_15_2_8.py
python -B -m unittest discover -s variant_gen/tests -p test_drill_11_15_source_revision.py
```

Uji workbench `test_webui.py`: 17 tes lulus. Suite `test_drill_11_15.py`: 15 lulus, satu error karena berkas bank indikator 1?5 `drill-1-indicators-1-5-levels-4-5-batch2/q0_bank.csv` tidak tersedia; di luar perubahan ini. Tidak ada perubahan database atau penyimpanan hasil varian runtime. Stok 22 soal konseptual tidak diubah.
