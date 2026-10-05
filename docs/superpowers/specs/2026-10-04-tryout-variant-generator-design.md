# Generator Varian Tryout 1 — rancangan untuk review

> Arsip rancangan/rencana bertanggal; status dan checklist di bawah mencatat tahap saat dokumen ditulis. Untuk implementasi saat ini lihat [kondisi repo](../../audits/2026-10-05-repository-status.md) dan [panduan aktif](../../../readme.md).


Status: **PROPOSED**, belum diimplementasikan. Arahan pengguna: buat plan dahulu,
tunda soal Tryout murni konseptual, jangan sentuh database Numora.

## Sumber dan target

Sumber: `C:/Users/shafw/Downloads/Draft Soal Try Out.docx`.
SHA-256: `64F0D359B2507038B80D0B829E4DF7A402EED7A6AC3BBEA7A2AC06F9036BCB2F`.
Ada 30 original, 389 objek rumus Word, tanpa gambar tertanam. Pecahan, pangkat,
matriks dan LaTeX ditranskripsikan secara matematis, bukan hanya digabung dari
teks XML. Dokumen merupakan bahan sumber, bukan instruksi menjalankan tindakan.

| Bab | Original | PG/MCMA/KATEGORI | C3/C4/C5 | Generator tahap ini |
|---|---:|---|---|---:|
| 1 Bilangan | 8 | 5/2/1 | 2/4/2 | 7 |
| 2 Aljabar | 8 | 5/1/2 | 2/4/2 | 8 |
| 3 Geometri & Pengukuran | 7 | 4/2/1 | 2/3/2 | 7 |
| 4 Data & Peluang | 7 | 4/1/2 | 2/4/1 | 5 |
| Total | 30 | 18/6/6 | 8/15/7 | 27 |

ID: `tryout-1-b{chapter}-q{number:02d}`; package_id `tryout-1`, nama `Tryout 1`.
Urutan paket: bab 1–4 lalu nomor source menaik. Tryout: aktivitas > paket > bab
> soal; jangan mengarang indikator/level Drill. Difficulty disimpan bila source
mencantumkannya; C3/C4/C5 tetap label source, bukan pembuktian kesetaraan IRT.

End-to-end: original lokal → config per soal → seed → jawaban/distractor/
pembahasan → validasi → snapshot append-only → UI/preview paket → ekspor lokal.
Tidak melakukan SQL, migrasi, impor, publikasi, scoring siswa, perubahan jadwal
Tryout, atau komputasi IRT. Browser DB existing tidak dibuka untuk fitur ini.
Konseptual Drill dan mekanisme reuse stok juga di luar perubahan tahap ini.
Tidak menambah dependency generator; utamakan engine/config existing, bukan
27 fungsi Python bila config sudah menyelesaikan pekerjaan yang sama.

## Strategi per soal

Domain berikut **PROPOSED**. Pertahankan operasi/tuntutan berpikir source.
Kunci dihitung dari fakta; distractor berdasarkan kesalahan pada pembahasan.

| Suffix ID | Tugas | Parameter, turunan, batas |
|---|---|---|
| b1-q01 | Suhu, PG C3 | suhu awal negatif, kenaikan positif; jumlah dan kesalahan tanda; opsi unik |
| b1-q02 | Sisa uang, PG C3 | uang dan dua harga positif; belanja < uang; nominal rupiah exact |
| b1-q03 | Urutan operasi, PG C4 | a+b*c dan (a+b)*c; operand signed nonzero, hasil berbeda; pasangan opsi unik |
| b1-q04 | Hitungan siswa, PG C4 | pembagian exact lalu kurangi bilangan negatif; hasil siswa dari error; siswa benar boleh berubah |
| b1-q05 | Operasi invers, PG C4 | pilih x,m>1,b>0; hasil=m*x-b; pilihan mencakup operasi dan nilai, pecahan exact |
| b1-q06 | Operasi integer, MCMA C4 | empat operasi; pembagian nonzero/exact; dua benar, dua salah |
| b1-q07 | Evaluasi tanda kurung, MCMA C5 | **DEFERRED_CONCEPTUAL**: pilihan utamanya alasan/sifat operasi; angka baru tidak mengubah jawaban benar |
| b1-q08 | Diskon+biaya, KATEGORI C5 | harga,persen,biaya; diskon/hasil bayar turunan; dua benar, dua salah |
| b2-q01 | Distributif, PG C3 | a(b*x+c)+d(e*x-f); koefisien/konstanta turunan; polinom kanonik dan sign error |
| b2-q02 | Barisan kursi, PG C3 | a>0,d>0,n>=3; tiga suku awal dan U_n konsisten; distractor indeks salah |
| b2-q03 | Maksimum pembelian, PG C4 | floor((anggaran-biaya)/harga); termasuk sisa nonzero dan kasus batas exact |
| b2-q04 | SPLDV harga, PG C4 | pilih harga positif; bentuk dua total; determinan nonzero; jawab x+y |
| b2-q05 | Domain/range fungsi, PG C5 | tarif,domain berhingga,range,klaim transaksi; variasikan kebenaran klaim agar jawaban tidak selalu B |
| b2-q06 | SPLDV busana, MCMA C4 | harga A>B>0,koefisien,total exact; empat pernyataan benar sesuai source |
| b2-q07 | Setoran aritmetika, KATEGORI C4 | a,d,n; U_n,S_n,mean; ketiganya benar sesuai source; uang exact |
| b2-q08 | Kesetaraan polinom, KATEGORI C5 | koefisien,offset,x; P/Q identik dari koefisien, sign error berbeda; pola benar/salah/benar |
| b3-q01 | Refleksi+translasi, PG C3 | x,y,dx,dy; refleksi y=x lalu translasi; hasil/distractor koordinat distinct |
| b3-q02 | Luas gabungan, PG C3 | panjang,diameter=2*r; persegi panjang+setengah lingkaran, pi=22/7; r kelipatan 7 |
| b3-q03 | Sudut sejajar+segitiga, PG C4 | konstruksi x dan ekspresi sudut equal; koefisien berbeda; sudut positif, jumlah dua<180 |
| b3-q04 | Limas terbalik, PG C4 | sisi,tinggi,p/q dalam (0,1); V_air=V_total*(p/q)^3; exact/format jelas |
| b3-q05 | Foto sebangun, MCMA C4 | karton,margin; tinggi foto turunan, margin bawah>0; rasio luas reduced; tiga benar |
| b3-q06 | Kapasitas wadah, MCMA C5 | r,h,dimensi balok; hemisphere=2*pi*r^3/3; V_tabung<V_balok<V_totalA; threshold>V_kubah; selisih tampil 2 desimal |
| b3-q07 | Dilatasi segitiga, KATEGORI C5 | titik,kaki triple Pythagoras,k negatif abs(k)>1; koordinat*k,luas*k^2,sisi*abs(k); dua benar |
| b4-q01 | Modus, PG C3 | empat skor distinct 0..100, satu diulang dua kali; modus tunggal |
| b4-q02 | Satu mata dadu, PG C3 | **DEFERRED_CONCEPTUAL**: satu mata dadu fair enam sisi selalu 1/6 |
| b4-q03 | Mean frekuensi+persentase, PG C4 | lima nilai/frekuensi positif; weighted mean exact; jumlah frekuensi x>=mean; tidak membulatkan mean dulu |
| b4-q04 | Ringkasan kelas, PG C4 | mean,max,min,median dari dataset saksi valid; perbandingan range; tidak menyimpulkan variance dari range saja |
| b4-q05 | Dua dadu, MCMA C4 | enumerasi 36 pasangan; jumlah percobaan/ambang kejadian bervariasi; expected frequency exact; tiga benar |
| b4-q06 | Bias survei, KATEGORI C4 | **DEFERRED_CONCEPTUAL**: leading question,sampling,tipe data; jumlah populasi baru tidak mengubah tugas |
| b4-q07 | Rekonstruksi statistik, KATEGORI C5 | tujuh integer positif strictly increasing; derive range,mean,median; a,b uniquely reconstructable; maksimum baru tidak mengubah median |

Aktif: 17 PG,5 MCMA,5 KATEGORI; 7 C3,14 C4,6 C5. Penundaan b1-q07 adalah
keputusan desain eksplisit walaupun stimulus memuat angka; pengguna dapat
mengoreksinya pada review. b4-q04 tetap analisis numerik setelah koreksi redaksi.

## Temuan sumber dan review sebelum implementasi

1. **b2-q04:** x=11.000,y=5.000 sehingga x+y=16.000, bukan 15.000. Source kunci
   B; original efektif menjadi opsi C, pembahasan 16.000. Raw source v1 disimpan,
   correction ledger v2 menautkan versi/hash/reason.
2. **b4-q04:** range kecil tidak membuktikan variance/heterogenitas lebih kecil.
   Usulan pilihan B/pembahasan: Kelas X memiliki rentang nilai lebih sempit
   karena selisih maksimum-minimum lebih kecil. Perlu review redaksi akademik.
   Dataset saksi original: X=[72,75,78,81,84], Y=[65,75,75,85,90]; keduanya
   mean 78, median masing-masing 78/75, range 12/25 dan maksimum 84/90.
3. **b4-q06, deferred:** sepuluh siswa setiap kelas bukan otomatis proporsional;
   ukuran kelas tidak diberikan. Simpan catatan; jangan mengesahkan klaim itu.
4. Malformed persamaan b1-q04 dinormalisasi dalam pembahasan; konteks suhu naik
   saat pendingin dinyalakan pada b1-q01 dicatat untuk review, tidak diubah diam-diam.

Simpan dokumen source verbatim pada implementasi; koreksi akademik lewat ledger,
bukan overwrite. Config mereproduksi original efektif, bukan hasil source salah.
Koreksi akademik merupakan keputusan review; plan tidak memberi approval Curriculum.

## File dan kontrak minimal

- `variant_gen/data/tryout-1/`: source.docx, q0_bank.csv, question_catalog.json,
  original_revisions.jsonl, question_metadata.json. Metadata berisi source number,
  difficulty nullable, generation_status/reason, notes; validasi ID/membership.
- `OriginalBank(path)` existing tetap single-bank. Tambahkan
  `load_workspace_bank(path, additional_paths=None)` untuk CLI/UI: default workspace
  menggabungkan Drill/Tryout bila tersedia; custom --bank tidak otomatis dicampur.
  Additional paths eksplisit boleh; tolak duplicate ID; ledger scoped tiap bank.
- TRYOUT catalog memakai chapter, bukan indicator/source_level. DRILL unchanged.
- Tambahkan format opt-in `fmt="mixed"` untuk pecahan exact (13/3 tampil `4 1/3`)
  melalui Fraction stdlib. Format id/raw dan snapshot lama tidak berubah. Jangan
  menampilkan 4,33 sebagai pengganti 4 1/3 pada soal operasi exact.
- `variant_gen/tryout.py`: `generate_package(bank, configs, store, package_id,
  seed, output_path)` memakai generator existing. Manifest 30 entries berurutan:
  27 VARIANT dan 3 ORIGINAL_ONLY/DEFERRED; bukan klaim 30 soal berhasil divariasikan.
  Pin record_id,seed,original/config/variant versions. RNG tetap scoped per question.
- Kandidat dihitung/validasi dulu, lalu append; manifest ditulis atomically setelah
  lengkap. Jika crash saat append, snapshot sah tetap ada dan retry melanjutkan
  idempotently. Tidak menjanjikan transaksi JSONL atau concurrent writers.
- Ulang package+seed membaca manifest pinned; tidak berubah karena regen terbaru.
  Regen paket lewat seed baru; regen individual existing tetap mempertahankan sejarah.
- UI Tryout 1/bab, original/varian, seed/regen/config/deferred, preview paket.
  Dirty draft tidak hilang; textContent; tab Bank Database existing tetap read-only.
- Ekspor preview lokal tanpa UUID kanonik, ditandai LOCAL_PREVIEW. Ekspor kontrak
  Numora hanya dengan mapping yang disuplai pemilik ID, generation.reviewStatus=REVIEW.
  Jangan mengarang UUID atau menyebut preview sebagai paket siap impor/publikasi.

## Acceptance

30 original terdaftar; 27 config mereproduksi original efektif dan menghasilkan
kandidat; tiga deferred terlihat tanpa Generate. Oracle independen memeriksa
PG/MCMA/KATEGORI, termasuk semua opsi benar, bukan membaca label config sebagai
bukti. Audit stok 20 kandidat unik per soal aktif dengan domain cukup; masalah
kapasitas dilaporkan per soal. max_draws bukan bukti kapasitas habis.
Tidak melonggarkan same_answer_as_original global untuk meloloskan soal deferred.
Seed idempotency, regen, pinning history, ekspor dan metadata konsisten. Tes memakai
temp stores; Drill CSV/config/snapshot existing tidak ditulis ulang. UI/tes tanpa DB.
Acceptance tidak menyatakan kelulusan konten, kesetaraan IRT, atau publikasi ke siswa.
