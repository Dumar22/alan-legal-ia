import io
import json
import unittest
from unittest.mock import patch, MagicMock

from main import app


class MainAppTestCase(unittest.TestCase):

    def setUp(self):
        """Set up a test client for the app."""
        self.app = app.test_client()
        self.app.testing = True

    def test_home_status_code(self):
        """Test if the home page loads correctly."""
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

    def test_chat_empty_message(self):
        """Test chat endpoint with an empty message returns friendly hint."""
        response = self.app.post('/chat', data={'message': ''})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertEqual(data['response'], 'Por favor escribe algo 😅')

    @patch('main.predict_cluster')
    def test_chat_greeting_message(self, mock_predict):
        """Test chat endpoint with a greeting message (mock cluster prediction)."""
        mock_predict.return_value = 0
        response = self.app.post('/chat', data={'message': 'Hola'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertTrue(len(data['response']) > 0)

    def test_upload_no_files(self):
        """Test upload endpoint with no files."""
        response = self.app.post('/upload')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('success', data)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], '❌ No se enviaron archivos')

    @patch('main.procesar_documento')
    @patch('main.save_document_to_db')
    def test_upload_single_file_success(self, mock_save_db, mock_procesar):
        """Test uploading a single valid file — mock processing and DB save."""
        mock_procesar.return_value = (True, '✅ Documento procesado')
        mock_save_db.return_value = True

        data = {
            'files': (io.BytesIO(b'contenido de prueba'), 'prueba.txt')
        }
        response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.data)
        self.assertIn('success', res)
        # Since procesar_documento returns success True, upload should report success True
        self.assertTrue(res['success'])

    def test_upload_invalid_extension(self):
        """Upload a file with a disallowed extension and expect failure."""
        data = {
            'files': (io.BytesIO(b'binario'), 'malo.exe')
        }
        response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        res = json.loads(response.data)
        self.assertIn('success', res)
        self.assertFalse(res['success'])
        self.assertTrue('Tipo no permitido' in res['message'] or 'Tipo no permitido' in res.get('message', ''))


if __name__ == '__main__':
    unittest.main()
