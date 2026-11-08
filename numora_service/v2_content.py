"""V2 media references are compute artifacts, never storage credentials or URLs."""
from copy import deepcopy
import re

from .content import fingerprint, payload, record_content, source_content
from .contracts import validate as validate_v1
from .errors import ServiceError
from .mapping_audit import media_assets

def strip_legacy_image(text):
    # Exact DOCX extraction representation; never remove arbitrary URLs/HTML.
    return re.sub(r'!\[Source image rId\d+\]\(media/image\d+\.(?:png|jpg)\)\s*', '', text)

def local_record(record):
    record=deepcopy(record)
    record['stem']=strip_legacy_image(record['stem'])
    return record


def normalized_source(source):
    row = deepcopy(source)
    assets = media_assets(row.get('media'))
    ids = [a.get('assetId') for a in assets]
    if len(set(ids)) != len(ids) or any(not isinstance(i, str) for i in ids):
        raise ServiceError('SOURCE_MEDIA_INVALID')
    for field in ['stem', 'explanation']:
        content = row.get(field, {})
        markers = re.findall(r'\[\[asset:([^\]]+)\]\]', content.get('text', ''))
        if not set(markers) <= set(ids) or not set(content.get('assetKeys', [])) <= set(ids):
            raise ServiceError('SOURCE_MEDIA_INVALID')
        content['text'] = strip_legacy_image(re.sub(r'\[\[asset:[^\]]+\]\]\s*', '', content.get('text', '')))
        content.pop('assetKeys', None)
    row['media'] = []
    return row


def source_fingerprint(source):
    # Pin the actual canonical media and explanation, independently of local source hash.
    return fingerprint({**source_content(normalized_source(source)),
                        'sourceStem': source['stem'], 'explanation': source['explanation'], 'media': media_assets(source.get('media'))})


def validate_payload(value):
    import json
    from pathlib import Path
    from jsonschema import Draft202012Validator, FormatChecker
    schema = json.loads((Path(__file__).resolve().parents[1]/'contracts/generator-service-v2/candidate.schema.json').read_text())
    if next(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value), None):
        raise ServiceError('INVALID_V2_CANDIDATE', 422)
    plain = deepcopy(value)
    ids = [a['assetId'] for a in value['media']]
    if len(ids) != len(set(ids)):
        raise ServiceError('INVALID_V2_MEDIA', 422)
    found = []
    for name in ['stem', 'explanation']:
        t = plain[name]
        markers = re.findall(r'\[\[asset:([^\]]+)\]\]', t['text'])
        keys = t.pop('assetKeys', [])
        expected = [m['assetId'] for m in value['media'] if m['placement'] == name.upper()]
        if sorted(markers) != sorted(expected) or sorted(keys) != sorted(expected):
            raise ServiceError('INVALID_V2_MEDIA', 422)
        found.extend(markers)
        t['text'] = re.sub(r'\[\[asset:[^\]]+\]\]\s*', '', t['text']).strip()
    if sorted(found) != sorted(ids):
        raise ServiceError('INVALID_V2_MEDIA', 422)
    if value['contentFingerprint'] != fingerprint({k:v for k,v in value.items() if k!='contentFingerprint'}):
        raise ServiceError('INVALID_V2_FINGERPRINT', 422)
    plain['media'] = []
    plain['contentFingerprint'] = fingerprint({k:v for k,v in plain.items() if k!='contentFingerprint'})
    from .contracts import validate_payload as validate_plain
    validate_plain(plain)


def candidate(record, source, image=None):
    result = payload(local_record(record), normalized_source(source))
    artifacts = []
    if image is not None:
        asset = {'assetId': 'diagram-1', 'sha256': image.sha256, 'byteLength': image.byte_length,
                 'width': image.width, 'height': image.height, 'contentType': 'image/png',
                 'placement': 'STEM', 'altText': image.scene.alt_text,
                 'provenanceDigest': fingerprint(image.provenance)}
        result['media'] = [asset]
        result['stem'] = {'text': result['stem']['text']+'\n\n[[asset:diagram-1]]', 'assetKeys': ['diagram-1']}
        artifacts = [{'sha256': image.sha256, 'pngBytes': image.png_bytes, 'byteLength': image.byte_length,
                      'width': image.width, 'height': image.height, 'provenance': image.provenance}]
    result['contentFingerprint'] = fingerprint({k:v for k,v in result.items() if k!='contentFingerprint'})
    validate_payload(result)
    return result, artifacts
