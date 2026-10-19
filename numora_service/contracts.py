import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from .errors import ServiceError

CONTRACTS = Path(__file__).resolve().parent.parent / "contracts/generator-service-v1"


def validate(name, value):
    schema = json.loads((CONTRACTS / f"{name}.schema.json").read_text(encoding="utf-8"))
    if next(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value), None):
        raise ServiceError("INVALID_" + name.upper().replace("-", "_"), 422)


def validate_notification(value):
    validate("notification", value)
    if type(value["contractVersion"]) is not int or type(value["dispatchGeneration"]) is not int:
        raise ServiceError("INVALID_NOTIFICATION", 422)


def validate_payload(value):
    validate("candidate", value)
    from .content import fingerprint, text
    text(value["stem"]["text"])
    text(value["explanation"]["text"])
    for option in value["optionsOrStatements"]["options"]:
        text(option["content"]["text"])
    ids = [o["id"] for o in value["optionsOrStatements"]["options"]]
    categories = value["optionsOrStatements"]["categories"]
    answer = value["answerKey"]
    kind = value["questionType"]
    valid = len(ids) == len(set(ids))
    if kind == "SINGLE_CHOICE":
        valid &= set(answer) == {"optionId"} and answer.get("optionId") in ids and not categories
    elif kind == "MULTIPLE_CHOICE_MULTIPLE_ANSWER":
        valid &= set(answer) == {"optionIds"} and set(answer.get("optionIds", [])) <= set(ids) and not categories
    else:
        category_ids = [c["id"] for c in categories]
        valid &= (len(categories) == 2 and len(set(category_ids)) == 2 and
                  set(answer) == {"categoryByStatementId"} and
                  set(answer.get("categoryByStatementId", {})) == set(ids) and
                  set(answer.get("categoryByStatementId", {}).values()) <= set(category_ids))
    valid &= value["contentFingerprint"] == fingerprint({k: v for k, v in value.items() if k != "contentFingerprint"})
    if not valid:
        raise ServiceError("INVALID_CANDIDATE", 422)
