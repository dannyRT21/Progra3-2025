# crud_comentarios.py
import os, sys
# 🔧 Agrega la carpeta actual ("Model") al path
sys.path.append(os.path.dirname(__file__))

from crud_de_base import PostgresDB, DatabaseError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import re
from typing import Optional, Dict, Any


class ValidationError(Exception):
    """Error de validación de datos de dominio."""
    pass


def _normalize_str(s: Optional[str]) -> str:
    return (s or "").strip()


def _validate_email(email: str) -> bool:
    # Validación simple y suficiente para backend (el cliente puede usar algo más estricto)
    # Evita regex demasiado compleja; formato básico usuario@dominio
    if not email or len(email) > 254:
        return False
    # patrón sencillo
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email) is not None


class CrudComentarios:
    """
    Lógica de negocio para la tabla 'comentarios'.

    Esquema esperado:
      id SERIAL PK,
      nombre TEXT NOT NULL,
      e_mail TEXT NOT NULL,
      asunto TEXT NOT NULL,
      comentario TEXT NOT NULL
    """
    def __init__(self, db: Optional[PostgresDB] = None):
        self.db = db or PostgresDB()

    # ---------- Consultas ----------
    def consultar(self, buscar: str = "") -> Dict[str, Any]:
        buscar = _normalize_str(buscar)
        try:
            if buscar:
                rows = self.db.execute_select(
                    """
                    SELECT id, nombre, e_mail, asunto, comentario
                    FROM comentarios
                    WHERE nombre ILIKE %s OR asunto ILIKE %s OR comentario ILIKE %s
                    ORDER BY id DESC
                    """,
                    (f"%{buscar}%", f"%{buscar}%", f"%{buscar}%"),
                )
            else:
                rows = self.db.execute_select(
                    """
                    SELECT id, nombre, e_mail, asunto, comentario
                    FROM comentarios
                    ORDER BY id DESC
                    """
                )
            return {"ok": True, "data": rows, "error": None}
        except DatabaseError as e:
            return {"ok": False, "data": [], "error": str(e)}

    # ---------- Creación ----------
    def crear(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            datos = self._validate_for_create(payload)
            row = self.db.insert_and_return(
                """
                INSERT INTO comentarios (nombre, e_mail, asunto, comentario)
                VALUES (%s, %s, %s, %s)
                RETURNING id, nombre, e_mail, asunto, comentario
                """,
                (datos["nombre"], datos["e_mail"], datos["asunto"], datos["comentario"]),
            )
            return {
                "ok": True,
                "data": row,
                "message": "Comentario creado correctamente",
                "error": None,
            }
        except (ValidationError, DatabaseError) as e:
            return {"ok": False, "data": None, "message": None, "error": str(e)}

    # ---------- Actualización ----------
    def actualizar(self, comentario_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            datos = self._validate_for_update(payload)
            affected = self.db.execute_query(
                """
                UPDATE comentarios
                SET nombre = %s, e_mail = %s, asunto = %s, comentario = %s
                WHERE id = %s
                """,
                (
                    datos["nombre"],
                    datos["e_mail"],
                    datos["asunto"],
                    datos["comentario"],
                    comentario_id,
                ),
            )
            if affected == 0:
                return {"ok": False, "data": None, "message": None, "error": "Comentario no encontrado"}
            return {
                "ok": True,
                "data": {"id": comentario_id, **datos},
                "message": "Comentario actualizado correctamente",
                "error": None,
            }
        except (ValidationError, DatabaseError) as e:
            return {"ok": False, "data": None, "message": None, "error": str(e)}

    # ---------- Eliminación ----------
    def eliminar(self, comentario_id: int) -> Dict[str, Any]:
        try:
            if not isinstance(comentario_id, int) or comentario_id <= 0:
                raise ValidationError("ID inválido")

            affected = self.db.execute_query(
                "DELETE FROM comentarios WHERE id = %s",
                (comentario_id,),
            )
            if affected == 0:
                return {"ok": False, "data": None, "message": None, "error": "Comentario no encontrado"}
            return {
                "ok": True,
                "data": {"id": comentario_id},
                "message": "Comentario eliminado correctamente",
                "error": None,
            }
        except (ValidationError, DatabaseError) as e:
            return {"ok": False, "data": None, "message": None, "error": str(e)}

    # ---------- Validaciones internas ----------
    def _validate_for_create(self, payload: Dict[str, Any]) -> Dict[str, str]:
        nombre = _normalize_str(payload.get("nombre"))
        e_mail = _normalize_str(payload.get("e_mail"))
        asunto = _normalize_str(payload.get("asunto"))
        comentario = _normalize_str(payload.get("comentario"))

        if not nombre:
            raise ValidationError("El nombre es obligatorio")
        if not e_mail or not _validate_email(e_mail):
            raise ValidationError("El e_mail es inválido")
        if not asunto:
            raise ValidationError("El asunto es obligatorio")
        if not comentario:
            raise ValidationError("El comentario es obligatorio")

        return {"nombre": nombre, "e_mail": e_mail, "asunto": asunto, "comentario": comentario}

    def _validate_for_update(self, payload: Dict[str, Any]) -> Dict[str, str]:
        # Para update exigimos los mismos campos que en create (formulario completo)
        return self._validate_for_create(payload)
