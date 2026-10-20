"""Seven bounded conceptual Indicator 20 families (k=0..24)."""
import json
from pathlib import Path

from build_drill_1_5_level45_batch1 import Author

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/drill-1-indicators-20-23-levels-4-5'
IDS = {'pg-20-4-1', 'pg-20-4-4', 'mcma-20-4-6', 'kategori-20-4-10',
       'pg-20-5-1', 'mcma-20-5-6', 'kategori-20-5-9'}


def selected():
    entries = json.loads((DATA / 'audit.json').read_text(encoding='utf8'))['entries']
    return [entry for entry in entries if entry['question_id'] in IDS]


def _derived(a, expression):
    token = a.var(expression)
    assert len(a.variables[token[1:-1]]['expr']) <= 300
    return token


def _choice(a, values, selector):
    # Each conditional stays comfortably below the expression-language limit;
    # the prior derived value is the fallback for the next branch.
    token = _derived(a, f"'' if k == 0 else {values[-1]!r}")
    for index in range(len(values) - 2, -1, -1):
        fallback = token[1:-1]
        token = _derived(a, f"'' if k == 0 else ({values[index]!r} if {selector} == {index} else {fallback})")
    return token


def _visible(a, text):
    return ''.join(_derived(a, f"'' if k == 0 else {chunk!r}")
                   for chunk in (text[i:i + 150] for i in range(0, len(text), 150)))


def _original(a, text):
    return ''.join(_derived(a, f"{chunk!r} if k == 0 else ''")
                   for chunk in (text[i:i + 150] for i in range(0, len(text), 150)))


def _field(a, original, generated):
    return _original(a, original) + generated


def author(entry):
    entry = dict(entry, source_number=int(entry['question_id'].split('-')[-1]))
    a = Author(entry)
    a.variables['k']['range'] = [0, 24]
    a.exp = entry['source_projection']['explanation']
    qid = a.qid
    domain = _choice(a, ['kegiatan membaca', 'latihan olahraga', 'penggunaan gawai',
                         'kunjungan perpustakaan', 'sarapan pagi', 'perjalanan ke sekolah'], '(k-1) % 6')
    population = _choice(a, ['siswa kelas VII', 'siswa kelas VIII', 'siswa kelas IX',
                             'anggota klub sekolah'], '(k-1) // 6')
    period = _choice(a, ['setiap hari', 'selama tujuh hari terakhir', 'dalam satu bulan terakhir',
                         'pada pekan sekolah ini'], '(k-1) // 6')

    def replace(stem, options, explanation, correct):
        a.stem = _field(a, a.stem, stem)
        a.options = [_field(a, old, new) for old, new in zip(a.options, options)]
        a.exp = _field(a, a.exp, explanation)
        a.correct = correct

    if qid == 'pg-20-4-1':
        outcome = _choice(a, ['nilai kuis', 'ketepatan tugas', 'kehadiran kelas', 'skor proyek'], '(k-1) // 6')
        replace(_visible(a, 'Peneliti mencatat ') + domain + _visible(a, ' dan ') + outcome +
                _visible(a, ' pada ') + population + _visible(a, '. Pertanyaan penelitian yang paling sesuai adalah ....'),
                [_visible(a, 'Berapa jumlah responden yang terdaftar?'),
                 _visible(a, 'Apa kegiatan sekolah yang paling disukai responden?'),
                 _visible(a, 'Apakah terdapat hubungan antara ') + domain + _visible(a, ' dan ') + outcome + _visible(a, '?'),
                 _visible(a, 'Berapa responden yang menyerahkan formulir?')],
                _visible(a, 'Alasan utama: pertanyaan ketiga menghubungkan kedua variabel yang benar-benar dicatat pada populasi sasaran.'),
                [False, False, True, False])
    elif qid == 'pg-20-4-4':
        benefit = _choice(a, ['lebih sehat', 'lebih cerdas', 'selalu disiplin', 'pasti berprestasi'], '(k-1) // 6')
        replace(_visible(a, 'Survei tentang ') + domain + _visible(a, ' menanyakan, “Tidakkah kamu setuju bahwa kegiatan ini sangat bermanfaat dan membuat semua peserta ') + benefit + _visible(a, '?” Kelemahan utamanya adalah ....'),
                [_visible(a, 'Nama sekolah tidak ditulis.'),
                 _visible(a, 'Kalimat mengarahkan jawaban sekaligus menggabungkan dua klaim.'),
                 _visible(a, 'Jawaban tidak harus berupa angka.'),
                 _visible(a, 'Kalimatnya terlalu singkat.')],
                _visible(a, 'Alasan utama: ungkapan “tidakkah setuju” bersifat mengarahkan, sedangkan manfaat dan akibat bagi semua peserta merupakan dua klaim.'),
                [False, True, False, False])
    elif qid == 'mcma-20-4-6':
        duration_question = _choice(a, [
            'Berapa menit kamu membaca setiap hari?', 'Berapa menit kamu berolahraga setiap hari?',
            'Berapa menit kamu menggunakan gawai setiap hari?', 'Berapa lama setiap kunjunganmu ke perpustakaan?',
            'Berapa menit yang kamu gunakan untuk sarapan?', 'Berapa menit perjalananmu ke sekolah?'], '(k-1) % 6')
        type_question = _choice(a, [
            'Jenis bacaan apa yang paling sering kamu baca?', 'Jenis olahraga apa yang paling sering kamu lakukan?',
            'Jenis aplikasi apa yang paling sering kamu gunakan?', 'Jenis layanan perpustakaan apa yang paling sering kamu gunakan?',
            'Menu apa yang paling sering kamu pilih untuk sarapan?', 'Moda transportasi apa yang paling sering kamu gunakan?'], '(k-1) % 6')
        frequency_question = _choice(a, [
            'Berapa kali kamu membaca dalam tujuh hari terakhir?', 'Berapa kali kamu berolahraga dalam tujuh hari terakhir?',
            'Berapa kali kamu menggunakan gawai untuk belajar dalam tujuh hari terakhir?', 'Berapa kali kamu mengunjungi perpustakaan dalam satu bulan terakhir?',
            'Berapa hari kamu sarapan dalam tujuh hari terakhir?', 'Berapa hari kamu memakai moda tersebut dalam tujuh hari terakhir?'], '(k-1) % 6')
        replace(_visible(a, 'Peneliti ingin mengukur kebiasaan ') + domain + _visible(a, ' pada ') + population + _visible(a, '. Pilih pertanyaan yang sesuai.'),
                [duration_question, type_question,
                 _visible(a, 'Mengapa orang yang jarang melakukannya pantas disebut malas?'),
                 frequency_question,
                 _visible(a, 'Apakah semua siswa wajib menyukai kegiatan itu?')],
                _visible(a, 'Alasan utama: durasi, jenis, dan frekuensi mengukur perilaku secara langsung; cap malas dan kewajiban menyukai adalah pertanyaan menghakimi atau normatif.'),
                [True, True, False, True, False])
    elif qid == 'kategori-20-4-10':
        first = _choice(a, ['hemat', 'nyaman', 'aman', 'praktis'], '(k-1) // 6')
        second = _choice(a, ['sehat', 'cepat', 'adil', 'menyenangkan', 'ramah lingkungan', 'bermanfaat'], '(k-1) % 6')
        replace(_visible(a, 'Survei tentang ') + domain + _visible(a, ' bertanya, “Apakah kamu setuju bahwa kebiasaan ini lebih ') + first + _visible(a, ', lebih ') + second + _visible(a, ', dan pasti lebih baik?” Tentukan kategori yang tepat.'),
                [_visible(a, 'Pertanyaan memuat beberapa aspek yang mungkin dijawab berbeda.'),
                 _visible(a, 'Setiap aspek sebaiknya ditanyakan secara terpisah dan spesifik.'),
                 _visible(a, 'Pertanyaan sudah netral hanya karena tidak menampilkan pilihan jawaban.'),
                 _visible(a, 'Aspek ') + first + _visible(a, ' dan ') + second + _visible(a, ' dapat ditanyakan secara terpisah.')],
                _visible(a, 'Alasan utama: pertanyaan menggabungkan aspek ') + first + _visible(a, ' dan ') + second + _visible(a, ' serta memakai arah “lebih baik”; pisahkan aspek dengan kalimat netral.'),
                [True, True, False, True])
    elif qid == 'pg-20-5-1':
        service = _choice(a, ['ruang belajar', 'lapangan olahraga', 'layanan kantin',
                              'koleksi perpustakaan', 'angkutan sekolah', 'kegiatan ekstrakurikuler'], '(k-1) % 6')
        replace(_visible(a, 'Peneliti hendak mengukur tingkat kepuasan ') + population + _visible(a, ' terhadap ') + service + _visible(a, '. Rancangan pertanyaan yang paling layak adalah ....'),
                [_visible(a, 'Bukankah layanan ini sangat bagus dan memuaskan?'),
                 _visible(a, 'Apakah kamu menyukai sekolahmu?'),
                 _visible(a, 'Bagaimana tingkat kepuasanmu terhadap ') + service + _visible(a, '? (Sangat tidak puas, tidak puas, puas, sangat puas)'),
                 _visible(a, 'Mengapa layanan ini pasti lebih baik daripada milik sekolah lain?')],
                _visible(a, 'Alasan utama: pertanyaan ketiga langsung mengukur kepuasan terhadap objek sasaran memakai skala berurutan yang jelas dan netral.'),
                [False, False, True, False])
    elif qid == 'mcma-20-5-6':
        replace(_visible(a, 'Sekolah akan menyurvei ') + domain + _visible(a, ' pada ') + population + _visible(a, '. Pilih keputusan yang meningkatkan kualitas data.'),
                [_visible(a, 'Memilih responden ') + population + _visible(a, ' dari beberapa kelas untuk menilai ') + domain + _visible(a, ' agar pengalaman beragam terwakili.'),
                 _visible(a, 'Menanyakan frekuensi ') + domain + _visible(a, ' dalam periode yang jelas: ') + period + _visible(a, '.'),
                 _visible(a, 'Hanya memilih responden yang sangat menyukai kegiatan tersebut.'),
                 _visible(a, 'Menggunakan pertanyaan netral tentang ') + domain + _visible(a, ' yang tidak mengarahkan jawaban.'),
                 _visible(a, 'Menganggap seluruh siswa setuju berdasarkan beberapa penggemar kegiatan.')],
                _visible(a, 'Alasan utama: cakupan beberapa kelas, periode ingatan yang jelas, dan kalimat netral memperbaiki keterwakilan serta konsistensi; sampel penggemar membiasakan hasil.'),
                [True, True, False, True, False])
    elif qid == 'kategori-20-5-9':
        replace(_visible(a, 'Penelitian mengevaluasi kepuasan ') + population + _visible(a, ' terhadap ') + domain + _visible(a, '. Tentukan kelayakan setiap rancangan.'),
                [_visible(a, 'Menggunakan pilihan tingkat kepuasan terhadap ') + domain + _visible(a, ' yang jelas dan berurutan.'),
                 _visible(a, 'Hanya meminta pendapat responden yang sudah menyukai kegiatan tersebut.'),
                 _visible(a, 'Menyajikan jawaban kepuasan terhadap ') + domain + _visible(a, ' dalam diagram batang berlabel.'),
                 _visible(a, 'Menghapus jawaban yang tidak sesuai dengan harapan peneliti.')],
                _visible(a, 'Alasan utama: skala kepuasan yang jelas dan diagram batang berlabel layak; memilih penggemar saja menimbulkan bias dan menghapus jawaban merusak integritas data.'),
                [True, False, True, False])
    else:
        raise AssertionError(qid)
    return a
