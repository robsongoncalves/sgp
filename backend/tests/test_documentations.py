"""Integration checks inside a rolled-back transaction on the configured database."""
import unittest
from unittest.mock import patch
from uuid import uuid4

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db
from app.models import Documentation, Service


class DocumentationsTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.context = self.app.app_context()
        self.context.push()
        self.client = self.app.test_client()
        self.commit = patch.object(db.session, 'commit', side_effect=db.session.flush)
        self.commit.start()

    def tearDown(self):
        db.session.rollback()
        self.commit.stop()
        db.session.remove()
        self.context.pop()

    def test_crud_and_shared_service_content(self):
        response = self.client.post('/api/documentations', json={
            'url': 'https://example.org/doc', 'description': '<p>Original</p>', 'headings': ['Topic']})
        self.assertEqual(response.status_code, 201)
        item_id = response.json['id']
        payload = {'name': 'Documentation test', 'slug': str(uuid4()),
                   'implementation_mode': 'standard', 'documentation_id': item_id}
        response = self.client.post('/api/services', json=payload)
        self.assertEqual(response.status_code, 201)
        service_id = response.json['id']
        self.assertEqual(response.json['description'], '<p>Original</p>')
        self.assertEqual(self.client.delete(f'/api/documentations/{item_id}').status_code, 409)
        self.assertEqual(self.client.put(f'/api/documentations/{item_id}', json={
            'url': 'https://example.org/updated', 'description': '<p>Updated</p>', 'headings': []}).status_code, 200)
        public = self.client.get('/api/public/services').json
        service = next(item for item in public if item['id'] == service_id)
        self.assertEqual(service['description_text'], 'Updated')
        self.assertEqual(service['documentation_url'], 'https://example.org/updated')
        self.assertEqual(self.client.get(f'/api/documentations/{item_id}').json['headings'], [])
        self.assertTrue(any(item['id'] == item_id for item in self.client.get('/api/documentations').json))
        payload['documentation_id'] = None
        self.assertEqual(self.client.put(f'/api/services/{service_id}', json=payload).status_code, 200)
        self.assertEqual(self.client.delete(f'/api/documentations/{item_id}').status_code, 204)
        self.assertEqual(self.client.get(f'/api/documentations/{item_id}').status_code, 404)

    def test_invalid_url_and_reference(self):
        self.assertEqual(self.client.post('/api/documentations', json={'url': 'javascript:alert(1)'}).status_code, 400)
        self.assertEqual(self.client.post('/api/services', json={
            'name': 'Invalid', 'implementation_mode': 'standard', 'documentation_id': -1}).status_code, 400)

    def test_sync_flag_and_batch_preserve_failed_and_unmarked(self):
        # Isolate the selection even if the configured database has opt-in records.
        Documentation.query.update({'sync_enabled': False})
        ids = []
        for flag, headings in [(True, ['Topic']), (True, []), (True, []), (False, [])]:
            response = self.client.post('/api/documentations', json={
                'url': 'https://example.org/doc', 'description': 'Previous',
                'headings': headings, 'sync_enabled': flag})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json['sync_enabled'], flag)
            ids.append(response.json['id'])
        calls = []
        def extract(payload):
            calls.append(payload)
            if len(calls) == 2:
                return None, 'Fetch failed'
            return {'description': '<p>Synced</p>'}, None
        with patch('app.routes.documentations.extract_documentation_sections', side_effect=extract):
            response = self.client.post('/api/documentations/sync')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['updated'], 2)
        self.assertEqual(response.json['failed'], 1)
        self.assertEqual(len(calls), 3)
        self.assertIn([], [call['headings'] for call in calls])
        failed_id = response.json['errors'][0]['id']
        self.assertEqual(db.session.get(Documentation, failed_id).description, 'Previous')
        self.assertEqual(db.session.get(Documentation, ids[-1]).description, 'Previous')

    def test_sync_empty_content_preserves_description(self):
        Documentation.query.update({'sync_enabled': False})
        item = Documentation(url='https://example.org/doc', description='Keep', headings=[], sync_enabled=True)
        db.session.add(item)
        db.session.flush()
        with patch('app.routes.documentations.extract_documentation_sections', return_value=({'description': ''}, None)):
            response = self.client.post('/api/documentations/sync')
        self.assertEqual(response.json['failed'], 1)
        self.assertEqual(item.description, 'Keep')

    def test_import_returns_draft_without_saving(self):
        count = Documentation.query.count()
        result = {'description': '<p>Imported</p>', 'headings': ['Topic']}
        with patch('app.routes.documentations.extract_documentation_sections', return_value=(result, None)):
            response = self.client.post('/api/documentations/import', json={'url': 'https://example.org/doc'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['description'], '<p>Imported</p>')
        self.assertEqual(Documentation.query.count(), count)
