#!/usr/bin/env python3
# src/app.py

import os, mimetypes
from wsgiref.simple_server import make_server
from urllib.parse       import quote, parse_qs

PORT     = 5001
BASE_DIR = os.path.dirname(__file__)
IMG_DIR  = os.path.join(BASE_DIR, "static/images")

# Diccionario de login tal como lo tenías
VALID_USERS = {
    "alumno@keyinstitute.edu.sv": "mi_contraseña_segura"
}

# Formulario de login...
LOGIN_FORM = """<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><title>KeyFeedback Login</title></head>
<body>
  <h1>Iniciar sesión</h1>
  <form method="post">
    <label>Correo: <input type="email" name="email" required></label><br><br>
    <label>Contraseña: <input type="password" name="password" required></label><br><br>
    <button type="submit">Entrar</button>
  </form>
</body></html>"""

def serve_static(path):
    full = os.path.join(BASE_DIR, path.lstrip("/"))
    if not os.path.isfile(full): return None, None
    ctype, _ = mimetypes.guess_type(full)
    return ctype or "application/octet-stream", open(full, "rb").read()

def dashboard_page(user_email):
    cards_html = []
    for fname in os.listdir(IMG_DIR):
        # Saltar ficheros ocultos (p.ej. .DS_Store)
        if fname.startswith("."):
            continue

        url = "/static/images/" + quote(fname)
        label = os.path.splitext(fname)[0]
        cards_html.append(f"""
        <div class="card">
          <img src="{url}" alt="{label}">
          <p>{label}</p>
        </div>""")

    cards = "\n".join(cards_html)
    return f"""<!DOCTYPE html>
<html lang="es"><head>…</head><body>
  <h1>Bienvenido, {user_email}</h1>
  <div class="grid">
    {cards}
  </div>
</body></html>"""

def app(environ, start_response):
    path   = environ.get("PATH_INFO", "/")
    method = environ["REQUEST_METHOD"]

    # 1) Sirve CSS o imágenes
    if path.startswith("/static/"):
        ctype, data = serve_static(path)
        if data is not None:
            start_response("200 OK", [("Content-Type", ctype)])
            return [data]

    # 2) Lógica de login (igual que antes)
    if path in ("/", "/login"):
        if method == "GET":
            body = LOGIN_FORM
        else:
            size = int(environ.get("CONTENT_LENGTH", 0) or 0)
            params = parse_qs(environ["wsgi.input"].read(size).decode())
            email = params.get("email", [""])[0]
            pwd   = params.get("password", [""])[0]
            if VALID_USERS.get(email) == pwd:
                # redirige al dashboard
                start_response("302 Found", [("Location", "/dashboard")])
                return [b""]
            body = LOGIN_FORM.replace(
                "<h1>Iniciar sesión</h1>",
                "<h1>Iniciar sesión</h1><p style='color:red;'>Credenciales inválidas</p>")
        start_response("200 OK", [("Content-Type","text/html; charset=utf-8")])
        return [body.encode("utf-8")]

    # 3) Dashboard
    if path == "/dashboard":
        # Aquí podrías checar sesión, pero para el ejemplo simplificamos:
        user_email = "alumno@keyinstitute.edu.sv"
        html = dashboard_page(user_email)
        start_response("200 OK", [("Content-Type","text/html; charset=utf-8")])
        return [html.encode("utf-8")]

    # 4) 404 por defecto
    start_response("404 Not Found", [("Content-Type","text/plain")])
    return [b"404 - Not Found"]

if __name__ == "__main__":
    print(f"Servidor escuchando en http://127.0.0.1:{PORT}/")
    make_server("", PORT, app).serve_forever()
