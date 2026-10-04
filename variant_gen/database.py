"""Direct PostgreSQL catalogue reads. Credentials stay in the Python backend."""
import os
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

import psycopg
from psycopg.conninfo import conninfo_to_dict
from psycopg.rows import dict_row


class DatabaseError(Exception):
    def __init__(self, message, status=503):
        super().__init__(message)
        self.status = status


def identifier(value):
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        raise ValueError('ID database harus UUID yang valid.') from None


def pagination(limit, offset):
    if type(limit) is not int or type(offset) is not int or limit < 1 or offset < 0:
        raise ValueError('Limit harus bilangan bulat positif; offset tidak boleh negatif.')


def json_value(value):
    if isinstance(value, dict):
        return {key: json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_value(item) for item in value]
    if isinstance(value, (UUID, Decimal)):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


@contextmanager
def connection():
    url = os.environ.get('DATABASE_URL', '').strip()
    if not url:
        raise DatabaseError('Isi DATABASE_URL di .env repo Numora-ai-service, lalu restart interface.')
    try:
        settings = conninfo_to_dict(url)
        hosts = settings.get('host', '').split(',')
        local = all(host in ('localhost', '127.0.0.1', '::1') for host in hosts)
        tls = {} if local else {'sslmode': settings.get('sslmode') if settings.get('sslmode') in
                               ('require', 'verify-ca', 'verify-full') else 'require'}
        with psycopg.connect(url, connect_timeout=5, options='-c statement_timeout=5000',
                             row_factory=dict_row, **tls) as db:
            db.read_only = True
            db.isolation_level = psycopg.IsolationLevel.REPEATABLE_READ
            yield db
    except (psycopg.Error, ValueError):
        raise DatabaseError('Database belum dapat dibaca. Periksa DATABASE_URL, jaringan, TLS, schema, dan izin akun.') from None


PACKAGE_COLUMNS = '''p.id, p.family_code AS "familyCode", p.package_version AS "packageVersion",
    p.name, p.assessment_type AS "assessmentType", p.purpose, p.status,
    p.is_demo AS "isDemo", p.chapter_id AS "chapterId", p.level_id AS "levelId",
    p.variant_index AS "variantIndex", p.duration_seconds AS "durationSeconds",
    p.release_at AS "releaseAt", p.close_at AS "closeAt"'''

VERSION_COLUMNS = '''v.id AS "versionId", v.version_number AS "versionNumber",
    v.question_type AS "questionType", v.stem, v.options_or_statements AS "optionsOrStatements",
    v.answer_key AS "answerKey", v.explanation, v.media, v.difficulty,
    v.parent_original_question_version_id AS "parentOriginalQuestionVersionId",
    v.revised_from_question_version_id AS "revisedFromQuestionVersionId",
    v.level_id AS "levelId", v.scoring_rubric_version_id AS "scoringRubricVersionId",
    v.content_fingerprint AS "contentFingerprint", v.validation_state AS "validationState",
    v.content_status AS "contentStatus", q.id AS "variantId", q.question_id AS "familyId",
    q.original_variant_id AS "originalVariantId", q.variant_code AS "variantCode", q.kind, q.origin'''


def page(db, count_sql, items_sql, params, limit, offset):
    total = db.execute(count_sql, params).fetchone()['total']
    items = db.execute(items_sql, (*params, limit, offset)).fetchall()
    return json_value(dict(items=items, total=total, limit=limit, offset=offset))


def status():
    with connection() as db:
        db.execute('SELECT 1 FROM public.assessment_packages LIMIT 0')
        db.execute('SELECT 1 FROM public.package_items LIMIT 0')
        db.execute('SELECT 1 FROM public.question_versions LIMIT 0')
        db.execute('SELECT 1 FROM public.question_variants LIMIT 0')
    return {'configured': True, 'connected': True, 'mode': 'read-only'}


def packages(assessment_type=None, limit=50, offset=0):
    pagination(limit, offset)
    if assessment_type not in (None, 'DRILL', 'TRYOUT', 'PRETEST', 'PVP'):
        raise ValueError('Aktivitas database tidak valid.')
    where = ' WHERE p.assessment_type = %s' if assessment_type else ''
    params = (assessment_type,) if assessment_type else ()
    with connection() as db:
        return page(db, 'SELECT count(*) AS total FROM public.assessment_packages p' + where,
                    f'''SELECT {PACKAGE_COLUMNS}, count(i.id) AS "itemCount"
                        FROM public.assessment_packages p LEFT JOIN public.package_items i ON i.package_id = p.id
                        {where} GROUP BY p.id ORDER BY p.name, p.package_version, p.id LIMIT %s OFFSET %s''',
                    params, limit, offset)


def package(package_id, limit=100, offset=0):
    package_id = identifier(package_id)
    pagination(limit, offset)
    with connection() as db:
        metadata = db.execute(f'SELECT {PACKAGE_COLUMNS} FROM public.assessment_packages p WHERE p.id = %s',
                              (package_id,)).fetchone()
        if metadata is None:
            raise DatabaseError('Paket tidak ditemukan atau tidak terlihat oleh akun ini.', 404)
        result = page(db, 'SELECT count(*) AS total FROM public.package_items WHERE package_id = %s',
                      f'''SELECT i.id AS "itemId", i.question_version_id AS "questionVersionId",
                          i.display_order AS "displayOrder", i.max_points AS "maxPoints",
                          i.rubric_version_id AS "rubricVersionId", i.maximum_score_category AS "maximumScoreCategory",
                          i.item_role AS "itemRole", {VERSION_COLUMNS}
                          FROM public.package_items i LEFT JOIN public.question_versions v ON v.id = i.question_version_id
                          LEFT JOIN public.question_variants q ON q.id = v.variant_id
                          WHERE i.package_id = %s ORDER BY i.display_order, i.id LIMIT %s OFFSET %s''',
                      (package_id,), limit, offset)
        return dict(result, package=json_value(metadata))


def family(family_id, limit=100, offset=0):
    family_id = identifier(family_id)
    pagination(limit, offset)
    source = '''FROM public.question_versions v JOIN public.question_variants q ON q.id = v.variant_id
                WHERE q.question_id = %s'''
    with connection() as db:
        return page(db, 'SELECT count(*) AS total ' + source,
                    f'''SELECT {VERSION_COLUMNS} {source}
                        ORDER BY q.kind, q.variant_code, v.version_number, v.id LIMIT %s OFFSET %s''',
                    (family_id,), limit, offset)
