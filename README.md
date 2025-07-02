# 📌 Nombre del Proyecto y Número de Grupo
Nombre del Proyecto: KeyOpina: Plataforma Web de Evaluación Docente
Número de Grupo: Grupo 05 A

# ⚙️ Instrucciones para ejecutar el proyecto
    1- Clona o descarga el repositorio en tu máquina local.
    2- Asegúrate de tener Python 3 instalado.
    3- Abre una terminal o línea de comandos en la carpeta del proyecto.
    4- Ejecuta el servidor con el comando:
        python app.py
    5- Abre tu navegador en la dirección:
        http://127.0.0.1:5001/
    6- Navega por la aplicación para:
        Registrar usuarios
        Iniciar sesión
        Enviar feedback

# 📦 Librerías necesarias
✅ Todas las librerías utilizadas son estándar de Python (no necesitas instalación con pip):

    os – manejo de rutas y archivos.
    mimetypes – detección de tipos MIME para archivos estáticos.
    wsgiref.simple_server – servidor WSGI incorporado para pruebas locales.
    urllib.parse – parseo de parámetros en URLs.
    csv – manejo de datos tabulares para evaluaciones.

# 🗂️ Estructura de Carpetas Sugerida
Organiza los archivos así para que funcione correctamente:

    /proyecto (Carpeta principal)
        /src
            /static
                /css
                    style.css
                /images
                    [imágenes de profesores y materias]
            usuarios.txt
            evaluaciones.csv
            app.py


Explicación de cada componente: 
        /static/css/style.css: esta es la hoja de estilos. 
        /static/images/: todas las imágenes referenciadas en el código.
        usuarios.txt: se crea automáticamente al registrar usuarios.
        evaluaciones.csv: se crea o actualiza al enviar feedback.

# ✅ Otros pasos relevantes
    - Asegúrate de tener creadas las carpetas /static/css y /static/images con sus contenidos antes de ejecutar el servidor.
    - Las imágenes deben tener los nombres exactos usados en el código para evitar errores 404.
    - Puedes editar el archivo CSS para personalizar el estilo de la app.
    - El servidor se ejecuta en localhost y puerto 5001 por defecto; si el puerto está ocupado, puedes cambiar la variable PORT en el código.

