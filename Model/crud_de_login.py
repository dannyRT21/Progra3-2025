# crud_usuarios.py
import os, sys, logging
sys.path.append(os.path.dirname(__file__))

from crud_de_base import PostgresDB, DatabaseError
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing import Optional, Dict, Any


def _normalize_str(s: Optional[str]) -> str:
    return (s or "").strip()


class CrudUsuarios:
    """
    Lógica de negocio para la tabla 'usuarios'.

    Esquema esperado:
      id SERIAL PK,
      nombre TEXT NOT NULL,
      correo_electronico TEXT NOT NULL UNIQUE,
      contrasena TEXT NOT NULL,
      rol TEXT NOT NULL
    """
    def __init__(self, db: Optional[PostgresDB] = None):
        self.db = db or PostgresDB()
        self.logger = logging.getLogger(__name__)

    # ---------- Consultas ----------
    def consultar(self, buscar: str = "") -> Dict[str, Any]:
        buscar = _normalize_str(buscar)
        try:
            if buscar:
                rows = self.db.execute_select(
                    """
                    SELECT id, nombre, correo_electronico, rol
                    FROM usuarios
                    WHERE nombre ILIKE %s OR correo_electronico ILIKE %s
                    ORDER BY id DESC
                    """,
                    (f"%{buscar}%", f"%{buscar}%"),
                )
            else:
                rows = self.db.execute_select(
                    """
                    SELECT id, nombre, correo_electronico, rol
                    FROM usuarios
                    ORDER BY id DESC
                    """
                )
            return {"ok": True, "data": rows, "error": None}
        except DatabaseError as e:
            self.logger.error(f"Error consultando usuarios: {e}")
            return {"ok": False, "data": [], "error": str(e)}

    # ---------- Validación de login ----------
    def verificar_login(self, correo: str, contrasena: str) -> Dict[str, Any]:
        correo = _normalize_str(correo)
        contrasena = _normalize_str(contrasena)
        try:
            rows = self.db.execute_select(
                """
                SELECT id, nombre, correo_electronico, contrasena, rol
                FROM usuarios
                WHERE correo_electronico = %s LIMIT 1
                """,
                (correo,)
            )
            if not rows:
                return {"ok": False, "error": "Usuario no encontrado."}

            usuario = rows[0]
            # ⚠️ En el futuro usar bcrypt: bcrypt.checkpw(contrasena.encode(), usuario["contrasena"].encode())
            if usuario["contrasena"].strip() == contrasena.strip():
                return {"ok": True, "data": usuario}
            else:
                return {"ok": False, "error": "Contraseña incorrecta."}

        except DatabaseError as e:
            self.logger.error(f"Error en verificar_login: {e}")
            return {"ok": False, "error": str(e)}
