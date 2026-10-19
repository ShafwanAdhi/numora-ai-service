"""Operator config registration. Default dry-run; never writes canonical tables."""
import argparse
import json
import sys

from psycopg.types.json import Jsonb

from . import SERVICE_CONTRACT
from .bridge import workspace
from bank import BankError
from config_store import ConfigError
from .content import fingerprint, source_content, uuid
from .contracts import validate
from .errors import ServiceError
from .repository import Repository
from .settings import Settings
from .task import validate_mapping


def register(repository, bank, configs, manifest, apply=False, seal=False):
    validate("registration", manifest)
    if seal and not apply:
        raise ServiceError("SEAL_REQUIRES_APPLY", 422)
    if not isinstance(manifest, dict) or set(manifest) != {"serviceContract", "items"} or manifest["serviceContract"] != SERVICE_CONTRACT:
        raise ServiceError("INVALID_REGISTRATION", 422)
    items = manifest["items"]
    if not isinstance(items, list) or not 1 <= len(items) <= 100:
        raise ServiceError("INVALID_REGISTRATION", 422)
    output, seen = [], set()
    with repository.connection() as db:
        repository.check_role(db)
        for item in items:
            required = {"questionExternalId", "configVersion", "parentQuestionVersionId", "familyId", "rubricVersionId", "contextId"}
            if not isinstance(item, dict) or set(item) != required:
                raise ServiceError("INVALID_REGISTRATION", 422)
            if type(item["configVersion"]) is not int or item["configVersion"] < 1:
                raise ServiceError("INVALID_REGISTRATION", 422)
            original = bank.get(item["questionExternalId"])
            cfg, cfg_hash = configs.load(original["id"], item["configVersion"])
            source = repository.one(db, "SELECT * FROM public.irt_input_content_v3 WHERE id=%s", (uuid(item["parentQuestionVersionId"]),))
            rubric = repository.one(db, "SELECT * FROM public.irt_input_rubrics_v3 WHERE id=%s", (uuid(item["rubricVersionId"]),))
            context = repository.one(db, "SELECT * FROM public.irt_input_contexts_v3 WHERE id=%s", (uuid(item["contextId"]),))
            if (rubric["question_type"] != source["question_type"] or rubric["status"] != "SEALED" or
                    context["ecosystem"] not in ("DRILL", "TRYOUT")):
                raise ServiceError("RUBRIC_MISMATCH")
            parameters = {"serviceContract": SERVICE_CONTRACT, **item, "originalVersion": original["version"],
                          "originalHash": original["hash"], "sourceFingerprint": fingerprint(source_content(source)),
                          "configHash": cfg_hash, "config": cfg}
            validate_mapping(parameters, original, source, item["contextId"])
            # Identity includes source/context; local config version alone is not a globally unique key.
            identity = "generator-v1-" + fingerprint({k: item[k] for k in required if k != "configVersion"})
            key = (identity, item["configVersion"])
            if key in seen:
                raise ServiceError("DUPLICATE_REGISTRATION", 422)
            seen.add(key)
            if apply:
                db.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,4))", (identity,))
            digest = repository.one(db, "SELECT irt_compute.payload_digest(%s) AS digest", (Jsonb(parameters),))["digest"]
            existing = db.execute("""SELECT * FROM irt_compute.generator_configs
                WHERE template_or_competency_id=%s AND config_version=%s""", key).fetchone()
            if existing and (existing["parameters"] != parameters or existing["digest"] != digest or
                             str(existing["context_id"]) != item["contextId"] or existing["curriculum_limits"] != {}):
                raise ServiceError("REGISTRATION_CONFLICT")
            row = existing
            if apply and row is None:
                row = repository.one(db, """INSERT INTO irt_compute.generator_configs
                    (template_or_competency_id,config_version,parameters,curriculum_limits,context_id,digest,status)
                    VALUES(%s,%s,%s,'{}',%s,%s,'DRAFT') RETURNING id,status""",
                    (*key, Jsonb(parameters), item["contextId"], digest))
            if apply and seal and row["status"] == "DRAFT":
                row = repository.one(db, "UPDATE irt_compute.generator_configs SET status='SEALED' WHERE id=%s RETURNING id,status", (row["id"],))
            output.append({"questionExternalId": item["questionExternalId"], "configVersion": item["configVersion"],
                           "generatorConfigId": str(row["id"]) if row else None, "digest": digest,
                           "status": row["status"] if row else "DRY_RUN", "sourceFingerprint": parameters["sourceFingerprint"]})
    return {"serviceContract": SERVICE_CONTRACT, "applied": apply, "items": output}


def main():
    from dotenv import load_dotenv
    from .bridge import ROOT
    load_dotenv(ROOT / ".env", override=False)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true")
    group.add_argument("--dry-run", action="store_true")
    parser.add_argument("--seal", action="store_true", help="Seal the technical snapshot; does not create main-owned approval")
    args = parser.parse_args()
    bank, configs = workspace()
    repository = Repository(Settings.from_env(), bank)
    try:
        manifest = json.loads(open(args.manifest, encoding="utf-8").read())
        if args.seal and not args.apply:
            raise ServiceError("SEAL_REQUIRES_APPLY", 422)
        print(json.dumps(register(repository, bank, configs, manifest, args.apply, args.seal), indent=2))
    except (ServiceError, OSError, ValueError, KeyError, BankError, ConfigError):
        print("Registration failed; inspect the mapping and compute configuration.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
