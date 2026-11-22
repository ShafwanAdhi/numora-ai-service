"""Optional Drill/LEVEL manifest pin on the existing generator-service-v2 wave."""
import json
import os
import re
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from .content import fingerprint
from .errors import ServiceError


@lru_cache(maxsize=1)
def manifest_validator():
    path = Path(__file__).resolve().parents[1] / "contracts/generator-service-v2/drill-variant-manifest.schema.json"
    return Draft202012Validator(json.loads(path.read_text(encoding="utf-8")), format_checker=FormatChecker())


def runtime_pin():
    if (os.environ.get("NUMORA_DRILL_VARIANT_GENERATION_ENABLED") != "true"
            or os.environ.get("NODE_ENV") not in ("development", "test")
            or os.environ.get("NUMORA_IRT_MODE") == "PRODUCTION"):
        return None
    profile = os.environ.get("NUMORA_DRILL_VARIANT_RUNTIME_PROFILE", "")
    image = os.environ.get("NUMORA_DRILL_VARIANT_IMAGE_DIGEST", "")
    if not re.fullmatch(r"[a-z0-9_.-]{1,128}", profile) or not re.fullmatch(r"sha256:[a-f0-9]{64}", image):
        return None
    return {"runtimeProfile": profile, "imageDigest": image}


def validate_manifest(repository, db, task, manifest):
    runtime = runtime_pin()
    if runtime is None:
        raise ServiceError("DRILL_VARIANT_GENERATION_DISABLED", 503)
    r, w, g, s, a, c = (task[k] for k in ("request", "wave", "config", "source", "approval", "context"))
    if not manifest_validator().is_valid(manifest):
        raise ServiceError("DRILL_VARIANT_MANIFEST_INVALID")
    frozen_digest = manifest.get("manifestDigest")
    if (fingerprint({k: v for k, v in manifest.items() if k != "manifestDigest"}) != frozen_digest
            or manifest.get("runtime") != runtime
            or manifest.get("contractVersion") != "generator-service-v2"
            or manifest.get("armKind") != "VARIANT"
            or manifest.get("ecosystem") != c["ecosystem"] or c["ecosystem"] != "DRILL"
            or manifest.get("dimension") != c["dimension"] or c["dimension"] != "LEVEL"
            or manifest.get("levelId") != str(c["level_id"])
            or manifest.get("contextId") != str(r["context_id"])
            or manifest.get("contextRevision") != c["revision"]):
        raise ServiceError("DRILL_VARIANT_MANIFEST_PIN_MISMATCH")
    items = manifest.get("items")
    if (len({i["familyId"] for i in items}) != 10
            or len({i["questionVersionId"] for i in items}) != 10):
        raise ServiceError("DRILL_VARIANT_ROSTER_MISMATCH")
    source_package, roster = repository.drill_source(db, manifest["sourcePackageId"])
    if (source_package is None or source_package["package_version"] != manifest["sourcePackageVersion"]
            or str(source_package["level_id"]) != manifest["levelId"]
            or str(source_package["scoring_policy_version_id"]) != manifest["policyVersionId"]
            or str(source_package["context_id"]) != manifest["contextId"]
            or str(source_package["original_revision_id"]) != manifest["originalRevisionId"]
            or str(source_package["variant_arm_id"]) != manifest["variantArmId"]
            or str(source_package["blueprint_version_id"]) != manifest["blueprintVersionId"]
            or sorted(str(i) for i in source_package["anchor_ids"]) !=
                sorted(i["questionVersionId"] for i in items if i["role"] == "ANCHOR")
            or len(roster) != len(items)):
        raise ServiceError("DRILL_VARIANT_SOURCE_CHANGED")
    for stored, item in zip(roster, items):
        if (str(stored["question_version_id"]) != item["questionVersionId"]
                or stored["display_order"] != item["displayOrder"]
                or str(stored["rubric_version_id"]) != item["rubricVersionId"]
                or str(stored["family_id"]) != item["familyId"]
                or stored["kind"] != "ORIGINAL" or stored["content_hash"] != item["contentHash"]
                or stored["content_fingerprint"] != item["sourceFingerprint"]
                or stored["maximum_score_category"] != item["maximumScoreCategory"]
                or str(stored["max_points"]) != item["maxPoints"]):
            raise ServiceError("DRILL_VARIANT_SOURCE_CHANGED")
    focal = next((i for i in items if i["questionVersionId"] == str(s["id"])), None)
    pin = focal.get("mapping") if focal and focal["role"] == "FOCAL" else None
    p = g["parameters"]
    if (not isinstance(pin, dict) or pin.get("approvalId") != str(a["id"])
            or pin.get("configId") != str(g["id"]) or pin.get("configVersion") != g["config_version"]
            or pin.get("configDigest") != g["digest"] or pin.get("mode") != p["mode"]
            or pin.get("originalHash") != p["originalHash"] or pin.get("originalVersion") != p["originalVersion"]
            or pin.get("sourceFingerprint") != p["sourceFingerprint"] or pin.get("mediaProfile") != p["mediaProfile"]
            or focal["seed"] != w["constraints"].get("seed")):
        raise ServiceError("DRILL_VARIANT_CONFIG_PIN_MISMATCH")
    return {
        "drillVariantManifestDigest": frozen_digest, "drillRuntime": runtime,
        "drillContextId": manifest["contextId"], "drillContextRevision": c["revision"],
        "drillFamilyId": focal["familyId"], "drillParentQuestionVersionId": focal["questionVersionId"],
        "drillConfigDigest": pin["configDigest"],
    }
