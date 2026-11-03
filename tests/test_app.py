import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from app import server


class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        server.DB_PATH = str(Path(self.temp.name) / 'test.db')
        server.init_db()
        self.http = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.http.server_port}'

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        self.thread.join()
        self.temp.cleanup()

    def post(self, kind, data):
        request = Request(self.url + '/api/' + kind, data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'})
        return urlopen(request)

    def test_student_grade_absence_persist_after_initialization(self):
        with self.post('students', {'name': 'Étudiant Démo', 'class_name': 'GI-2'}) as response:
            student = json.load(response)['id']
        with self.post('grades', {'student_id': student, 'subject_id': 1, 'value': 16.5}) as response:
            self.assertEqual(response.status, 201)
        with self.post('absences', {'student_id': student, 'subject_id': 1, 'date': '2026-11-03', 'justified': True}) as response:
            self.assertEqual(response.status, 201)
        server.init_db()
        with urlopen(self.url + '/api/data') as response:
            data = json.load(response)
        self.assertEqual(len(data['students']), 1)
        self.assertEqual(data['grades'][0]['value'], 16.5)
        self.assertEqual(data['absences'][0]['justified'], 1)

    def test_reject_invalid_inputs(self):
        cases = [('students', {'name': ' ', 'class_name': 'GI'}), ('grades', {'student_id': 1, 'subject_id': 1, 'value': 21}), ('grades', {'student_id': 999, 'subject_id': 1, 'value': 12}), ('absences', {'student_id': 1, 'subject_id': 1, 'date': '2026-02-30'}), ('grades', {'student_id': 1, 'subject_id': 1, 'value': 'NaN'})]
        for kind, data in cases:
            with self.subTest(kind=kind, data=data), self.assertRaises(HTTPError) as context:
                self.post(kind, data)
            self.assertEqual(context.exception.code, 400)
            context.exception.close()

    def test_health_and_page(self):
        with urlopen(self.url + '/health') as response:
            self.assertEqual(json.load(response), {'status': 'ok'})
        with urlopen(self.url) as response:
            self.assertIn('Notes & absences', response.read().decode())


if __name__ == '__main__':
    unittest.main()
