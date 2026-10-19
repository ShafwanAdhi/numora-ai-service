"""Validate main-owned authorization and reconcile a sealed config with local source."""
from .bridge import config_hash, original_record, validate_config
from bank import BankError
from .content import fingerprint, record_content, source_content, uuid
from .errors import ServiceError


def validate_mapping(parameters, original, source, context_id):
    required = {"serviceContract", "questionExternalId", "originalVersion", "originalHash",
                "parentQuestionVersionId", "familyId", "rubricVersionId", "contextId",
                "sourceFingerprint", "configVersion", "configHash", "config"}
    if not isinstance(parameters, dict) or set(parameters) != required:
        raise ServiceError("INVALID_CONFIG_MAPPING", 422)
    if (parameters["serviceContract"] != "generator-service-v1" or
            parameters["questionExternalId"] != original["id"] or
            type(parameters["originalVersion"]) is not int or parameters["originalVersion"] != original["version"] or
            parameters["originalHash"] != original["hash"] or
            uuid(parameters["parentQuestionVersionId"]) != str(source["id"]) or
            uuid(parameters["familyId"]) != str(source["family_id"]) or
            uuid(parameters["rubricVersionId"]) != str(source["scoring_rubric_version_id"]) or
            uuid(parameters["contextId"]) != str(context_id) or source["kind"] != "ORIGINAL"):
        raise ServiceError("SOURCE_MAPPING_MISMATCH")
    canonical_source = source_content(source)
    local_source = record_content(original_record(original), canonical_source["optionsOrStatements"]["categories"] or None)
    if canonical_source != local_source or parameters["sourceFingerprint"] != fingerprint(canonical_source):
        raise ServiceError("SOURCE_CONTENT_MISMATCH")
    cfg = parameters["config"]
    if (not isinstance(cfg, dict) or parameters["configHash"] != config_hash(cfg) or
            type(parameters["configVersion"]) is not int or cfg.get("config_version") != parameters["configVersion"]):
        raise ServiceError("CONFIG_PIN_MISMATCH")
    try:
        invalid = validate_config(cfg, original)
    except (ValueError, TypeError, KeyError, ArithmeticError):
        raise ServiceError("INVALID_CONFIG", 422) from None
    if invalid:
        raise ServiceError("INVALID_CONFIG", 422)
    return cfg


def validate_task(task, bank):
    request, wave, config, source, approval, rubric, context = (
        task[k] for k in ("request", "wave", "config", "source", "approval", "rubric", "context"))
    if request["request_type"] != "GENERATE_VARIANTS" or request["snapshot_id"] is not None:
        raise ServiceError("UNSUPPORTED_REQUEST", 422)
    if wave["target_count"] != 1:
        raise ServiceError("UNSUPPORTED_TARGET_COUNT", 422)
    if (wave["wave_status"] not in ("APPROVED", "RUNNING") or
            str(wave["context_id"]) != str(request["context_id"]) or
            str(config["context_id"]) != str(request["context_id"]) or config["status"] != "SEALED" or
            str(wave["original_question_version_id"]) != str(source["id"]) or
            str(wave["generator_config_id"]) != str(config["id"])):
        raise ServiceError("UNAUTHORIZED_WAVE")
    scope = approval["scope"]
    pins = request["configuration_pins"]
    if (approval["revoked_at"] is not None or str(approval["generator_config_id"]) != str(config["id"]) or
            config["digest"] != approval["approved_digest"] or
            scope.get("ecosystem") != context["ecosystem"] or
            scope.get("contextId", str(request["context_id"])) != str(request["context_id"]) or
            not any(p == {"approvalId": str(approval["id"]), "digest": config["digest"]} for p in pins)):
        raise ServiceError("CONFIG_APPROVAL_MISMATCH")
    if (rubric["status"] != "SEALED" or rubric["question_type"] != source["question_type"] or
            str(rubric["id"]) != str(source["scoring_rubric_version_id"])):
        raise ServiceError("RUBRIC_MISMATCH")
    if (source["content_status"] == "ARCHIVED" or source["validation_state"] in ("QUARANTINED", "ARCHIVED")):
        raise ServiceError("SOURCE_NOT_ELIGIBLE")
    constraints = wave["constraints"]
    if (not isinstance(constraints, dict) or constraints.get("serviceContract") != "generator-service-v1" or
            type(constraints.get("seed")) is not int or not 1 <= constraints["seed"] <= 1_000_000_000):
        raise ServiceError("INVALID_GENERATION_CONSTRAINTS", 422)
    parameters = config["parameters"]
    try:
        original = bank.get(parameters["questionExternalId"])
        cfg = validate_mapping(parameters, original, source, request["context_id"])
    except (KeyError, TypeError, BankError):
        raise ServiceError("INVALID_CONFIG_MAPPING", 422) from None
    return {"original": original, "config": cfg, "seed": constraints["seed"], "source": source}
