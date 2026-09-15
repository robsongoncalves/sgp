import unittest
from unittest.mock import patch
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()
from app import create_app
from app.extensions import db
from app.models import Service, ServiceSituation, ServiceRequest, ServiceRequestMovement, User, DocumentType, ServiceRequestDocument


class CancellationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.context = self.app.app_context()
        self.context.push()
        self.client = self.app.test_client()
        self.commit = patch.object(db.session, 'commit', side_effect=db.session.flush)
        self.commit.start()
        self.user = User.query.first()
        self.service = Service(name='Cancellation test', slug=str(uuid4()), implementation_mode='standard')
        db.session.add(self.service)
        db.session.flush()
        self.situation = ServiceSituation(service_id=self.service.id, name='Solicitacao', is_initial=True)
        db.session.add(self.situation)
        db.session.flush()
        self.item = ServiceRequest(number=str(uuid4())[:25], service_id=self.service.id,
            requester_user_id=self.user.id, current_situation_id=self.situation.id,
            status='Submetido para CPPD', form_data={'preserved': True})
        db.session.add(self.item)
        db.session.flush()

    def tearDown(self):
        db.session.rollback()
        self.commit.stop()
        db.session.remove()
        self.context.pop()

    def test_cancel_preserves_history_and_allows_new_request(self):
        document_type = DocumentType.query.first()
        doc = ServiceRequestDocument(service_request_id=self.item.id, service_situation_id=self.situation.id,
            document_type_id=document_type.id, created_by_user_id=self.user.id,
            assigned_to_user_id=self.user.id, status='submitted', content_data={'text': 'Keep'})
        db.session.add(doc)
        db.session.flush()
        response = self.client.post(f'/api/service-requests/{self.item.id}/cancel', json={'user_id': self.user.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'Cancelada')
        self.assertEqual(response.json['situation_before_cancellation'], 'Submetido para CPPD')
        self.assertEqual(response.json['canceled_by_user_id'], self.user.id)
        self.assertIsNotNone(response.json['canceled_at'])
        self.assertEqual(response.json['form_data'], {'preserved': True})
        self.assertEqual(db.session.get(ServiceRequestDocument, doc.id).content_data, {'text': 'Keep'})
        assigned = self.client.get(f'/api/service-request-documents?assigned_to_user_id={self.user.id}').json
        self.assertFalse(any(d['id'] == doc.id for d in assigned))
        self.client.post(f'/api/service-requests/{self.item.id}/cancel', json={'user_id': self.user.id})
        self.assertEqual(ServiceRequestMovement.query.filter_by(service_request_id=self.item.id).count(), 1)
        for path, method in [('form-data', 'patch'), ('situation', 'patch'), ('documents', 'post'),
                             (f'documents/{doc.id}', 'delete'), ('attachments', 'post')]:
            result = getattr(self.client, method)(f'/api/service-requests/{self.item.id}/{path}', json={})
            self.assertEqual(result.status_code, 409)
        new = self.client.post('/api/service-requests', json={'service_id': self.service.id, 'requester_user_id': self.user.id})
        self.assertEqual(new.status_code, 201)
        self.assertNotEqual(new.json['id'], self.item.id)
        self.assertEqual(new.json['current_situation_name'], 'Solicitacao')

    def test_reject_other_user_and_completed_request(self):
        self.assertEqual(self.client.post(f'/api/service-requests/{self.item.id}/cancel', json={'user_id': 2147483647}).status_code, 403)
        self.situation.is_final = True
        db.session.flush()
        self.assertEqual(self.client.post(f'/api/service-requests/{self.item.id}/cancel', json={'user_id': self.user.id}).status_code, 409)
        self.assertIsNone(self.item.canceled_at)

    def test_situation_name_is_preserved(self):
        response = self.client.get(f'/api/service-requests/{self.item.id}')
        self.assertEqual(response.json['current_situation_name'], 'Submetido para CPPD')

    def test_save_situation_updates_catalog_and_new_requests_only(self):
        service = next(s for s in self.client.get('/api/services').json if s['id'] == self.service.id)
        service['situations'][0]['name'] = 'Nome atualizado'
        response = self.client.put(f'/api/services/{self.service.id}/situations', json={'situations': service['situations']})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['situations'][0]['name'], 'Nome atualizado')
        self.assertEqual(self.client.get(f'/api/service-requests/{self.item.id}').json['current_situation_name'], 'Submetido para CPPD')
        self.client.post(f'/api/service-requests/{self.item.id}/cancel', json={'user_id': self.user.id})
        new = self.client.post('/api/service-requests', json={'service_id': self.service.id, 'requester_user_id': self.user.id})
        self.assertEqual(new.status_code, 201)
        self.assertEqual(new.json['current_situation_name'], 'Nome atualizado')
