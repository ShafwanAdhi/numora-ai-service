"""Append-only variant store (JSON Lines). Nothing is ever updated or deleted:
a regenerated variant is a NEW line with variant_ver + 1 and the old line stays."""
import json
from pathlib import Path


class StoreError(Exception):
    pass


class VariantStore:
    def __init__(self, path):
        self.path = Path(path)

    def _all(self):
        if not self.path.exists():
            return []
        with open(self.path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def for_question(self, qid):
        return [r for r in self._all() if r["question_id"] == qid]

    def versions_of_seed(self, qid, seed):
        return sorted((r for r in self.for_question(qid) if r["seed"] == seed), key=lambda r: r["variant_ver"])

    def get(self, qid, seed, ver=None):
        vs = self.versions_of_seed(qid, seed)
        if ver is None:
            return vs[-1] if vs else None
        return next((r for r in vs if r["variant_ver"] == ver), None)

    def latest_by_seed(self, qid):
        out = {}
        for r in self.for_question(qid):
            if r["seed"] not in out or r["variant_ver"] > out[r["seed"]]["variant_ver"]:
                out[r["seed"]] = r
        return out

    def append(self, rec):
        if self.get(rec["question_id"], rec["seed"], rec["variant_ver"]):
            raise StoreError(f"{rec['record_id']} already exists; the store never overwrites")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
