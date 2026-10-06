"""Import the existing script modules without changing their import/CLI behavior."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENGINE_ROOT = ROOT / "variant_gen"
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from bank import load_workspace_bank  # noqa: E402
from config_store import ConfigStore, config_hash, validate_config  # noqa: E402
from engine import generate, make_record, original_record  # noqa: E402
from conceptual_stock import load_stock  # noqa: E402


def workspace():
    bank = load_workspace_bank(ENGINE_ROOT / "data/q0_bank.csv")
    return bank, ConfigStore(ENGINE_ROOT / "configs")


def catalog(bank, configs):
    stock = load_stock(ENGINE_ROOT / "data/conceptual_stock.json", bank)
    result = []
    for qid in bank.ids():
        orig = bank.get(qid)
        versions = configs.versions(qid)
        status = orig.get("metadata", {}).get("generation_status", "ACTIVE")
        mode = ("held" if status == "HOLD_SOURCE" else "stock" if stock.get(qid) else
                "generator" if versions and status == "ACTIVE" else "unavailable")
        cfg, digest = configs.load(qid) if versions else (None, None)
        result.append({"questionExternalId": qid, "format": orig["format"], "mode": mode,
                       "originalVersion": orig["version"], "originalHash": orig["hash"],
                       "configVersion": cfg["config_version"] if cfg else None,
                       "configHash": digest, "stockCount": len(stock.get(qid, [])),
                       "classification": orig.get("classification"),
                       "generationStatus": status})
    return result
