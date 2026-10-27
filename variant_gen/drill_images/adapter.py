"""Bind accepted raw values to reviewed images; no random calls or implicit writes."""
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import cli
from config_store import config_hash
from engine import assemble, build_values, make_record, original_record
from filters import validate_candidate
from image_variants import ImageVariantError, build_scene, render_scene
from image_variants.templates import canonical, sha256
from .templates import IDS, ROOT, load_template, snapshot_sha


def exact_json(value):
    if isinstance(value, Fraction):
        return {'numerator': value.numerator, 'denominator': value.denominator}
    raise TypeError(type(value).__name__)


def exact_sha(value):
    import json
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                             default=exact_json).encode('utf-8'))


def verify_content(contract, original, config, *, config_path=None):
    if (original['id'] != contract.image.question_id
            or original['version'] != contract.original_version
            or original['hash'] != contract.original_hash
            or snapshot_sha(original) != contract.original_full_sha256
            or config['config_version'] != contract.config_version
            or config_hash(config) != contract.config_hash
            or snapshot_sha(config) != contract.config_snapshot_sha256):
        raise ImageVariantError('Drill original/config pin mismatch; template review is required')
    path = config_path or ROOT / 'configs' / original['id'] / f'v{contract.config_version}.json'
    try:
        if sha256(Path(path).read_bytes()) != contract.config_file_sha256:
            raise ImageVariantError('Drill config file pin mismatch; exact pinned bytes required')
    except OSError as exc:
        raise ImageVariantError('Drill config file pin cannot be verified') from exc


def annotate(image, contract, record, mode, values=None):
    stable = deepcopy(record)
    stable.pop('created_at', None)
    folder = Path(__file__).parent
    code = b'\n'.join(p.read_bytes().replace(b'\r\n', b'\n') for p in sorted(folder.glob('*.py')))
    provenance = {**image.provenance, 'render_artifact_id': image.provenance['artifact_id'],
                  'adapter': {'version': 'drill-numeric-images-v1', 'code_sha256': sha256(code)},
                  'content': {'mode': mode, 'record_id': record['record_id'],
                              'record_sha256': exact_sha(stable),
                              'original_version': contract.original_version,
                              'original_hash': contract.original_hash,
                              'original_full_sha256': contract.original_full_sha256,
                              'config_version': contract.config_version,
                              'config_hash': contract.config_hash,
                              'config_file_sha256': contract.config_file_sha256,
                              'accepted_raw_values_sha256': exact_sha(values) if values is not None else None}}
    provenance.pop('artifact_id')
    provenance['artifact_id'] = sha256(canonical(provenance))
    return replace(image, provenance=provenance)


def render_accepted(original, config, result, record, *, config_path=None):
    """Use one accepted Result; re-evaluate formulas only to validate its integrity."""
    try:
        contract = load_template(original['id'])
        verify_content(contract, original, config, config_path=config_path)
        k = result.values['k']
        if type(k) is not int or not 1 <= k <= 30:
            raise ImageVariantError('Drill accepted k must be an exact integer in 1..30')
        # This source supplies an existing k, not an RNG. It detects stale/mutated raw values.
        checked = build_values(config, lambda name, spec: k)
        if exact_sha(checked) != exact_sha(result.values) or assemble(config, result.values) != result.cand:
            raise ImageVariantError('Drill accepted values/candidate mismatch')
        if validate_candidate(result.cand, original, []):
            raise ImageVariantError('Drill candidate does not pass existing filters')
        if type(record['seed']) is not int or not 1 <= record['seed'] <= 1_000_000_000:
            raise ImageVariantError('Invalid Drill record seed')
        expected = make_record(original, config, contract.config_hash, record['seed'], 1, result)
        expected.pop('created_at'); stable = deepcopy(record); stable.pop('created_at', None)
        if expected != stable:
            raise ImageVariantError('Drill accepted record mismatch')
        aliases = {}
        for alias, variable, original_dimension in contract.dimensions:
            value = result.values[variable]
            if type(value) is not int or value != original_dimension*(k+1):
                raise ImageVariantError('Drill exact dimension does not match the reviewed scale')
            aliases[alias] = value
        scene = build_scene(contract.image, aliases)
        return annotate(render_scene(contract.image, scene), contract, record, 'generator', result.values)
    except ImageVariantError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise ImageVariantError('Invalid numerical Drill render input') from exc


def render_original(original, config, *, config_path=None):
    """Original record/dimensions are pinned independently from invalid k=0 candidates."""
    try:
        contract = load_template(original['id'])
        verify_content(contract, original, config, config_path=config_path)
        record = original_record(original)
        scene = build_scene(contract.image, dict(contract.original_bindings))
        return annotate(render_scene(contract.image, scene), contract, record, 'original')
    except ImageVariantError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise ImageVariantError('Invalid numerical Drill original input') from exc


def preview(bank, configs, question_id, seed=0):
    """Opt-in Python preview -> (unchanged record, RenderedImage); no storage/network."""
    if question_id not in IDS or type(seed) is not int or not 0 <= seed <= 1_000_000_000:
        raise ImageVariantError('Unsupported numerical Drill question or seed')
    original = bank.get(question_id)
    config, _ = configs.load(question_id)
    config_path = configs.root / question_id / f"v{config['config_version']}.json"
    verify_content(load_template(question_id), original, config, config_path=config_path)
    if seed == 0:
        return cli.preview(bank, configs, question_id, 0), render_original(original, config, config_path=config_path)
    images = []
    def capture(original, config, result, record):
        images.append(render_accepted(original, config, result, record, config_path=config_path))
    record = cli.preview(bank, configs, question_id, seed, on_generated=capture)
    if len(images) != 1:
        raise ImageVariantError('Drill preview requires exactly one accepted image')
    return record, images[0]
