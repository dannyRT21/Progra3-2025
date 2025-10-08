import psycopg2

class PostgresDB:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print("✅ Conexión a la base de datos exitosa.")
        except psycopg2.Error as error:
            print("❌ Error al establecer la conexión:", error)
            self.conn = None

    def fetch_all(self, query):
        if not self.conn:
            print("⚠️ No hay conexión activa.")
            return []

        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
        except psycopg2.Error as error:
            print("❌ Error al ejecutar la consulta:", error)
            return []

    def close(self):
        if self.conn:
            self.conn.close()
            print("🔒 Conexión cerrada.")

# Ejemplo de uso
if __name__ == "__main__":
    db = PostgresDB(
        dbname='db_copyvariedades',
        user='postgres',
        password='romero',
        host='localhost',
        port='5432'
    )

    db.connect()

    resultados = db.fetch_all("SELECT * FROM comentarios;")
    for fila in resultados:
        print(fila)

    db.close()
