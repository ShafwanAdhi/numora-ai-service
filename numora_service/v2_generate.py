"""Pinned numeric/stock execution and rendering from the same accepted result."""
from .bridge import ENGINE_ROOT, config_hash, generate, make_record
from .content import fingerprint
from .errors import ServiceError
from .v2_content import candidate


def stocks(bank):
    from conceptual_stock import load_stock
    return load_stock(ENGINE_ROOT/'data/conceptual_stock.json', bank)


def stock_manifest(items):
    return {'items': [{'variantId': s['variant_id'], 'stockIndex': s['stock_index'],
                       'stockVersion': s['stock_version'], 'contentHash': fingerprint(s)} for s in items]}


def image_ids():
    from drill_images import IDS
    from drill_concept_images import IDS as CONCEPT
    from tryout_media import IMAGE_IDS
    return set(IDS) | set(CONCEPT) | set(IMAGE_IDS)


def media_profile(qid):
    if qid not in image_ids():
        return None
    from image_variants.renderer import renderer_identity
    from drill_images import IDS
    from drill_concept_images import IDS as CONCEPT
    renderer = renderer_identity()
    renderer.pop('platform', None)
    if qid in IDS:
        from drill_images.templates import load_template
        templates = [load_template(qid).image]
    elif qid in CONCEPT:
        from drill_concept_images import load_scenario
        from .bridge import workspace
        bank, _ = workspace()
        templates = [load_scenario(qid, s['variant_id']).image for s in stocks(bank)[qid]]
    else:
        from image_variants import load_template
        templates = [load_template(qid)]
    from renderer_profiles import selected_profile
    return {'profileId':selected_profile(), 'renderer': renderer, 'templateDefinitions': [t.definition_sha256 for t in templates]}


def generate_result(work):
    original = work['original']
    qid = original['id']
    if media_profile(qid) != work['mediaProfile']:
        raise ServiceError('RENDERER_TEMPLATE_PIN_MISMATCH')
    image = None
    provenance = {'serviceContract': 'generator-service-v2', 'mode': work['mode'],
                  'questionExternalId': qid, 'originalHash': original['hash'],
                  'originalVersion': original['version'], 'mediaProfile': work['mediaProfile']}
    if work['mode'] == 'NUMERIC':
        cfg, seed = work['config'], work['seed']
        result = generate(original, cfg, seed, [])
        record = make_record(original, cfg, config_hash(cfg), seed, 1, result)
        provenance.update(configHash=config_hash(cfg), configVersion=cfg['config_version'],
                          seed=seed, drawsUsed=result.draws_used, valuesUsed=record['values_used'])
        if qid in image_ids():
            from drill_images import IDS
            if qid in IDS:
                from drill_images.adapter import render_accepted
                image = render_accepted(original, cfg, result, record)
            else:
                from image_variants import load_template, build_scene, render_scene
                template = load_template(qid)
                image = render_scene(template, build_scene(template, result.values))
    else:
        from conceptual_stock import stock_record
        record = stock_record(original, work['stockItem'])
        provenance.update(stockReservationId=work['reservation']['id'], stockSetId=work['stockSetId'],
                          stockSetDigest=work['stockSetDigest'], stockVariantId=work['stockItem']['variant_id'],
                          stockVersion=work['stockItem']['stock_version'], reused=work['reservation']['reused'],
                          cycle=work['reservation']['cycle'])
        if qid in image_ids():
            from drill_concept_images import preview
            class PinnedBank:
                def get(self, key):
                    if key != qid: raise ServiceError('STOCK_SOURCE_MISMATCH')
                    return original
            rendered_record, image = preview(PinnedBank(), {qid: [work['stockItem']]}, qid, work['stockItem']['variant_id'])
            if rendered_record != record:
                raise ServiceError('STOCK_RENDER_CONTENT_MISMATCH')
    if original.get('metadata',{}).get('category_labels'):
        record['metadata']={'category_labels':original['metadata']['category_labels']}
    content, artifacts = candidate(record, work['source'], image)
    return {'payload': content, 'provenance': provenance, 'mediaArtifacts': artifacts}
