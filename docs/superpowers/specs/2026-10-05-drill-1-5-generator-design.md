# Desain generator Drill Paket 1 indikator 1–5

Scope terbaru pengguna menggantikan usulan awal: hanya level 1–3; tahap sekarang indikator 1–2. Indikator 3–5 menjadi tahap berikutnya, bukan bank runtime sekarang. Level 4–5 tidak diimpor, tidak dibuat grup katalog baru. DOCX mentah tetap utuh sebagai provenance.

## Sumber dan baseline

Sumber `C:/Users/shafw/Downloads/banksoal_indikator1-5.docx`, SHA256 `f12c25edf8b1e6a4a10daa19cbbe7459624450f619921186d0c75818e6b499c6`. Inventaris terbatas 150 soal: PG75/MCMA45/KATEGORI30. Tahap1 mengambil60: PG30/MCMA18/KATEGORI12;6 grup indikator×level. Indikator3–5 menyisakan90 soal untuk tahap berikutnya.

Checkout awal0553c29 telah memuat670 original/575 config/94 grup;97 tes baseline lulus. Integrasi11–15 sudah tersedia. Jangan mengulang implementasi bank lama.

## Alur dan batas

DOCX → CSV/catalog/metadata → config JSON per soal ACTIVE → engine existing → snapshot JSONL → CLI/workbench. Config adalah fungsi generator per soal; tidak diperlukan fungsi Python runtime tambahan. Loader mendaftarkan bank secara eksplisit. Custom `--bank` tetap standalone.

Pertahankan raw source, declared key, explanation, source hash dan lokasi dokumen. Normalisasi hanya tipografi: grouping pecahan/akar/pangkat, angka campuran, suhu dan currency. Instruksi rekonstruksi dalam DOCX bukan izin mengubah akademik.

ACTIVE harus mereproduksi original tepat, seluruh opsi konsisten, pembahasan valid dan hasil substantif berbeda. HOLD_SOURCE menyimpan konflik spesifik, tanpa config. DEFERRED_CONCEPTUAL menyimpan sumber valid tetapi template substantif belum tersedia. Semua skipped dicatat per ID di `variant_gen/soalskip.md`.

Gunakan engine/stdlb current, conditional predicate opsi, Fraction/format mixed. Tidak menambah dependency, evaluator, importer runtime, LLM, UI baru, CUD atau integrasi DB. Numora, .env dan user store tidak disentuh. Bank/config/history lama dipertahankan. Guard hash/status/correct-count/same_answer_as_original tetap strict.

## Verifikasi

Oracle test independen menghitung dari teks rendered, tanpa config/evaluator produksi: Fraction, dekomposisi akar exact, AST terbatas, perbandingan Decimal50 digit fail-closed pada selisih terlalu dekat. Periksa seluruh opsi, nilai operasi dan pembahasan numerik yang relevan. Target20 hasil unik per generator, seed tambahan201–250. Domain bounded; stok bukan tak terbatas dan bukan kalibrasi IRT.

CLI/UI diuji dengan store sementara dan DB mock: generate, reuse, regen, history, HOLD/DEFERRED. Jalankan full suite, browser smoke, preflight SHA dan diff whitespace. Satu review akhir read-only; tanpa commit/push otomatis. Progres tiap task disampaikan selama pekerjaan panjang.

## Tahap3–5 diimplementasikan6 Oktober2026

90 runtimeoriginal level1–3,64 configaktif,25 HOLD/1 DEFERRED. Workspace820 originals/673 configs/109groups. Tidak membuatlevel4–5 indikator1–5. Lihat audit/progres2026-10-06. Scope tahapberikut dalam teks awal di atas merupakan catatan fase1–2.
