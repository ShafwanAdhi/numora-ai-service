"""Database boundary checks; no external database or credentials required."""
import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import database

ID = '00000000-0000-0000-0000-000000000001'


class Database(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict('os.environ', {'DATABASE_URL': ''})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_missing_configuration_never_connects(self):
        with patch('database.psycopg.connect') as connect:
            with self.assertRaises(database.DatabaseError) as caught:
                database.status()
            self.assertEqual(caught.exception.status, 503)
            self.assertIn('DATABASE_URL', str(caught.exception))
            connect.assert_not_called()

    def test_invalid_inputs_never_connect(self):
        with patch('database.psycopg.connect') as connect:
            for work in (lambda: database.package('../secret'),
                         lambda: database.family('invalid'),
                         lambda: database.packages('SQL'),
                         lambda: database.packages(limit=0),
                         lambda: database.packages(offset=-1),
                         lambda: database.packages(limit=True)):
                with self.assertRaises(ValueError):
                    work()
            connect.assert_not_called()

    def connection(self, rows):
        mock = MagicMock()
        mock.__enter__.return_value = mock
        mock.execute.side_effect = [MagicMock(fetchone=MagicMock(return_value=row))
                                    if not isinstance(row, list) else
                                    MagicMock(fetchall=MagicMock(return_value=row)) for row in rows]
        return mock

    def test_empty_package_and_read_only_connection(self):
        connection = self.connection([{'id': UUID(ID), 'name': 'Kosong'}, {'total': 0}, []])
        with patch.dict('os.environ', {'DATABASE_URL': 'postgresql://user:secret@localhost/db'}), \
                patch('database.psycopg.connect', return_value=connection) as connect:
            result = database.package(ID)
        self.assertEqual(result['total'], 0)
        self.assertEqual(result['items'], [])
        self.assertEqual(result['package']['id'], ID)
        self.assertTrue(connection.read_only)
        self.assertEqual(connect.call_args.kwargs['connect_timeout'], 5)
        self.assertIn('statement_timeout=5000', connect.call_args.kwargs['options'])
        self.assertEqual(connection.isolation_level, database.psycopg.IsolationLevel.REPEATABLE_READ)

    def test_driver_errors_never_expose_credentials(self):
        with patch.dict('os.environ', {'DATABASE_URL': 'postgresql://user:secret@cloud/db'}), \
                patch('database.psycopg.connect', side_effect=database.psycopg.OperationalError('secret password DSN')):
            with self.assertRaises(database.DatabaseError) as caught:
                database.status()
        self.assertEqual(caught.exception.status, 503)
        self.assertNotIn('secret', str(caught.exception))

    def test_package_uses_pinned_version_and_preserves_missing_content(self):
        rows = [{'id': ID}, {'total': 1}, [{'questionVersionId': ID, 'stem': None, 'maxPoints': Decimal('2.50')}]]
        connection = self.connection(rows)
        with patch.dict('os.environ', {'DATABASE_URL': 'postgresql://u:p@localhost/db'}), \
                patch('database.psycopg.connect', return_value=connection):
            result = database.package(ID, limit=10001)
        sql, params = connection.execute.call_args.args
        self.assertIn('v.id = i.question_version_id', sql)
        self.assertIn('LEFT JOIN public.question_versions', sql)
        self.assertEqual(params, (ID, 10001, 0))
        self.assertIsNone(result['items'][0]['stem'])
        self.assertEqual(result['items'][0]['maxPoints'], '2.50')
        json.dumps(result)

    def test_missing_package_is_404(self):
        connection = self.connection([None])
        with patch.dict('os.environ', {'DATABASE_URL': 'postgresql://u:p@localhost/db'}), \
                patch('database.psycopg.connect', return_value=connection):
            with self.assertRaises(database.DatabaseError) as caught:
                database.package(ID)
        self.assertEqual(caught.exception.status, 404)


if __name__ == '__main__':
    unittest.main()
