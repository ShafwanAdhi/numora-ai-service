# Pemeriksaan masukan 679 generator Drill — 7 Oktober 2026

**ENGINEERING DECISION — cakupan permintaan pengguna:** selesaikan langkah pertama rancangan penyesuaian, tanpa membuat atau mengaktifkan penyesuaian otomatis. Pemeriksaan memakai konfigurasi terbaru per ID pada repo lokal. Tidak ada batas angka, filter, rumus, original, konfigurasi aktif, stok, `.env`, atau database yang diubah.

**PROPOSED — interpretasi pengaruh:** klasifikasi di bawah merupakan penilaian statis dan bukti representasi/perilaku generator. Ini belum merupakan persetujuan Curriculum/Data/Produk untuk mengubah pengaturan otomatis, arah perubahan kesulitan, atau hasil kesetaraan IRT pada siswa.

## Hasil dan berkas

| Pemeriksaan | Hasil |
|---|---:|
| Generator Drill diperiksa, hanya config terbaru per ID | 679 |
| Masukan langsung, tidak menghitung variabel derived | 1.027 |
| Enumerasi penuh domain setelah filter lokal | 677 generator |
| Kapasitas dan proyeksi domain dengan bukti analitik + probe | 2 generator |
| Kombinasi masukan yang benar-benar diperiksa | 5.026.631 |
| Proyeksi nilai efektif yang sudah lengkap | 1.027/1.027 masukan |
| Generator dengan kapasitas konten berbeda yang sudah tepat | 679/679 |
| Pemeriksaan matematika independen tambahan pada 33 generator revisi | 11.689 hasil valid |
| Soal HOLD dikecualikan | 4 |
| Revisi tanpa generator, menunggu generator selesai | 40 |
| Masukan disetujui untuk penyesuaian otomatis / penyesuaian aktif | 0 / 0 |

[Laporan JSON lengkap](2026-10-07-generator-input-audit.json) menyimpan versi/hash original dan config, klasifikasi paket, spesifikasi masukan, daftar nilai efektif, syarat gabungan, dependensi rumus, pasangan pembanding, alasan penolakan, bukti matematika, status sumber, dan status persetujuan. [CSV per masukan](2026-10-07-generator-input-audit.csv) memuat 1.027 baris untuk disaring menurut soal, masukan, kelompok, rentang, kapasitas, dan versi. Identitas original/config sama pada JSON dan CSV.

Tryout dan 67 keluarga stok manual tidak masuk audit generator Drill ini. Empat HOLD adalah `pg-1-2-1`, `pg-5-3-3`, `mcma-6-3-7`, dan `mcma-15-2-8`; alasan dan versi masing-masing tersedia pada `excluded_hold`. Empat puluh revisi 1–5 tercatat pada `waiting_for_generator`, berstatus `WAITING_FOR_GENERATOR` dan tetap tanpa persetujuan penyesuaian. Tidak dibuatkan rentang atau kapasitas generator fiktif.

## Cara pemeriksaan

1. Muat original efektif melalui ledger revisi dan pilih config terbaru. Periksa schema/hash dan reproduksi stem, setiap opsi, serta kunci original. Catatan reproduksi, jika ada, tetap disimpan.
2. Hitung daftar pilihan asli sesuai perilaku `range`/`choice`, termasuk kelipatan `step`, lalu terapkan filter lokal. Batas komputasi enumerasi adalah 2.000.000 kombinasi, **bukan perubahan batas angka generator**.
3. Enumerasi semua kombinasi untuk 677 generator. Jalankan derived, filter, syarat gabungan, render, dan seluruh validator global. `same_answer_as_original` tetap berlaku. Masukan valid untuk satu konteks belum tentu valid dengan masukan lain.
4. Hitung identitas konten dari stem dan kumpulan teks/kebenaran opsi menurut validator existing. Urutan opsi, jumlah request/seed, dan pembahasan tidak dihitung sebagai varian tambahan. Kombinasi masukan yang menghasilkan isi sama hanya dihitung sekali. Dua domain yang lebih besar memakai bukti analitik terjaga sesuai bagian berikut.
5. Untuk setiap masukan, bandingkan hasil dengan seluruh masukan langsung lain tetap. Simpan jalur dependensi ke stimulus, opsi, kunci, pembahasan dan syarat; simpan contoh pasangan perubahan yang bisa diperiksa ulang. Ini tidak menyamakan masukan hanya karena namanya `k`.
6. Catat jumlah/maksimum digit, tanda negatif, desimal, garis pecahan dan akar pada hasil render sebagai **indikator representasi**, bukan skor kesulitan. Ada 954 masukan dengan perubahan indikator tersebut. Angka ini juga mencakup konteks angka dan tidak membuktikan bahwa 954 masukan mengubah beban belajar.
7. Gunakan kembali oracle independen hasil render untuk seluruh kandidat valid 33 generator revisi: 11 dari 6–10, empat dari 11–15, dua dari 16–19, dan 16 dari 20–23. Bukti sebelumnya tetap ditautkan dengan hash. Pada 646 generator lainnya, audit ini memperluas pemeriksaan domain/validator dan dependensi; bukan klaim bahwa seluruh keluaran telah mendapat oracle matematika baru atau persetujuan akademik baru.

Rentang efektif berarti **proyeksi masukan pada kombinasi yang diterima**, setelah seluruh penyaringan. Daftar `values` adalah acuan; minimum–maksimum saja tidak menunjukkan lubang atau semua kombinasi yang diizinkan. Domain efektif tidak boleh diperluas dengan menganggap setiap pasangan nilai dalam proyeksi bebas digabungkan.

## Kelompok pengaruh per masukan

| Kelompok utama | Jumlah | Arti dan batas kesimpulan |
|---|---:|---|
| `POTENTIAL_WORKLOAD` | 900 | Masukan angka mempunyai jalur ke stimulus/opsi/penilaian dan berpotensi memengaruhi pembacaan atau aritmetika. Pasangan serta indikator perubahan dicatat; besar/arah pengaruh belum terbukti pada siswa. |
| `CONTENT_PROFILE` | 32 | Memilih pola data, klaim, posisi pernyataan salah, atau peran. Memerlukan review isi/alasan pengerjaan; tidak diperlakukan sebagai pengatur skala angka yang sudah terbukti. |
| `NUMERIC_CONTEXT` | 72 | Konteks angka, faktor pada tugas sifat transformasi, translasi data revisi, atau perubahan stimulus tanpa jalur ke teks opsi/kunci. Langkah/jawaban konseptual tetap; perubahan digit dan pembacaan tetap dicatat terpisah. |
| `DISPLAY_CONTEXT` | 2 | Masukan nama himpunan/titik pada generator revisi 11–15, dengan pemeriksaan tugas tetap dan angka lain tetap. |
| `NO_EFFECT` | 21 | Hanya satu nilai efektif, tidak memengaruhi konten, atau perubahan satu masukan dengan yang lain tetap tidak mengubah isi. Berlaku pada config/domain sekarang, bukan semua kemungkinan desain baru. |

Empat pertanyaan dalam desain bukan empat kelompok eksklusif: seluruh 1.027 masukan memiliki bukti menghasilkan kandidat sesuai aturan runtime; 932 adalah calon angka/profil untuk review beban, 74 terutama konteks/tampilan, dan **seluruh 1.027 belum menyediakan pilihan penyesuaian yang disetujui**. `review_groups` menyimpan keempat pertanyaan ini terpisah. `classification_status = PROPOSED_STATIC_AUDIT`, `approval_status = NO_APPROVED_CONTROL`, `adjustment_enabled = false`, dan arah kesulitan null berlaku pada seluruh masukan.

Status persetujuan sumber (`source_review_status`) terpisah dari izin penyesuaian otomatis. Metadata sumber yang tidak mencatat approval tetap `NOT_RECORDED`; keberadaan config atau kelulusan validator tidak mengisi approval yang tidak tersedia.

## Temuan yang dapat diperiksa ulang

| Soal / masukan | Nilai efektif dan kapasitas | Implikasi |
|---|---|---|
| `pg-21-1-1` | `k={1}`; `t={-60..-1,1..10}`; 70 varian | `k` tidak menyediakan pilihan saat ini. `t=0` ditolak karena jawaban sama dengan original. Perubahan representasi `t` bukan bukti arah kesulitan. |
| `pg-18-3-1` | `r1=2..12`, `k={4,5,6}`; 33 varian | `r1` saling menghapus dalam rasio luas; jawaban adalah `k²`. Jangan menyamakan radius dengan faktor perbandingan. |
| `pg-7-1-1` | `k=2..40`; 39 varian | Skala mengubah angka model/harga dan digit; `k=1` mereproduksi jawaban original dan ditolak. Tetap calon pengatur yang belum disetujui. |
| `mcma-17-1-8`, `kategori-17-2-10` | Delapan faktor dan empat/tiga posisi salah; 32/24 varian | `variant={1}` hanya penanda jalur produksi. Faktor mengubah konteks sifat; posisi salah mengubah profil klaim. Tidak menambah perhitungan koordinat. |
| `kategori-11-3-9` | `r1=1..5`, `r2=2..6`, `r3=4..7`, `labels={1,2}`; 68 varian | Proyeksi akar bukan domain bebas; urutan harus tetap. `labels=0` tidak lolos karena teks jawaban benar sama. Nama saja bukan pengatur kesulitan. |
| `pg-15-4-2` | `short=4..9`, `long=7..12`, `angle=30..60` kelipatan 5, `labels={1,2}`; 418 varian | Syarat sisi panjang dan satu kasus segitiga tetap. Angka geometri menjadi konteks tugas alasan kongruensi, bukan izin menambah perhitungan trigonometri. |
| `pg-23-3-5` | `trials=30..900` kelipatan 30, `p={6}`; 30 varian | `p` adalah kode numerator: `frequency=p/30`, sehingga hanya profil 1/5 efektif. Profil 2/15 ditolak oleh jawaban sama; bukan kontrol frekuensi yang bebas. |
| `kategori-23-3-10` | `observed` mempunyai 293 nilai efektif dari 0..500; 40.990 varian | Banyak nilai di dalam interval tidak tersedia karena syarat frekuensi/desimal dan kombinasi percobaan. Daftar lengkap wajib digunakan. |
| `pg-22-3-2` | `ma,mb=40..90`; `ra,rb=0..40` kelipatan 2; 27.846 varian | Probe awal melewatkan sejumlah nilai yang valid hanya pada konteks tertentu. Enumerasi penuh menutup proyeksinya. |
| `pg-22-3-3` | `center=20..80`, `gap={5,10,15,20}`, `shift=-3..5`; `skew` 45 nilai dengan batas -19..30; 14.410 varian | Penyaringan sangat mempersempit shift/skew. Interval skew mempunyai lubang; jangan menggantikan daftar efektif dengan interval penuh. |

## Dua kapasitas dengan bukti analitik

- **`pg-17-2-5`: 18.905.679.** Enam angka integer tampil di posisi yang berbeda, sehingga tuple masukan mengidentifikasi stimulus secara unik. Karena `c2` dan `d1` tidak nol, empat opsi koordinat berbeda. Dari 18.939.904 tuple lokal, 185×185 = 34.225 menghasilkan koordinat benar original dan ditolak. Kapasitas tepat adalah selisihnya. Semua nilai pada setiap proyeksi memiliki pasangan valid pada dimensi lain.
- **`pg-20-1-3`: 1.377.918.** Empat hari dalam opsi harus berbeda, Kamis lebih kecil dari maksimum, dan hari jawaban original (Jumat) tidak boleh menjadi jawaban kandidat. Untuk maksimum peringkat `m`, tiga hari pemenang yang diizinkan mempunyai `(m−1)(m−2)(m−3)` penempatan tiga nilai lebih rendah dan `(m−1)` pilihan Kamis. Jumlahnya `3 × Σ(m−1)²(m−2)(m−3)`, untuk `m=4..20`. Proyeksi Kamis/Jumat berhenti pada 95; Senin/Selasa/Rabu sampai 100.

Pembuktian menolak config yang rumus, template, format input, opsi atau syarat relevannya berbeda. Bukti dipin ke hash config, disandingkan dengan probe runtime, dan dibandingkan dengan enumerasi penuh pada domain kecil melalui tes. Pengacakan posisi opsi bukan kapasitas konten baru, sesuai identitas validator existing.

## Verifikasi dan penggunaan berikutnya

- **166 tes suite existing + audit lulus**, exit code 0. Enam tes audit memeriksa deduplikasi isi versus tuple, filter/kelipatan, penyusutan domain, larangan mengklaim kapasitas tepat dari probe, serta dua pembuktian versus enumerasi.
- Manifest hash bank/config/runtime sebelum dan sesudah audit sama. Laporan menyimpan hash dokumen/tes bukti dan helper matematika. Seluruh versi original/config dapat diperiksa ulang; konteks yang berubah membuat laporan tidak berlaku.
- CSV/JSON mencatat kapasitas **dalam domain saat ini**, bukan pilihan angka baru. Seed berbeda tetap dapat menghasilkan isi sama. Izin penyesuaian otomatis dan data siswa tetap belum tersedia.

Jalankan ulang dari akar repo AI untuk batas pemeriksaan yang sama:

```powershell
python -B variant_gen/tests/audit_generator_inputs.py --exhaustive-limit 2000000 --output docs/audits/2026-10-07-generator-input-audit.json
python -B -m unittest discover -s variant_gen/tests -p test_generator_input_audit.py -v
```

**OPEN — tahap berikutnya:** Curriculum/Data/Produk masih perlu menilai calon kontrol beserta invariannya, memilih pengaturan yang disetujui, dan membuktikan pengaruh dari respons siswa. Audit ini menyelesaikan inventaris, domain, kapasitas, serta pengelompokan statis langkah 1; tidak melaksanakan prototipe/alur langkah 2–4.
