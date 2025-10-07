from crud_de_base import PostgresDB
db = PostgresDB()
class crud_comentarios:
    def consultar(self, buscar):
        return db.consultar("SELECT * FROM comentarios WHERE nombre ILIKE %s", (f"%{buscar}%",))

    def administrar(self, datos):
        if datos['accion'] == "nuevo":
            sql = """
                INSERT INTO comentarios (nombre, e_mail, asunto, comentario, fecha_envio)
                VALUES (%s, %s, %s, %s, %s)
            """
            valores = (
                datos['nombre'],
                datos['e_mail'],
                datos['asunto'],
                datos['comentario'],
                datos['fecha_envio']
            )

        elif datos['accion'] == "modificar":
            sql = """
                UPDATE comentarios SET nombre=%s, e_mail=%s, asunto=%s, comentario=%s, fecha_envio=%s
                WHERE id=%s
            """
            valores = (
                datos['nombre'],
                datos['e_mail'],
                datos['asunto'],
                datos['comentario'],
                datos['fecha_envio'],
                datos['id']
            )

        elif datos['accion'] == "eliminar":
            sql = "DELETE FROM comentarios WHERE id=%s"
            valores = (datos['id'],)

        else:
            raise ValueError("Acción no válida")

        return db.ejecutar(sql, valores)