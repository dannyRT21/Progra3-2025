from crud_de_base import PostgresDB

# Conexión a la base de datos
db = PostgresDB(
    dbname='db_copyvariedades',
    user='postgres',
    password='romero',
    host='localhost',
    port='5432'
)

class CrudComentarios:
    def consultar(self, buscar):
        return db.consultar(
            "SELECT * FROM comentarios WHERE nombre ILIKE %s",
            (f"%{buscar}%",)
        )

    def administrar(self, datos):
        if datos['accion'] == "nuevo":
            sql = """
                INSERT INTO comentarios (nombre, e_mail, asunto, comentario)
                VALUES (%s, %s, %s, %s)
            """
            valores = (
                datos['nombre'],
                datos['e_mail'],
                datos['asunto'],
                datos['comentario']
            )

        elif datos['accion'] == "modificar":
            sql = """
                UPDATE comentarios SET nombre=%s, e_mail=%s, asunto=%s, comentario=%s
                WHERE id=%s
            """
            valores = (
                datos['nombre'],
                datos['e_mail'],
                datos['asunto'],
                datos['comentario'],
                datos['id']
            )

        elif datos['accion'] == "eliminar":
            sql = "DELETE FROM comentarios WHERE id=%s"
            valores = (datos['id'],)

        else:
            return "acción inválida"

        return db.ejecutar(sql, valores)
