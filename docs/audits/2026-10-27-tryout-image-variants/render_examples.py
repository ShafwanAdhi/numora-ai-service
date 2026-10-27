"""Explicit local review exporter for completed stages 1–2, not a package importer.

Run from the AI repo root: python docs/audits/2026-10-27-tryout-image-variants/render_examples.py
"""
import hashlib
import io
import json
import sys
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'variant_gen'))
from bank import OriginalBank
from config_store import ConfigStore
from engine import build_values, generate
from expr import to_num
from image_variants import build_scene, load_template, render_scene


def json_default(value):
    if isinstance(value, Fraction):
        return {'numerator': value.numerator, 'denominator': value.denominator}
    raise TypeError(type(value).__name__)


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=json_default)+'\n', encoding='utf-8')


def main():
    from PIL import Image, ImageDraw, ImageFont
    output = Path(__file__).resolve().parent
    bank = OriginalBank(ROOT/'variant_gen/data/tryout-1/q0_bank.csv')
    configs = ConfigStore(ROOT/'variant_gen/configs')
    manifest = json.loads((ROOT/'docs/sources/incoming/2026-10-26-tryout-images/image-manifest.json').read_text(encoding='utf-8'))
    sources = {x['candidate_local_question_id']: x for x in manifest['images']}
    records = []
    for qid, stage, name in (('tryout-1-b4-q05',1,'dice'), ('tryout-1-b3-q02',2,'garden'), ('tryout-1-b3-q06',2,'tank')):
        folder = output/f'stage-{stage}'
        folder.mkdir(exist_ok=True)
        t = load_template(qid)
        cfg, config_hash = configs.load(qid)
        original = bank.get(qid)
        panels = [('Source', Image.open(ROOT/'docs/sources/incoming/2026-10-26-tryout-images'/sources[qid]['local_path']).convert('RGB')),
                  ('Clean template', Image.open(io.BytesIO(t.base_bytes)).convert('RGB'))]
        examples = [('original-values', build_values(cfg, lambda key,spec: to_num(cfg['original_values'][key]), check=False), None)]
        for seed in range(1, 21):
            result = generate(original, cfg, seed, [])
            examples.append((f'seed-{seed}', result.values, result.cand))
        if stage == 1:
            examples.extend((f'times-{n}', {'times':n}, None) for n in (72,180,612,720))
        for label, values, candidate in examples:
            rendered = render_scene(t, build_scene(t, values))
            filename = f'{name}-{label}.png'
            (folder/filename).write_bytes(rendered.png_bytes)
            record = {'question_id': qid, 'example': label, 'file': f'stage-{stage}/{filename}',
                      'original_version': original['version'], 'original_hash': original['hash'],
                      'config_version': cfg['config_version'], 'config_hash':config_hash,
                      'raw_values':values, 'candidate':candidate, 'sha256':rendered.sha256,
                      'byte_length':rendered.byte_length, 'scene':asdict(rendered.scene),
                      'provenance':rendered.provenance}
            records.append(record)
            if label in ('original-values','seed-1','seed-20'):
                panels.append((label,Image.open(io.BytesIO(rendered.png_bytes)).convert('RGB')))
        card_width, card_height = t.width+20, t.height+45
        sheet = Image.new('RGB', (card_width*3,card_height*2), '#eef1f4')
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.truetype(io.BytesIO(t.font_bytes), 14)
        for i,(caption,panel) in enumerate(panels):
            x,y = (i%3)*card_width,(i//3)*card_height
            draw.text((x+10,y+8),caption,font=font,fill='black')
            sheet.paste(panel,(x+10,y+32))
        sheet.save(folder/f'{name}-contact-sheet.png')
    save_json(output/'examples.json', {'scope':'LOCAL_RENDERED stages 1–2 only; no R2/database writes',
                                     'examples':records})
    print(f'Wrote {len(records)} review PNGs and 3 contact sheets to {output}')


if __name__ == '__main__':
    main()
