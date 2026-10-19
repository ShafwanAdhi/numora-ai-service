"""Start a disposable cluster, migrate using Numora, run role-bound integration.

Never reads .env or uses shared databases. Requires local PostgreSQL binaries
and the built canonical Numora migration module. No production guard is edited.
"""
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    repo = Path(os.environ.get("NUMORA_REPO_PATH", "D:/Dev/Numora")).resolve()
    binaries = Path(os.environ.get("POSTGRES_BIN", str(repo / ".tmp/pg-runtime/node_modules/@embedded-postgres/windows-x64/native/bin")))
    suffix = ".exe" if os.name == "nt" else ""
    if not (binaries / ("initdb" + suffix)).exists():
        raise SystemExit("Set POSTGRES_BIN to local PostgreSQL binaries.")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    with tempfile.TemporaryDirectory(prefix="generator-local-") as directory:
        target = Path(directory).resolve()
        cluster = target / "cluster"
        def run(*args, env=None):
            with (target / "command.log").open("w", encoding="utf-8") as log:
                result = subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, timeout=180, env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0, cwd=ROOT)
            if result.returncode:
                raise RuntimeError((target / "command.log").read_text(encoding="utf-8", errors="replace"))
            return (target / "command.log").read_text(encoding="utf-8", errors="replace")
        run(str(binaries / ("initdb" + suffix)), "-D", str(cluster), "-U", "fixture", "-A", "trust", "--no-locale", "-E", "UTF8")
        run(str(binaries / ("pg_ctl" + suffix)), "-D", str(cluster), "-l", str(target / "postgres.log"),
            "-o", f"-h 127.0.0.1 -p {port}", "-w", "start")
        try:
            import psycopg
            database = "generator_test_" + uuid4().hex
            url = f"postgresql://fixture@127.0.0.1:{port}/{database}"
            with psycopg.connect(f"postgresql://fixture@127.0.0.1:{port}/postgres", autocommit=True) as db:
                db.execute(psycopg.sql.SQL("CREATE DATABASE {}").format(psycopg.sql.Identifier(database)))
            env = {**os.environ, "NUMORA_REPO_PATH": str(repo), "TEST_COMPUTE_OWNER_URL": url,
                   "PYTHONIOENCODING": "utf-8", "NODE_ENV": "test"}
            print(run("node", str(ROOT / "tests/service/migrate_local.mjs"), env=env).strip())
            print(run(sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests/service", "-p", "test_postgres.py", "-v", env=env))
        finally:
            run(str(binaries / ("pg_ctl" + suffix)), "-D", str(cluster), "-m", "fast", "-w", "stop")


if __name__ == "__main__":
    main()
