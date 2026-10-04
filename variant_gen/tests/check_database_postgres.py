"""Opt-in real SQL check: python -B tests/check_database_postgres.py.

Creates a disposable LOCAL cluster; never reads DATABASE_URL or the repo .env.
Requires PostgreSQL initdb/pg_ctl binaries (PATH or Windows default).
"""
import os
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import database


def main():
    binaries = Path('C:/Program Files/PostgreSQL/16/bin')
    def executable(name):
        return shutil.which(name) or str(binaries / f'{name}.exe')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    with tempfile.TemporaryDirectory(prefix='numora-db-check-') as directory:
        target = Path(directory).resolve()
        assert target.parent == Path(tempfile.gettempdir()).resolve()
        cluster = target / 'cluster'
        def run(*args):
            # Windows postgres inherits pipe handles; a file avoids waiting for server EOF.
            output = target / 'command.log'
            with output.open('w') as log:
                result = subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, timeout=60,
                                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            if result.returncode:
                raise RuntimeError(output.read_text(errors='replace'))
        run(executable('initdb'), '-D', str(cluster), '-U', 'fixture', '-A', 'trust', '--no-locale', '-E', 'UTF8')
        run(executable('pg_ctl'), '-D', str(cluster), '-l', str(target / 'postgres.log'),
            '-o', f'-h 127.0.0.1 -p {port}', '-w', 'start')
        try:
            url = f'postgresql://fixture@127.0.0.1:{port}/postgres'
            package_id, empty_id, family_id, original_id, variant_id, v1, v2, variant_version = map(str, (uuid4() for _ in range(8)))
            with database.psycopg.connect(url, autocommit=True) as db:
                db.execute('''
                    CREATE TABLE assessment_packages (id uuid PRIMARY KEY, family_code text, package_version int,
                      name text, assessment_type text, purpose text, status text, is_demo boolean,
                      chapter_id uuid, level_id uuid, variant_index int, duration_seconds int,
                      release_at timestamptz, close_at timestamptz);
                    CREATE TABLE question_variants (id uuid PRIMARY KEY, question_id uuid, original_variant_id uuid,
                      variant_code text, kind text, origin text);
                    CREATE TABLE question_versions (id uuid PRIMARY KEY, variant_id uuid, version_number int,
                      question_type text, stem jsonb, options_or_statements jsonb, answer_key jsonb,
                      explanation jsonb, media jsonb, difficulty text, parent_original_question_version_id uuid,
                      revised_from_question_version_id uuid, level_id uuid, scoring_rubric_version_id uuid,
                      content_fingerprint text, validation_state text, content_status text);
                    CREATE TABLE package_items (id uuid PRIMARY KEY, package_id uuid, question_version_id uuid,
                      display_order int, max_points numeric, rubric_version_id uuid,
                      maximum_score_category int, item_role text);
                    CREATE ROLE browser LOGIN;
                    GRANT SELECT ON ALL TABLES IN SCHEMA public TO browser;
                ''')
                for pid, name in ((package_id, 'Pinned'), (empty_id, 'Empty')):
                    db.execute('''INSERT INTO assessment_packages
                        (id, family_code, package_version, name, assessment_type, purpose, status, is_demo)
                        VALUES (%s, 'fixture', 1, %s, 'DRILL', 'REGULAR', 'DRAFT', true)''', (pid, name))
                for vid, kind, parent in ((original_id, 'ORIGINAL', None), (variant_id, 'VARIANT', original_id)):
                    db.execute('INSERT INTO question_variants VALUES (%s,%s,%s,%s,%s,%s)',
                               (vid, family_id, parent, kind, kind, 'fixture'))
                for version, vid, number, text in ((v1, original_id, 1, 'pinned-v1'),
                                                  (v2, original_id, 2, 'new-v2'),
                                                  (variant_version, variant_id, 1, 'variant')):
                    db.execute('''INSERT INTO question_versions (id,variant_id,version_number,question_type,stem,
                        options_or_statements,answer_key,explanation,difficulty,validation_state,content_status)
                        VALUES (%s,%s,%s,'PG',%s,'[]','{}','{}','demo','DRAFT','DRAFT')''',
                               (version, vid, number, database.psycopg.types.json.Jsonb({'text': text})))
                db.execute('INSERT INTO package_items (id,package_id,question_version_id,display_order,max_points) VALUES (%s,%s,%s,1,2.5)',
                           (str(uuid4()), package_id, v1))
            with patch.dict(os.environ, {'DATABASE_URL': f'postgresql://browser@127.0.0.1:{port}/postgres'}):
                assert database.status()['connected']
                packages = database.packages('DRILL', limit=1)
                assert packages['total'] == 2 and packages['items'][0]['itemCount'] == 0
                assert len(database.packages(offset=1, limit=1)['items']) == 1
                assert database.package(empty_id)['items'] == []
                item = database.package(package_id)['items'][0]
                assert item['versionId'] == v1 and item['stem']['text'] == 'pinned-v1'
                assert len(database.family(family_id)['items']) == 3
                with database.connection() as db:
                    assert db.execute('SHOW transaction_read_only').fetchone()['transaction_read_only'] == 'on'
                    assert db.execute('SHOW transaction_isolation').fetchone()['transaction_isolation'] == 'repeatable read'
                    assert db.execute('SHOW statement_timeout').fetchone()['statement_timeout'] == '5s'
            print('PostgreSQL fixture: empty packages, pagination, pinned v1, historical versions, direct SELECT role, read-only transaction OK')
        finally:
            run(executable('pg_ctl'), '-D', str(cluster), '-m', 'fast', '-w', 'stop')


if __name__ == '__main__':
    main()
