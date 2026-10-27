"""Extract only held revisions. Run with --check to verify without writing."""

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from xml.dom import minidom
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PENDING = REPO / 'docs/audits/2026-10-21-all-indicators-progress-after-indicator20/pending.csv'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
FILES = {'indikator1-5_final.docx': 2, 'indikator6-10_final.docx': 1,
         'indikator20-23_final.docx': 13}


def text(node):
    if node.nodeType == node.TEXT_NODE:
        return node.data
    return ''.join(text(child) for child in node.childNodes)


def document(path):
    with ZipFile(path) as archive:
        dom = minidom.parseString(archive.read('word/document.xml'))
    return dom, dom.getElementsByTagNameNS(W, 'body')[0]


def select(path, targets):
    dom, body = document(path)
    indicator = level = previous = 0
    continuous = path.name.startswith('indikator20')
    if continuous:
        indicator = 19
    active = None
    blocks = {}
    for node in body.childNodes:
        if node.nodeType != node.ELEMENT_NODE:
            continue
        value = text(node).strip()
        mi = re.match(r'^indikator\s*(\d+)\s*[:.]', value, re.I)
        ml = re.match(r'^(?:[A-Z]\.\s*)?level\s*([1-5])', value, re.I)
        mq = re.match(r'^soal\s*(\d+)\b', value, re.I)
        section = re.match(r'^[IVX]+\.\s*(?:Pilihan|PG|Soal)', value, re.I)
        if mi or ml or mq or section:
            active = None
        if mi and not continuous:
            indicator = int(mi[1])
        if ml:
            level = int(ml[1])
        if mq:
            number = int(mq[1])
            if continuous:
                if number == 1 and previous != 1:
                    indicator += 1
                previous = number
                level, question = (number - 1) // 10 + 1, (number - 1) % 10 + 1
            else:
                question = number
            active = targets.get((indicator, level, question))
            if active:
                assert active not in blocks, f'Duplicate question: {active}'
                blocks[active] = []
        if active and node.localName != 'sectPr':
            blocks[active].append(node)
    return dom, body, blocks


def digest(nodes):
    return hashlib.sha256(''.join(node.toxml() for node in nodes).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--source-dir', type=Path, default=Path.home() / 'Downloads')
    args = parser.parse_args()
    with PENDING.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 16 and all(row['mode'] == 'held' for row in rows)
    targets = {(int(row['indicator']), int(row['level']), int(row['question_id'].rsplit('-', 1)[1])):
               row['question_id'] for row in rows}
    manifest = {'status': 'HOLD', 'purpose': 'Source revisions only; active bank unchanged',
                'unresolved_conflicts': ['kategori-21-4-9', 'kategori-21-4-10', 'pg-22-4-3'],
                'files': []}
    seen = set()
    for filename, expected in FILES.items():
        source = args.source_dir / filename
        output = HERE / filename.replace('_final.docx', '_held-only.docx')
        dom, body, blocks = select(source, targets)
        assert len(blocks) == expected, (filename, list(blocks))
        assert not seen.intersection(blocks)
        seen.update(blocks)
        keep = {id(node) for nodes in blocks.values() for node in nodes}
        if not args.check:
            for node in list(body.childNodes):
                if id(node) not in keep and not (node.nodeType == node.ELEMENT_NODE and node.localName == 'sectPr'):
                    body.removeChild(node)
            with ZipFile(source) as original, ZipFile(output, 'w') as selected:
                for item in original.infolist():
                    selected.writestr(item, dom.toxml(encoding='UTF-8') if item.filename == 'word/document.xml'
                                      else original.read(item.filename))
        _, selected_body = document(output)
        actual = [node for node in selected_body.childNodes
                  if node.nodeType == node.ELEMENT_NODE and node.localName != 'sectPr']
        wanted = [node for nodes in blocks.values() for node in nodes]
        assert [node.toxml() for node in actual] == [node.toxml() for node in wanted], filename
        assert sum(bool(re.match(r'^soal\s*\d+\b', text(node).strip(), re.I)) for node in actual) == expected
        manifest['files'].append({'source': filename, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                                  'extracted': output.name,
                                  'questions': [{'id': key, 'status': 'HOLD', 'xml_sha256': digest(nodes)}
                                                for key, nodes in blocks.items()]})
        print(f'{filename}: {expected} questions; source XML, tables and math preserved')
    assert seen == set(targets.values())
    manifest_path = HERE / 'manifest.json'
    if args.check:
        assert json.loads(manifest_path.read_text(encoding='utf-8')) == manifest
    else:
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Verified: 16 held revisions (2 + 1 + 13); no other question body included')


if __name__ == '__main__':
    main()
