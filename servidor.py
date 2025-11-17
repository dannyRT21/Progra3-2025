import os
from flask import Flask, jsonify, request, render_template, redirect, session, url_for
from flask_cors import CORS
from Model.crud_comentarios import CrudComentarios
from Model.crud_de_login import CrudUsuarios
from Model.crud_de_base import PostgresDB, DatabaseError
from Model.crud_carrito import carrito_bp


from werkzeug.utils import secure_filename
from Model.crud_productos import CrudProductos
import uuid

# -------------------------------------------------------
# Configuración general
# -------------------------------------------------------
APP_PORT = int(os.getenv("APP_PORT", "2020"))
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")

app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static'
)

# 🔐 Clave secreta para sesiones
app.secret_key = "clave_secreta_segura_123"  # puedes cambiarla

# Habilitar CORS solo para endpoints /api/*
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configurar carpeta de subida de imágenes
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'img', 'productos')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Servicios
productos_service = CrudProductos()
comentarios_service = CrudComentarios()
usuarios_service = CrudUsuarios()

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

def fail_500(error_message, status=500, data=None):
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
    # ✅ Verificamos si el usuario está logueado
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/subir', methods=['GET', 'POST'])
def subir():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            print("DEBUG: Iniciando subida de producto...")
            print(f"DEBUG: Datos del formulario: {dict(request.form)}")
            print(f"DEBUG: Archivos recibidos: {dict(request.files)}")

            nombre = request.form['nombre']
            categoria_id = request.form.get('categoria_id')
            descripcion = request.form.get('descripcion')
            precio = float(request.form['precio'])
            cod_barras = request.form['cod_barras']
            inventario = int(request.form['inventario'])
            activo = 'activo' in request.form

            imagen = request.files.get('imagen')
            filename = None
            if imagen and imagen.filename:
                safe_name = secure_filename(imagen.filename)
                filename = f"{uuid.uuid4().hex}_{safe_name}"
                imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

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

            result = productos_service.crear(datos_producto)
            if result["ok"]:
                return redirect('/productos')
            else:
                return fail(result["error"], status=500)

        except Exception as e:
            return fail(str(e), status=500)
    return render_template('subir.html')


@app.route('/productos')
def productos():
    result = productos_service.listar()
    if not result["ok"]:
        return fail(result["error"], status=500)

    productos = result["data"]

    # Si el usuario está logueado mostramos la vista de admin,
    # si no está logueado mostramos la vista para clientes con los mismos datos.
    if 'usuario' in session:
        return render_template('productos.html', productos=productos)

    return render_template('vistas_clientes/productos_clientes.html', productos=productos)


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

@app.route('/panel_admin')
def panel_admin():
    return render_template('panel_admin.html')

@app.route('/login', methods=['GET'])
def login():
    return render_template('Login.html')



crudUsuarios = CrudUsuarios()

@app.route('/procesar_login', methods=['POST'])
def procesar_login():
    data = request.get_json(force=True)
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"ok": False, "error": "Por favor, ingresa usuario y contraseña."})

    # Consulta segura
    resultado = crudUsuarios.db.execute_select(
        "SELECT * FROM usuarios WHERE correo_electronico = %s LIMIT 1", (username,)
    )

    if not resultado:
        return jsonify({"ok": False, "error": "Usuario no encontrado."})

    usuario = resultado[0]
    if usuario["contrasena"].strip() == password.strip():  # ⚠️ luego usar hashing (bcrypt)
        session['usuario'] = username
        return jsonify({"ok": True, "redirect": url_for('index')})
    else:
        return jsonify({"ok": False, "error": "Contraseña incorrecta."})


# 🔸 Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))


@app.route('/service')
def service():
    return render_template('service.html')

@app.route('/productos_clientes')
def productos_clientes():
    result = productos_service.listar()
    if not result["ok"]:
        return fail(result["error"], status=500)
    productos = result["data"]
    return render_template('vistas_clientes/productos_clientes.html', productos=productos)

@app.route('/carrito_compras')
def carrito_compras():
    return render_template('carrito_compras.html')


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
        # aceptar precio == 0, por eso comprobamos is not None
        if not data.get("nombre") or data.get("precio") is None:
            return fail("Nombre y precio son obligatorios", status=400)

        result = productos_service.actualizar(producto_id, data)
        if result["ok"]:
            # Obtener lista actualizada de productos para que la vista cliente pueda refrescar
            lista = productos_service.listar()
            productos = lista["data"] if lista["ok"] else []
            return ok(
                message="Producto actualizado correctamente",
                data={"producto": result["data"], "productos": productos}
            )
        return fail(result["error"], status=404)
    except Exception as e:
        return fail(str(e), status=500)


@app.delete('/api/productos/<producto_id>')
def eliminar_producto(producto_id):
    result = productos_service.eliminar(producto_id)
    if result["ok"]:
        return ok(message=result["message"])
    return fail(result["error"], status=404)


@app.get('/api/productos')
def listar_productos():
    """
    Devuelve la lista de productos en formato JSON para el frontend.
    """
    # Usamos el mismo método que ya usas en /productos
    result = productos_service.listar()

    if result["ok"]:
        return ok(data=result["data"])
    else:
        return fail(result["error"], status=500)

@app.get('/api/usuarios')
def listar_usuarios():
    buscar = request.args.get("buscar", "", type=str)
    result = usuarios_service.consultar(buscar)
    return ok(data=result["data"]) if result["ok"] else fail(result["error"], status=500)

# Registrar Blueprint del carrito
app.register_blueprint(carrito_bp)



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
# ARRANQUE DE LA APLICACIÓN (Con apertura automática de Login)
# -------------------------------------------------------

if __name__ == "__main__":
    print(f"🚀 Servidor Flask corriendo en: http://{APP_HOST}:{APP_PORT}")
    
    # 🧠 Solución: abrir automáticamente la vista de login sin error 500
    import webbrowser, threading, time

    def abrir_login():
        time.sleep(1)  # Espera a que el servidor esté listo
        webbrowser.open_new_tab(f"http://127.0.0.1:{APP_PORT}/login")

    threading.Thread(target=abrir_login).start()

    app.run(host=APP_HOST, port=APP_PORT, debug=True, use_reloader=True)
