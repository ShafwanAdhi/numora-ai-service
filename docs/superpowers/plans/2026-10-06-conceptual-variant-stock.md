# Stok Varian Konseptual Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Menyediakan stok varian konseptual Drill Paket 1 yang ditulis manual secara offline, dengan target dan batas maksimal 4 varian tambahan per original dan pengecualian 2–3 varian yang beralasan.

**Architecture:** Konten varian disimpan sebagai aset JSON tetap, terpisah dari original dan config generator. Pembaca stok memvalidasi konten dan keterkaitannya dengan original, lalu UI/CLI menampilkan varian yang dipilih. Membaca stok tidak membuat varian baru dan tidak mencatat riwayat pemakaian.

**Tech Stack:** Python stdlib, JSON UTF-8, unittest existing, HTTP server dan HTML/JavaScript existing; tanpa dependency baru.

**Spec:** Instruksi pengguna pada 6 Oktober 2026: `same_answer_as_original` tidak berlaku untuk soal konseptual; varian dibuat manual offline; maksimal 4 per soal menggantikan target awal 5, hasil 2–3 diperbolehkan jika terbatas. Keputusan rinci dan inventaris sumber berada dalam dokumen ini. Rencana disetujui pengguna dan telah dilaksanakan dalam dua tahap; hasil aktual dan bukti pemeriksaan tercatat pada ledger serta audit, bukan dihitung dari kuota rencana.

## Global Constraints

- Cakupan: 67 soal konseptual dari 144 soal Drill yang sebelumnya belum memiliki generator. Tiga soal Tryout tidak termasuk.
- Indikator 1–5 hanya level sumber 1–3. Level 4–5 indikator 11–15 yang sudah tersedia tetap termasuk; jangan menyamakan level sumber dengan label kognitif C1–C6.
- Target dan batas maksimal 4 adalah jumlah varian tambahan; original tidak dihitung sebagai varian. Batas berlaku pada setiap original, bukan rata-rata seluruh bank.
- Jawaban sama dengan original diperbolehkan khusus stok konseptual. Semua pemeriksaan lain tetap berlaku.
- Kompetensi, format, label kognitif, jumlah opsi/pernyataan, jumlah jawaban benar/anggota kategori pertama, dan label kategori mengikuti original.
- Keberagaman ditinjau dari stimulus, representasi, relasi, klaim, atau kesalahan konsep yang dianalisis. Pergantian nama, urutan opsi, parafrasa, atau angka tanpa perubahan tugas yang berarti tidak cukup sendiri.
- Jangan mengubah original, ledger revisi, config generator existing, `.env`, Numora, DB, API produksi, atau IRT.
- Tidak ada generator konseptual, LLM runtime, parameter konten runtime, penyimpanan hasil generate, riwayat pemakaian, CUD stok melalui API, commit, push, atau dependency baru.
- Konten stok dikelola offline di Git; layanan hanya membaca. Satu varian dapat dibaca berulang kali, tanpa habis dan tanpa penanda sudah dipakai.
- Target jumlah tidak mengalahkan validitas akademik. Varian yang belum diperiksa tidak boleh ditampilkan sebagai stok siap pakai.
- Berikan progres per task/batch selama eksekusi, paling lambat sekitar setiap 60 detik kerja; catat jumlah ditulis, diverifikasi, ditahan, dan alasan penahanan.

## Review Focus

1. Jawaban tetap: stok konseptual menerima jawaban sama, tetapi generator numerik tetap menolaknya. Task 2 menguji kedua jalur.
2. KATEGORI khusus: `Kuantitatif/Kualitatif` dan `Sesuai/Tidak Sesuai` tidak berubah menjadi Benar/Salah. Task 2 dan Task 4 menguji pembacaan dan tampilan.
3. Original berubah: hash/versi stok yang usang harus ditolak, bukan diam-diam ditampilkan. Task 2 menguji ketidakcocokan keduanya.
4. Kapasitas terbatas: stok 2–3 tidak dipaksa menjadi 4 melalui pengulangan atau pemetaan seed. Task 2 menolak stok lebih dari 4 per original; Task 4 menguji pilihan di luar stok.
5. Kualitas akademik: kepastian bangun, asumsi peluang seimbang, kuantifier universal, harga satuan, dan interpretasi statistik wajib diperiksa dari isi setiap varian. Task 3 menghasilkan catatan penilaian per varian; validator struktur bukan bukti kesetaraan atau kalibrasi IRT.

## Temuan repo saat perencanaan

- HEAD yang diperiksa: `473c563` (`delete variant stored`), setelah `9106fa4` (`adding more indicator`). Working tree bersih sebelum dokumen ini dibuat.
- `variant_gen/store.py` sekarang hanya mendefinisikan `StoreError`; tidak ada penyimpanan varian.
- `cli.preview(...)` dan `/api/generate` menghasilkan respons saja. `/api/question` mengembalikan `variant: null` tanpa generate; tidak ada API stok manual.
- UI masih menganggap ketersediaan varian ditentukan oleh config. Stok perlu dibedakan dari config tanpa menciptakan config dummy.
- `filters.validate_candidate` saat ini tetap menolak `same_answer_as_original`. Pengecualian pengguna belum diterapkan dalam kode.
- Bank efektif: 820 original, termasuk 790 Drill; 673 config, termasuk 646 Drill. Seluruh 67 ID dalam inventaris belum memiliki config.
- Sebanyak 59 ID memiliki metadata `DEFERRED_CONCEPTUAL`; 8 ID legacy indikator 16–17 tidak memiliki metadata status. Identifikasi delapan ID tersebut berasal dari review historis di `soalskip.md`, bukan inferensi dari ketiadaan config saja.
- Beberapa panduan masih menyebut snapshot/regen. Jadikan kode dan `tests/test_stateless.py` acuan integrasi; perbarui hanya bagian dokumentasi yang terkait stok.

## Identifikasi awal

Pembacaan awal mencakup stimulus, opsi/pernyataan, kunci, format, label kognitif, klasifikasi, serta metadata yang tersedia pada 67 original efektif. Ini belum review lengkap semua DOCX dan belum authoring varian.

| Indikator | Soal konseptual | Target varian tambahan |
|---|---:|---:|
| 1 | 5 | 20 |
| 2 | 4 | 16 |
| 5 | 1 | 4 |
| 6 | 4 | 16 |
| 7 | 3 | 12 |
| 9 | 1 | 4 |
| 10 | 1 | 4 |
| 11 | 6 | 24 |
| 12 | 2 | 8 |
| 14 | 10 | 40 |
| 15 | 4 | 16 |
| 16 | 6 | 24 |
| 17 | 2 | 8 |
| 20 | 9 | 36 |
| 21 | 1 | 4 |
| 22 | 6 | 24 |
| 23 | 2 | 8 |
| **Total** | **67** | **268** |

Format: **32 PG, 15 MCMA, 20 KATEGORI**. Indikator 3, 4, 8, 13, 18, 19 tidak memiliki soal dalam kelompok konseptual yang ditargetkan ini.

Target dan batas maksimal setiap ID berikut adalah **4**, belum jumlah final yang sudah terverifikasi. Kolom perhatian menunjukkan keterbatasan akademik awal, bukan bukti kapasitas yang sudah teruji. Enam ID bertanda **Uji batas** boleh diturunkan menjadi 2–3 setelah percobaan penulisan dan review; soal lain juga boleh mendapat pengecualian apabila ditemukan batas nyata.

### Inventaris 67 ID

| ID | Konsep original | Arah variasi manual | Perhatian/batas awal |
|---|---|---|---|
| `pg-1-1-4` | Distributif dalam biaya gabungan | Bentuk ekspresi dan model penggabungan biaya yang berbeda | Jawaban Distributif boleh tetap; jangan hanya mengganti nominal |
| `mcma-1-1-8` | Sifat operasi real | Contoh, identitas, dan kontra contoh pada operasi | Kuantifier setiap/selalu dan domain harus tepat |
| `kategori-1-1-10` | Distributif, komutatif, pengurangan | Dua cara perhitungan dan klaim sifat yang berbeda | Contoh numerik tidak membuktikan identitas universal |
| `kategori-1-2-10` | Rasional dan irasional | Klaim penjumlahan/perkalian serta syarat nol | Bedakan klaim universal dari contoh |
| `kategori-1-3-10` | Struktur himpunan bilangan | Relasi subset, representasi desimal, operasi | Pertahankan kedalaman analisis level sumber 3 |
| `pg-2-2-5` | Distributif dan diskon | Model total belanja dan alasan analisis yang berbeda | Diskon total versus per item dinyatakan eksplisit |
| `pg-2-3-1` | Tanda transaksi kas | Pengembalian, koreksi transaksi, penerimaan/pengeluaran | Arti setiap transaksi jelas; semua saldo dihitung ulang |
| `pg-2-3-4` | Urutan operasi | Ekspresi serta jejak kesalahan pengerjaan berbeda | Tepat satu analisis valid; bukan sekadar ganti nama siswa |
| `pg-2-3-5` | Distributif pada pembayaran | Analisis pemfaktoran, kuantitas, dan pengurangan | Nilai alasan, bukan klaim efisiensi tanpa kriteria |
| `pg-5-2-4` | Harga satuan versus harga total | Paket dan kesalahan perbandingan yang berbeda | Jangan mengesahkan perbandingan total saja; hindari opsi ganda saat harga satuan sama |
| `mcma-6-1-6` | Perbandingan berbalik nilai | Relasi besaran pada perjalanan, konsumsi, produksi | Nyatakan jarak/persediaan/produktivitas yang tetap |
| `mcma-6-2-6` | Klasifikasi hubungan perbandingan | Konteks relasi senilai dan berbalik nilai berbeda | Produktivitas pekerja sama dan pekerjaan dapat dibagi |
| `mcma-6-3-6` | Senilai, berbalik nilai, nonlinear | Hubungan geometri dan kegiatan dengan kondisi tetap | Senilai berarti rasio tetap, bukan sekadar sama-sama naik |
| `kategori-6-3-9` | Biaya tetap dan tarif proporsional | Bentuk penawaran, waktu pembanding, klaim proporsional | Bandingkan biaya tepat; pertahankan jumlah kategori pertama |
| `kategori-7-1-10` | Identitas dan kontradiksi | Bentuk persamaan ekuivalen dan klaim solusi | Penyederhanaan dan substitusi diperiksa |
| `kategori-7-2-10` | Analisis jenis solusi PLSV | Persamaan, faktor, dan klaim solusi berbeda | Hindari perubahan menjadi soal hitung sederhana saja |
| `pg-7-3-1` | Harga dasar dari dua model linear | Tagihan, biaya tambahan, dan model diskon | Perbandingan harga dasar mengikuti dua persamaan |
| `kategori-9-1-10` | Garis berhimpit dan sejajar | Sistem, representasi hubungan, dan klaim titik | Jangan menilai identitas garis hanya dari satu titik |
| `kategori-10-2-10` | Ekuivalensi bentuk aljabar | Ekspansi, faktorisasi, dan distribusi faktor berbeda | Semua klaim original benar; pertahankan profil kategori |
| `pg-11-1-1` | Syarat relasi menjadi fungsi | Skenario pemetaan dan karakteristik domain | Setiap anggota domain tepat satu pasangan |
| `mcma-11-1-8` | Sifat fungsi | Contoh relasi, pasangan berurutan, dan klaim | Bedakan domain, kodomain, dan range |
| `kategori-11-1-9` | Penyajian fungsi | Tabel, pasangan berurutan, grafik/deskripsi, rumus | Fungsi tidak harus kuadrat; tanpa gambar tak terdefinisi |
| `mcma-11-2-6` | Analisis relasi sebagai fungsi | Pemetaan dan klaim tentang percabangan | Semua anggota domain harus tercakup |
| `kategori-11-2-9` | Arah parabola dan ekstrem | Fungsi kuadrat serta karakteristik yang dinilai | a bukan nol; cek arah buka dan -D/(4a) |
| `mcma-11-5-6` | Evaluasi klaim sifat fungsi | Klaim siswa dan kontra contoh relasi | Pertahankan evaluasi C5, bukan hanya definisi hafalan |
| `pg-12-2-4` | Pola rasio geometri | Kombinasi rasio dan representasi beberapa barisan | Tanda suku pertama memengaruhi naik/turun |
| `kategori-12-3-10` | Rasio negatif dan nilai mutlak | Barisan serta klaim tanda, selisih, pertumbuhan | Bedakan perubahan nilai suku dari nilai mutlak |
| `pg-14-1-1` | Identifikasi hubungan sudut | Pasangan sudut dan penomoran yang jelas | Posisi pada kedua perpotongan harus eksplisit |
| `mcma-14-1-6` | Kebenaran hubungan pasangan sudut | Kumpulan pasangan serta klaim yang berbeda | Dua benar sesuai original; cek posisi tiap pasangan |
| `kategori-14-1-9` | Sudut dalam dan luar segitiga | Klaim relasi sudut dan kontra contoh | Sudut luar memakai dua sudut dalam tidak berdekatan |
| `pg-14-2-1` | Pemilihan pasangan sudut | Pilihan pasangan yang berbeda pada diagram terdeskripsi | Jangan membuat dua opsi ekuivalen benar |
| `pg-14-3-1` | Pasangan dengan hubungan berbeda | Tiga pasangan sejenis dan satu pengecualian | Hubungan benar-benar berbeda, bukan hanya label |
| `pg-14-4-1` | Evaluasi alasan hubungan sudut | Klaim siswa, pasangan sudut, dan alasan | Bedakan relasi umum dari kebetulan sudut 90 derajat |
| `pg-14-4-3` | Syarat kesejajaran dari sudut | Pengukuran sudut dan alasan kesimpulan | Posisi sudut dinyatakan; sehadap harus sama besar |
| `kategori-14-4-10` | Validitas segitiga dan sudut luar | Sudut-sudut serta klaim yang harus dievaluasi | Total 180 derajat, nondegenerat, dan kuantifier tepat |
| `pg-14-5-1` | Evaluasi beberapa klaim hubungan sudut | Klaim siswa serta pasangan sudut berbeda | Hanya satu opsi himpunan klaim benar |
| `kategori-14-5-10` | Sifat sudut luar segitiga | Klaim, contoh segitiga, dan kondisi sudut | Satu sudut luar per titik; segitiga nondegenerat |
| `pg-15-1-3` | Syarat kongruensi SAS | Data sisi/sudut dan korespondensi segitiga | Sudut harus diapit kedua sisi; pertahankan tugas identifikasi |
| `mcma-15-2-7` | Bangun yang pasti sebangun | Pasangan bangun dengan syarat bentuk eksplisit | Ukuran berbeda saja tidak menjamin kesebangunan persegi panjang |
| `pg-15-3-3` | Kesebangunan versus kongruensi | Korespondensi sudut dan sisi tak bersesuaian | Hindari sudut sama yang membuat sisi tampak tidak bersesuaian menjadi ekuivalen |
| `pg-15-5-3` | Evaluasi klaim kongruensi | Bukti kesamaan sudut dan perbedaan ukuran | AAA hanya menjamin sebangun; panjang positif valid |
| `pg-16-1-1` | Komponen jaring-jaring tabung | Komponen dalam representasi inventaris, rancangan, atau pemeriksaan | **Uji batas:** fakta dua lingkaran dan selimut tetap; hindari parafrasa saja |
| `pg-16-1-2` | Jaring-jaring limas segi empat | Representasi alas dan sisi tegak yang berbeda | **Uji batas:** bentuk dan kecocokan komponen harus cukup menentukan bangun |
| `mcma-16-1-6` | Jaring-jaring prisma segitiga | Klaim komponen, pasangan alas, dan jumlah bidang | Nyatakan prisma tegak jika sisi tegak disebut persegi panjang |
| `kategori-16-1-9` | Identitas dan unsur limas | Komponen jaring-jaring dan klaim unsur berbeda | Bangun dan jumlah unsur terdefinisi |
| `kategori-16-2-9` | Analisis unsur dari jaring-jaring | Deskripsi konstruksi dan penilaian unsur | Pertahankan analisis level sumber 2 |
| `pg-16-3-2` | Komponen tabung tanpa tutup | Analisis komponen tersedia, hilang, dan rancangan terbuka | **Uji batas:** jangan berubah menjadi hitungan luas atau sekadar nama wadah |
| `pg-17-3-2` | Transformasi tunggal dari komposisi | Jejak koordinat umum, pemetaan, dan alasan komposisi | **Uji batas:** ekuivalensi harus berlaku umum, bukan hanya satu titik khusus |
| `kategori-17-3-10` | Sifat transformasi dan skala luas | Klaim translasi, refleksi, rotasi, dilatasi berbeda | Perubahan ukuran memakai abs(k); luas memakai k^2 |
| `pg-20-1-1` | Pertanyaan sesuai tujuan survei | Tujuan kategori preferensi dan jenis pertanyaan berbeda | Tepat satu opsi mengukur variabel yang diminta |
| `mcma-20-1-6` | Pertanyaan untuk kebiasaan | Tujuan kebiasaan serta dimensi pertanyaan | Relevansi tidak bergantung asumsi tersembunyi |
| `kategori-20-1-9` | Data kuantitatif/kualitatif | Pertanyaan jumlah, pengukuran, dan kategori | Pertahankan label **Kuantitatif/Kualitatif** |
| `kategori-20-1-10` | Kegunaan penyajian data | Klaim tabel, batang, lingkaran dan tujuan penggunaan | Klaim tentang lingkaran perlu makna bagian dari keseluruhan |
| `pg-20-2-1` | Pertanyaan untuk alasan perilaku | Tujuan penelitian dan distractor variabel berbeda | Pertanyaan alasan tidak tertukar dengan jumlah/preferensi |
| `mcma-20-2-7` | Penyajian untuk membandingkan kategori | Data kategori serta syarat penyajian yang jelas | Diagram lingkaran sah jika bagian dari keseluruhan dinyatakan |
| `kategori-20-2-10` | Relevansi pertanyaan penelitian | Tujuan dan pertanyaan langsung/tidak relevan | Pertahankan label **Sesuai/Tidak Sesuai** |
| `pg-20-3-5` | Pengumpulan data dua variabel | Pasangan variabel dan pertanyaan pengukuran | Data berpasangan pada responden/periode yang sama |
| `mcma-20-3-8` | Pertanyaan kepuasan fasilitas | Dimensi kepuasan dan distractor yang berbeda | Jangan menambahkan variabel yang hanya berkorelasi secara dugaan |
| `pg-21-2-5` | Pengaruh pencilan pada mean | Dataset, posisi pencilan, dan perbandingan sebelum/sesudah | Hitung pengaruh mean/median/modus; tidak sekadar mengklaim mean paling terpengaruh |
| `pg-22-1-4` | Ukuran penyebaran | Dataset dan kebutuhan perbandingan penyebaran | Jangan mengganti tugas menjadi ukuran pemusatan |
| `mcma-22-1-8` | Relasi statistik dua dataset | Dataset serta klaim mean/median/modus/jangkauan | Modus tunggal/jamak dan jumlah klaim benar diperiksa |
| `pg-22-2-3` | Median dan nilai tengah | Dataset serta alasan pemilihan nilai tengah | Makna nilai tengah ditetapkan agar mean tidak sama-sama layak |
| `pg-22-2-5` | Konsistensi kelompok | Dataset, kelompok pembanding, dan alasan jangkauan | Nyatakan konsistensi berdasarkan jangkauan; jangan simpulkan varians |
| `mcma-22-2-8` | Kesamaan pusat dan perbedaan rentang | Dataset serta klaim perbandingan yang berbeda | Semua pernyataan diperiksa dari angka aktual |
| `pg-22-3-5` | Konsistensi berdasarkan jangkauan | Profil data dan argumen perbandingan | Kunci dan alasan harus menunjuk kelompok yang sama |
| `pg-23-1-1` | Peluang satu hasil dari enam | Representasi enam hasil seimbang dalam satu percobaan | **Uji batas:** ganti mata dadu saja tidak cukup; jangan naik ke percobaan majemuk |
| `pg-23-1-2` | Peluang satu hasil dari dua | Representasi dua hasil seimbang dalam satu percobaan | **Uji batas:** gambar/angka saja tidak memberi empat varian substantif |

### Soal konseptual yang belum dimasukkan karena ambigu

Tujuh ID berikut berkaitan dengan konsep, tetapi alasan utama skip adalah penilaian/kuantifier yang ambigu. Mereka tetap berada di kelompok 77 soal review sumber, terpisah dari target 67:

- `mcma-17-1-8`, `kategori-17-2-10`: klaim dilatasi mengubah ukuran harus mengecualikan abs(k)=1.
- `pg-23-3-2`, `pg-23-3-5`, `mcma-23-3-7`, `mcma-23-3-8`, `kategori-23-3-9`: istilah mendekati/jauh lebih besar belum mempunyai aturan penilaian eksplisit.

Penambahan ketujuh ID ini membutuhkan review tersendiri. Pengecualian jawaban sama tidak menyelesaikan ambiguitas mereka.

## Format stok yang diusulkan

Satu file `variant_gen/data/conceptual_stock.json`, bukan satu config generator per soal. File memuat `schema_version: 1` dan array `variants`.

Setiap item memuat:

| Field | Ketentuan |
|---|---|
| `variant_id` | ID stabil `{question_id}:stock-01` sampai `stock-04`; tidak memakai UUID Numora |
| `question_id` | Salah satu dari 67 ID dalam inventaris |
| `stock_index` | Integer 1–4; indeks VERIFIED berurutan 1–N, DRAFT hanya setelah N; maksimal 4 item per original termasuk DRAFT |
| `stock_version` | Integer positif; mulai 1, naik ketika konten varian direvisi offline |
| `original_hash`, `original_version` | Diambil dari original efektif `bank.get(question_id)` saat authoring |
| `stem` | Stimulus lengkap, siap ditampilkan, tanpa placeholder |
| `options` | Array `{id, text}` dengan ID dan jumlah mengikuti format original |
| `key` | String ID benar, dipisahkan koma; untuk KATEGORI memilih label kategori pertama |
| `explanation` | Pembahasan lengkap yang menjelaskan kunci dan setiap opsi/pernyataan |
| `variation_note` | Penjelasan perubahan konsep/stimulus/representasi dibanding original dan stok lain |
| `review_status` | `DRAFT` atau `VERIFIED`; hanya VERIFIED menjadi stok tersedia |
| `review_note` | Hasil pemeriksaan isi, perhitungan/asumsi, profil jawaban, serta kesetaraan tugas |

Format, klasifikasi paket/indikator/level, label kognitif, dan label kategori diwarisi dari original; jangan diduplikasi dengan nilai yang dapat berbeda. Keterangan keterbatasan per original ditulis pada laporan audit, bukan dibuat sebagai config runtime.

Record untuk UI/CLI memakai `source_kind: "conceptual_stock"`, `record_id: "{variant_id}:v{stock_version}"`, `variant_ver: stock_version`, dan identitas original existing. `seed`, `config_ver`, `config_hash`, `draws_used` bernilai null, `values_used` kosong. Ini konten stok, bukan hasil draw generator.

Jangan menambahkan field/parameter kosong untuk fitur masa depan. Pembaca stok mengembalikan record yang mengikuti renderer existing; renderer menampilkan nomor stok dan versi stok pada mode ini.

## File yang akan dibuat/diubah saat implementasi

- Create: `variant_gen/data/conceptual_stock.json` — konten manual, target sampai 268 varian.
- Create: `variant_gen/conceptual_stock.py` — pembaca, validasi, adapter record; tanpa write path.
- Create: `variant_gen/tests/test_conceptual_stock.py` — satu file unittest untuk kontrak konten, validasi, dan pembacaan UI/CLI.
- Create: `docs/audits/2026-10-06-conceptual-stock-audit.md` — jumlah aktual per ID, pengecualian, review isi dan bukti verifikasi. Tanggal disesuaikan tanggal eksekusi bila berbeda.
- Modify: `variant_gen/filters.py` — satu parameter internal opsional untuk pengecualian jawaban sama, default tetap ketat.
- Modify: `variant_gen/cli.py`, `variant_gen/webui.py`, `variant_gen/webui.html` — akses baca stok dan pemilihan nomor varian.
- Modify: `variant_gen/soalskip.md`, `docs/GENERATOR.md`, `docs/OPERATIONS.md` — kebijakan konseptual dan cara membaca stok. Jangan menulis ulang arsip audit lama.

## Task 1: Identifikasi dan batas cakupan — selesai pada tahap plan

**Files read:** `variant_gen/bank.py`, seluruh `variant_gen/data/**/q0_bank.csv`, metadata/katalog/revisi bank melalui loader, `variant_gen/soalskip.md`, config directory, engine/filters/CLI/UI dan tes stateless.

**Interfaces:** Produces: inventaris 67 ID dalam dokumen ini; tidak membuat atau mengubah metadata runtime.

- [x] Cocokkan ID konseptual dengan original efektif dan ketiadaan config.
- [x] Baca stimulus, opsi, format, label, dan kunci seluruh 67 original.
- [x] Pisahkan 59 DEFERRED konseptual, 8 legacy, dan 7 konsep ambigu yang belum eligible.
- [x] Catat sebaran indikator/format, arah variasi dan enam kandidat uji batas.
- [x] Sesuaikan rencana dengan penghapusan penyimpanan hasil generate pada HEAD terbaru.

## Task 2: Stok percontohan dan pembaca minimal

**Files:** Create JSON, `conceptual_stock.py`, dan `tests/test_conceptual_stock.py`; modify `filters.py`.

**Interfaces:**
- Consumes: `OriginalBank.get(qid)`, `filters.signature(...)`, `filters.validate_candidate(...)`.
- Produces: `load_stock(path: Path, bank: OriginalBank) -> dict[str, list[dict]]` untuk item VERIFIED dan `stock_record(original: dict, item: dict) -> dict` untuk renderer.
- Extend: `validate_candidate(cand, orig, others, *, allow_same_answer=False)`; hanya pemanggil pembaca stok memilih True. Jalur `engine.generate` tetap memakai default False.

- [x] Sebelum perubahan konten/runtime, catat hash file bank, metadata, katalog, revisi, source dan config sebagai baseline preservasi untuk Task 5.
- [x] Tulis tes gagal: stok dengan teks jawaban sama original diterima; generator numerik tetap menolak `same_answer_as_original`.
- [x] Tulis tes gagal untuk hash/versi salah, ID soal tidak dikenal, ID varian duplikat, opsi/key invalid, label kategori khusus, placeholder, pembahasan kosong, varian sama original, dan stok duplikat tanpa memperhatikan urutan opsi.
- [x] Tentukan maksimal 4 rancangan manual berbeda untuk masing-masing enam original percontohan: `pg-1-1-4`, `mcma-6-1-6`, `kategori-20-1-9`, `pg-16-3-2`, `pg-23-1-1`, `pg-23-1-2`. Target total 24; catat pengecualian bila hanya 2–3 rancangan sah.
- [x] Tulis konten lengkap percontohan, verifikasi semua opsi/pernyataan dan pembahasan, tandai VERIFIED setelah review; varian meragukan tetap DRAFT.
- [x] Implementasikan pembaca minimal dan adapter. File stok belum ada berarti stok kosong; JSON rusak atau provenance salah memberi `StoreError` yang jelas. Tidak mengabaikan item invalid secara diam-diam. Validasi semua item, hanya melayani VERIFIED.
- [x] Tolak sumber HOLD_SOURCE dan ID di luar inventaris 67. Cakupan diketahui dari daftar yang disetujui dalam rencana ini; jangan menganggap semua DEFERRED_CONCEPTUAL otomatis layak.
- [x] Pertahankan profil opsi dan jumlah kategori pertama; uji KATEGORI semua benar seperti `kategori-10-2-10`.
- [x] Validasi tipe setiap field, kesesuaian `variant_id`/question ID/index, versi positif, indeks unik dan indeks VERIFIED tanpa lubang; item DRAFT tidak dihitung sebagai stok tersedia.
- [x] Uji penolakan `stock_index: 5` dan lebih dari 4 item untuk satu original, termasuk item DRAFT; batas setiap original tidak dapat dilonggarkan oleh total stok bank yang masih kecil.
- [x] Run: `python -B -m unittest discover -s variant_gen/tests -p test_conceptual_stock.py -v`. Expected: PASS setelah implementasi dan review fixture.

## Task 3: Penulisan offline seluruh stok dan review akademik

**Files:** Modify JSON; create laporan audit.

**Interfaces:** Consumes: inventaris Task 1, schema dan validator Task 2. Produces: konten terverifikasi serta jumlah VERIFIED aktual per original.

- [x] Untuk setiap original, catat kompetensi, tugas berpikir, syarat stimulus, profil jawaban dan kesalahan konsep yang diuji sebelum menulis varian.
- [x] Tulis manual varian lengkap; jangan membuat skrip yang menghasilkan kombinasi template sebagai pengganti penulisan manual yang diminta.
- [x] Batch A: indikator 1–10, **19 original**, target **76 varian** termasuk percontohan yang sudah selesai.
- [x] Batch B: indikator 11–15, **22 original**, target **88 varian**.
- [x] Batch C: indikator 16–17, **8 original**, target **32 varian**.
- [x] Batch D: indikator 20–22, **16 original**, target **64 varian**.
- [x] Batch E: indikator 23, **2 original**, target **8 varian** termasuk percontohan.
- [x] Review isi setiap varian: kunci dihitung/dinilai ulang, alasan opsi salah benar, asumsi eksplisit, representasi tidak ambigu, dan tugas tetap setara original. Untuk angka gunakan perhitungan independen berbasis Fraction/statistics/math stdlib; jangan hanya percaya pembahasan yang ditulis bersama soal.
- [x] Review keberagaman di dalam keluarga serta antarkeluarga berdekatan. Jangan menyalin satu varian ke dua original yang mirip untuk memenuhi kuota.
- [x] Cocokkan sumber DOCX/source_text saat ada keraguan normalisasi atau asumsi; instruksi dalam dokumen tetap konten sumber, bukan izin koreksi original.
- [x] Pertahankan label kognitif gabungan seperti `C3 & C4`; jangan menormalkan tanpa dasar. Jangan menyatakan kesetaraan IRT dari review konten.
- [x] Jika VERIFIED <4, catat jumlah aktual, rancangan yang ditolak dan alasan konkret. Utamakan 2–3 varian sah; jika bahkan 2 tidak layak, laporkan khusus tanpa mengarang stok.
- [x] Pada audit, sediakan tabel 67 ID: target, VERIFIED, DRAFT, kekurangan, alasan, catatan isi. Jumlah stok dihitung dari item VERIFIED, bukan jumlah rancangan.
- [x] Jalankan tes kontrak setelah setiap batch; laporkan progres batch beserta jumlah aktual.

## Task 4: Tampilan dan akses baca stok melalui UI/CLI

**Files:** Modify CLI, HTTP handler, HTML; tambah tes pada file Task 2.

**Interfaces:**
- Consumes: `load_stock(...)` dan `stock_record(...)` dari Task 2.
- `/api/questions`: tambah `variant_mode: "generator" | "stock" | "unavailable"` dan `stock_count`; `has_config` tetap berarti config generator.
- `GET /api/question?id={qid}&stock_variant={index}`: tambah daftar ringkas `stock_variants`, mode, dan jumlah stok. Pada soal stock, default index 1 bila stok tersedia; indeks eksplisit harus menunjuk item VERIFIED yang ada. Respons `variant` berisi record stok pilihan, bukan hasil generate.
- CLI: `python -B variant_gen/cli.py stock {question_id} --variant {index} --json`; tanpa `--variant`, tampilkan daftar varian tersedia. Tambahkan `cmd_stock(a, bank, configs)` agar mengikuti dispatcher existing.

- [x] Tulis tes gagal untuk list/select stok via CLI dan HTTP, original tetap sama, pembacaan berulang tidak menulis file, dan dua soal tidak saling memperoleh stok.
- [x] Tulis tes gagal untuk stok 3: indeks 1–3 valid; 0, 4, nilai noninteger dan ID soal asing gagal jelas. Tidak melakukan modulo atau mengarang varian untuk seed besar.
- [x] Tambahkan mode stock dalam tab Service-AI existing. Panel original/varian dan gaya tetap konsisten dengan tab DB Utama; gunakan selector Varian 1–N.
- [x] Pada mode stock, ganti kontrol seed dengan pilihan stok; sembunyikan editor config/generate, tampilkan jumlah stok, nomor dan versi stok. Jangan membuat tab utama ketiga.
- [x] Tampilkan label kategori custom dan kunci/pernyataan sebagaimana original. Metadata status original historis tidak dijadikan alasan menonaktifkan akses stok yang sudah VERIFIED.
- [x] Generate numerik dan database browser mempertahankan alur existing. Tidak menambahkan jalur tulis stok atau ekspor Numora baru.
- [x] Jalankan tes Task 2 dan smoke browser: pilih PG, MCMA, dua label kategori custom, keluarga stok terbatas, soal generator existing, dan soal sumber HOLD. Expected: stok/kunci/pembahasan benar, pilihan terbatas sesuai jumlah nyata, tanpa error console.

## Task 5: Rekonsiliasi, dokumentasi, dan verifikasi akhir

**Files:** Modify skip ledger dan panduan terkait; finalisasi audit.

**Interfaces:** Consumes: jumlah VERIFIED dari Task 3, akses baca Task 4. Produces: laporan stok aktual dan bukti tidak ada perubahan bank/config/source.

- [x] Bandingkan hash file bank, metadata, katalog, revisi, source dan config dengan baseline Task 2. Original dan config existing harus tetap sama.
- [x] Perbarui `soalskip.md`: setiap 67 ID tetap tanpa generator, tetapi catat memiliki stok, jumlah, atau alasan kekurangan. Pertahankan alasan historis; tandai aturan jawaban berbeda pada review lama telah digantikan untuk stok konseptual.
- [x] Pisahkan angka jumlah generator, jumlah original dengan stok, jumlah varian stok, dan jumlah original belum terlayani. Jika seluruh 67 terlayani: **646 generator + 67 original dengan stok + 77 original belum terlayani = 790 Drill**. Ini target cakupan, bukan kondisi sebelum implementasi.
- [x] Jangan menghitung original sebagai stok atau menghitung DRAFT sebagai tersedia. Sebutan 144 soal tanpa generator tetap benar meskipun 67 di antaranya nanti memiliki stok.
- [x] Perbarui panduan membaca stok dan kebijakan `same_answer_as_original` khusus konseptual; bersihkan referensi snapshot/regen hanya pada alur yang disentuh.
- [x] Run: `python -B -m unittest discover -s variant_gen/tests -p "test_*.py" -v`. Expected: suite PASS; laporkan jumlah tes aktual, jangan memakai jumlah historis sebagai bukti.
- [x] Run: `git diff --check`. Expected: tanpa error whitespace. Audit hanya file terencana yang berubah; tanpa DB, Numora, `.env`, commit, atau push.
- [x] Final report: jumlah original terlayani dari 67, jumlah VERIFIED aktual dari target 268, daftar semua pengecualian 2–3/ditahan, validasi UI/CLI, dan hash preservation.

## Handoff

Implementasi dua tahap selesai: 67/67 original dengan 206 stok VERIFIED, masing-masing2?4. Cross-check seluruh stok memperbaiki beban tugas dan keragaman; jumlah maksimum268 merupakan batas, bukan klaim206 harus dipaksakan menjadi268. [Ledger progres](2026-10-06-conceptual-stock-progress.md) dan [audit per ID/varian](../../audits/2026-10-06-conceptual-stock-audit.md) mencatat jumlah aktual, kandidat yang dibuang dan batas kesetaraan kesulitan.
