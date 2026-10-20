"""Semantic oracle derived only from rendered Indicator 20 text."""
import re


def _low(text):
    return ' '.join(text.lower().split())


def check_math(qid, candidate):
    stem = _low(candidate['stem'])
    options = [_low(option['text']) for option in candidate['options']]
    explanation = _low(candidate['explanation'])

    if qid == 'pg-20-4-1':
        match = (re.search(r'mencatat (.+?) dan (.+?) pada ', stem) or
                 re.search(r'hubungan antara (.+?) dan (.+?) siswa', stem))
        assert match, stem
        left, right = match.group(1), match.group(2)
        truth = ['hubungan antara' in option and left in option and right in option and 'berapa' not in option
                 for option in options]
        assert sum(truth) == 1 and ('kedua variabel' in explanation or 'dua variabel' in explanation)
    elif qid == 'pg-20-4-4':
        assert ('sangat bermanfaat' in stem and 'semua' in stem) or 'lebih pintar' in stem
        truth = [('mengarahkan' in option and 'dua klaim' in option) for option in options]
        assert sum(truth) == 1 and ('mengarahkan' in explanation or 'menggiring' in explanation) and ('dua klaim' in explanation or 'menggabungkan' in explanation)
    elif qid == 'mcma-20-4-6':
        target_match = re.search(r'kebiasaan (.+?) (?:pada|siswa)', stem)
        target = target_match.group(1) if target_match else None
        vocabulary = {
            'membaca': ('membaca', 'bacaan', 'buku'),
            'kegiatan membaca': ('membaca', 'bacaan'),
            'latihan olahraga': ('olahraga',), 'penggunaan gawai': ('gawai', 'aplikasi'),
            'kunjungan perpustakaan': ('perpustakaan',), 'sarapan pagi': ('sarapan', 'menu'),
            'perjalanan ke sekolah': ('perjalanan', 'transportasi', 'moda'),
        }
        def target_bound(option):
            return target is None or any(word in option for word in vocabulary[target])
        truth = [(option.startswith(('berapa ', 'apa jenis ', 'jenis ', 'menu ', 'moda ')))
                 and 'malas' not in option and 'wajib' not in option
                 and target_bound(option) for option in options]
        assert sum(truth) == 3 and ('penilaian negatif' in explanation or
                                    all(word in explanation for word in ('durasi', 'jenis', 'frekuensi')))
    elif qid == 'kategori-20-4-10':
        assert stem.count('lebih ') >= 2
        aspects = re.findall(r'lebih ([\w ]+?)(?:,| dan| daripada)', stem)
        assert len(aspects) >= 2, stem
        truth = [('beberapa aspek' in option or 'dipecah menjadi' in option or
                  ('setiap aspek' in option and 'secara terpisah' in option) or
                  ('secara terpisah' in option and aspects[0] in option and aspects[1] in option))
                 and 'sudah netral' not in option for option in options]
        assert sum(truth) == 3 and ('pisahkan aspek' in explanation or 'secara terpisah' in explanation) and 'netral' in explanation
    elif qid == 'pg-20-5-1':
        service = re.search(r'terhadap (.+?)(?:\.| sekolah\.)', stem)
        assert service, stem
        target = service.group(1).replace('fasilitas olahraga sekolah', 'fasilitas olahraga')
        truth = [('tingkat kepuasanmu' in option and target in option and 'sangat tidak puas' in option
                  and 'sangat puas' in option) for option in options]
        assert sum(truth) == 1 and ('skala' in explanation or 'pilihan jawaban' in explanation) and 'jelas' in explanation
    elif qid == 'mcma-20-5-6':
        generated = re.search(r'sekolah akan menyurvei (.+?) pada (.+?)\.', stem)
        target = generated.group(1) if generated else None
        population = generated.group(2) if generated else None
        truth = [('beberapa kelas' in option or 'beberapa tingkat kelas' in option or 'periode yang jelas' in option or
                  'pertanyaan netral' in option) and 'hanya' not in option and
                 'seluruh siswa' not in option and
                 (target is None or target in option) for option in options]
        if generated:
            assert population in options[0]
        assert sum(truth) == 3 and ('netral' in explanation or 'keterwakilan' in explanation) and ('bias' in explanation or 'konsisten' in explanation)
    elif qid == 'kategori-20-5-9':
        generated = re.search(r'terhadap (.+?)\. tentukan', stem)
        target = generated.group(1) if generated else None
        truth = [(('tingkat kepuasan' in option and 'jelas' in option) or
                  ('diagram batang' in option and ('berlabel' in option or 'setiap kategori' in option))) and
                 (target is None or target in option) for option in options]
        assert sum(truth) == 2 and 'bias' in explanation and ('integritas' in explanation or 'objektivitas' in explanation)
    else:
        raise AssertionError(qid)

    rendered = [option['correct'] for option in candidate['options']]
    assert rendered == truth, (qid, rendered, truth, options)
    return truth
