"""Numora content representation, source comparison and cross-language fingerprint.

Fingerprint uses Numora's recursively key-sorted compact UTF-8 JSON. PostgreSQL
jsonb digests are a DIFFERENT encoding and are always computed by the database.
"""
import hashlib
import json
import re
from uuid import UUID

from .errors import ServiceError

TYPES = {"PG": "SINGLE_CHOICE", "MCMA": "MULTIPLE_CHOICE_MULTIPLE_ANSWER", "KATEGORI": "CATEGORY"}
PAYLOAD_FIELDS = {"questionType", "stem", "optionsOrStatements", "answerKey", "explanation",
                  "media", "difficulty", "rubricVersionId", "contentFingerprint"}


def canonical(value):
    # Fixed ASCII field names; sort category/statement IDs with JavaScript UTF-16 ordering.
    if isinstance(value, dict):
        return "{" + ",".join(json.dumps(k, ensure_ascii=False) + ":" + canonical(value[k])
                              for k in sorted(value, key=lambda s: s.encode("utf-16-be"))) + "}"
    if isinstance(value, list):
        return "[" + ",".join(map(canonical, value)) + "]"
    if isinstance(value, float):
        raise ServiceError("NON_CANONICAL_NUMBER", 422)
    if type(value) is int and abs(value) > 9007199254740991:
        raise ServiceError("NON_CANONICAL_NUMBER", 422)
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def uuid(value):
    try:
        if not isinstance(value, str) or UUID(value).int == 0:
            raise ValueError()
        return str(UUID(value))
    except (ValueError, AttributeError):
        raise ServiceError("INVALID_CANONICAL_ID", 422) from None


def text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 100000:
        raise ServiceError("INVALID_CONTENT", 422)
    if re.search(r"\[\[asset:|!\[[^\]]*\]\(|<(?:img|svg|iframe)\b|\\includegraphics\b", value, re.I):
        raise ServiceError("MEDIA_NOT_SUPPORTED", 422)
    return {"text": value.replace("\r\n", "\n")}


def record_content(record, categories=None):
    kind = TYPES.get(record.get("format"))
    if not kind:
        raise ServiceError("UNSUPPORTED_FORMAT", 422)
    options = [{"id": o["id"], "content": text(o["text"])} for o in record["options"]]
    ids = [o["id"] for o in options]
    correct = record["key"].split(",") if record["key"] else []
    if len(ids) != len(set(ids)) or not 2 <= len(ids) <= 100 or not set(correct) <= set(ids):
        raise ServiceError("INVALID_ANSWER", 422)
    cats = []
    if kind == "SINGLE_CHOICE":
        if len(correct) != 1:
            raise ServiceError("INVALID_ANSWER", 422)
        answer = {"optionId": correct[0]}
    elif kind == "MULTIPLE_CHOICE_MULTIPLE_ANSWER":
        if not correct:
            raise ServiceError("INVALID_ANSWER", 422)
        answer = {"optionIds": [i for i in ids if i in correct]}
    else:
        labels = record.get("metadata", {}).get("category_labels", ["Benar", "Salah"])
        cats = categories or [{"id": "category_1", "label": labels[0]},
                              {"id": "category_2", "label": labels[1]}]
        if (len(cats) != 2 or {c["label"] for c in cats} != set(labels) or
                len({c["id"] for c in cats}) != 2):
            raise ServiceError("CATEGORY_MAPPING_MISMATCH", 422)
        by_label = {c["label"]: c["id"] for c in cats}
        answer = {"categoryByStatementId": {i: by_label[labels[0] if i in correct else labels[1]] for i in ids}}
    return {"questionType": kind, "stem": text(record["stem"]),
            "optionsOrStatements": {"options": options, "categories": cats}, "answerKey": answer}


def source_content(row):
    """Normalize canonical source for comparison; explanation/taxonomy are not guessed."""
    if row.get("media"):
        raise ServiceError("MEDIA_NOT_SUPPORTED", 422)
    collection = row["options_or_statements"]
    if isinstance(collection, list):
        collection = {"options": collection, "categories": []}
    options = []
    for o in collection["options"]:
        content = o["content"]
        if content.get("assetKeys"):
            raise ServiceError("MEDIA_NOT_SUPPORTED", 422)
        options.append({"id": o["id"], "content": text(content["text"])})
    if row["stem"].get("assetKeys") or row.get("explanation", {}).get("assetKeys"):
        raise ServiceError("MEDIA_NOT_SUPPORTED", 422)
    text(row.get("explanation", {}).get("text", ""))
    answer = row["answer_key"]
    if row["question_type"] == TYPES["MCMA"]:
        if (set(answer) != {"optionIds"} or not isinstance(answer["optionIds"], list) or
                not answer["optionIds"] or len(set(answer["optionIds"])) != len(answer["optionIds"]) or
                not set(answer["optionIds"]) <= {o["id"] for o in options}):
            raise ServiceError("INVALID_ANSWER", 422)
        answer = {"optionIds": [o["id"] for o in options if o["id"] in answer["optionIds"]]}
    return {"questionType": row["question_type"], "stem": text(row["stem"]["text"]),
            "optionsOrStatements": {"options": options, "categories": collection.get("categories", [])},
            "answerKey": answer}


def payload(record, source):
    core = record_content(record, source_content(source)["optionsOrStatements"]["categories"] or None)
    core.update(explanation=text(record["explanation"]), media=[], difficulty=source["difficulty"],
                rubricVersionId=uuid(str(source["scoring_rubric_version_id"])))
    if core["difficulty"] not in (None, "EASY", "MEDIUM", "HARD"):
        raise ServiceError("INVALID_DIFFICULTY", 422)
    return {**core, "contentFingerprint": fingerprint(core)}
