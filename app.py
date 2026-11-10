"""Application de démonstration du service de scolarité."""

import argparse
import hmac
import os
import re
import secrets
import sqlite3
from contextlib import closing
from html import escape
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from wsgiref.simple_server import make_server

ROOT = Path(__file__).resolve().parent
FIELDS = {
    "matricule": ("Matricule", 24, "ETU-003"),
    "nom": ("Nom", 80, "El Amrani"),
    "prenom": ("Prénom", 80, "Lina"),
    "filiere": ("Filière", 80, "Informatique"),
    "niveau": ("Niveau", 30, "S5"),
}
DEMO = [
    ("ETU-001", "El Amrani", "Lina", "Informatique", "S5"),
    ("ETU-002", "El Amrani", "Lina", "Mathématiques", "S3"),
    ("ETU-004", "Benali", "Adam", "Gestion", "S1"),
]


def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    return db


def init_db(path, seed=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(connect(path)) as db, db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS etudiants (
                id INTEGER PRIMARY KEY,
                matricule TEXT NOT NULL COLLATE NOCASE UNIQUE,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                filiere TEXT NOT NULL,
                niveau TEXT NOT NULL
            )
        """)
        if seed:
            db.executemany(
                "INSERT INTO etudiants (matricule, nom, prenom, filiere, niveau) "
                "VALUES (?, ?, ?, ?, ?) ON CONFLICT(matricule) DO NOTHING", DEMO,
            )


def page(title, content):
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · Scolarité</title>
<link rel="stylesheet" href="/style.css"></head><body>
<header><div class="wrap masthead"><a href="/">Scolarité</a><span>Projet 05 / Gestion des étudiants</span></div></header>
<main class="wrap">{content}</main>
<footer class="wrap">Environnement de démonstration · Fiches fictives</footer>
</body></html>"""


def listing(db, query, notice):
    if query:
        rows = db.execute(
            "SELECT * FROM etudiants WHERE instr(matricule, ?) > 0 ORDER BY matricule",
            (query.upper(),),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM etudiants ORDER BY matricule").fetchall()
    messages = {"added": "Fiche enregistrée.", "edited": "Fiche mise à jour.", "deleted": "Fiche supprimée."}
    banner = f'<p class="notice" role="status">{messages[notice]}</p>' if notice in messages else ""
    body = []
    for student in rows:
        student_id = student["id"]
        cells = "".join(f"<td>{escape(student[key])}</td>" for key in FIELDS)
        body.append(
            f'<tr>{cells}<td class="actions"><a href="/etudiants/{student_id}/modifier">Modifier</a>'
            f'<a href="/etudiants/{student_id}/supprimer">Supprimer</a></td></tr>'
        )
    if not body:
        body.append('<tr><td colspan="6">Aucune fiche trouvée.</td></tr>')
    headings = "".join(f'<th scope="col">{label}</th>' for label, _, _ in FIELDS.values())
    return page("Registre", f"""
<p class="eyebrow">Service de scolarité</p>
<div class="intro"><div><h1>Registre des étudiants</h1>
<p>Inscrivez un étudiant ou retrouvez sa fiche par matricule.</p></div>
<a class="button" href="/etudiants/nouveau">Ajouter un étudiant</a></div>
{banner}
<section class="panel" aria-label="Liste des étudiants">
<form class="search" action="/" method="get">
<label for="q">Recherche par matricule</label>
<div><input id="q" name="q" value="{escape(query)}" placeholder="ETU-001" maxlength="24">
<button type="submit">Rechercher</button><a href="/">Réinitialiser</a></div></form>
<p class="count">{len(rows)} fiche(s)</p>
<div class="table-scroll"><table><thead><tr>{headings}<th scope="col">Actions</th></tr></thead>
<tbody>{''.join(body)}</tbody></table></div></section>""")


def student_form(title, values, token, error=""):
    fields = "".join(
        f'<label for="{key}">{label}</label><input id="{key}" name="{key}" '
        f'value="{escape(values.get(key, ""))}" maxlength="{length}" '
        f'placeholder="{example}" required>'
        for key, (label, length, example) in FIELDS.items()
    )
    message = f'<p class="error" role="alert">{escape(error)}</p>' if error else ""
    return page(title, f"""<a class="back" href="/">← Retour au registre</a>
<h1>{title}</h1><p>Les cinq champs sont obligatoires.</p>{message}
<form class="panel editor" method="post">
<input type="hidden" name="token" value="{token}">{fields}
<div class="actions"><button type="submit">Enregistrer</button><a href="/">Annuler</a></div>
</form>""")


def validate(form):
    values = {key: form.get(key, [""])[0].strip() for key in FIELDS}
    values["matricule"] = values["matricule"].upper()
    for key, (label, limit, _) in FIELDS.items():
        if not 1 <= len(values[key]) <= limit:
            return values, f"Le champ « {label} » doit contenir entre 1 et {limit} caractères."
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9-]*", values["matricule"]):
        return values, "Le matricule doit commencer par une lettre ou un chiffre et peut contenir des tirets."
    return values, ""


def create_app(path):
    init_db(path)
    token = secrets.token_urlsafe()
    stylesheet = (ROOT / "style.css").read_bytes()

    def app(environ, start_response):
        def send(status, body="", content_type="text/html; charset=utf-8", extra=()):
            if isinstance(body, str):
                body = body.encode("utf-8")
            start_response(status, [
                ("Content-Type", content_type), ("Content-Length", str(len(body))),
                ("X-Content-Type-Options", "nosniff"), ("Cache-Control", "no-store"), *extra,
            ])
            return [body]

        def fail(status, message):
            return send(status, page("Scolarité", f'<h1>{message}</h1><p><a href="/">Retour au registre</a></p>'))

        def redirect(notice):
            return send("303 See Other", extra=(("Location", f"/?notice={notice}"),))

        method = environ["REQUEST_METHOD"]
        route = environ.get("PATH_INFO", "/")
        if method == "GET":
            if route == "/style.css":
                return send("200 OK", stylesheet, "text/css; charset=utf-8")
            if route == "/health":
                try:
                    with closing(connect(path)) as db:
                        db.execute("SELECT id FROM etudiants LIMIT 1").fetchone()
                except sqlite3.Error:
                    return send("503 Service Unavailable", '{"status":"unavailable"}', "application/json")
                return send("200 OK", '{"status":"ok"}', "application/json")
            if route == "/":
                params = parse_qs(environ.get("QUERY_STRING", ""))
                with closing(connect(path)) as db:
                    return send("200 OK", listing(db, params.get("q", [""])[0].strip()[:24], params.get("notice", [""])[0]))

        match = re.fullmatch(r"/etudiants/([0-9]{1,19})/(modifier|supprimer)", route)
        if route != "/etudiants/nouveau" and not match:
            return fail("404 Not Found", "Page introuvable")
        if method not in {"GET", "POST"}:
            return send("405 Method Not Allowed", extra=(("Allow", "GET, POST"),))

        form = {}
        if method == "POST":
            origin = environ.get("HTTP_ORIGIN")
            if origin and urlsplit(origin).netloc != environ.get("HTTP_HOST"):
                return fail("403 Forbidden", "Origine de la requête refusée")
            try:
                length = int(environ.get("CONTENT_LENGTH") or 0)
                if not 0 <= length <= 8192:
                    return fail("413 Content Too Large", "Formulaire trop volumineux")
                form = parse_qs(environ["wsgi.input"].read(length).decode("utf-8"), max_num_fields=12)
            except ValueError:
                return fail("400 Bad Request", "Formulaire illisible")
            if not hmac.compare_digest(form.get("token", [""])[0].encode("utf-8"), token.encode("ascii")):
                return fail("403 Forbidden", "Rechargez la page avant de réessayer")

        with closing(connect(path)) as db, db:
            student = None
            if match:
                student = db.execute("SELECT * FROM etudiants WHERE id = ?", (match[1],)).fetchone()
                if student is None:
                    return fail("404 Not Found", "Fiche introuvable")
            if match and match[2] == "supprimer":
                if method == "GET":
                    return send("200 OK", page("Supprimer", f"""
<a class="back" href="/">← Retour au registre</a>
<h1>Supprimer la fiche</h1>
<p>Confirmer la suppression de {escape(student['prenom'])} {escape(student['nom'])}
({escape(student['matricule'])}) ?</p>
<form class="actions" method="post"><input type="hidden" name="token" value="{token}">
<button class="danger" type="submit">Confirmer la suppression</button><a href="/">Annuler</a></form>"""))
                result = db.execute("DELETE FROM etudiants WHERE id = ?", (student["id"],))
                if not result.rowcount:
                    return fail("404 Not Found", "Fiche introuvable")
                db.commit()
                return redirect("deleted")

            title = "Modifier la fiche" if student else "Nouvel étudiant"
            if method == "GET":
                return send("200 OK", student_form(title, dict(student) if student else {}, token))
            values, error = validate(form)
            if error:
                return send("422 Unprocessable Content", student_form(title, values, token, error))
            fields = tuple(values.values())
            try:
                if student:
                    result = db.execute(
                        "UPDATE etudiants SET matricule=?, nom=?, prenom=?, filiere=?, niveau=? WHERE id=?",
                        (*fields, student["id"]),
                    )
                    if not result.rowcount:
                        return fail("404 Not Found", "Fiche introuvable")
                else:
                    db.execute(
                        "INSERT INTO etudiants (matricule, nom, prenom, filiere, niveau) VALUES (?, ?, ?, ?, ?)",
                        fields,
                    )
                db.commit()
            except sqlite3.IntegrityError as exc:
                if exc.sqlite_errorcode != sqlite3.SQLITE_CONSTRAINT_UNIQUE:
                    raise
                return send("409 Conflict", student_form(title, values, token, "Ce matricule est déjà utilisé."))
            return redirect("edited" if student else "added")

    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", default=int(os.environ.get("PORT", "8000")), type=int)
    parser.add_argument("--db", default=os.environ.get("STUDENT_DB", ROOT / "data" / "etudiants.db"), type=Path)
    parser.add_argument("--seed", action="store_true", help="Ajouter des fiches fictives au démarrage.")
    args = parser.parse_args()
    if args.seed:
        init_db(args.db, seed=True)
    with make_server(args.host, args.port, create_app(args.db)) as server:
        print(f"Scolarité · http://{args.host}:{args.port}", flush=True)
        server.serve_forever()
