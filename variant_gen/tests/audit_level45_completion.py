"""Exhaustive evidence for the remaining 67 and their strict draft/live boundary."""
import csv
import hashlib
import json
import re
from collections import Counter
from copy import deepcopy
from pathlib import Path

from level45_completion_common import ROOT, REPO, LIVE_DATA, DRAFT_DATA, key
from build_level45_completion import prepare_all, modules
from bank import OriginalBank, load_workspace_bank
from config_store import ConfigStore, validate_config, ConfigError
from engine import build_values, assemble, generate
from expr import RejectDraw
from filters import validate_candidate, signature
from lint import reproduce_original

OUTPUT=REPO/'docs/audits/2026-10-20-drill-1-5-level45-completion'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def write_review_documents(report):
    summary, findings = report['summary'], report['entries']
    lines = [
        '# Penyelesaian generator indikator 1-5 level 4-5', '', 'Dilanjutkan dan diverifikasi 21 Oktober 2026; nama folder mempertahankan tanggal awal pekerjaan.', '',
        '**ENGINEERING DECISION - instruksi pengguna:** selesaikan 67 soal setelah tahap pertama 33 soal. '
        'Untuk 28 soal dengan temuan akademik, siapkan usulan koreksi dan generator terpisah untuk review; belum aktif.', '',
        '**Cakupan 100 keluarga: 72 generator lokal dan 28 generator draf terkarantina.** '
        'Tahap ini menambah 39 generator lokal dan 28 draf. Tidak ada publikasi atau perubahan database.', '',
        '| Indikator | Generator lokal baru | Generator draf |',
        '|---|---:|---:|',
    ]
    for indicator in range(1,6):
        rows = [f for f in findings if f['indicator']==indicator]
        lines.append(f"| {indicator} | {sum(not f['review_only'] for f in rows)} | {sum(f['review_only'] for f in rows)} |")
    lines += [
        '', '## Pemisahan dan versi', '',
        '- Bank tambahan lokal: `variant_gen/data/drill-1-indicators-1-5-levels-4-5-batch2/`. '
        '39 original v1 memakai config v1. Posisi tetap `DRILL / drill-1 / indikator / level / nomor sumber`; '
        'katalog tahap pertama dan kedua digabung berdasarkan kelompok yang sama, lalu diurutkan menurut nomor sumber.',
        '- Draf: `variant_gen/drafts/2026-10-20-level45-academic/`. '
        '28 usulan original v2 dan config v1 tidak dimuat oleh bank atau config default. '
        '`HOLD_SOURCE`, `review_only=true`, `approval_status=PROPOSED_NOT_APPROVED`; '
        'generate langsung tetap ditolak. Audit memakai salinan sementara di memori untuk memeriksa matematikanya.',
        '- `proposed_corrections.json` menyimpan isi sumber v1, isi usulan v2, perubahan setiap komponen, '
        'temuan audit awal dan alasan koreksi. Ini usulan review, bukan revisi Kurikulum yang telah disetujui.',
        '- 33 original/config tahap pertama dan aset pekerjaan indikator 6-10 yang sudah ada dipertahankan. '
        'Angka pada laporan tahap pertama adalah snapshot historis. Tiga aset bank indikator 11-15/stok dan kode terkait berubah oleh pekerjaan lain selama jeda; manifest resume mencatat hash sebelum/sesudahnya. Klaim hash tetap sama berlaku sejak snapshot resume ini.',
        '', '## Bukti verifikasi', '',
        f"- {summary['exhaustive_parameter_tuples']} kombinasi parameter diperiksa menyeluruh, termasuk nilai original. "
        'Oracle terpisah menghitung dari teks soal yang sudah dirender; tidak membaca nilai tersembunyi generator.',
        f"- Kapasitas efektif gabungan keluarga baru: {summary['exact_new_family_variant_capacity']} varian; "
        f"minimum {summary['min_family_capacity']} per keluarga. Setiap keluarga memiliki sedikitnya 20 masukan matematis berbeda "
        'di bagian inti stimulus. Label tambahan tidak dihitung sebagai perubahan matematika.',
        f"- {summary['unique_samples']} sampel unik (20 per keluarga) dan {summary['additional_deterministic_samples']} "
        'sampel seed 201-250 diperiksa; pemanggilan ulang seed yang sama harus identik.',
        f"- Hash {summary['protected_prior_files']} aset sebelumnya tetap sama. "
        'Baseline, hash sumber, original/config, rentang deklaratif dan efektif, penolakan serta contoh tersedia dalam JSON.',
        '- Tes meliputi reproduksi original, mutasi kunci dan pembahasan, penggabungan paket, urutan sumber, '
        'serta pemisahan draf dari katalog dan generate workbench tanpa database/penyimpanan hasil.',
        '', '## Batas persetujuan', '',
        '**PROPOSED:** seluruh rentang dan keluarga varian baru belum mendapat persetujuan Kurikulum atau kalibrasi IRT. '
        'Generator lokal memakai `NOT_CURRICULUM_APPROVED`; draf memakai `PROPOSED_NOT_APPROVED`. '
        '`self_adjustment_enabled=false`. Tidak memperluas batas generator lama secara otomatis. '
        'Perubahan angka maupun penerapan konsep dapat mengubah beban pengerjaan; label level sumber bukan bukti kesetaraan kesulitan.',
        '', '## Berkas review dan reproduksi', '',
        '- [JSON lengkap, hash, rentang dan contoh](audit.json)',
        '- [Semua 67 keluarga](entries.csv)',
        '- [39 generator lokal baru](local-generators.csv)',
        '- [28 generator draf](academic-drafts.csv)',
        '- [Ringkasan perubahan dan alasan koreksi](correction-review.csv)',
        '- [Usulan koreksi sebelum/sesudah](../../../variant_gen/drafts/2026-10-20-level45-academic/proposed_corrections.json)',
        '', '```powershell',
        'python -B variant_gen/tests/build_level45_completion.py',
        'python -B variant_gen/tests/audit_level45_completion.py',
        'python -B -m unittest discover -s variant_gen/tests -p "test_level45*.py" -v',
        'python -B -m unittest discover -s variant_gen/tests -v',
        'python -B -m unittest discover -s tests/service -v',
        '```', '',
        'Builder adalah penyusunan aset offline yang belum dirilis. Jangan menjalankannya untuk menimpa versi yang sudah digunakan; '
        'revisi berikutnya harus membuat versi baru. Audit membaca manifest masukan `resume-2026-10-21-baseline.json` yang dibekukan sebelum build; tidak memakai `.scratch` atau keluarannya sendiri sebagai baseline.', '',
    ]
    (OUTPUT/'README.md').write_text('\n'.join(lines),encoding='utf-8')
    (DRAFT_DATA/'README.md').write_text(
        '# Draf koreksi dan generator: belum aktif\n\n'
        '28 usulan original v2/config v1 ini hanya untuk review. Sumber asli dan perubahan per komponen '
        'tersimpan dalam [proposed_corrections.json](proposed_corrections.json). '
        'Bank dan config default tidak memuat direktori ini. Status HOLD_SOURCE menolak generate; '
        'tes dan audit memakai salinan sementara di memori. Jangan menyalin config ke direktori runtime sebelum koreksi dan varian disetujui.\n\n'
        '[Bukti audit](../../../docs/audits/2026-10-20-drill-1-5-level45-completion/README.md). '
        'Penyesuaian otomatis tetap nonaktif.\n',encoding='utf-8')


def audit():
    workspace=load_workspace_bank(ROOT/'data/q0_bank.csv')
    held=OriginalBank(DRAFT_DATA/'q0_bank.csv')
    prepared=prepare_all()
    findings=[]
    for p in prepared:
        e=p['entry'];qid=key(e);draft=p['draft']
        original=held.get(qid) if draft else workspace.get(qid)
        root=DRAFT_DATA/'configs' if draft else ROOT/'configs'
        cfg,cfg_hash=ConfigStore(root).load(qid)
        if draft:
            assert qid not in workspace.ids()
            assert not ConfigStore(ROOT/'configs').versions(qid)
            assert original['metadata']['generation_status']=='HOLD_SOURCE'
            assert validate_config(cfg,original)
            try:generate(original,cfg,1,[])
            except ConfigError:pass
            else:raise AssertionError('Draft unexpectedly executable without review sandbox')
        sandbox=deepcopy(original)
        if draft:sandbox['metadata']['generation_status']='ACTIVE'
        assert not validate_config(cfg,sandbox),qid
        assert reproduce_original(sandbox,cfg)==([],[]),qid
        _,oracle=modules(e['indicator'])
        spec=cfg['variables']['k']
        domain=spec['values'] if spec['gen']=='choice' else list(range(spec['range'][0],spec['range'][1]+1,spec.get('step',1)))
        inputs=[];sigs=set();core_math=set();rejected=Counter()
        for k in domain:
            try:values=build_values(cfg,lambda name,spec:k)
            except RejectDraw as exc:
                rejected[str(exc)]+=1;continue
            candidate=assemble(cfg,values)
            oracle.check_math(qid,candidate)
            errors=validate_candidate(candidate,sandbox,[])
            if errors:rejected.update(errors);continue
            inputs.append(k);sigs.add(signature(candidate['stem'],candidate['options']))
            # Ignore any appended serial/annotation; varied data must be in the task itself.
            core_math.add(tuple(re.findall(r'-?\d+(?:[.,]\d+)*',candidate['stem'][:len(sandbox['stem'])])))
        assert len(sigs)>=20,(qid,len(sigs))
        assert len(core_math)>=20,(qid,'Insufficient distinct mathematical input',len(core_math))
        made=[];samples=[]
        for seed in range(1,21):
            r=generate(sandbox,cfg,seed,made)
            oracle.check_math(qid,r.cand);made.append(r.cand)
            samples.append(dict(seed=seed,k=r.values['k'],candidate=r.cand,
                review_only=draft,approval_status='PROPOSED_NOT_APPROVED' if draft else 'NOT_CURRICULUM_APPROVED'))
        for seed in range(201,251):
            a=generate(sandbox,cfg,seed,[]);b=generate(sandbox,cfg,seed,[])
            assert a.cand==b.cand and a.values==b.values
            oracle.check_math(qid,a.cand)
        findings.append(dict(question_id=qid,indicator=e['indicator'],level=e['level'],source_number=e['source_number'],
            mode='QUARANTINED_DRAFT' if draft else 'LOCAL_GENERATOR',format=e['source_projection']['format'],
            runtime_active=not draft,review_only=draft,self_adjustment_enabled=False,
            approval_status=original['metadata']['approval_status'],source_audit_id=e['audit_id'],
            source_location=e['source'],source_sha256=p['source']['source']['sha256'],
            source_projection_sha256=content_sha(p['source']['source_projection']),
            proposed_projection_sha256=content_sha(e['source_projection']),
            original_hash=original['hash'],original_version=original['version'],config_version=cfg['config_version'],
            config_hash=cfg_hash,config_sha256=sha(root/qid/'v1.json'),config_path=str((root/qid/'v1.json').relative_to(REPO)),
            declared_k=list(domain),effective_k=inputs,rejection_counts=dict(rejected),
            exact_variant_capacity=len(sigs),distinct_core_numeric_inputs=len(core_math),unique_samples=20,additional_deterministic_seeds=[201,250],
            academic_issues=p['source']['academic'],correction_rationale=p['reasons'],component_changes=p['changes'],samples=samples))
    baseline=OUTPUT/'resume-2026-10-21-baseline.json'
    before=json.loads(baseline.read_text(encoding='utf-8'))['files']
    allowed={'docs/README.md','variant_gen/bank.py','readme.md','docs/GENERATOR.md','variant_gen/README.md',
        'tests/service/test_api.py','tests/service/test_content.py','variant_gen/tests/test_drill_1_2.py',
        'variant_gen/tests/test_drill_3_5.py','variant_gen/tests/test_drill_6_10.py','variant_gen/tests/test_drill_11_15.py',
        'variant_gen/tests/test_drill_20_23.py','variant_gen/tests/test_webui.py',
        'variant_gen/tests/test_drill_1_5_level45_batch1.py'}
    changed=[p for p,h in before.items() if not (REPO/p).exists() or sha(REPO/p)!=h]
    assert not set(changed)-allowed,('Unexpected change to previous work',set(changed)-allowed)
    protected={p:h for p,h in before.items() if p.startswith(('variant_gen/data/','variant_gen/configs/',
        'docs/sources/','docs/audits/','numora_service/','contracts/'))}
    assert all(sha(REPO/p)==h for p,h in protected.items())
    by_id={f['question_id']:f for f in findings}
    live_ids={f['question_id'] for f in findings if not f['review_only']}
    draft_ids={f['question_id'] for f in findings if f['review_only']}
    assert len(live_ids)==39 and len(draft_ids)==28
    # The previous batch is an immutable, independently verified source of evidence.
    prior_path=REPO/'docs/audits/2026-10-20-drill-1-5-level45-batch1/audit.json'
    prior=json.loads(prior_path.read_text(encoding='utf-8'))
    prior_ids={p['question_id'] for p in prior['entries']}
    assert len(prior_ids)==33 and not prior_ids & by_id.keys()
    for p in prior['entries']:assert sha(ROOT/'configs'/p['question_id']/'v1.json')==p['config_sha256']
    assert len(prior_ids|live_ids|draft_ids)==100
    summary=dict(date='2026-10-21',started_date='2026-10-20',target=100,previous_generators=33,new_local_generators=39,
        quarantined_draft_generators=28,covered_families=100,local_generator_total=72,
        awaiting_curriculum_review=28,self_adjustment_enabled=False,
        exhaustive_parameter_tuples=sum(len(f['declared_k']) for f in findings),
        exact_new_family_variant_capacity=sum(f['exact_variant_capacity'] for f in findings),
        min_family_capacity=min(f['exact_variant_capacity'] for f in findings),
        unique_samples=67*20,additional_deterministic_samples=67*50,
        workspace_originals=len(workspace.ids()),runtime_configs=len(list((ROOT/'configs').glob('*/v1.json'))),
        quarantined_configs=len(list((DRAFT_DATA/'configs').glob('*/v1.json'))),
        protected_prior_files=len(protected),protected_prior_files_unchanged=True,
        source_numbering_preserved=True,quarantine_boundary_verified=True)
    report=dict(summary=summary,previous_batch_audit_path=str(prior_path.relative_to(REPO)),
        previous_batch_audit_sha256=sha(prior_path),
        baseline_manifest_path=str(baseline.relative_to(REPO)),baseline_manifest_sha256=sha(baseline),
        prior_workspace_baseline=before,
        protected_baseline=protected,changed_prior_files=changed,entries=findings)
    OUTPUT.mkdir(parents=True,exist_ok=True)
    write_review_documents(report)
    report['artifact_hashes']={str(p.relative_to(REPO)):sha(p) for directory in [LIVE_DATA,DRAFT_DATA]
        for p in directory.rglob('*') if p.is_file() and '__pycache__' not in str(p)}
    (OUTPUT/'audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    keys=['question_id','indicator','level','source_number','mode','runtime_active','original_version',
          'config_version','exact_variant_capacity','approval_status','config_path']
    for filename,items in [('entries.csv',findings),('local-generators.csv',[f for f in findings if not f['review_only']]),
                           ('academic-drafts.csv',[f for f in findings if f['review_only']])]:
        with (OUTPUT/filename).open('w',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
            writer.writerows({k:row[k] for k in keys} for row in items)
    with (OUTPUT/'correction-review.csv').open('w',encoding='utf-8',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=['question_id','changed_components','source_key',
            'proposed_key','rationale','approval_status'])
        writer.writeheader()
        for proposal in prepared:
            if not proposal['draft']:
                continue
            writer.writerow(dict(question_id=key(proposal['entry']),
                changed_components=','.join(proposal['changes']),
                source_key=','.join(proposal['source']['source_projection']['key']),
                proposed_key=','.join(proposal['entry']['source_projection']['key']),
                rationale=' | '.join(proposal['reasons']),approval_status='PROPOSED_NOT_APPROVED'))
    print(json.dumps(summary,indent=2))
    return report


if __name__=='__main__':audit()
