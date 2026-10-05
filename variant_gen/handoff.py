"""Export stored candidates using Numora's draft question-variant envelope.

Canonical IDs are supplied by Numora; this module never fabricates them or writes
to either database. A mapping must pin the exact original content/version.
"""
from uuid import UUID

from expr import PLACEHOLDER
from store import StoreError


def export_record(record, mapping):
    if record.get("metadata", {}).get("category_labels", ["Benar", "Salah"]) != ["Benar", "Salah"]:
        raise StoreError("canonical export requires boolean Benar/Salah categories; custom labels remain local")
    if record.get("cognitive_level") not in ("C1", "C2", "C3", "C4", "C5", "C6"):
        raise StoreError("canonical export requires a single cognitive label C1..C6; mixed source labels remain local")
    if not isinstance(mapping, dict):
        raise StoreError("mapping must be a JSON object")
    for field, expected in (("questionExternalId", record["question_id"]),
                            ("originalHash", record["original_hash"]),
                            ("originalVersion", record["original_version"])):
        if mapping.get(field) != expected:
            raise StoreError(f"mapping {field} does not match the stored original")
    ids = {}
    for field in ("familyId", "parentQuestionVersionId", "scoringRubricVersionId", "generationWaveItemId"):
        value = mapping.get(field)
        if field == "generationWaveItemId" and value is None:
            continue
        try:
            if not isinstance(value, str) or UUID(value).int == 0:
                raise ValueError()
            ids[field] = str(UUID(value))
        except (ValueError, AttributeError):
            raise StoreError(f"mapping {field} must be a real non-zero Numora UUID") from None
    explanation = record.get("explanation")
    if not isinstance(explanation, str) or not explanation.strip() or PLACEHOLDER.search(explanation):
        raise StoreError("stored variant has no complete explanation; regenerate with a newer config")
    correct = set(record["key"].split(",")) - {""}
    answer = ({"correctOptionId": next(iter(correct))} if record["format"] == "PG" else
              {"correctOptionIds": [o["id"] for o in record["options"] if o["id"] in correct]})
    if record["format"] == "KATEGORI":
        answer = {"statements": [{"id": o["id"], "correct": o["id"] in correct} for o in record["options"]]}
    return {
        "questionExternalId": record["question_id"],
        "variantExternalId": record["record_id"],
        "payload": {**ids, "format": record["format"], "cognitiveLevel": record["cognitive_level"],
                    "stem": record["stem"], "options": record["options"]},
        "answer": answer,
        "explanation": {"text": explanation},
        "generation": {"seed": record["seed"], "variantVersion": record["variant_ver"],
                       "configVersion": record["config_ver"], "configHash": record["config_hash"],
                       "originalHash": record["original_hash"], "originalVersion": record["original_version"],
                       "drawsUsed": record["draws_used"], "valuesUsed": record["values_used"],
                       "replacementOf": record["replacement_of"], "regenReason": record["regen_reason"],
                       "createdAt": record["created_at"], "reviewStatus": "REVIEW"},
    }
