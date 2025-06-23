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

# -------------- Formulario de evaluación --------------
EVAL_FORM = """<!DOCTYPE html>
<html lang='es'>
<head>
  <meta charset='UTF-8'>
  <title>KeyFeedback – Evaluación</title>
  <link rel='stylesheet' href='/static/css/style.css'>
</head>
<body>
  <h1>Evaluar al Profesor: {professor}</h1>
  <form id='evalForm' method='post'>
    <label>Puntuación:</label><br>
    <input type='radio' id='r1' name='rating' value='1'><label for='r1'>🔑</label>
    <input type='radio' id='r2' name='rating' value='2'><label for='r2'>🔑🔑</label>
    <input type='radio' id='r3' name='rating' value='3'><label for='r3'>🔑🔑🔑</label>
    <input type='radio' id='r4' name='rating' value='4'><label for='r4'>🔑🔑🔑🔑</label>
    <input type='radio' id='r5' name='rating' value='5'><label for='r5'>🔑🔑🔑🔑🔑</label><br><br>
    <label>Comentario (mín. 15 palabras):</label><br>
    <textarea id='comment' name='comment' rows='4'></textarea><br>
    <small id='wordCount'>0 palabras</small><br><br>
    <button id='submitBtn' type='submit' disabled>Enviar evaluación</button>
  </form>
  <script>
    const comment = document.getElementById('comment');
    const radios  = document.getElementsByName('rating');
    const btn     = document.getElementById('submitBtn');
    const wc      = document.getElementById('wordCount');
    const bad     = ['insulto1','insulto2'];
    function validate() {{
      const text = comment.value.trim();
      const words = text ? text.split(/\\s+/) : [];
      wc.textContent = words.length + ' palabras';
      const rated = Array.from(radios).some(r => r.checked);
      const okLen = words.length >= 15;
      const okBad = !bad.some(b => text.toLowerCase().includes(b));
      btn.disabled = !(rated && okLen && okBad);
    }}
    comment.addEventListener('input', validate);
    Array.from(radios).forEach(r => r.addEventListener('change', validate));
  </script>
</body>
</html>"""


# -------------- Página de agradecimiento --------------
THANKS_PAGE = """<!DOCTYPE html>
<html lang='es'>
<head><meta charset='UTF-8'><title>Gracias</title></head>
<body><h1>¡Gracias por tu evaluación!</h1></body>
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
        label = os.path.splitext(fname)[0]
        url   = "/static/images/" + quote(fname)
        # Cada tarjeta es ahora un enlace a /evaluate?professor=<label>
        cards.append(f"""
        <div class="card">
          <a href="/evaluate?professor={quote(label)}">
            <img src="{url}" alt="{label}">
            <p>{label}</p>
          </a>
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
    
        # 5) Formulario de evaluación (/evaluate)
    if path.startswith("/evaluate"):
      qs   = parse_qs(environ.get("QUERY_STRING", ""))
      prof = qs.get("professor", [""])[0]

      if method == "GET":
        form = EVAL_FORM.format(professor=prof)
        start_response("200 OK", [("Content-Type","text/html; charset=utf-8")])
        return [form.encode("utf-8")]

      elif method == "POST":
        size   = int(environ.get("CONTENT_LENGTH", 0) or 0)
        post_data = environ["wsgi.input"].read(size).decode()
        params = parse_qs(post_data)

        rating  = params.get("rating", [""])[0]
        comment = params.get("comment", [""])[0]

        if not rating or len(comment.split()) < 15:
            error_msg = "<p style='color:red;'>Debes seleccionar una puntuación y escribir al menos 15 palabras.</p>"
            form = EVAL_FORM.format(professor=prof).replace("<form", error_msg + "<form")
            start_response("200 OK", [("Content-Type","text/html; charset=utf-8")])
            return [form.encode("utf-8")]

        # Guardar en archivo CSV
        with open("evaluaciones.csv", "a", encoding="utf-8") as f:
            f.write(f"{prof},{rating},{comment.replace(',', ' ')}\n")

        print(f"[EVAL] Profesor: {prof} | Rating: {rating} | Comentario: {comment}")
        start_response("200 OK", [("Content-Type","text/html; charset=utf-8")])
        return [THANKS_PAGE.encode("utf-8")]





    # 6) 404 por defecto
    start_response("404 Not Found", [("Content-Type","text/plain")])
    return [b"404 - Not Found"]

if __name__ == "__main__":
    print(f"Servidor escuchando en http://127.0.0.1:{PORT}/ …")
    make_server("", PORT, app).serve_forever()