"""Original question bank (CSV). READ-ONLY: this module has no write path, and get() hands out copies,
so nothing downstream can tamper with an original."""
import csv
import hashlib
import json
from copy import deepcopy
from pathlib import Path

FORMATS = ("PG", "MCMA", "KATEGORI")


class BankError(Exception):
    pass


def option_ids(fmt, n):
    """PG / MCMA options are A, B, C...; KATEGORI statements are 1, 2, 3..."""
    return [str(i + 1) for i in range(n)] if fmt == "KATEGORI" else [chr(65 + i) for i in range(n)]


def original_hash(o):
    """Stable fingerprint of an original's content. Stands in for a question version until a DB exists."""
    payload = {
        "format": o["format"],
        "stem": o["stem"],
        "options": [x["text"] for x in o["options"]],
        "key": [x["id"] for x in o["options"] if x["correct"]],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def _parse_row(row, line):
    qid = row["id"].strip()
    fmt = row["format"].strip()
    if fmt not in FORMATS:
        raise BankError(f"{qid} (row {line}): unknown format '{fmt}'")
    try:
        texts = json.loads(row["options_json"])
    except json.JSONDecodeError as e:
        raise BankError(f"{qid} (row {line}): options_json is not valid JSON ({e})")
    ids = option_ids(fmt, len(texts))
    key = [k.strip() for k in row["key"].split(",") if k.strip()]
    bad = [k for k in key if k not in ids]
    if bad:
        raise BankError(f"{qid} (row {line}): key ids {bad} are not among options {ids}")
    if fmt == "PG" and len(key) != 1:
        raise BankError(f"{qid} (row {line}): PG needs exactly one correct id, got {key}")
    o = {
        "id": qid, "format": fmt, "cognitive_level": row.get("cognitive_level", ""),
        "stem": row["stem"], "version": int(row.get("version") or 1),
        "options": [{"id": i, "text": t, "correct": i in key} for i, t in zip(ids, texts)],
    }
    o["hash"] = original_hash(o)
    return o


class OriginalBank:
    def __init__(self, path):
        self._rows = {}
        try:
            f = open(path, newline="", encoding="utf-8-sig")
        except OSError as e:
            raise BankError(f"cannot open bank file: {e}")
        with f:
            for line, row in enumerate(csv.DictReader(f), start=2):
                o = _parse_row(row, line)
                if o["id"] in self._rows:
                    raise BankError(f"duplicate question id {o['id']}")
                self._rows[o["id"]] = o
        revisions = Path(path).with_name("original_revisions.jsonl")
        if revisions.exists():
            try:
                for line, text in enumerate(revisions.read_text(encoding="utf-8").splitlines(), start=1):
                    if not text.strip():
                        continue
                    revision = json.loads(text)
                    current = self._rows[revision["question_id"]]
                    previous = _parse_row(revision["original_row"], line)
                    replacement = _parse_row(revision["replacement_row"], line)
                    if (previous["id"] != current["id"] or previous["hash"] != current["hash"]
                            or previous["version"] != current["version"]
                            or revision["original_version"] != current["version"]
                            or replacement["id"] != current["id"]
                            or replacement["version"] != current["version"] + 1
                            or revision["replacement_version"] != replacement["version"]
                            or not isinstance(revision.get("reason"), str) or not revision["reason"].strip()):
                        raise BankError(f"{revisions.name} (row {line}): revision provenance/version mismatch")
                    self._rows[current["id"]] = replacement
            except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
                raise BankError(f"cannot load original revisions: {error}") from error

    def ids(self):
        return list(self._rows)

    def get(self, qid):
        if qid not in self._rows:
            raise BankError(f"unknown question id '{qid}'")
        return deepcopy(self._rows[qid])
