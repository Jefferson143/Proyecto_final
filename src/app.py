import os
import mimetypes
from wsgiref.simple_server import make_server
from urllib.parse import parse_qs, quote, unquote
import csv

PORT = 5001
BASE_DIR = os.path.dirname(__file__)
CSS_PATH = "/static/css/style.css"
USERS_FILE = os.path.join(BASE_DIR, "usuarios.txt")
EVAL_FILE = os.path.join(BASE_DIR, "evaluaciones.csv")

CURRENT_USER = {"email": "", "nombre": "", "rol": ""}

MATERIAS_PROFESORES = {
    "Desarrollo Personal": [
        ("Jimena Alcaine", "/static/images/jimena.jpg"),
        ("Valeria Moncada", "/static/images/Valeria.jpeg"),
        ("Rebeca Quintanilla", "/static/images/Rebeca.jpeg")
    ],
    "Calculo 1": [
        ("Alberto Martinez", "/static/images/Albert.png")
    ],
    "Fisica 1": [
        ("Josue Quintanilla", "/static/images/josue.jpeg")
    ],
    "Introducción a la Ingeniería": [
        ("Regina Serpas", "/static/images/regi.png"),
        ("Sergio Navarro", "/static/images/sergio.png"),
        ("Roher Alfaro", "/static/images/roher.png"),
        ("Miguel Batres", "/static/images/miguel.png")
    ],
    "Fundamentos de Programación": [
        ("Erick Varela", "/static/images/erick.png")
    ]
}

MATERIAS_IMAGENES = {
    "Desarrollo Personal": "/static/images/dp.jpg",
    "Calculo 1": "/static/images/calculo.jpeg",
    "Fisica 1": "/static/images/fisica.webp",
    "Introducción a la Ingeniería": "/static/images/intro.jpg",
    "Fundamentos de Programación": "/static/images/progra.png"
}

def serve_static(path):
    full = os.path.join(BASE_DIR, path.lstrip("/"))
    if os.path.isfile(full):
        ctype, _ = mimetypes.guess_type(full)
        with open(full, "rb") as f:
            return ctype or "application/octet-stream", f.read()
    return None, None

def render_header():
    return """
    <header>
        <img src='/static/images/key_logo.png' alt='Key Logo'>
        <span>KeyOpina</span>
    </header>
    """

def save_feedback(usuario, profesor, data):
    nuevo = not os.path.exists(EVAL_FILE)
    with open(EVAL_FILE, "a", encoding="utf-8") as f:
        if nuevo:
            f.write("Usuario,Profesor,Opinion,Gusto,Comentario,Mejora,Rating\n")
        f.write(f"{usuario},{profesor},{data['opinion']},{data['gusto']},{data['comentario']},{data['mejora']},{data['rating']}\n")

def obtener_feedback_para(profesor):
    feedbacks = []
    if not os.path.exists(EVAL_FILE):
        return feedbacks
    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Profesor"] == profesor:
                feedbacks.append(row)
    return feedbacks

def app(environ, start_response):
    global CURRENT_USER
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")
    query = environ.get("QUERY_STRING", "")

    try:
        if path.startswith("/static/"):
            ctype, data = serve_static(path)
            if data:
                start_response("200 OK", [("Content-Type", ctype)])
                return [data]
            else:
                start_response("404 Not Found", [("Content-Type", "text/plain")])
                return [b"Archivo no encontrado"]

        if path == "/":
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
            return [f"""
            <html><head><link rel="stylesheet" href="{CSS_PATH}"></head><body>
            {render_header()}
            <h1>Bienvenido a KeyOpina</h1>
            <a href="/login">Iniciar sesión</a> | <a href="/register">Crear cuenta nueva</a>
            </body></html>
            """.encode("utf-8")]

        if path == "/register":
            if method == "GET":
                start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
                return [f"""
                <html><head><link rel="stylesheet" href="{CSS_PATH}"></head><body>
                {render_header()}
                <h1>Registrar nuevo usuario</h1>
                <form method='post'>
                    <label>Nombre y Apellido: <input type='text' name='nombre' required></label><br><br>
                    <label>Email: <input type='email' name='email' required></label><br><br>
                    <label>Contraseña: <input type='password' name='password' required></label><br><br>
                    <label>Rol:</label>
                    <select name='rol' required>
                        <option value='Estudiante'>Estudiante</option>
                        <option value='Profesor'>Profesor</option>
                    </select><br><br>
                    <button type='submit'>Registrarse</button>
                </form>
                </body></html>
                """.encode("utf-8")]
            else:
                size = int(environ.get("CONTENT_LENGTH", 0) or 0)
                data = environ["wsgi.input"].read(size).decode()
                params = parse_qs(data)
                nombre = params.get("nombre", [""])[0]
                email = params.get("email", [""])[0]
                password = params.get("password", [""])[0]
                rol = params.get("rol", ["Estudiante"])[0]
                with open(USERS_FILE, "a", encoding="utf-8") as f:
                    f.write(f"{nombre},{email},{password},{rol}\n")
                start_response("302 Found", [("Location", "/login")])
                return [b""]

        if path == "/login":
            if method == "GET":
                start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
                return [f"""
                <html><head><link rel="stylesheet" href="{CSS_PATH}"></head><body>
                {render_header()}
                <h1>Login</h1>
                <form method='post'>
                    <label>Email: <input type='email' name='email' required></label><br><br>
                    <label>Contraseña: <input type='password' name='password' required></label><br><br>
                    <button type='submit'>Entrar</button>
                </form>
                </body></html>
                """.encode("utf-8")]
            else:
                size = int(environ.get("CONTENT_LENGTH", 0) or 0)
                data = environ["wsgi.input"].read(size).decode()
                params = parse_qs(data)
                email = params.get("email", [""])[0]
                password = params.get("password", [""])[0]
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split(",")
                        if len(parts) >= 4 and parts[1] == email and parts[2] == password:
                            CURRENT_USER = {"email": email, "nombre": parts[0], "rol": parts[3]}
                            if CURRENT_USER["rol"] == "Profesor":
                                start_response("302 Found", [("Location", "/prof_feedback")])
                            else:
                                start_response("302 Found", [("Location", "/dashboard")])
                            return [b""]
                start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
                return [f"<p style='color:red;'>Usuario o contraseña incorrectos</p><a href='/login'>Intentar de nuevo</a>".encode("utf-8")]

        if path == "/dashboard":
            params = parse_qs(query)
            materia = params.get("materia", [""])[0]
            if materia and materia in MATERIAS_PROFESORES:
                profesores = MATERIAS_PROFESORES[materia]
                prof_cards = "".join([f"""
                <div class='card'>
                    <a href='/feedback?profesor={quote(prof)}'>
                        <img src='{foto}' alt='{prof}'><br>
                        <span>{prof}</span>
                    </a>
                </div>""" for prof, foto in profesores])
                content = f"<h2>Profesores de {materia}</h2><div class='grid'>{prof_cards}</div><p><a href='/dashboard'>Volver</a></p>"
            else:
                materias_links = "".join([f"""
                <div class='card'>
                    <a href='/dashboard?materia={quote(m)}'>
                        <img src='{MATERIAS_IMAGENES[m]}' alt='{m}'><br>
                        <span>{m}</span>
                    </a>
                </div>""" for m in MATERIAS_PROFESORES])
                content = f"<div class='grid'>{materias_links}</div>"
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
            return [f"""
            <html><head><link rel="stylesheet" href="{CSS_PATH}"></head><body>
            {render_header()}
            <h1>Bienvenido a KeyOpina, {CURRENT_USER['nombre']}</h1>
            {content}
            <p><a href='/logout'>Cerrar sesión</a></p>
            </body></html>
            """.encode("utf-8")]

        if path == "/feedback":
            if method == "GET":
                params = parse_qs(query)
                profesor = unquote(params.get("profesor", [""])[0])
                start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
                return [f"""
                <html><head><link rel="stylesheet" href="{CSS_PATH}"></head><body>
                {render_header()}
                <h1>Feedback para {profesor}</h1>
                <form method='post'>
                    <input type='hidden' name='profesor' value='{profesor}'>
                    <label>¿Qué opinas sobre tu profesor?</label><br>
                    <textarea name='opinion' required></textarea><br><br>
                    <label>¿Qué es lo que más te gusta de tu profesor?</label><br>
                    <textarea name='gusto' required></textarea><br><br>
                    <label>¿Tienes algún comentario general para tu profesor?</label><br>
                    <textarea name='comentario'></textarea><br><br>
                    <label>¿Cómo mejorarías la manera de enseñar de tu profesor?</label><br>
                    <textarea name='mejora'></textarea><br><br>
                    <label>¿Cuántas llaves le das a tu profesor? (1-5)</label><br>
                    <input type='number' name='rating' min='1' max='5' required><br><br>
                    <button type='submit'>Enviar feedback</button>
                </form>
                <p><a href='/dashboard'>Volver</a></p>
                </body></html>
                """.encode("utf-8")]
            else:
                size = int(environ.get("CONTENT_LENGTH", 0) or 0)
                data = environ["wsgi.input"].read(size).decode()
                params = parse_qs(data)
                profesor = params.get("profesor", [""])[0]
                feedback_data = {
                    "opinion": params.get("opinion", [""])[0],
                    "gusto": params.get("gusto", [""])[0],
                    "comentario": params.get("comentario", [""])[0],
                    "mejora": params.get("mejora", [""])[0],
                    "rating": params.get("rating", [""])[0]
                }
                save_feedback(CURRENT_USER["email"], profesor, feedback_data)
                start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
                return [f"<p>¡Gracias por tu feedback sobre {profesor}!</p><a href='/dashboard'>Volver al dashboard</a>".encode("utf-8")]

        if path == "/prof_feedback":
            feedbacks = obtener_feedback_para(CURRENT_USER["nombre"])
            rows = "".join([
                f"<tr><td>{f['Usuario']}</td><td>{f['Opinion']}</td><td>{f['Rating']}</td></tr>"
                for f in feedbacks
            ])
            table = f"""
            <h2>Feedback recibido</h2>
            <table border='1' style='margin:auto;'>
                <tr><th>Estudiante</th><th>Opinión</th><th>Llaves</th></tr>
                {rows}
            </table>
            <p><a href='/logout'>Cerrar sesión</a></p>
            """
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
            return [f"<html><head><link rel='stylesheet' href='{CSS_PATH}'></head><body>{render_header()}{table}</body></html>".encode("utf-8")]

        if path == "/logout":
            CURRENT_USER = {"email": "", "nombre": "", "rol": ""}
            start_response("302 Found", [("Location", "/")])
            return [b""]

        start_response("404 Not Found", [("Content-Type", "text/html; charset=utf-8")])
        return ["<h1>Página no encontrada</h1>".encode("utf-8")]

    except Exception as e:
        print(f"Error: {e}")
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [b"Error interno del servidor"]

if __name__ == "__main__":
    print(f"Servidor en http://127.0.0.1:{PORT}/")
    make_server("", PORT, app).serve_forever()
