# server.py
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from Model.crud_comentarios import CrudComentarios
from Model.crud_de_base import PostgresDB, DatabaseError


# -------------------------------------------------------
# Configuración
# -------------------------------------------------------
APP_PORT = int(os.getenv("APP_PORT", "2020"))
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")

app = Flask(__name__)

# CORS para permitir llamadas desde el frontend en otro puerto (ej. vite, webpack, etc.)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Servicio de comentarios (inyecta PostgresDB por dentro)
comentarios_service = CrudComentarios()


# -------------------------------------------------------
# Helpers de respuesta
# -------------------------------------------------------
def ok(data=None, message=None, status=200):
    return jsonify({"ok": True, "data": data, "message": message, "error": None}), status


def fail(error_message, status=400, data=None):
    return jsonify({"ok": False, "data": data, "message": None, "error": error_message}), status


# -------------------------------------------------------
# Rutas RESTful
# -------------------------------------------------------
@app.get("/api/comentarios")
def listar_comentarios():
    """
    GET /api/comentarios?buscar=texto
    Lista comentarios (filtra por nombre/asunto/comentario si 'buscar' está presente).
    """
    buscar = request.args.get("buscar", "", type=str)
    result = comentarios_service.consultar(buscar)
    if result["ok"]:
        return ok(data=result["data"])
    return fail(result["error"], status=500)


@app.post("/api/comentarios")
def crear_comentario():
    """
    POST /api/comentarios
    Body JSON: { nombre, e_mail, asunto, comentario }
    """
    payload = request.get_json(silent=True) or {}
    result = comentarios_service.crear(payload)
    if result["ok"]:
        return ok(data=result["data"], message=result["message"], status=201)
    # Si es validación, 400; si es BD, 500. Para simplificar, usamos 400 si contiene palabra 'inválido/obligatorio'
    msg = (result["error"] or "").lower()
    status = 400 if any(k in msg for k in ("inválido", "obligatorio", "id")) else 500
    return fail(result["error"], status=status)


@app.put("/api/comentarios/<int:comentario_id>")
def actualizar_comentario(comentario_id: int):
    """
    PUT /api/comentarios/<id>
    Body JSON: { nombre, e_mail, asunto, comentario }
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
    DELETE /api/comentarios/<id>
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
# Manejadores de errores generales (por si algo se escapa)
# -------------------------------------------------------
@app.errorhandler(404)
def not_found(_e):
    return fail("Ruta no encontrada", status=404)


@app.errorhandler(405)
def method_not_allowed(_e):
    return fail("Método no permitido", status=405)


@app.errorhandler(500)
def internal_error(e):
    # En producción podrías loguear e (stacktrace) con logging/observabilidad
    return fail("Error interno del servidor", status=500)


# -------------------------------------------------------
# Arranque
# -------------------------------------------------------
if __name__ == "__main__":
    print(f"🚀 API de Comentarios corriendo en http://{APP_HOST}:{APP_PORT}")
    app.run(host=APP_HOST, port=APP_PORT, debug=True)
            