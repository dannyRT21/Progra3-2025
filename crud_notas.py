# crud_notas.py
import crud_academico

db = crud_academico.crud()

class crud_notas:
    def consultar(self, buscar=""):
        """
        Devuelve las notas con los nombres de alumno y materia.
        Filtra por nombre del alumno o de la materia usando LIKE.
        OJO: db.consultar(sql) no soporta parámetros, por eso armamos el LIKE aquí
        cuidando el escape de comillas simples.
        """
        termino = (buscar or "").replace("'", "''")  # escape básico
        where = ""
        if termino:
            where = f"WHERE a.nombre LIKE '%{termino}%' OR m.nombre LIKE '%{termino}%'"

        sql = f"""
            SELECT
                n.idNota,
                n.idAlumno,
                n.idMateria,
                n.nota,
                n.aprobado,
                a.nombre AS nombre_alumno,
                m.nombre AS nombre_materia
            FROM notas n
            JOIN alumnos a ON n.idAlumno = a.idAlumno
            JOIN materias m ON n.idMateria = m.idMateria
            {where}
            ORDER BY a.nombre ASC, m.nombre ASC
        """
        res = db.consultar(sql)
        return res or []

    def administrar(self, datos):
        """
        Inserta, actualiza o elimina registros de la tabla notas.
        Usa SQL parametrizada porque db.ejecutar(sql, valores) sí soporta parámetros.
        """
        accion = datos.get('accion')

        if accion == "nuevo":
            sql = """
                INSERT INTO notas (idAlumno, idMateria, nota, aprobado)
                VALUES (%s, %s, %s, %s)
            """
            valores = (
                datos['idAlumno'],
                datos['idMateria'],
                datos['nota'],
                datos.get('aprobado')  # puede venir None
            )

        elif accion == "modificar":
            sql = """
                UPDATE notas
                SET idAlumno = %s, idMateria = %s, nota = %s, aprobado = %s
                WHERE idNota = %s
            """
            valores = (
                datos['idAlumno'],
                datos['idMateria'],
                datos['nota'],
                datos.get('aprobado'),
                datos['idNota']
            )

        elif accion == "eliminar":
            sql = "DELETE FROM notas WHERE idNota = %s"
            valores = (datos['idNota'],)

        else:
            return {"msg": "accion no soportada"}

        return db.ejecutar(sql, valores)
