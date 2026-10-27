"""Explicit Stage-2 review artifacts for all five originals and 150 accepted variants.

This is an operator audit, not a runtime exporter, API, or persistence pipeline.
"""
import argparse
import copy
import html
import io
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'variant_gen'))
import cli
from bank import load_workspace_bank
from config_store import ConfigStore
from engine import build_values
from image_variants.templates import sha256
from drill_images import IDS, load_template, preview
from drill_images.adapter import exact_sha


def number(value):
    if type(value) is int or isinstance(value, Fraction): return Fraction(value)
    if not isinstance(value, str) or not re.fullmatch(r'\d+(?:[.,]\d+)*', value):
        raise ValueError('Unexpected number in academic oracle')
    return Fraction(value.replace('.', '').replace(',', '.'))


def mathematical_checks(qid, k, record, values, bound):
    """Independent formulas, not generator expressions or config correctness flags."""
    pi = Fraction(22, 7)
    scale = k+1
    if qid in ('pg-16-4-1', 'pg-16-4-3', 'pg-16-4-4'):
        if qid == 'pg-16-4-1':
            radius, height = bound['radius'], bound['height']
            answer = 2*pi*radius*(radius+height)
            assert bound['wrap'] == 2*pi*radius
        elif qid == 'pg-16-4-3':
            radius, slant = bound['radius'], bound['slant']
            assert slant > radius and bound['angle'] == 360*radius/slant
            answer = 2*pi*radius
        else:
            side, face = bound['side'], bound['face_height']
            assert face > side/2
            answer = side*side + 4*Fraction(side*face, 2)
        correct = [option['id'] for option in record['options']
                   if number(re.match(r'[\d.,]+', option['text']).group()) == answer]
        assert len(correct) == 1 and record['key'] == correct[0]
        return {'independent_answer': str(answer), 'correct_options': correct}
    if qid == 'pg-16-5-3':
        slant, angle = bound['slant'], bound['angle']
        radius = Fraction(angle, 360)*slant
        claim = number(values['v6'])
        assert radius == claim == 5*scale
        assert number(values['v7']) == 2*radius
        assert number(values['v8']) != radius
        assert radius != slant/2 and record['key'] == 'A'
        assert 'radius' not in bound and 'jari-jari alas' not in record.get('image_alt_text', '')
        return {'independent_radius': str(radius), 'arc_over_pi': str(2*radius), 'correct_options': ['A']}
    side, face = bound['side'], bound['face_height']
    height_squared = Fraction(face*face)-Fraction(side*side, 4)
    assert height_squared.denominator == 1
    height = math.isqrt(height_squared.numerator)
    assert height*height == height_squared
    area = side*side + 2*side*face
    truths = [number(values['v7']) == side*side,
              number(values['v8']) == Fraction(side*face, 2),
              number(values['v9']) == height,
              number(values['v10']) == area]
    assert truths == ([True, True, False, True] if k == 0 else [True, True, True, False])
    assert record['key'] == ('D' if k == 0 else 'C')
    return {'base_area': side*side, 'one_triangle_area': str(Fraction(side*face, 2)),
            'true_pyramid_height': height, 'surface_area': area,
            'statement_truths': truths, 'correct_options': [record['key']]}


def geometry_checks(qid):
    spec = json.loads((ROOT / 'variant_gen/image_templates' / qid / 'v1/template.json').read_text(encoding='utf-8'))
    geo = spec['geometry_evidence']
    if qid == 'pg-16-4-1':
        x0, y0, x1, y1 = geo['rectangle']
        assert Fraction(x1-x0, y1-y0) == Fraction(44, 10)
        assert all(c[2] == 70 for c in geo['circles'])
        assert geo['circles'][0][1]+70 == y0 and geo['circles'][1][1]-70 == y1
    elif qid == 'pg-16-4-3':
        assert Fraction(geo['sector_sweep_degrees'], 360)*geo['sector_radius'] == geo['base_circle'][2]
    elif qid == 'pg-16-4-4':
        square = geo['square']
        assert all(math.dist(square[i], square[(i+1) % 4]) == 168 for i in range(4))
        assert len(geo['triangles']) == 4
        for triangle in geo['triangles']:
            a, b, apex = triangle
            assert math.dist(a, apex) == math.dist(b, apex)
            assert math.dist(((a[0]+b[0])/2, (a[1]+b[1])/2), apex) == 140
    else:
        from PIL import Image, ImageChops, ImageDraw
        source_file = geo['source']
        src = ROOT / 'docs/sources/incoming/2026-10-27-indikator-16-19-final-images/media' / source_file
        original = Image.open(src).convert('RGB')
        cleaned = Image.open(ROOT / 'variant_gen/image_templates' / qid / 'v1/cleaned-source.png').convert('RGB')
        diff = ImageChops.difference(original, cleaned)
        mask = Image.new('L', original.size, 0)
        draw = ImageDraw.Draw(mask)
        for polygon in geo['masks']: draw.polygon([tuple(p) for p in polygon], fill=255)
        diff.paste((0, 0, 0), (0, 0), mask)
        assert diff.getbbox() is None
    return {'status': 'PASS', 'kind': geo['kind']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bank-root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/audits/2026-10-27-drill-image-variants/stage-2/review')
    args = parser.parse_args()
    # Existing loader auto-discovers extra banks only beside its own module.
    # Explicitly select this stage's additional bank when auditing another checkout.
    bank = load_workspace_bank(args.bank_root / 'variant_gen/data/q0_bank.csv', additional_paths=[
        args.bank_root / 'variant_gen/data/drill-1-indicators-16-19-levels-4-5/q0_bank.csv'])
    configs = ConfigStore(args.bank_root / 'variant_gen/configs')
    if args.output.exists(): raise ValueError('Refusing to overwrite review evidence')
    args.output.mkdir(parents=True)
    (args.output / 'images').mkdir()
    entries, cards, family_results = [], [], {}

    def retain(qid, k, seed, record, image, raw_values, generator_calls):
        oracle = mathematical_checks(qid, k, record, raw_values, dict(image.scene.bindings))
        from PIL import Image
        with Image.open(io.BytesIO(image.png_bytes)) as png:
            assert png.format == 'PNG' and png.size == (960, 640)
        assert sha256(image.png_bytes) == image.sha256
        for label in image.scene.labels:
            x0, y0, x1, y1 = (coordinate*2 for coordinate in label.box)
            a, b, c, d = label.ink_box
            assert x0 <= a <= c <= x1 and y0 <= b <= d <= y1
        if qid == 'pg-16-5-3':
            texts = {label.id: label.text for label in image.scene.labels}
            assert texts['slant_left'] == texts['slant_right']
            assert 'jari-jari alas' not in image.scene.alt_text.lower()
        assert 'bukan tinggi limas' not in image.scene.alt_text.lower()
        filename = f'images/{qid}-k{k:02d}.png'
        (args.output / filename).write_bytes(image.png_bytes)
        entry = {'question_id': qid, 'k': k, 'seed': seed, 'record': record,
                 'image': {'path': filename, 'sha256': image.sha256, 'width': image.width,
                           'height': image.height, 'alt_text': image.scene.alt_text,
                           'provenance': image.provenance},
                 'independent_math': oracle, 'generator_calls_for_image': generator_calls,
                 'record_unchanged': True, 'label_layout': 'PASS'}
        entries.append(entry)
        key = html.escape(record['key'])
        cards.append(f'<article id="{qid}-k{k}"><h2>{qid} / '+('Original' if k == 0 else f'k={k}, seed={seed}')+
                     f'</h2><img loading="lazy" src="{filename}" width="960" height="640" alt="{html.escape(image.scene.alt_text, quote=True)}">'+
                     f'<p class="stem">{html.escape(record["stem"])}</p><ol type="A">'+
                     ''.join(f'<li>{html.escape(o["text"])}</li>' for o in record['options'])+
                     f'</ol><details><summary>Kunci {key} dan pembahasan</summary><pre>{html.escape(record["explanation"])}</pre></details></article>')

    for qid in IDS:
        geo = geometry_checks(qid)
        original = bank.get(qid)
        config, _ = configs.load(qid)
        original_values = build_values(config, lambda name, spec: config['original_values'][name])
        with patch('cli.generate', side_effect=AssertionError('Original must not draw')):
            record, image = preview(bank, configs, qid, 0)
        retain(qid, 0, 0, record, image, original_values, 0)
        seeds, search_count = {}, 0
        for seed in range(1, 5001):
            captured = []
            def capture(o, c, result, record): captured.append(copy.deepcopy(result))
            baseline = cli.preview(bank, configs, qid, seed, on_generated=capture)
            search_count += 1
            raw = captured[0]
            k = raw.values['k']
            if k in seeds: continue
            before = copy.deepcopy((raw.values, raw.cand, raw.draws_used, raw.rejections))
            with patch('cli.generate', wraps=cli.generate) as generate:
                actual, image = preview(bank, configs, qid, seed)
                assert generate.call_count == 1
            assert before == (raw.values, raw.cand, raw.draws_used, raw.rejections)
            assert {k: v for k, v in baseline.items() if k != 'created_at'} == {
                k: v for k, v in actual.items() if k != 'created_at'}
            assert image.provenance['content']['accepted_raw_values_sha256'] == exact_sha(raw.values)
            seeds[k] = seed
            retain(qid, k, seed, actual, image, raw.values, 1)
            if len(seeds) == 30: break
        assert sorted(seeds) == list(range(1, 31))
        family_results[qid] = {'original': 'PASS', 'accepted_k': sorted(seeds),
                               'seed_by_k': seeds, 'seed_search_draws': search_count,
                               'geometry': geo, 'variants': 30}
    payload = {'stage': 2, 'status': 'LOCAL_REVIEW', 'counts': {'originals': 5, 'variants': 150, 'images': 155},
               'families': family_results, 'entries': entries,
               'notes': ['No runtime/API/UI/exporter integration in this stage.',
                         'Mathematical checks are engineering evidence, not Curriculum/IRT approval.',
                         'All variants used real existing generator seeds; rejected k=0 was not bypassed.']}
    (args.output / 'review.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    doc = ('''<!doctype html><html lang="id"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Review lokal gambar Drill - Tahap 2</title><link rel="icon" href="data:,"><style>*{box-sizing:border-box}body{margin:0;background:#f5f7f8;color:#182b34;font:15px/1.6 system-ui}main{max-width:1080px;margin:auto;padding:24px}article{background:white;margin:24px 0;padding:24px;border:1px solid #d2dde1}h1{font-size:25px}h2{font-size:20px}img{display:block;max-width:100%;height:auto}.stem,pre{white-space:pre-wrap;overflow-wrap:anywhere}details{margin-top:16px}summary{cursor:pointer}a{color:#126a66}nav{display:flex;flex-wrap:wrap;gap:16px}</style><main>
<h1>Review lokal gambar Drill - Tahap 2</h1><p>Lima original dan 150 varian dari generator existing. Untuk review operator; bukan publikasi siswa.</p>'''+
        '<nav>'+''.join(f'<a href="#{qid}-k0">{qid}</a>' for qid in IDS)+'</nav>'+''.join(cards)+'</main></html>')
    (args.output / 'preview.html').write_text(doc, encoding='utf-8')
    summary = {'stage': 2, 'status': 'PASS', 'originals': 5, 'accepted_variants': 150,
               'real_seed_coverage': True, 'mathematical_checks': 155, 'geometry_checks': 5,
               'identical_generator_record_checks': 150, 'label_layout_checks': 155,
               'families': family_results,
               'files_sha256': {p.relative_to(args.output).as_posix(): sha256(p.read_bytes())
                                for p in sorted(args.output.rglob('*')) if p.is_file()}}
    (args.output.parent / 'domain-verification.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: summary[k] for k in summary if k not in ('families', 'files_sha256')}, indent=2))


if __name__ == '__main__': main()
