import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from Model.crud_comentarios import CrudComentarios
from Model.crud_de_base import PostgresDB, DatabaseError

# -------------------------------------------------------
# Configuración general
# -------------------------------------------------------
APP_PORT = int(os.getenv("APP_PORT", "2020"))
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")

# Inicializar Flask (con soporte de plantillas y archivos estáticos)
app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static'
)

# Habilitar CORS solo para endpoints /api/*
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Servicio CRUD de comentarios
comentarios_service = CrudComentarios()

# -------------------------------------------------------
# Helpers de respuesta estándar
# -------------------------------------------------------
def ok(data=None, message=None, status=200):
    return jsonify({
        "ok": True,
        "data": data,
        "message": message,
        "error": None
    }), status


def fail(error_message, status=400, data=None):
    return jsonify({
        "ok": False,
        "data": data,
        "message": None,
        "error": error_message
    }), status


# -------------------------------------------------------
# RUTAS DE VISTAS HTML
# -------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/subir')
def subir():
    return render_template('subir.html')

@app.route('/productos')
def productos():
    return render_template('productos.html')

@app.route('/copias')
def copias():
    return render_template('copias.html')

@app.route('/papeleria')
def papeleria():
    return render_template('papeleria.html')

@app.route('/abarrotes')
def abarrotes():
    return render_template('abarrotes.html')

@app.route('/detalles')
def detalles():
    return render_template('detalles.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/product')
def product():
    return render_template('product.html')

@app.route('/login')
def login():
    return render_template('Login.html')
@app.route('/service')
def service():
    return render_template('service.html')


# -------------------------------------------------------
# RUTAS RESTFUL (API de comentarios)
# -------------------------------------------------------

@app.get("/api/comentarios")
def listar_comentarios():
    """
    Lista comentarios (opcionalmente filtrando por texto en 'buscar')
    """
    buscar = request.args.get("buscar", "", type=str)
    result = comentarios_service.consultar(buscar)
    return ok(data=result["data"]) if result["ok"] else fail(result["error"], status=500)


@app.post("/api/comentarios")
def crear_comentario():
    """
    Crea un nuevo comentario
    """
    payload = request.get_json(silent=True) or {}
    result = comentarios_service.crear(payload)
    if result["ok"]:
        return ok(data=result["data"], message=result["message"], status=201)

    msg = (result["error"] or "").lower()
    status = 400 if any(k in msg for k in ("inválido", "obligatorio", "id")) else 500
    return fail(result["error"], status=status)


@app.put("/api/comentarios/<int:comentario_id>")
def actualizar_comentario(comentario_id: int):
    """
    Actualiza un comentario existente
    """
    payload = request.get_json(silent=True) or {}
    result = comentarios_service.actualizar(comentario_id, payload)

    if result["ok"]:
        return ok(data=result["data"], message=result["message"])

    msg = (result["error"] or "").lower()
    if "no encontrado" in msg:
        return fail(result["error"], status=404)

    status = 400 if any(k in msg for k in ("inválido", "obligatorio", "id")) else 500
    return fail(result["error"], status=status)


@app.delete("/api/comentarios/<int:comentario_id>")
def eliminar_comentario(comentario_id: int):
    """
    Elimina un comentario por ID
    """
    result = comentarios_service.eliminar(comentario_id)

    if result["ok"]:
        return ok(data=result["data"], message=result["message"])

    msg = (result["error"] or "").lower()
    if "no encontrado" in msg:
        return fail(result["error"], status=404)

    status = 400 if "id" in msg or "inválido" in msg else 500
    return fail(result["error"], status=status)


# -------------------------------------------------------
# MANEJADORES DE ERRORES
# -------------------------------------------------------

@app.errorhandler(404)
def not_found(_e):
    return fail("Ruta no encontrada", status=404)


@app.errorhandler(405)
def method_not_allowed(_e):
    return fail("Método no permitido", status=405)


@app.errorhandler(500)
def internal_error(e):
    return fail("Error interno del servidor", status=500)


# -------------------------------------------------------
# ARRANQUE DE LA APLICACIÓN
# -------------------------------------------------------

if __name__ == "__main__":
    print(f"🚀 Servidor Flask corriendo en: http://{APP_HOST}:{APP_PORT}")
    app.run(host=APP_HOST, port=APP_PORT, debug=True)
