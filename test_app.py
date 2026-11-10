import re
import unittest
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlencode
from wsgiref.util import setup_testing_defaults
from wsgiref.validate import validator

from app import create_app, init_db


class RegisterTests(unittest.TestCase):
    def setUp(self):
        temp = self.enterContext(TemporaryDirectory())
        self.path = Path(temp) / "etudiants.db"
        init_db(self.path, seed=True)
        self.app = validator(create_app(self.path))
        self.student = dict(matricule="ETU-003", nom="El Amrani", prenom="Lina", filiere="Informatique", niveau="S5")

    def request(self, path, form=None):
        route, _, query = path.partition("?")
        payload = urlencode(form).encode() if form is not None else b""
        environ = {}
        setup_testing_defaults(environ)
        environ.update(
            PATH_INFO=route, QUERY_STRING=query,
            REQUEST_METHOD="GET" if form is None else "POST",
            CONTENT_LENGTH=str(len(payload)), HTTP_HOST="localhost",
        )
        environ["wsgi.input"] = BytesIO(payload)
        response = {}

        def start_response(status, headers, exc_info=None):
            response.update(code=int(status.split()[0]), headers=dict(headers))

        result = self.app(environ, start_response)
        try:
            body = b"".join(result).decode("utf-8")
        finally:
            result.close()
        return response["code"], body, response["headers"]

    def submit(self, path, fields):
        code, page, _ = self.request(path)
        self.assertEqual(code, 200)
        token = re.search(r'name="token" value="([^"]+)"', page)[1]
        return self.request(path, dict(fields, token=token))

    def test_create_search_and_persist(self):
        code, _, headers = self.submit("/etudiants/nouveau", self.student)
        self.assertEqual((code, headers["Location"]), (303, "/?notice=added"))
        self.app = validator(create_app(self.path))
        code, page, _ = self.request("/?q=etu-003")
        self.assertEqual(code, 200)
        self.assertIn("<td>ETU-003</td>", page)
        self.assertNotIn("<td>ETU-001</td>", page)

    def test_duplicate_preserves_existing_record(self):
        duplicate = dict(self.student, matricule=" etu-001 ", filiere="Physique")
        code, page, _ = self.submit("/etudiants/nouveau", duplicate)
        self.assertEqual(code, 409)
        self.assertIn("Ce matricule est déjà utilisé.", page)
        _, page, _ = self.request("/?q=ETU-001")
        self.assertIn("<td>Informatique</td>", page)
        self.assertNotIn("<td>Physique</td>", page)

    def test_validation(self):
        code, page, _ = self.submit("/etudiants/nouveau", dict(self.student, nom="   "))
        self.assertEqual(code, 422)
        self.assertIn("Le champ « Nom »", page)
        self.assertEqual(self.submit("/etudiants/nouveau", dict(self.student, matricule="ETU / 003"))[0], 422)

    def test_edit_and_confirm_delete(self):
        _, page, _ = self.request("/?q=ETU-002")
        student_id = re.search(r"/etudiants/(\d+)/modifier", page)[1]
        edit = f"/etudiants/{student_id}/modifier"
        delete = f"/etudiants/{student_id}/supprimer"
        self.assertEqual(self.submit(edit, dict(self.student, matricule="ETU-001"))[0], 409)
        self.assertEqual(self.submit(edit, dict(self.student, matricule="ETU-002", niveau="S4"))[0], 303)
        self.assertIn("<td>S4</td>", self.request("/?q=ETU-002")[1])
        self.assertEqual(self.request(delete)[0], 200)
        self.assertIn("<td>ETU-002</td>", self.request("/?q=ETU-002")[1])
        self.assertEqual(self.submit(delete, {})[0], 303)
        self.assertIn("Aucune fiche trouvée", self.request("/?q=ETU-002")[1])

    def test_health_and_missing_route(self):
        self.assertEqual(self.request("/health")[:2], (200, '{"status":"ok"}'))
        self.assertEqual(self.request("/introuvable")[0], 404)

    def test_rejects_post_without_token_and_escapes_text(self):
        self.assertEqual(self.request("/etudiants/nouveau", self.student)[0], 403)
        self.assertEqual(self.submit("/etudiants/nouveau", dict(self.student, nom="<script>"))[0], 303)
        page = self.request("/?q=ETU-003")[1]
        self.assertIn("&lt;script&gt;", page)
        self.assertNotIn("<script>", page)


if __name__ == "__main__":
    unittest.main()
