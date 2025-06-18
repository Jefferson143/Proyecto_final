#!/usr/bin/env python3
# src/app.py

import os
import mimetypes
from wsgiref.simple_server import make_server
from urllib.parse import quote, parse_qs

PORT     = 5001
BASE_DIR = os.path.dirname(__file__)
IMG_DIR  = os.path.join(BASE_DIR, "static/images")

# Usuario de prueba
VALID_USERS = {"alumno@keyinstitute.edu.sv": "mi_contraseña_segura"}


# -------------- Paso 4: pantalla de carga --------------
LOADING_PAGE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>KeyFeedback – Cargando</title>
  <link rel="stylesheet" href="/static/css/style.css">
  <!-- tras 2s redirige a /login -->
  <meta http-equiv="refresh" content="2;URL=/login">
</head>
<body>
  <div class="loader">
    <img src="/static/images/logo.png" alt="Logo KeyFeedback">
  </div>
</body>
</html>"""

# -------------- HTML del login --------------
LOGIN_FORM = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>KeyFeedback – Login</title>
  <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
  <h1>Iniciar sesión</h1>
  <form method="post">
    <label>Correo: <input type="email" name="email" required></label><br><br>
    <label>Contraseña: <input type="password" name="password" required></label><br><br>
    <button type="submit">Entrar</button>
  </form>
</body>
</html>"""

# Construcción del Dashboard
def dashboard_page(user_email):
    # Cabecera con logo
    header = """
    <header>
      <img src=\"/static/images/logo.png\" alt=\"KeyFeedback Logo\" class=\"header-logo\">
    </header>"""

    # -------------- Paso 3: generar tarjetas dinámicas --------------
    cards = []
    for fname in os.listdir(IMG_DIR):
        # Saltar archivos ocultos y logo.png
        if fname.startswith('.') or fname.lower() == 'logo.png':
            continue
        url   = "/static/images/" + quote(fname)
        label = os.path.splitext(fname)[0]
        cards.append(f"""
        <div class=\"card\">
          <img src=\"{url}\" alt=\"{label}\">
          <p>{label}</p>
        </div>""")

    cards_html = "\n".join(cards)
    return f"""<!DOCTYPE html>
<html lang=\"es\">
<head>
  <meta charset=\"UTF-8\">
  <title>KeyFeedback – Dashboard</title>
  <link rel=\"stylesheet\" href=\"/static/css/style.css\">
</head>
<body>
  {header}
  <h1>Bienvenido, {user_email}</h1>
  <div class=\"grid\">
    {cards_html}
  </div>
</body>
</html>"""

# Lógica WSGI
def serve_static(path):
    full = os.path.join(BASE_DIR, path.lstrip("/"))
    if not os.path.isfile(full):
        return None, None
    ctype, _ = mimetypes.guess_type(full)
    with open(full, "rb") as f:
        return ctype or "application/octet-stream", f.read()


def app(environ, start_response):
    path   = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    # 1) Servir CSS e imágenes estáticas
    if path.startswith("/static/"):
        ctype, data = serve_static(path)
        if data is not None:
            start_response("200 OK", [("Content-Type", ctype)])
            return [data]

    # 2) Pantalla de carga en "/"
    if path == "/":
        start_response("200 OK", [("Content-Type","text/html; charset=utf-8")])
        return [LOADING_PAGE.encode("utf-8")]

    # 3) Login en "/login"
    if path == "/login":
        if method == "GET":
            body = LOGIN_FORM
        else:
            size   = int(environ.get("CONTENT_LENGTH", 0) or 0)
            params = parse_qs(environ["wsgi.input"].read(size).decode())
            email  = params.get("email", [""])[0]
            pwd    = params.get("password", [""])[0]

            if VALID_USERS.get(email) == pwd:
                # Redirigir a dashboard
                start_response("302 Found", [("Location", "/dashboard")])
                return [b""]
            # Credenciales inválidas: recarga con mensaje
            body = LOGIN_FORM.replace(
                "<h1>Iniciar sesión</h1>",
                "<h1>Iniciar sesión</h1><p style='color:red;'>Credenciales inválidas</p>"
            )

        start_response("200 OK", [("Content-Type","text/html; charset=utf-8")])
        return [body.encode("utf-8")]

    # 4) Dashboard en "/dashboard"
    if path == "/dashboard":
        user_email = "alumno@keyinstitute.edu.sv"
        html = dashboard_page(user_email)
        start_response("200 OK", [("Content-Type","text/html; charset=utf-8")])
        return [html.encode("utf-8")]

    # 5) 404 por defecto
    start_response("404 Not Found", [("Content-Type","text/plain")])
    return [b"404 - Not Found"]

if __name__ == "__main__":
    print(f"Servidor escuchando en http://127.0.0.1:{PORT}/ …")
    make_server("", PORT, app).serve_forever()