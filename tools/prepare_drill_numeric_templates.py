"""Explicit build-time preparation of five assets. Never called by question generation.

Two cleaned raster inputs come from the image_gen edit tool. Only reviewed masks
are composited into the original illustration; other source pixels are preserved.
Three new nets are drawn as deterministic geometry in code. No random numbers.
"""
import argparse
import io
import json
import math
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'variant_gen'))
from image_variants.templates import sha256

SOURCE = ROOT / 'docs/sources/incoming/2026-10-27-indikator-16-19-final-images'
OUTPUT = ROOT / 'variant_gen/image_templates'
AUDIT = ROOT / 'docs/audits/2026-10-27-drill-image-variants/stage-2/asset-preparation'
SCALE = 2
INK = '#263d48'
BLUE = '#d6e9f2'
GREEN = '#e0eee5'


def save_png(image):
    stream = io.BytesIO()
    image.save(stream, format='PNG', compress_level=9, optimize=False)
    return stream.getvalue()


def start_canvas():
    image = Image.new('RGB', (960*SCALE, 640*SCALE), 'white')
    return image, ImageDraw.Draw(image)


def points(values):
    return [(round(x*SCALE), round(y*SCALE)) for x, y in values]


def line(draw, values, fill=INK, width=2):
    draw.line(points(values), fill=fill, width=width*SCALE)


def arrow(draw, first, second):
    line(draw, [first, second])
    angle = math.atan2(second[1]-first[1], second[0]-first[0])
    ends = [(second[0]-9*math.cos(angle-d), second[1]-9*math.sin(angle-d)) for d in (-.4, .4)]
    draw.polygon(points([second, *ends]), fill=INK)


def dashed(draw, first, second):
    length = math.dist(first, second)
    for start in range(0, math.ceil(length), 12):
        fractions = (start/length, min(start+7, length)/length)
        line(draw, [(first[0]+t*(second[0]-first[0]), first[1]+t*(second[1]-first[1]))
                    for t in fractions], fill='#6b8490', width=1)


def finish(image):
    return image.resize((960, 640), Image.Resampling.LANCZOS)


def native_net(qid):
    image, draw = start_canvas()
    geometry = {}
    if qid == 'pg-16-4-1':
        draw.rectangle((520, 540, 1400, 740), fill=BLUE, outline=INK, width=4)
        for cx, cy in ((480, 200), (480, 440)):
            draw.ellipse(((cx-70)*2, (cy-70)*2, (cx+70)*2, (cy+70)*2),
                         fill=GREEN, outline=INK, width=4)
        arrow(draw, (480, 200), (550, 200))
        for y in (270, 370): line(draw, [(710, y), (730, y)])
        arrow(draw, (720, 270), (720, 370)); arrow(draw, (720, 370), (720, 270))
        geometry = {'kind': 'cylinder-net', 'rectangle': [260, 270, 700, 370],
                    'circles': [[480, 200, 70], [480, 440, 70]],
                    'reference_radius': 7, 'reference_height': 10, 'units_per_cm': 10,
                    'pi_for_question': [22, 7]}
    elif qid == 'pg-16-4-3':
        draw.pieslice((300, 160, 1100, 960), start=-36, end=216, fill=BLUE, outline=INK, width=4)
        draw.ellipse((1240, 540, 1800, 1100), fill=GREEN, outline=INK, width=4)
        arrow(draw, (760, 410), (900, 410))
        line(draw, [(440, 215), (480, 140)], width=1)
        geometry = {'kind': 'cone-net', 'sector_center': [350, 280], 'sector_radius': 200,
                    'sector_start_degrees': -36, 'sector_sweep_degrees': 252,
                    'base_circle': [760, 410, 140], 'reference_radius': 14,
                    'reference_slant': 20, 'units_per_cm': 10}
    elif qid == 'pg-16-4-4':
        square = [(396, 236), (564, 236), (564, 404), (396, 404)]
        draw.polygon(points(square), fill=GREEN)
        triangles = [[square[0], square[1], (480, 96)],
                     [square[1], square[2], (704, 320)],
                     [square[2], square[3], (480, 544)],
                     [square[3], square[0], (256, 320)]]
        for triangle in triangles:
            draw.polygon(points(triangle), fill=BLUE)
            line(draw, [*triangle, triangle[0]])
        for i in range(4): dashed(draw, square[i], square[(i+1) % 4])
        arrow(draw, (564, 320), (704, 320))
        line(draw, [(564, 306), (578, 306), (578, 320)], width=1)
        geometry = {'kind': 'square-pyramid-net', 'square': square,
                    'triangles': triangles, 'face_altitude': [[564, 320], [704, 320]],
                    'reference_side': 12, 'reference_face_height': 10, 'units_per_cm': 14}
    else:
        raise ValueError(qid)
    return finish(image), geometry


def preserve_art(source_name, edited_path, masks, offset):
    source_bytes = (SOURCE / 'media' / source_name).read_bytes()
    original = Image.open(io.BytesIO(source_bytes)).convert('RGB')
    edited = Image.open(edited_path).convert('RGB').resize(original.size, Image.Resampling.LANCZOS)
    mask = Image.new('L', original.size, 0)
    draw = ImageDraw.Draw(mask)
    for polygon in masks: draw.polygon(polygon, fill=255)
    cleaned = original.copy()
    cleaned.paste(edited, (0, 0), mask)
    canvas = Image.new('RGB', (960, 640), 'white')
    canvas.paste(cleaned, offset)
    return canvas, cleaned, {'source': source_name, 'source_sha256': sha256(source_bytes),
                            'edited_input_sha256': sha256(edited_path.read_bytes()),
                            'masks': masks, 'offset': offset,
                            'outside_mask_preserved': True}


def label(identity, text, box, size=22):
    return {'id': identity, 'text': text, 'box': box, 'font_size': size, 'min_font_size': 14}


def build(cone_clean, pyramid_clean):
    inventory_bytes = (SOURCE / 'image-inventory.json').read_bytes()
    inventory = json.loads(inventory_bytes)
    families = {
        'pg-16-4-1': ('Jaring-jaring tabung', [('radius', 'v0', 7), ('height', 'v1', 10)],
            [{'name': 'radius'}, {'name': 'height'}, {'name': 'wrap', 'expr': '44*radius/7'}],
            ['radius*10==height*7', 'wrap==44*radius/7'],
            [label('radius', 'r = {radius} cm', [550, 165, 800, 205]),
             label('height', 'tinggi = {height} cm', [745, 290, 950, 350], 20),
             label('wrap_symbol', 'panjang = 2πr', [310, 300, 650, 340], 22)],
            'Jaring-jaring tabung: dua lingkaran berjari-jari {radius} cm dan persegi panjang dengan tinggi {height} cm. Gambar skematis.'),
        'pg-16-4-3': ('Jaring-jaring kerucut', [('radius', 'v0', 14), ('slant', 'v1', 20)],
            [{'name': 'radius'}, {'name': 'slant'}, {'name': 'angle', 'expr': '360*radius/slant'}],
            ['slant>radius', 'angle==252'],
            [label('slant', 's = {slant} cm', [285, 100, 485, 140]),
             label('radius', 'r = {radius} cm', [700, 345, 910, 390])],
            'Jaring-jaring kerucut terdiri dari juring dengan jari-jari s = {slant} cm dan lingkaran dengan r = {radius} cm. Gambar skematis.'),
        'pg-16-4-4': ('Jaring-jaring limas segi empat', [('side', 'v0', 12), ('face_height', 'v1', 10)],
            [{'name': 'side'}, {'name': 'face_height'}], ['side*5==face_height*6'],
            [label('side', 'sisi = {side} cm', [400, 275, 560, 315], 18),
             label('face_height', 'tinggi segitiga\n{face_height} cm', [715, 275, 950, 350], 20)],
            'Jaring-jaring limas segi empat: alas persegi bersisi {side} cm dan empat segitiga dengan tinggi masing-masing {face_height} cm. Gambar skematis.'),
        'pg-16-5-3': ('Jaring-jaring kerucut', [('slant', 'v0', 12)],
            [{'name': 'slant'}, {'name': 'angle', 'expr': '150'}], ['angle==150'],
            [label('slant_left', 's = {slant} cm', [245, 85, 410, 120], 20),
             label('slant_right', 's = {slant} cm', [535, 110, 745, 150], 20)],
            'Jaring-jaring kerucut berupa juring dengan dua sisi s = {slant} cm dan sudut pusat {angle} derajat, serta sebuah lingkaran tanpa ukuran. Gambar skematis.'),
        'pg-16-5-5': ('Jaring-jaring limas segi empat', [('side', 'v2', 10), ('face_height', 'v4', 13)],
            [{'name': 'side'}, {'name': 'face_height'}], ['side*13==face_height*10'],
            [label('side', 'sisi alas persegi = {side} cm', [550, 165, 950, 210], 20),
             label('face_height', 'tinggi segitiga\n{face_height} cm', [570, 280, 945, 350], 22)],
            'Jaring-jaring limas segi empat: sisi alas persegi {side} cm, tinggi segitiga sisi tegak {face_height} cm. Gambar skematis.'),
    }
    for qid in families:
        if (OUTPUT / qid).exists(): raise ValueError('Refusing to overwrite an existing template: ' + qid)
    AUDIT.mkdir(parents=True, exist_ok=False)
    for name, path in [('cone-clean-output.png', cone_clean), ('pyramid-clean-output.png', pyramid_clean)]:
        shutil.copyfile(path, AUDIT / name)
    preparation = {}
    for qid, (title, dimensions, bindings, constraints, labels, alt) in families.items():
        folder = OUTPUT / qid / 'v1'
        folder.mkdir(parents=True)
        extra_files = {}
        if qid == 'pg-16-5-3':
            masks = [[(43, 95), (150, 34), (166, 62), (60, 121)],
                     [(345, 58), (459, 119), (447, 141), (335, 80)],
                     [(348, 24), (365, 24), (365, 39), (348, 39)],
                     [(453, 157), (463, 157), (463, 174), (453, 174)]]
            base, clean, info = preserve_art('image6.png', cone_clean, masks, (200, 75))
            extra_files['cleaned-source.png'] = save_png(clean)
            preparation[qid] = info
            geometry = {'kind': 'source-illustration', 'fixed_angle_degrees': 150,
                        'scale_relation': 'uniform similarity; labels only', **info}
        elif qid == 'pg-16-5-5':
            masks = [[(246, 43), (385, 43), (385, 64), (246, 64)],
                     [(288, 204), (472, 204), (472, 229), (288, 229)]]
            base, clean, info = preserve_art('image14.jpg', pyramid_clean, masks, (80, 150))
            extra_files['cleaned-source.png'] = save_png(clean)
            preparation[qid] = info
            # The label for face altitude points to the horizontal altitude,
            # not the unrelated slanted dimension arrow in the old illustration.
            draw = ImageDraw.Draw(base)
            # Connect to the existing leader endpoint rather than drawing across the net.
            draw.line([(555, 187), (339, 215)], fill=INK, width=1)
            draw.line([(570, 310), (390, 305)], fill=INK, width=1)
            geometry = {'kind': 'source-illustration', 'face_altitude_target': [390, 305],
                        'base_side_target': [254, 253], 'scale_relation': 'uniform similarity', **info}
        else:
            base, geometry = native_net(qid)
        base_bytes = save_png(base)
        pin = inventory['family_pins'][qid]
        cfg = pin['configs'][0]
        from drill_images.templates import snapshot_sha
        compatibility = {'original_version': pin['original_version'], 'original_hash': pin['original_hash'],
            'original_full_sha256': pin['original_full_sha256'], 'config_version': cfg['version'],
            'config_hash': cfg['config_hash'], 'config_snapshot_sha256': snapshot_sha(cfg['config_snapshot']),
            'config_file_sha256': cfg['file_sha256']}
        asset = next(a for a in inventory['assets'] if a['question_id'] == qid)
        spec = {'schema_version': 1, 'question_id': qid, 'template_version': 1,
            'renderer': 'labels-v1', 'canvas': [960, 640], 'compatibility': compatibility,
            'source_inventory_sha256': sha256(inventory_bytes), 'source_sha256': asset['sha256'],
            'base_sha256': sha256(base_bytes),
            'font_sha256': sha256((OUTPUT / 'fonts/DejaVuSans.ttf').read_bytes()),
            'dimensions': [{'alias': alias, 'variable': variable, 'original': value}
                           for alias, variable, value in dimensions],
            'original_bindings': {alias: value for alias, _, value in dimensions},
            'bindings': bindings, 'constraints': constraints,
            'labels': [label('title', title, [20, 20, 940, 70], 25), *labels,
                       label('schematic', 'Gambar skematis, tidak berskala.', [20, 590, 940, 630], 16)],
            'alt_text': alt, 'geometry_evidence': geometry,
            'prepared_asset_sha256': {name: sha256(data) for name, data in extra_files.items()}}
        (folder / 'base.png').write_bytes(base_bytes)
        for name, data in extra_files.items(): (folder / name).write_bytes(data)
        (folder / 'template.json').write_text(json.dumps(spec, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (AUDIT / 'preparation.json').write_text(json.dumps({'mode': 'built-in-image_gen edits plus deterministic geometry',
        'notes': ['image_gen only prepared two blank-label inputs; no image model runs at question generation time.',
                  'All source pixels outside recorded cleanup masks are preserved before canvas placement.',
                  'Three corrected nets are repo-native geometry; no question config is edited.'],
        'preserved_illustrations': preparation}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cone-clean', required=True, type=Path)
    parser.add_argument('--pyramid-clean', required=True, type=Path)
    args = parser.parse_args()
    build(args.cone_clean, args.pyramid_clean)
