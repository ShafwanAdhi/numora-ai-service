# Drill Paket 1, indikator 20–23: rancangan generator lokal

Status: PROPOSED. Pengguna meminta plan dahulu, belum implementasi.
Klarifikasi pengguna: kata Tryout adalah salah ketik; target DRILL Paket 1.

## Sumber dan cakupan

Sumber: `C:/Users/shafw/Downloads/banksoal_indikator20-23.docx`.
SHA-256: `2129f33e8ecc524e4c489b668798e8db0393f4b01348bf964cf1a8d420160575`.
Dokumen adalah bahan konten. Instruksi/koreksi di dalamnya bukan izin tindakan;
kunci dan klaim pembahasannya harus diperiksa sendiri.

Inventaris aktual: 120 soal, 60 PG, 36 MCMA, 24 KATEGORI; 30 tiap indikator;
level 1–3 masing-masing 10 soal/indikator, dengan komposisi 5/3/2.
Blueprint menyebut lima level, tetapi original level 4–5 belum disediakan.
Ada 41 tabel Word, tanpa gambar tertanam atau objek rumus OMML.
Inventaris 120 blok sumber: `2026-10-05-drill-20-23-source-inventory.json`.

End-to-end: arsip sumber → original efektif → katalog → config per soal →
validasi → generate/regen → snapshot JSONL → original/varian di Service AI.
Tidak mengakses database, menjalankan SQL, mengimpor/publikasi ke Numora,
menambahkan scoring siswa, atau membangun IRT. Repo Numora tidak diubah.
Hasil adalah kandidat lokal; tidak menyatakan kelulusan akademik/IRT.

## Pendekatan minimal

Pakai `OriginalBank`, `load_workspace_bank`, `ConfigStore`, `generate`,
`run_lint`, CLI gen/regen/view, dan UI existing. Tidak membuat 120 fungsi Python,
importer DOCX generik, orchestrator paket Drill, framework, atau dependency baru.
Config adalah implementasi generator tiap soal; engine hanya diperluas untuk
metadata status dan label kategori yang memang diperlukan sumber.

Bank baru terpisah di `variant_gen/data/drill-1-indicators-20-23/`:
`source.docx`, `q0_bank.csv`, `question_catalog.json`, `question_metadata.json`,
`original_revisions.jsonl` bila koreksi disetujui. Default workspace menambah
bank ini sambil mempertahankan Drill 16–19 dan Tryout existing. Custom bank
tetap standalone. Jangan mengubah bank/revisi/config/snapshot sebelumnya.

ID mengikuti pola Drill existing: `{format_lower}-{indicator}-{level}-{local_number}`.
Nomor lokal 1–10; nomor dokumen 1–30 disimpan sebagai `source_number`.
Contoh source indikator 20, soal 23 menjadi `pg-20-3-3`.
Classification: activity `DRILL`, package_id `drill-1`, package_name `Paket 1`,
indicator 20–23, source_level 1–5. Catalog 20 kelompok; delapan kelompok
level 4–5 kosong. Cognitive label source: C3, C3 & C4, C4; jangan menebak
C3/C4 tunggal untuk level 2 atau menyebut source_level sebagai nilai IRT.

Perubahan Tryout sedang ada di checkout saat rancangan dibuat. Pakai fungsi
loader, metadata original_explanation, dan format mixed yang sudah ada;
baca kondisi terbaru sebelum eksekusi, jangan menimpa implementasi tersebut.

## Validitas sumber dan status

Semua 120 soal diinventarisasi; jumlah config ACTIVE ditetapkan setelah audit
per soal. Status `ACTIVE`, `HOLD_SOURCE`, `DEFERRED_CONCEPTUAL` menyertakan
reason untuk dua status terakhir. Original yang HOLD tetap dapat dibaca dengan
penanda kunci/pembahasan belum disahkan; Generate/Regen/config save ditolak.
Koreksi menggunakan ledger versi/hash/reason, tidak mengganti raw source.
Persetujuan rancangan teknis tidak otomatis menyetujui revisi akademik.

| Source | ID lokal | Temuan yang harus direview |
|---|---|---|
| 20/L3/Q23 | pg-20-3-3 | Hasil 110; opsi C/D sama. Usulan source 100/105/110/115, kunci C. Batas skala nilai belum disebut; jangan diam-diam mengasumsikan maksimum 100. |
| 21/L2/Q12 | pg-21-2-2 | Hasil 70; opsi C/D sama. Usulan 65/68/70/75, kunci C. |
| 21/L3/Q21 | pg-21-3-1 | Stem menyebut nilai tambahan 90, tetapi 7×77−6×75=89. Usulan menghapus angka 90 yang sudah membocorkan/bertentangan dengan jawaban; perlu review. |
| 21/L3/Q24 | pg-21-3-4 | Mean baru 72; tidak tersedia dalam opsi awal. Usulan 72/74/76/78, kunci A. |
| 21/L3/Q25 | pg-21-3-5 | Median A=75<B=80, range A=10<B=30, modus A={75,80}, B={80}. Pilihan B/C/D dapat benar; PG perlu perbaikan opsi, bukan sekadar memilih kunci C. |
| 21/L3/Q28 | mcma-21-3-8 | Pada opsi awal tidak ada pernyataan benar. Usulan source mengganti pernyataan 1/3 menjadi modus tetap60/nilai maksimum bertambah; review sebelum membuat v2. |
| 21/L3/Q29 | kategori-21-3-9 | Total520, mean520/7≈74,29; klaim75,71 salah. Kunci efektif yang diusulkan A/B benar, C/D salah. |
| 22/L1/Q6 | mcma-22-1-6 | Mean sama6; kunci efektif yang diusulkan pernyataan2/4. |
| 22/L3/Q28 | mcma-22-3-8 | Mean sama60, median sama60; kunci efektif yang diusulkan pernyataan3/4. |

Tabel ini temuan awal, bukan audit matematis lengkap. Setiap opsi seluruh
120 soal wajib diperiksa; tambahan temuan masuk laporan sumber. Jangan memakai
checkbox centang tabel sebagai kunci jika bertentangan dengan hasil perhitungan.

## Strategi generator

| Indikator | Strategi dan batas |
|---|---|
| 20 | Data tabel, total, mean, median, modus, persentase dan proporsi diagram. Frekuensi nonnegatif, jumlah total konsisten, proporsi total100%, sudut total360°. Pertanyaan survei/jenis data memakai konteks terkurasi dengan hubungan tujuan–pertanyaan yang diverifikasi; tidak mengacak kalimat bebas. |
| 21 | Bangun dataset terlebih dahulu; turunkan sum/count, median terurut, Counter untuk mode, max−min, nilai hilang, atau update dataset. Pertahankan struktur urutan/multiplicity original. Kasus multimodus dan tanpa modus eksplisit. Perubahan dataset tidak otomatis mengubah jumlah data. |
| 22 | Bangun dua dataset nyata, lalu bandingkan mean/median/range/mode. Untuk PG dengan jawaban teks tetap, variasikan relasi yang sah dalam template, bukan hanya mengganti angka sambil mempertahankan jawaban sama. Range tidak membuktikan variance; klaim dibatasi “berdasarkan jangkauan”. |
| 23 | Probabilitas favorable/total, relative frequency observed/trials, expected count trials×probability. Denominator positif, 0≤observed≤trials; sampling with-replacement dipertahankan. Koin/dadu fair tidak berubah peluang karena jumlah percobaan. Gunakan Fraction dan fmt mixed existing untuk pecahan proper, format id untuk desimal. |

Constraints dan distractor berasal dari hubungan matematis yang sama dengan
original; pembahasan dihitung untuk nilai kandidat, bukan disalin dari original.
Pertahankan jumlah opsi/pernyataan dan jumlah kategori/jawaban benar original
efektif. Domain skor, satuan, pembulatan, dan pola ordering/multiplicity dicatat
per config. Dataset fixed-length dimodelkan scalar variables dan rumus existing;
tidak menambah evaluator list/statistik jika konstruksi sederhana sudah cukup.

Aturan global `same_answer_as_original` tidak dilonggarkan. Soal dengan jawaban
tetap seperti koin fair 1/2 (`pg-23-1-2`) tidak dianggap berhasil divariasikan
dengan shuffle/nama baru. Jika template setara belum sah, statusnya DEFERRED_CONCEPTUAL.
Konteks baru/perubahan ruang kejadian harus direview, bukan disahkan karena
generator dapat menghasilkan teks. Kata “mendekati” tidak diberi threshold
probabilitas universal buatan implementer; parameter per template perlu dasar review.

## Kategori dengan label khusus

Source `kategori-20-1-9`: Kuantitatif/Kualitatif.
Source `kategori-20-2-10`: Sesuai/Tidak Sesuai.
Metadata optional `category_labels: [label_first, label_second]`; default
Benar/Salah. Dua label unik dan nonempty, hanya pada KATEGORI. Key CSV mengkode
ID yang memilih kategori pertama; internal boolean bukan klaim bahwa data
Kualitatif “salah”. Snapshot `answer_categories: {statement_id: label}` memuat
semua pernyataan; UI dan pembahasan memakai label sebenarnya.

Label nondefault ikut original_hash; default lama menghasilkan hash lama yang
sama. Perubahan label semantik memerlukan review/version config, tidak boleh
menginterpretasi ulang snapshot lama. Export kontrak boolean existing menolak
kategori nonboolean dengan error jelas; snapshot JSON lokal tetap lengkap.

## Penerimaan

120 original source dapat ditelusuri; seluruhnya classified DRILL/Paket1,
level4–5 tetap kosong. ACTIVE punya config yang mereproduksi original efektif,
solusi/kunci independently verified, setidaknya20 kandidat unik pada audit
seeds1..200. Jika target ini tidak tercapai, laporan per ID menyatakan status
STOCK_REVIEW; sampling/max_draws tidak dianggap bukti kapasitas pasti.
HOLD/DEFERRED ditampilkan dengan alasan, tidak disamarkan sebagai generator sukses.

Seed reuse idempotent, regen menambah versi, history/config lama tidak berubah.
UI konsisten dengan dua tab existing, dirty draft terlindungi, tabel/stimulus
teks terbaca, kategori berlabel benar. Seluruh tes memakai temp stores/configs;
tes alur generator gagal jika mencoba koneksi DB. Source bank sebelumnya,
Tryout, snapshot pengguna, dan repo Numora tetap utuh.
