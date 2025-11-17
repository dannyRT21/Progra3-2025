from flask import Blueprint, request, jsonify
from Model.crud_de_base import PostgresDB, DatabaseError

carrito_bp = Blueprint('carrito', __name__)

class CrudCarrito(PostgresDB):

    def obtener_carrito(self):
        try:
            query = "SELECT * FROM carrito ORDER BY id ASC;"
            return self.fetch_all(query)
        except DatabaseError as e:
            raise e

    def agregar_item(self, producto_id, nombre, descripcion, cod_barras, imagen, precio):
        try:
           
            existe = self.fetch_one(
                "SELECT * FROM carrito WHERE producto_id = %s;",
                (producto_id,)
            )

            if existe:
                query_update = """
                    UPDATE carrito 
                    SET cantidad = cantidad + 1
                    WHERE producto_id = %s
                    RETURNING *;
                """
                return self.fetch_one(query_update, (producto_id,))
            
            # Si no existe, lo insertamos
            query_insert = """
                INSERT INTO carrito 
                (producto_id, nombre, descripcion, cod_barras, imagen, precio, cantidad)
                VALUES (%s, %s, %s, %s, %s, %s, 1)
                RETURNING *;
            """
            return self.fetch_one(query_insert, (producto_id, nombre, descripcion, cod_barras, imagen, precio))

        except DatabaseError as e:
            raise e

    def actualizar_cantidad(self, item_id, qty):
        try:
            query = "UPDATE carrito SET cantidad = %s WHERE id = %s RETURNING *;"
            return self.fetch_one(query, (qty, item_id))
        except DatabaseError as e:
            raise e

    def vaciar_carrito(self):
        try:
            self.execute("DELETE FROM carrito;")
            return True
        except DatabaseError as e:
            raise e


carrito_crud = CrudCarrito()


# ------------ RUTAS API -------------------

@carrito_bp.route('/api/cart', methods=['GET'])
def api_get_cart():
    try:
        data = carrito_crud.obtener_carrito()
        return jsonify({"ok": True, "data": data})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@carrito_bp.route('/api/cart/add', methods=['POST'])
def api_add_cart():
    data = request.get_json()
    try:
        added = carrito_crud.agregar_item(
            data['producto_id'],
            data['nombre'],
            data.get('descripcion', ''),
            data.get('cod_barras', ''),
            data.get('imagen', ''),
            data['precio']
        )
        return jsonify({"ok": True, "data": added})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@carrito_bp.route('/api/cart/update', methods=['POST'])
def api_update_quantity():
    payload = request.get_json()
    try:
        updated = carrito_crud.actualizar_cantidad(payload['id'], payload['quantity'])
        return jsonify({"ok": True, "data": updated})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@carrito_bp.route('/api/cart/checkout', methods=['POST'])
def api_checkout():
    try:
        carrito_crud.vaciar_carrito()
        return jsonify({"ok": True, "msg": "Checkout completado"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})
