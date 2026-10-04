# Tryout generator: hasil implementasi

30 original; 27 generator; 3 konseptual ditunda. Data/config/preview lokal;
tidak mengakses atau menulis database Numora. Tidak commit/push.

Verifikasi: 55 unittest PASS; 27 reproduksi original efektif; 540 kandidat
unik dengan oracle matematika dan pemeriksaan kunci; CLI package-gen/export PASS.
Browser memakai store/config sementara: filter bab 8/8/7/7, deferred disabled,
preview30, download, regen/pinning, dirty cancellation, lint, mobile390.

Review independen: tidak ada Critical. Temuan Important diperbaiki dengan
regresi: manifest tidak lengkap/berubah/provenance hilang, metadata invalid,
oracle kunci. Suite akhir55/55.

Keputusan:
- Worktree terisolasi membawa baseline pengguna; hanya delta task dikembalikan,
  tanpa commit perubahan pengguna. Biaya jika keliru: rekonsiliasi file.
- Raw DOCX/source_text dipertahankan; original runtime dinormalisasi dengan
  koreksi substansial di ledger. Biaya jika keliru: revisi akademik baru.
- Revisi original konseptual setelah paket dibuat membuat manifest lama ditolak
  daripada diam-diam berubah; gunakan seed/paket baru. Biaya: regenerasi paket.

Minor ditunda: pembahasan b2-q04 masih menyebut koreksi “source”.

Batas review: persetujuan kurikulum/label kognitif/IRT; kapasitas stok exact;
integrasi DB live/publikasi/scoring; concurrent writers/torn JSONL recovery;
autentikasi kriptografis preview. Di luar tahap ini. Snapshot varian lama tetap
mempertahankan original/config lama; perubahan baseline pengguna tidak direview.
