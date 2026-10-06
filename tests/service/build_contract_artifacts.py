"""Rebuild synthetic handoff fixtures and static OpenAPI without connecting to DB."""
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from numora_service.api import create_app
from numora_service.content import canonical, fingerprint
from numora_service.contracts import validate_payload
from numora_service.settings import Settings

TARGET = ROOT / "contracts/generator-service-v1"


def write(name, value):
    (TARGET / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fixtures():
    base = {
        "questionType": "SINGLE_CHOICE", "stem": {"text": r"Tentukan nilai \(x\) jika \(x+2=5\)."},
        "optionsOrStatements": {"options": [
            {"id": "A", "content": {"text": "2"}}, {"id": "B", "content": {"text": "3"}},
            {"id": "C", "content": {"text": "5"}}], "categories": []},
        "answerKey": {"optionId": "B"}, "explanation": {"text": r"\[x=5-2=3\]"},
        "media": [], "difficulty": "EASY", "rubricVersionId": "00000000-0000-4000-8000-000000000001"}
    pg = copy.deepcopy(base)
    mcma = copy.deepcopy(base)
    mcma.update(questionType="MULTIPLE_CHOICE_MULTIPLE_ANSWER", stem={"text": "Pilih bilangan prima."},
                answerKey={"optionIds": ["A", "B", "C"]}, explanation={"text": "2, 3, dan 5 adalah bilangan prima."})
    boolean = copy.deepcopy(base)
    boolean.update(questionType="CATEGORY", stem={"text": "Kategorikan pernyataan berikut."},
                   answerKey={"categoryByStatementId": {"A": "true", "B": "false"}},
                   explanation={"text": "Pernyataan A benar dan B salah."}, difficulty=None)
    boolean["optionsOrStatements"] = {"options": [
        {"id": "A", "content": {"text": "2 adalah bilangan prima."}},
        {"id": "B", "content": {"text": "4 adalah bilangan prima."}}],
        "categories": [{"id": "true", "label": "Benar"}, {"id": "false", "label": "Salah"}]}
    custom = copy.deepcopy(boolean)
    custom["optionsOrStatements"]["categories"] = [{"id": "sesuai", "label": "Sesuai"}, {"id": "tidak_sesuai", "label": "Tidak Sesuai"}]
    custom["answerKey"] = {"categoryByStatementId": {"A": "sesuai", "B": "tidak_sesuai"}}
    custom["explanation"] = {"text": "Pernyataan A sesuai dan B tidak sesuai."}
    candidates, hashes = [], []
    for name, core in (("pg-latex", pg), ("mcma", mcma), ("category-boolean", boolean), ("category-custom", custom)):
        candidate = {**core, "contentFingerprint": fingerprint(core)}
        validate_payload(candidate)
        candidates.append({"name": name, "testOnly": True, "payload": candidate})
        hashes.append({"name": name, "input": core, "canonical": canonical(core), "sha256": fingerprint(core)})
    for name, value in (("unicode", {"text": "Soal: \\(x^2\\)\nSesuai — π 😀", "categories": boolean["optionsOrStatements"]["categories"]}),
                        ("keys", {"z": True, "a": None, "n": 123, "map": {"2": "yes", "1": "no"}}),
                        ("utf16-order", {"\ue000": "bmp", "😀": "supplementary", "line": "a\n\tb"})):
        hashes.append({"name": name, "input": value, "canonical": canonical(value), "sha256": fingerprint(value)})
    write("candidates.fixture.json", candidates)
    write("fingerprints.fixture.json", hashes)


def openapi():
    doc = create_app(Settings()).openapi()
    doc["info"]["description"] = "generator-service-v1. Compute v3 notification only; one text candidate per request."
    doc["servers"] = [{"url": "http://127.0.0.1:8770", "description": "Local service; TLS proxy for remote worker"}]
    components = doc.setdefault("components", {})
    schemas = components.setdefault("schemas", {})
    for name in ("notification", "response", "candidate", "registration"):
        schema = json.loads((TARGET / (name + ".schema.json")).read_text(encoding="utf-8"))
        title = name.title()
        # JSON Schema references must point at their component after embedding.
        def rewrite(v):
            if isinstance(v, list): return [rewrite(i) for i in v]
            if isinstance(v, dict):
                return {k: (f"#/components/schemas/{title}/" + i[2:] if k == "$ref" and i.startswith("#/") else rewrite(i)) for k, i in v.items()}
            return v
        schema.pop("$id", None)
        schemas[title] = rewrite(schema)
    schemas["Problem"] = {"type": "object", "additionalProperties": False, "required": ["type", "title", "status", "code"],
                          "properties": {"type": {"type": "string"}, "title": {"type": "string"}, "code": {"type": "string"}, "status": {"type": "integer"}}}
    components["securitySchemes"] = {"ServiceBearer": {"type": "http", "scheme": "bearer"}}
    for path, methods in doc["paths"].items():
        for operation in methods.values():
            operation["security"] = [] if path == "/health/live" else [{"ServiceBearer": []}]
            operation["responses"]["default"] = {"description": "Stable failure code; no raw exception or content",
                "content": {"application/problem+json": {"schema": {"$ref": "#/components/schemas/Problem"}}}}
    execute = doc["paths"]["/api/v1/compute/execute"]["post"]
    execute["requestBody"] = {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Notification"}}}}
    execute["responses"] = {"200": {"description": "Terminal execution (SUCCEEDED, FAILED or EXPIRED)", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Response"}}}},
                            "202": {"description": "Existing RUNNING execution; wait via Numora", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Response"}}}},
                            "default": execute["responses"]["default"]}
    write("openapi.json", doc)


if __name__ == "__main__":
    fixtures()
    openapi()
