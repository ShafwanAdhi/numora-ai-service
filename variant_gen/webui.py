"""Local variant workbench: python -B webui.py."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from dotenv import load_dotenv
import database

from bank import OriginalBank, load_workspace_bank
from tryout import generate_package
import re
from cli import KNOWN_ERRORS, preview
from config_store import ConfigError, ConfigStore, validate_config
from engine import original_record
from expr import ExprError
from lint import run_lint
from conceptual_stock import load_stock, stock_record

HERE = Path(__file__).resolve().parent
load_dotenv(HERE.parent / '.env', override=False)


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
            bank, configs = self.server.bank, self.server.configs
            if url.path == "/":
                self.reply(200, (HERE / "webui.html").read_text(encoding="utf-8"), "text/html")
            elif url.path.startswith('/api/database/'):
                query = parse_qs(url.query, keep_blank_values=True, max_num_fields=10)
                if any(len(values) != 1 for values in query.values()):
                    raise ValueError('Parameter database tidak boleh berulang.')
                route = url.path.rsplit('/', 1)[-1]
                allowed = {'status': set(), 'packages': {'type', 'limit', 'offset'},
                           'package': {'id', 'limit', 'offset'}, 'family': {'id', 'limit', 'offset'}}
                if route not in allowed:
                    self.reply(404, {'error': 'Halaman tidak ditemukan.'})
                    return
                if query.keys() - allowed[route]:
                    raise ValueError('Parameter database tidak dikenal.')
                get = lambda key, default: query.get(key, [default])[0]
                if route == 'status':
                    result = database.status()
                else:
                    limit = int(get('limit', '50' if route == 'packages' else '100'))
                    offset = int(get('offset', '0'))
                    result = (database.packages(get('type', '') or None, limit, offset) if route == 'packages'
                              else getattr(database, route)(get('id', ''), limit, offset))
                self.reply(200, result)
            elif url.path == "/api/questions":
                self.reply(200, [{"id": qid, "format": bank.get(qid)["format"],
                                  "stem": bank.get(qid)["stem"], "has_config": bool(configs.versions(qid)),
                                  "stock_count": len(self.server.stock.get(qid, [])),
                                  "variant_mode": ('stock' if self.server.stock.get(qid) else
                                                   'generator' if configs.versions(qid) else 'unavailable'),
                                  "classification": bank.get(qid).get("classification"),
                                  "metadata": bank.get(qid).get("metadata")}
                                 for qid in bank.ids()])
            elif url.path == "/api/catalog":
                self.reply(200, bank.catalog())
            elif url.path == "/api/question":
                query = parse_qs(url.query, keep_blank_values=True, max_num_fields=10)
                if any(len(values) != 1 for values in query.values()):
                    raise ValueError('Parameter soal tidak boleh berulang.')
                qid = query.get("id", [""])[0]
                original = bank.get(qid)  # Check bank membership before using any ID as a path.
                items = self.server.stock.get(qid, [])
                selected = None
                if items or 'stock_variant' in query:
                    index = int(query.get('stock_variant', ['1'])[0])
                    if not 1 <= index <= len(items):
                        raise ValueError(f'Nomor varian tidak tersedia; stok aktual {len(items)} (maksimal 4).')
                    selected = stock_record(original, items[index - 1])
                seed = positive_integer(int(query.get("seed", ["1"])[0]))
                ver = query.get("version", [""])[0]
                ver = positive_integer(int(ver)) if ver else None
                versions = configs.versions(qid)
                latest, latest_hash = configs.load(qid) if versions else (None, None)
                cfg_ver = query.get("config_version", [""])[0]
                cfg = configs.load(qid, positive_integer(int(cfg_ver)))[0] if cfg_ver else latest
                if ver:
                    raise ValueError("Riwayat varian tidak tersedia; gunakan generate.")
                self.reply(200, {"original": original_record(original), "variant": selected,
                                 "variant_mode": 'stock' if items else 'generator' if versions else 'unavailable',
                                 "stock_count": len(items),
                                 "stock_variants": [{k: item[k] for k in ('variant_id', 'stock_index', 'stock_version')} for item in items],
                                 "seed": seed,
                                 "config": cfg, "config_versions": versions,
                                 "latest_config_version": versions[-1] if versions else 0,
                                 "config_hash": latest_hash})
            else:
                self.reply(404, {"error": "Halaman tidak ditemukan."})
        except database.DatabaseError as error:
            self.reply(error.status, {'error': str(error)})
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
            if urlsplit(self.path).path.startswith('/api/database/'):
                self.reply(405, {'error': 'Database saat ini hanya mendukung pembacaan GET.'})
                return
            if self.headers.get_content_type() != "application/json":
                self.reply(415, {"error": "Content-Type harus application/json."})
                return
            data = json.loads(body)
            if not isinstance(data, dict):
                raise ValueError("Body harus berupa objek JSON.")
            json.dumps(data, allow_nan=False)
            if urlsplit(self.path).path not in ('/api/tryout/generate-package', '/api/generate', '/api/config', '/api/lint'):
                self.reply(404, {"error": "Aksi tidak ditemukan."})
                return
            if urlsplit(self.path).path == '/api/tryout/generate-package':
                package_id=data.get('package_id')
                if not isinstance(package_id,str) or not re.fullmatch(r'[a-z0-9-]+',package_id):
                    raise ValueError('ID paket tidak valid.')
                seed=positive_integer(data.get('seed'))
                result=generate_package(self.server.bank,self.server.configs,package_id,seed)
                self.reply(200,result)
                return
            qid = data.get("question_id")
            if not isinstance(qid, str):
                raise ValueError("question_id harus berupa teks.")
            original = self.server.bank.get(qid)
            if original.get('metadata',{}).get('generation_status','ACTIVE')!='ACTIVE':
                raise ConfigError(original['metadata']['reason'])
            configs = self.server.configs
            path = urlsplit(self.path).path
            if path == "/api/generate":
                seed = positive_integer(data.get("seed"))
                self.reply(200, preview(self.server.bank, configs, qid, seed))
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
                configs=HERE / "configs", store=HERE / "store" / "variants.jsonl", stock=None):
    originals = load_workspace_bank(bank)
    stock_items = load_stock(stock or Path(bank).with_name('conceptual_stock.json'), originals)
    server = HTTPServer(("127.0.0.1", port), Handler)
    server.bank, server.configs = originals, ConfigStore(configs)
    server.stock = stock_items
    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--bank", type=Path, default=HERE / "data" / "q0_bank.csv")
    parser.add_argument("--configs", type=Path, default=HERE / "configs")
    parser.add_argument("--store", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--stock", type=Path)
    args = parser.parse_args()
    try:
        with make_server(args.port, args.bank, args.configs, args.store, args.stock) as server:
            print(f"Buka http://127.0.0.1:{server.server_port} — Ctrl+C untuk berhenti.", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        pass
    except (OSError, ValueError, *KNOWN_ERRORS) as error:
        parser.exit(1, f"error: {error}\n")
