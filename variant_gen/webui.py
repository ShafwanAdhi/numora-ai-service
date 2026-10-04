"""Local variant workbench: python -B webui.py (Python standard library only)."""
import argparse
import contextlib
import io
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from bank import OriginalBank
from cli import KNOWN_ERRORS, cmd_gen, cmd_regen
from config_store import ConfigError, ConfigStore, validate_config
from engine import original_record
from expr import ExprError
from lint import run_lint
from store import VariantStore

HERE = Path(__file__).resolve().parent


def positive_integer(value):
    if type(value) is not int or not 1 <= value <= 1_000_000_000:
        raise ValueError("Seed/versi harus bilangan bulat positif (maksimal 1.000.000.000).")
    return value


def check_draft(cfg, original):
    if not isinstance(cfg, dict):
        raise ConfigError("Config harus berupa objek JSON.")
    try:
        json.dumps(cfg, ensure_ascii=False, allow_nan=False).encode("utf-8")
        errors = validate_config(cfg, original)
        if errors:
            raise ConfigError("\n".join(errors))
        ok, lines = run_lint(original, cfg, n=5)
    except (ArithmeticError, AttributeError, KeyError, TypeError, ValueError, ExprError) as error:
        raise ConfigError(f"Struktur config tidak valid: {error}") from error
    return ok, lines


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(1)  # Bound idle browser sockets; writes remain serialized.

    def reply(self, status, data, content_type="application/json"):
        body = (json.dumps(data, ensure_ascii=False) if content_type == "application/json" else data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def local_request(self):
        port = self.server.server_port
        hosts = (f"127.0.0.1:{port}", f"localhost:{port}")
        if self.headers.get("Host") not in hosts:
            self.reply(403, {"error": "Host lokal diperlukan."})
            return False
        origin = self.headers.get("Origin")
        if origin and origin not in tuple(f"http://{host}" for host in hosts):
            self.reply(403, {"error": "Permintaan dari origin lain ditolak."})
            return False
        return True

    def do_GET(self):
        if not self.local_request():
            return
        try:
            url = urlsplit(self.path)
            bank, configs, store = self.server.bank, self.server.configs, self.server.store
            if url.path == "/":
                self.reply(200, (HERE / "webui.html").read_text(encoding="utf-8"), "text/html")
            elif url.path == "/api/questions":
                self.reply(200, [{"id": qid, "format": bank.get(qid)["format"],
                                  "stem": bank.get(qid)["stem"], "has_config": bool(configs.versions(qid))}
                                 for qid in bank.ids()])
            elif url.path == "/api/question":
                query = parse_qs(url.query, max_num_fields=10)
                qid = query.get("id", [""])[0]
                original = bank.get(qid)  # Check bank membership before using any ID as a path.
                seed = positive_integer(int(query.get("seed", ["1"])[0]))
                ver = query.get("version", [""])[0]
                ver = positive_integer(int(ver)) if ver else None
                versions = configs.versions(qid)
                latest, latest_hash = configs.load(qid) if versions else (None, None)
                cfg_ver = query.get("config_version", [""])[0]
                cfg = configs.load(qid, positive_integer(int(cfg_ver)))[0] if cfg_ver else latest
                variant = store.get(qid, seed, ver)
                if ver and not variant:
                    raise ValueError("Versi varian tidak ditemukan.")
                self.reply(200, {"original": original_record(original), "variant": variant,
                                 "history": store.versions_of_seed(qid, seed),
                                 "seeds": sorted(store.latest_by_seed(qid)), "seed": seed,
                                 "config": cfg, "config_versions": versions,
                                 "latest_config_version": versions[-1] if versions else 0,
                                 "config_hash": latest_hash})
            else:
                self.reply(404, {"error": "Halaman tidak ditemukan."})
        except (ValueError, *KNOWN_ERRORS) as error:
            self.reply(400, {"error": str(error)})
        except OSError as error:
            self.reply(500, {"error": str(error)})

    def do_POST(self):
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 262144:
                self.reply(413, {"error": "Body JSON kosong atau melebihi 256 KB."})
                return
            body = self.rfile.read(size)  # Consume bounded bodies before rejecting/closing on Windows.
            if not self.local_request():
                return
            if self.headers.get_content_type() != "application/json":
                self.reply(415, {"error": "Content-Type harus application/json."})
                return
            data = json.loads(body)
            if not isinstance(data, dict):
                raise ValueError("Body harus berupa objek JSON.")
            json.dumps(data, allow_nan=False)
            qid = data.get("question_id")
            if not isinstance(qid, str):
                raise ValueError("question_id harus berupa teks.")
            original = self.server.bank.get(qid)
            configs, store = self.server.configs, self.server.store
            path = urlsplit(self.path).path
            if path in ("/api/generate", "/api/regen"):
                seed = positive_integer(data.get("seed"))
                reason = data.get("reason", "")
                if not isinstance(reason, str):
                    raise ValueError("Alasan regen harus berupa teks.")
                args = argparse.Namespace(question_id=qid, seed=str(seed), seeds=str(seed),
                                          reason=reason, json=True)
                output, errors = io.StringIO(), io.StringIO()
                command = cmd_gen if path == "/api/generate" else cmd_regen
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                    status = command(args, self.server.bank, configs, store)
                if status:
                    raise ValueError(errors.getvalue().strip())
                self.reply(200, json.loads(output.getvalue()))
            elif path in ("/api/config", "/api/lint"):
                cfg = data.get("config")
                if not isinstance(cfg, dict):
                    raise ConfigError("Config harus berupa objek JSON.")
                versions = configs.versions(qid)
                latest_version = versions[-1] if versions else 0
                latest_hash = configs.load(qid)[1] if versions else None
                if path == "/api/config":
                    if data.get("base_version") != latest_version or data.get("base_hash") != latest_hash:
                        self.reply(409, {"error": "Config sudah berubah. Muat ulang sebelum menyimpan."})
                        return
                    cfg = dict(cfg, config_version=latest_version + 1)
                ok, lines = check_draft(cfg, original)
                if path == "/api/lint":
                    self.reply(200, {"ok": ok, "lines": lines})
                    return
                if not ok:
                    raise ConfigError("\n".join(lines))
                target = configs.root / qid / f"v{cfg['config_version']}.json"
                text = (json.dumps(cfg, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
                target.parent.mkdir(parents=True, exist_ok=True)
                # ponytail: one local HTTP process; do not run another writer on these files.
                # Upgrade to a shared lock/transaction before supporting concurrent writers.
                with target.open("xb") as file:
                    try:
                        file.write(text)
                        file.flush()
                    except OSError:
                        file.close()
                        target.unlink()
                        raise
                self.reply(200, {"config_version": cfg["config_version"], "lines": lines})
            else:
                self.reply(404, {"error": "Aksi tidak ditemukan."})
        except (ValueError, UnicodeError, *KNOWN_ERRORS) as error:
            self.reply(400, {"error": str(error)})
        except OSError as error:
            self.reply(500, {"error": str(error)})


def make_server(port=8765, bank=HERE / "data" / "q0_bank.csv",
                configs=HERE / "configs", store=HERE / "store" / "variants.jsonl"):
    originals = OriginalBank(bank)
    server = HTTPServer(("127.0.0.1", port), Handler)
    server.bank, server.configs, server.store = originals, ConfigStore(configs), VariantStore(store)
    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--bank", type=Path, default=HERE / "data" / "q0_bank.csv")
    parser.add_argument("--configs", type=Path, default=HERE / "configs")
    parser.add_argument("--store", type=Path, default=HERE / "store" / "variants.jsonl")
    args = parser.parse_args()
    try:
        with make_server(args.port, args.bank, args.configs, args.store) as server:
            print(f"Buka http://127.0.0.1:{server.server_port} — Ctrl+C untuk berhenti.", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        pass
    except (OSError, ValueError, *KNOWN_ERRORS) as error:
        parser.exit(1, f"error: {error}\n")
