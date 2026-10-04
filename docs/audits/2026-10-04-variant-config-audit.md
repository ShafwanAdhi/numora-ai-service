# Audit config dan snapshot generator varian ? 4 Oktober 2026

## Ruang lingkup

Audit lokal `Numora-ai-service`: bank CSV beserta ledger revisi, seluruh config, engine/validator, dan snapshot JSONL. Tidak membandingkan isi dengan soal demo Numora, tidak mengakses DB, tidak mengubah engine/config/bank/snapshot. Semua rekomendasi di bawah **PROPOSED**; bukan approval Curriculum atau kelulusan IRT.

## Hasil utama

| Pemeriksaan | Hasil |
|---|---|
| Original | 120: 60 PG, 36 MCMA, 24 KATEGORI |
| Config | 110 soal, 116 file termasuk 6 versi historis |
| Struktur dan reproduksi original | 110 config terbaru lulus; tidak ada warning reproduksi |
| Generasi independen | Semua 110 config menghasilkan kandidat untuk masing-masing seed 1?20 |
| Simulasi stok 20 kandidat unik | 86 mencapai 20; 24 tidak mencapai 20 |
| Belum memiliki config | 10 soal membutuhkan review konten/policy |
| Inventaris variabel config terbaru | 265 input acak, 555 nilai turunan; tidak ada variabel tanpa referensi pemakaian |
| Snapshot tersimpan | 9; seluruh config hash cocok dan teks/opsi/kunci dapat direkonstruksi |
| Pembahasan snapshot | 5 lengkap, 4 historis belum memiliki pembahasan |
| Tes existing | 36 lulus, 0 gagal |

Angka 20 adalah ukuran probe audit, **bukan target stok produk**. Kegagalan menambah stok tidak otomatis berarti rumus salah. Untuk kebanyakan config, jumlah yang ditemukan adalah hasil sampling, bukan kapasitas maksimum. Semua kandidat lolos validator engine saat ini; audit ini tidak membuktikan kebenaran akademik seluruh distractor/solusi atau kesetaraan empiris.

## Variabel: apa yang sudah ada

`gen` sudah membedakan input acak (`range`, `choice`, `scale`) dan turunan (`derived`). `original_values` menyimpan input original. `values_used` menyimpan nilai input dan turunan kandidat. Pemakaian tiap variabel pada stem, opsi, pembahasan, correctness, constraint, dan ekspresi turunan tercatat pada lampiran JSON.

Contoh `pg-18-3-1`: `r1` dan `k` adalah input; `r2=r1*k` turunan; `o1..o4` menghasilkan nilai opsi. Angka literal dalam rumus, misalnya `3.14`, tetap bagian definisi config. Angka konstan dalam redaksi tidak otomatis menjadi parameter yang boleh diubah.

Label semantik seperti input ukuran, jawaban, distractor, atau satuan **belum dideklarasikan**. Audit menampilkan referensi pemakaian, tidak menebak peran akademik dari nama variabel. Nilai yang digunakan pada correctness belum tentu merupakan distractor.

## Temuan dan tindakan yang disarankan

### 1. Stok terbatas ? prioritaskan target nyata

Enumerasi semua nilai input pada tiga config kecil menghasilkan kapasitas pasti dengan aturan sekarang:

| Soal | Kapasitas unik | Penyebab |
|---|---:|---|
| `mcma-16-3-6` | 4 | `k` hanya 2?6; nilai 2 mereproduksi original |
| `pg-18-1-2` | 9 | Radius hanya 10 kelipatan 7; satu mereproduksi original |
| `pg-19-1-4` | 4 | Radius 2?15; constraint presisi dan jawaban berbeda menyaring kandidat |

**PROPOSED:** tentukan kebutuhan stok per keluarga sebelum memperluas range. Bila target masih di bawah kapasitas yang tersedia, tidak perlu mengubah config. Jika target melebihi kapasitas, review batas Curriculum lalu buat config versi baru. Menaikkan `max_draws` tidak menciptakan nilai baru pada domain yang habis.

24 config dengan warning stok tercantum pada tabel seluruh soal. Rejection terbanyak adalah duplikat stok; penghitung rejection dapat mencatat beberapa alasan untuk satu draw, sehingga jumlahnya bukan jumlah draw unik.

### 2. Metadata hasil generasi

**Sudah tersedia:** seed, config version/hash, original version/hash, nilai konkret, jumlah draw, teks, opsi, kunci, waktu, hubungan replacement, alasan regen; pembahasan tersedia pada snapshot baru.

**PROPOSED, prioritas pertama:** simpan identitas versi implementasi generator/validator dan ringkasan rejection untuk snapshot baru. Gunakan satu versi rilis yang mengikat keduanya jika selalu dirilis bersama; tidak wajib membuat dua sistem versi terpisah. Rekam kegagalan sebagai evidence run tersendiri, bukan kandidat kosong.

**PROPOSED, saat format berubah:** tambahkan `schema_version` untuk membedakan struktur snapshot. `template_version` terpisah baru diperlukan jika template memang dipisah dari config; saat ini seluruh template berada di config yang sudah berversi. Jangan menambah field yang mengulang informasi tanpa kebutuhan.

### 3. Snapshot historis

Empat record awal pada `pg-16-1-3`, `kategori-19-1-9`, dan `mcma-18-1-7` belum mempunyai pembahasan. Mereka cocok dengan config yang dipin; hash original yang dicatat berbeda dari bank aktif. Reproduksi isi original dari config lama sesuai bank aktif setelah normalisasi whitespace pada checker existing. Jangan menyimpulkan perubahan akademik hanya dari selisih hash tersebut.

**PROPOSED:** pertahankan record lama. Gunakan `regen` ke config baru bila membutuhkan snapshot yang dapat diekspor; alur ini sudah tersedia dan diuji. Definisikan normalisasi/version untuk fingerprint berikutnya sebelum integrasi, tanpa menulis ulang hash historis.

### 4. Presisi nilai tersimpan

Engine menghitung dengan `Fraction`, tetapi `json_number` mengubah pecahan menjadi float JSON. Probe menemukan round-trip tidak exact pada:

| Soal | Variabel |
|---|---|
| `mcma-19-1-6` | `sphere` |
| `mcma-19-2-8` | `sphere` |
| `mcma-19-3-8` | `cone` |

Temuan ini tentang fidelity metadata numerik; bukan bukti bahwa teks/kunci salah.

**PROPOSED:** simpan representasi exact hanya bila nilai tersebut dibutuhkan untuk replay perhitungan/evaluator, misalnya pasangan numerator/denominator pada metadata terpisah yang tervalidasi. Payload tampilan tetap mengikuti aturan format. Jangan mengganti semua angka menjadi string karena konsumen `to_num` saat ini tidak menerima string.

### 5. Satuan, peran, dan izin adjustment

**PROPOSED:** satuan dan peran semantik dapat membantu reviewer, tetapi tidak perlu diwajibkan pada seluruh 820 variabel. Prioritaskan input yang hendak di-adjust. Batas yang diizinkan Curriculum harus dibedakan dari range eksperimen aktif, sehingga adjuster tidak dapat memperluas batas akademik.

Per-variable key baru seperti `unit` atau `role` akan ditolak oleh schema sekarang; penambahan harus disertai validasi dan versi format, bukan sekadar ditempel pada file config. Jangan menduplikasi daftar input/turunan: informasi itu sudah tersedia lewat `gen`.

### 6. Sepuluh original menunggu review

Alasan rinci tersedia pada `../../variant_gen/soalskip.md`. Soal konseptual tidak harus dipaksa menjadi soal numerik. `same_answer_as_original` adalah aturan engine saat ini; perubahan terhadapnya membutuhkan keputusan eksplisit agar tidak meloloskan varian kosmetik. Keberadaan config juga belum merupakan approval Curriculum.

## Urutan perbaikan yang disarankan

1. Tentukan kebutuhan stok; review hanya keluarga yang kapasitasnya tidak mencukupi.
2. Lengkapi provenance versi implementasi dan rejection pada output baru.
3. Lengkapi nilai exact bila evaluator membutuhkan replay matematika.
4. Tambahkan unit/peran/izin adjustment untuk input yang benar-benar akan di-adjust.
5. Siapkan adapter DB/consumer setelah struktur output disepakati; tidak bergantung pada isi demo Numora.

Tidak ada perubahan perilaku diterapkan pada audit ini.

## Inventaris seluruh soal

`LENGKAP_TEKNIS_SAMPEL`: config lulus struktur/reproduksi dan probe stok 20. `PERLU_REVIEW_STOK`: tetap lulus struktur/reproduksi/probe independen, tetapi probe stok tidak mencapai 20. `PERLU_REVIEW_CURRICULUM`: belum memiliki config. Label tidak memberi kelulusan konten atau IRT.

| Soal | Config terbaru | Input / turunan | Stok ditemukan / 20 | Status |
|---|---:|---:|---:|---|
| `pg-16-1-1` | ? | ? | ? | PERLU_REVIEW_CURRICULUM |
| `pg-16-1-2` | ? | ? | ? | PERLU_REVIEW_CURRICULUM |
| `pg-16-1-3` | v2 | 1 / 4 | 18 | PERLU_REVIEW_STOK |
| `pg-16-1-4` | v2 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-16-1-5` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-16-2-1` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-16-2-2` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-16-2-3` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-16-2-4` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-16-2-5` | v1 | 1 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-16-3-1` | v1 | 2 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-16-3-2` | ? | ? | ? | PERLU_REVIEW_CURRICULUM |
| `pg-16-3-3` | v1 | 2 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-16-3-4` | v1 | 2 / 7 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-16-3-5` | v2 | 2 / 9 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-17-1-1` | v1 | 4 / 8 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-17-1-2` | v1 | 2 / 8 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-17-1-3` | v1 | 2 / 8 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-17-1-4` | v1 | 3 / 8 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-17-1-5` | v1 | 2 / 8 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-17-2-1` | v1 | 4 / 8 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-17-2-2` | v1 | 2 / 8 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-17-2-3` | v1 | 2 / 8 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-17-2-4` | v1 | 3 / 9 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-17-2-5` | v1 | 6 / 8 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-17-3-1` | v1 | 5 / 10 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-17-3-2` | ? | ? | ? | PERLU_REVIEW_CURRICULUM |
| `pg-17-3-3` | v1 | 3 / 2 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-17-3-4` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-17-3-5` | v1 | 4 / 14 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-18-1-1` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-18-1-2` | v1 | 1 / 4 | 9 | PERLU_REVIEW_STOK |
| `pg-18-1-3` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-18-1-4` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-18-1-5` | v1 | 1 / 4 | 6 | PERLU_REVIEW_STOK |
| `pg-18-2-1` | v1 | 1 / 5 | 9 | PERLU_REVIEW_STOK |
| `pg-18-2-2` | v1 | 3 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-18-2-3` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-18-2-4` | v1 | 2 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-18-2-5` | v1 | 3 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-18-3-1` | v1 | 2 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-18-3-2` | v1 | 1 / 7 | 9 | PERLU_REVIEW_STOK |
| `pg-18-3-3` | v1 | 2 / 4 | 12 | PERLU_REVIEW_STOK |
| `pg-18-3-4` | v1 | 2 / 6 | 11 | PERLU_REVIEW_STOK |
| `pg-18-3-5` | v1 | 1 / 7 | 11 | PERLU_REVIEW_STOK |
| `pg-19-1-1` | v1 | 3 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-19-1-2` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-19-1-3` | v1 | 2 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-19-1-4` | v1 | 1 / 3 | 4 | PERLU_REVIEW_STOK |
| `pg-19-1-5` | v1 | 3 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-19-2-1` | v1 | 3 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-19-2-2` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-19-2-3` | v1 | 1 / 4 | 5 | PERLU_REVIEW_STOK |
| `pg-19-2-4` | v1 | 3 / 7 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-19-2-5` | v1 | 3 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-19-3-1` | v1 | 4 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-19-3-2` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-19-3-3` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-19-3-4` | v1 | 4 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `pg-19-3-5` | v1 | 1 / 3 | 19 | PERLU_REVIEW_STOK |
| `mcma-16-1-6` | ? | ? | ? | PERLU_REVIEW_CURRICULUM |
| `mcma-16-1-7` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-16-1-8` | v1 | 2 / 3 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-16-2-6` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-16-2-7` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-16-2-8` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-16-3-6` | v1 | 1 / 1 | 4 | PERLU_REVIEW_STOK |
| `mcma-16-3-7` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-16-3-8` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-17-1-6` | v1 | 4 / 6 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-17-1-7` | v1 | 3 / 8 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-17-1-8` | ? | ? | ? | PERLU_REVIEW_CURRICULUM |
| `mcma-17-2-6` | v1 | 5 / 8 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-17-2-7` | v1 | 2 / 1 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-17-2-8` | v1 | 4 / 7 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-17-3-6` | v1 | 5 / 9 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-17-3-7` | v1 | 2 / 2 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-17-3-8` | v1 | 2 / 8 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-18-1-6` | v1 | 1 / 5 | 13 | PERLU_REVIEW_STOK |
| `mcma-18-1-7` | v2 | 1 / 4 | 6 | PERLU_REVIEW_STOK |
| `mcma-18-1-8` | v1 | 4 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-18-2-6` | v1 | 3 / 6 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-18-2-7` | v1 | 2 / 4 | 15 | PERLU_REVIEW_STOK |
| `mcma-18-2-8` | v1 | 5 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-18-3-6` | v1 | 2 / 6 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-18-3-7` | v1 | 2 / 6 | 15 | PERLU_REVIEW_STOK |
| `mcma-18-3-8` | v1 | 5 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-19-1-6` | v1 | 3 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-19-1-7` | v1 | 1 / 4 | 7 | PERLU_REVIEW_STOK |
| `mcma-19-1-8` | v1 | 1 / 4 | 6 | PERLU_REVIEW_STOK |
| `mcma-19-2-6` | v1 | 3 / 6 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-19-2-7` | v1 | 1 / 4 | 7 | PERLU_REVIEW_STOK |
| `mcma-19-2-8` | v1 | 3 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `mcma-19-3-6` | v1 | 1 / 4 | 12 | PERLU_REVIEW_STOK |
| `mcma-19-3-7` | v1 | 1 / 5 | 9 | PERLU_REVIEW_STOK |
| `mcma-19-3-8` | v1 | 2 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-16-1-9` | ? | ? | ? | PERLU_REVIEW_CURRICULUM |
| `kategori-16-1-10` | v1 | 1 / 2 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-16-2-9` | ? | ? | ? | PERLU_REVIEW_CURRICULUM |
| `kategori-16-2-10` | v1 | 2 / 2 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-16-3-9` | v1 | 2 / 2 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-16-3-10` | v2 | 3 / 3 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-17-1-9` | v1 | 4 / 6 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-17-1-10` | v1 | 2 / 6 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-17-2-9` | v1 | 4 / 6 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-17-2-10` | ? | ? | ? | PERLU_REVIEW_CURRICULUM |
| `kategori-17-3-9` | v1 | 5 / 7 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-17-3-10` | ? | ? | ? | PERLU_REVIEW_CURRICULUM |
| `kategori-18-1-9` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-18-1-10` | v1 | 1 / 4 | 9 | PERLU_REVIEW_STOK |
| `kategori-18-2-9` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-18-2-10` | v1 | 1 / 5 | 18 | PERLU_REVIEW_STOK |
| `kategori-18-3-9` | v1 | 1 / 5 | 9 | PERLU_REVIEW_STOK |
| `kategori-18-3-10` | v1 | 3 / 5 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-19-1-9` | v2 | 3 / 3 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-19-1-10` | v1 | 3 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-19-2-9` | v1 | 5 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-19-2-10` | v1 | 2 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-19-3-9` | v1 | 4 / 3 | 20 | LENGKAP_TEKNIS_SAMPEL |
| `kategori-19-3-10` | v1 | 3 / 4 | 20 | LENGKAP_TEKNIS_SAMPEL |

## Evidence dan pemeriksaan ulang

Lampiran [JSON audit](2026-10-04-variant-config-audit.json) berisi seluruh definisi variabel/pemakaian/dependency, original values, constraint, hasil kedua probe, rejection, config historis, pemeriksaan snapshot, dan SHA-256 130 file input.

Probe: 4.400 percobaan generate (110 config ? 20 seed ? 2 mode), 110 pemeriksaan determinisme, 9 replay body/opsi/kunci snapshot, 3 enumerasi kapasitas lengkap. Mode stok menggunakan daftar kandidat di memori yang awalnya kosong, tidak menulis ke store; kapasitas tersisa dalam store pengguna bukan objek probe ini. Replay snapshot mengabaikan urutan opsi melalui signature substantif; pembahasan hanya diperiksa keberadaannya, bukan ditinjau akademik.

36 tes existing lulus dengan perintah berikut dari `variant_gen`:

```powershell
python -B -m unittest discover -s tests -v
```

File input tetap memiliki hash yang sama selama audit. `variant_gen/store/variants.jsonl` sudah modified sebelum audit dan tidak disentuh. Tidak ada perubahan repo Numora.
