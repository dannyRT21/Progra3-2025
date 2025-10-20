import crud_academico

db = crud_academico.crud()

class crud_materia:
    def consultar(self, buscar=""):
        """
        Tu helper db.consultar(sql) acepta solo SQL (sin tuplas de valores).
        Por eso armamos el LIKE aquí y escapamos comillas simples para evitar romper el SQL.
        """
        termino = (buscar or "").replace("'", "''")  # escape básico de comilla simple
        sql = f"""
            SELECT
                m.idMateria,
                m.nombre AS nombre_materia,
                m.codigo,
                d.nombre AS nombre_docente,
                m.idDocente
            FROM materias m
            LEFT JOIN docentes d ON m.idDocente = d.idDocente
            WHERE m.nombre LIKE '%{termino}%'
            ORDER BY m.nombre ASC
        """
        res = db.consultar(sql)
        return res or []

    def administrar(self, datos):
        """
        Mantengo los INSERT/UPDATE/DELETE usando parámetros, porque db.ejecutar(sql, valores)
        en tu proyecto sí los soporta y ya te funcionaba el POST.
        """
        if datos['accion'] == "nuevo":
            sql = """
                INSERT INTO materias (nombre, codigo, idDocente)
                VALUES (%s, %s, %s)
            """
            valores = (
                datos['nombre'],
                datos['codigo'],
                datos['idDocente']
            )

        elif datos['accion'] == "modificar":
            sql = """
                UPDATE materias
                SET nombre = %s, codigo = %s, idDocente = %s
                WHERE idMateria = %s
            """
            valores = (
                datos['nombre'],
                datos['codigo'],
                datos['idDocente'],
                datos['idMateria']
            )

        elif datos['accion'] == "eliminar":
            sql = "DELETE FROM materias WHERE idMateria = %s"
            valores = (datos['idMateria'],)

        else:
            return "accion no soportada"

        return db.ejecutar(sql, valores)
    
