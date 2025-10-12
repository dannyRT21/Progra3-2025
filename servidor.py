import os
from flask import Flask, jsonify, request, render_template, redirect
from flask_cors import CORS
from Model.crud_comentarios import CrudComentarios
from Model.crud_de_base import PostgresDB, DatabaseError
from werkzeug.utils import secure_filename
from Model.crud_productos import CrudProductos
import uuid

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

# Configurar carpeta de subida de imágenes
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'img', 'productos')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Servicios
productos_service = CrudProductos()
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
    return render_template('index.html')  # ✅ Cambiado para mostrar página de inicio real


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/subir', methods=['GET', 'POST'])
def subir():
    if request.method == 'POST':
        try:
            print("DEBUG: Iniciando subida de producto...")

            # Log de los datos recibidos
            print(f"DEBUG: Datos del formulario: {dict(request.form)}")
            print(f"DEBUG: Archivos recibidos: {dict(request.files)}")

            nombre = request.form['nombre']
            categoria_id = request.form.get('categoria_id')
            descripcion = request.form.get('descripcion')
            precio = float(request.form['precio'])
            cod_barras = request.form['cod_barras']
            inventario = int(request.form['inventario'])
            activo = 'activo' in request.form

            print(f"DEBUG: Datos procesados - Nombre: {nombre}, Precio: {precio}, Cod Barras: {cod_barras}")

            imagen = request.files.get('imagen')
            filename = None
            if imagen and imagen.filename:
                safe_name = secure_filename(imagen.filename)
                filename = f"{uuid.uuid4().hex}_{safe_name}"
                print(f"DEBUG: Guardando imagen como: {filename}")
                imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                print("DEBUG: No se recibió imagen")

            datos_producto = {
                "nombre": nombre,
                "categoria_id": categoria_id,
                "descripcion": descripcion,
                "precio": precio,
                "cod_barras": cod_barras,
                "inventario": inventario,
                "activo": activo,
                "imagen": filename
            }

            print(f"DEBUG: Enviando a BD: {datos_producto}")

            result = productos_service.crear(datos_producto)
            print(f"DEBUG: Resultado de crear producto: {result}")

            if result["ok"]:
                print("DEBUG: Producto creado exitosamente, redirigiendo...")
                return redirect('/productos')
            else:
                print(f"DEBUG: Error al crear producto: {result['error']}")
                return fail(result["error"], status=500)

        except Exception as e:
            print(f"DEBUG: Excepción en subir: {str(e)}")
            return fail(str(e), status=500)
    return render_template('subir.html')


@app.route('/productos')
def productos():
    result = productos_service.listar()
    if result["ok"]:
        return render_template('productos.html', productos=result["data"])
    return fail(result["error"], status=500)


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


@app.route('/login', methods=['GET'])
def login():
    return render_template('Login.html')


# 🔹 Nueva ruta para procesar el formulario de login
@app.route('/procesar_login', methods=['POST'])
def procesar_login():
    """
    Procesa los datos del formulario de login enviado por POST desde Login.html
    """
    username = request.form.get('username')
    password = request.form.get('password')

    # Validación de campos vacíos
    if not username or not password:
        error = "Por favor, ingresa usuario y contraseña."
        return render_template('Login.html', error=error)

    # Ejemplo de validación (puedes cambiar esto para usar PostgreSQL)
    if username == "admin@copyvariedades.com" and password == "1234":
        return redirect('/')  # ✅ Redirige al index después de login
    else:
        error = "Usuario o contraseña incorrectos"
        return render_template('Login.html', error=error)


@app.route('/service')
def service():
    return render_template('service.html')


# -------------------------------------------------------
# RUTAS RESTFUL (API de comentarios)
# -------------------------------------------------------

@app.get("/api/comentarios")
def listar_comentarios():
    buscar = request.args.get("buscar", "", type=str)
    result = comentarios_service.consultar(buscar)
    return ok(data=result["data"]) if result["ok"] else fail(result["error"], status=500)


@app.post("/api/comentarios")
def crear_comentario():
    payload = request.get_json(silent=True) or {}
    result = comentarios_service.crear(payload)
    if result["ok"]:
        return ok(data=result["data"], message=result["message"], status=201)

    msg = (result["error"] or "").lower()
    status = 400 if any(k in msg for k in ("inválido", "obligatorio", "id")) else 500
    return fail(result["error"], status=status)


@app.put("/api/comentarios/<int:comentario_id>")
def actualizar_comentario(comentario_id: int):
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
    result = comentarios_service.eliminar(comentario_id)
    if result["ok"]:
        return ok(data=result["data"], message=result["message"])

    msg = (result["error"] or "").lower()
    if "no encontrado" in msg:
        return fail(result["error"], status=404)

    status = 400 if "id" in msg or "inválido" in msg else 500
    return fail(result["error"], status=status)


@app.put('/api/productos/<producto_id>')
def actualizar_producto(producto_id):
    try:
        data = request.get_json(silent=True) or {}
        if not data.get("nombre") or not data.get("precio"):
            return fail("Nombre y precio son obligatorios", status=400)

        result = productos_service.actualizar(producto_id, data)
        if result["ok"]:
            return ok(message="Producto actualizado correctamente", data=result["data"])
        return fail(result["error"], status=404)
    except Exception as e:
        return fail(str(e), status=500)


@app.delete('/api/productos/<producto_id>')
def eliminar_producto(producto_id):
    result = productos_service.eliminar(producto_id)
    if result["ok"]:
        return ok(message=result["message"])
    return fail(result["error"], status=404)


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
