import crud_academico

db = crud_academico.crud()

class crud_usuario:
    def consultar(self, buscar):
        # Búsqueda por nombre parcial
        return db.consultar("SELECT * FROM usuarios WHERE nombre LIKE '%" + buscar + "%'")
    
    def administrar(self, datos):
        if datos['accion'] == "nuevo":
            sql = """
                INSERT INTO usuarios (usuario, clave, nombre, direccion, telefono)
                VALUES (%s, %s, %s, %s, %s)
            """
            valores = (
                datos['usuario'],
                datos['clave'],
                datos['nombre'],
                datos['direccion'],
                datos['telefono']
            )

        elif datos['accion'] == "modificar":
            sql = """
                UPDATE usuarios 
                SET usuario=%s, clave=%s, nombre=%s, direccion=%s, telefono=%s
                WHERE idUsuario=%s
            """
            valores = (
                datos['usuario'],
                datos['clave'],
                datos['nombre'],
                datos['direccion'],
                datos['telefono'],
                datos['idUsuario']
            )

        elif datos['accion'] == "eliminar":
            sql = "DELETE FROM usuarios WHERE idUsuario=%s"
            valores = (datos['idUsuario'],)

        return db.ejecutar(sql, valores)
    
    def login(self, usuario, clave):
        # Consulta para login (usuario exacto y clave exacta)
        sql = "SELECT * FROM usuarios WHERE usuario=%s AND clave=%s"
        valores = (usuario, clave)
        resultado = db.consultar_uno(sql, valores)
        return resultado
