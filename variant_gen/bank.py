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
    labels = o.get("metadata", {}).get("category_labels", ["Benar", "Salah"])
    if labels != ["Benar", "Salah"]:
        payload["category_labels"] = labels
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def _parse_row(row, line, allow_missing_key=False):
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
    if fmt == "PG" and len(key) != 1 and not (allow_missing_key and not key):
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
        self._catalog = []
        metadata = Path(path).with_name("question_metadata.json")
        items = {}
        if metadata.exists():
            try:
                items = json.loads(metadata.read_text(encoding="utf-8"))
                if not isinstance(items, dict):
                    raise ValueError("question metadata must be an object")
            except (OSError, ValueError) as error:
                raise BankError(f"cannot load question metadata: {error}") from error
        try:
            f = open(path, newline="", encoding="utf-8-sig")
        except OSError as e:
            raise BankError(f"cannot open bank file: {e}")
        with f:
            for line, row in enumerate(csv.DictReader(f), start=2):
                item = items.get(row["id"].strip(), {})
                held = (isinstance(item, dict) and item.get("generation_status") == "HOLD_SOURCE"
                        and isinstance(item.get("reason"), str) and bool(item["reason"].strip()))
                o = _parse_row(row, line, allow_missing_key=held)
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

        catalog = Path(path).with_name("question_catalog.json")
        if catalog.exists():
            try:
                groups = json.loads(catalog.read_text(encoding="utf-8"))
                if not isinstance(groups, list):
                    raise ValueError("catalog must be a list")
                memberships = set()
                for group in groups:
                    keys = (("activity", "chapter", "package_id") if group.get("activity") == "TRYOUT"
                            else ("activity", "indicator", "source_level", "package_id"))
                    meta = {key: group[key] for key in keys}
                    if (meta["activity"] not in ("DRILL", "TRYOUT", "PRETEST")
                            or any(type(meta[k]) is not int or meta[k] <= 0 for k in keys if k not in ("activity", "package_id"))
                            or not isinstance(meta["package_id"], str) or not meta["package_id"].strip()
                            or not isinstance(group["question_ids"], list)):
                        raise ValueError("invalid/duplicate package classification")
                    membership = tuple(meta.values())
                    if membership in memberships:
                        raise ValueError("duplicate package/indicator/level")
                    memberships.add(membership)
                    for qid in group["question_ids"]:
                        original = self._rows[qid]
                        if "classification" in original:
                            raise ValueError(f"duplicate classification: {qid}")
                        original["classification"] = deepcopy(meta)
                self._catalog = groups
            except (OSError, ValueError, KeyError, TypeError) as error:
                raise BankError(f"cannot load question catalog: {error}") from error
        if metadata.exists():
            try:
                for qid, item in items.items():
                    if not isinstance(item, dict) or item.get("generation_status") not in ("ACTIVE", "HOLD_SOURCE", "DEFERRED_CONCEPTUAL"):
                        raise ValueError(f"invalid generation status: {qid}")
                    if ("notes" in item and (not isinstance(item["notes"],list) or any(not isinstance(note,str) for note in item["notes"]))):
                        raise ValueError(f"notes must be a list of strings: {qid}")
                    if item["generation_status"] != "ACTIVE" and (not isinstance(item.get("reason"),str) or not item["reason"].strip()):
                        raise ValueError(f"deferred question requires reason: {qid}")
                    if "category_labels" in item:
                        labels = item["category_labels"]
                        if (self._rows[qid]["format"] != "KATEGORI" or not isinstance(labels, list)
                                or len(labels) != 2 or any(not isinstance(s, str) or not s.strip() for s in labels)
                                or labels[0].strip().casefold() == labels[1].strip().casefold()):
                            raise ValueError(f"invalid category labels: {qid}")
                    self._rows[qid]["metadata"] = item
                    self._rows[qid]["hash"] = original_hash(self._rows[qid])
            except (OSError, ValueError, KeyError, TypeError) as error:
                raise BankError(f"cannot load question metadata: {error}") from error

    def ids(self):
        return list(self._rows)

    def catalog(self):
        return deepcopy(self._catalog)

    def get(self, qid):
        if qid not in self._rows:
            raise BankError(f"unknown question id '{qid}'")
        return deepcopy(self._rows[qid])


def load_workspace_bank(path, additional_paths=None):
    bank = OriginalBank(path)
    default = Path(__file__).resolve().parent / "data/q0_bank.csv"
    if additional_paths is None:
        additional_paths = ([extra for extra in (default.parent / "tryout-1/q0_bank.csv",
                            default.parent / "drill-1-indicators-1-2/q0_bank.csv",
                            default.parent / "drill-1-indicators-3-5/q0_bank.csv",
                            default.parent / "drill-1-indicators-6-10/q0_bank.csv",
                            default.parent / "drill-1-indicators-11-15/q0_bank.csv",
                            default.parent / "drill-1-indicators-20-23/q0_bank.csv") if extra.exists()]
                            if Path(path).resolve() == default else [])
    for extra in additional_paths:
        other = OriginalBank(extra)
        duplicates = bank._rows.keys() & other._rows.keys()
        if duplicates:
            raise BankError(f"duplicate question ids across banks: {sorted(duplicates)}")
        bank._rows.update(other._rows)
        bank._catalog.extend(other._catalog)
    return bank
