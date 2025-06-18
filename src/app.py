#!/usr/bin/env python3
# src/app.py

from wsgiref.simple_server import make_server
from urllib.parse       import parse_qs

# Usuario de prueba (más adelante leerás esto de tu .txt)
VALID_USERS = {
    "alumno@keyinstitute.edu.sv": "mi_contraseña_segura"
}

# Formulario de login (HTML puro)
LOGIN_FORM = """<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>KeyFeedback Login</title></head>
<body>
  <h1>Iniciar sesión</h1>
  <form method="post">
    <label>Correo: <input type="email" name="email" required></label><br><br>
    <label>Contraseña: <input type="password" name="password" required></label><br><br>
    <button type="submit">Entrar</button>
  </form>
</body>
</html>"""

def app(environ, start_response):
    # Determinar método HTTP
    method = environ["REQUEST_METHOD"]
    response_body = ""

    if method == "GET":
        # Mostrar siempre el formulario al hacer GET
        response_body = LOGIN_FORM

    else:  # POST
        # Leer el cuerpo y parsear los parámetros
        try:
            size = int(environ.get("CONTENT_LENGTH", 0))
        except ValueError:
            size = 0
        body = environ["wsgi.input"].read(size).decode()
        params = parse_qs(body)

        email = params.get("email", [""])[0]
        pwd   = params.get("password", [""])[0]

        # Validar credenciales
        if VALID_USERS.get(email) == pwd:
            response_body = f"""<!DOCTYPE html>
<html lang="es"><body>
  <h1>¡Bienvenido, {email}!</h1>
  <p>Tu login fue exitoso.</p>
  <a href="/">Salir</a>
</body></html>"""
        else:
            # Si falla, mostrar mensaje de error + formulario
            response_body = LOGIN_FORM.replace(
                "<h1>Iniciar sesión</h1>",
                "<h1>Iniciar sesión</h1><p style='color:red;'>Credenciales inválidas</p>"
            )

    # Cabeceras HTTP y envío de la respuesta
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    return [response_body.encode("utf-8")]

if __name__ == "__main__":
    port = 5001
    print(f"Servidor escuchando en http://127.0.0.1:{port}/ …")
    make_server("", port, app).serve_forever()
