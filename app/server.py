"""Week-2 local prototype. Python standard library only."""
import json
import os
import sqlite3
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DB_PATH = os.environ.get('DATABASE_PATH', 'data/school.db')
SCHEMA = '''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY, name TEXT NOT NULL, class_name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS subjects(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL);
CREATE TABLE IF NOT EXISTS grades(id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL REFERENCES students(id), subject_id INTEGER NOT NULL REFERENCES subjects(id), value REAL NOT NULL CHECK(value BETWEEN 0 AND 20));
CREATE TABLE IF NOT EXISTS absences(id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL REFERENCES students(id), subject_id INTEGER NOT NULL REFERENCES subjects(id), date TEXT NOT NULL, justified INTEGER NOT NULL DEFAULT 0 CHECK(justified IN (0,1)));
'''


@contextmanager
def connect():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    try:
        with db:
            yield db
    finally:
        db.close()


def init_db():
    with connect() as db:
        db.executescript(SCHEMA)
        db.executemany('INSERT OR IGNORE INTO subjects(name) VALUES (?)', [('DevOps',), ('Bases de données',), ('Développement web',)])


def create_record(kind, data):
    from datetime import date
    if kind == 'students':
        name, group = str(data.get('name', '')).strip(), str(data.get('class_name', '')).strip()
        if not name or not group or max(len(name), len(group)) > 100:
            raise ValueError('Nom et classe obligatoires (100 caractères maximum).')
        fields, values = 'name,class_name', (name, group)
    elif kind in ('grades', 'absences'):
        student, subject = int(data['student_id']), int(data['subject_id'])
        if kind == 'grades':
            value = float(data['value'])
            if not 0 <= value <= 20:
                raise ValueError('La note doit être comprise entre 0 et 20.')
            fields, values = 'student_id,subject_id,value', (student, subject, value)
        else:
            day = date.fromisoformat(data['date']).isoformat()
            justified = data.get('justified', False)
            if not isinstance(justified, bool):
                raise ValueError('Justification invalide.')
            fields, values = 'student_id,subject_id,date,justified', (student, subject, day, int(justified))
    else:
        raise ValueError('Ressource inconnue.')
    with connect() as db:
        cursor = db.execute(f'INSERT INTO {kind}({fields}) VALUES ({",".join("?" for _ in values)})', values)
        return cursor.lastrowid


class Handler(BaseHTTPRequestHandler):
    def respond(self, code, payload, content_type='application/json; charset=utf-8'):
        body = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/health':
            with connect() as db:
                db.execute('SELECT 1')
            return self.respond(200, {'status': 'ok'})
        if self.path == '/api/data':
            with connect() as db:
                result = {table: [dict(row) for row in db.execute(f'SELECT * FROM {table} ORDER BY id DESC')] for table in ('students', 'subjects', 'grades', 'absences')}
            return self.respond(200, result)
        if self.path == '/':
            return self.respond(200, Path(__file__).with_name('index.html').read_bytes(), 'text/html; charset=utf-8')
        self.respond(404, {'error': 'Page introuvable'})

    def do_POST(self):
        kind = self.path.removeprefix('/api/')
        if self.path not in ('/api/students', '/api/grades', '/api/absences'):
            return self.respond(404, {'error': 'Ressource inconnue'})
        try:
            length = int(self.headers.get('Content-Length', 0))
            if not 0 < length <= 10000:
                raise ValueError('Taille de requête invalide.')
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError('Objet JSON attendu.')
            record_id = create_record(kind, data)
            self.respond(201, {'id': record_id})
        except (ValueError, KeyError, TypeError, sqlite3.IntegrityError) as error:
            self.respond(400, {'error': str(error)})


if __name__ == '__main__':
    init_db()
    host = os.environ.get('HOST', '127.0.0.1')
    print(f'Application: http://{host}:8000', flush=True)
    ThreadingHTTPServer((host, 8000), Handler).serve_forever()
