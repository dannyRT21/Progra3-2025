# Model/crud_productos.py
import os, sys, uuid
sys.path.append(os.path.dirname(__file__))

from crud_de_base import PostgresDB, DatabaseError
from typing import Optional, Dict, Any


class CrudProductos:
    """
    CRUD para la tabla productos.
    """

    def __init__(self, db: Optional[PostgresDB] = None):
        self.db = db or PostgresDB()

    # ------------------------
    # 📜 LISTAR
    # ------------------------
    def listar(self) -> Dict[str, Any]:
        try:
            rows = self.db.execute_select(
                """
                SELECT id, categoria_id, nombre, descripcion, precio, cod_barras, inventario, activo, imagen
                FROM productos
                ORDER BY nombre ASC
                """
            )
            return {"ok": True, "data": rows}
        except DatabaseError as e:
            return {"ok": False, "error": str(e), "data": []}

    # ------------------------
    # 🧾 CREAR
    # ------------------------
    def crear(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        try:
            producto_id = str(uuid.uuid4())
            self.db.execute_query(
                """
                INSERT INTO productos (
                    id, categoria_id, nombre, descripcion, precio, cod_barras, inventario, activo, imagen
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    producto_id,
                    datos.get("categoria_id"),
                    datos["nombre"],
                    datos.get("descripcion"),
                    datos["precio"],
                    datos["cod_barras"],
                    datos["inventario"],
                    datos["activo"],
                    datos.get("imagen")
                )
            )
            return {
                "ok": True,
                "data": {"id": producto_id},
                "message": "Producto creado correctamente"
            }
        except DatabaseError as e:
            return {"ok": False, "error": str(e)}

    # ------------------------
    # ❌ ELIMINAR
    # ------------------------
    def eliminar(self, producto_id: str) -> Dict[str, Any]:
        try:
            affected = self.db.execute_query(
                "DELETE FROM productos WHERE id = %s", (producto_id,)
            )
            if affected == 0:
                return {"ok": False, "error": "Producto no encontrado"}
            return {"ok": True, "message": "Producto eliminado correctamente"}
        except DatabaseError as e:
            return {"ok": False, "error": str(e)}

    # ------------------------
    # ✏️ ACTUALIZAR
    # ------------------------
    def actualizar(self, producto_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza los datos de un producto existente.
        Compatible con PostgresDB.execute_select() sin argumentos extra.
        """
        try:
            campos = []
            valores = []

            # Solo se actualizan los campos que vengan en data
            for campo in [
                "nombre", "descripcion", "precio",
                "inventario", "categoria_id", "imagen", "activo"
            ]:
                if campo in data and data[campo] is not None:
                    campos.append(f"{campo} = %s")
                    valores.append(data[campo])

            if not campos:
                return {"ok": False, "error": "No hay campos válidos para actualizar"}

            valores.append(producto_id)

            # Ejecuta la actualización
            query = f"""
                UPDATE productos
                SET {', '.join(campos)}
                WHERE id = %s;
            """
            affected = self.db.execute_query(query, tuple(valores))

            if affected == 0:
                return {"ok": False, "error": "Producto no encontrado"}

            # Volver a leer el producto actualizado
            fila = self.db.execute_select(
                """
                SELECT id, nombre, descripcion, precio, inventario, imagen, activo
                FROM productos
                WHERE id = %s
                """,
                (producto_id,)
            )

            if not fila:
                return {"ok": False, "error": "Error al recuperar el producto actualizado"}

            return {
                "ok": True,
                "data": fila[0],
                "message": "Producto actualizado correctamente"
            }

        except DatabaseError as e:
            return {"ok": False, "error": str(e)}
        except Exception as e:
            return {"ok": False, "error": f"Error inesperado: {str(e)}"}
