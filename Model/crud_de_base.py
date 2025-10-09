# crud_de_base.py
import os
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor


class DatabaseError(Exception):
    """Error de base de datos para propagar al nivel de servicio."""
    pass


class PostgresDB:
    """
    Capa de acceso a datos con:
    - Pool de conexiones
    - Consultas parametrizadas
    - Manejo de transacciones (commit/rollback)
    - Métodos separados para SELECT y DML (INSERT/UPDATE/DELETE)
    """
    def __init__(
        self,
        dbname=None,
        user=None,
        password=None,
        host=None,
        port=None,
        minconn=1,
        maxconn=5,
    ):
        # Permite configuración por variables de entorno o argumentos
        self.dbname = dbname or os.getenv("PGDATABASE", "db_copyvariedades")
        self.user = user or os.getenv("PGUSER", "postgres")
        self.password = password or os.getenv("PGPASSWORD", "romero")
        self.host = host or os.getenv("PGHOST", "localhost")
        self.port = port or os.getenv("PGPORT", "5432")

        self.minconn = int(os.getenv("PG_MINCONN", minconn))
        self.maxconn = int(os.getenv("PG_MAXCONN", maxconn))
        self._pool = None

        self._init_pool()

    def _init_pool(self):
        try:
            self._pool = pool.SimpleConnectionPool(
                self.minconn,
                self.maxconn,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
        except psycopg2.Error as e:
            raise DatabaseError(f"Error al crear el pool de conexiones: {e}")

    def close_pool(self):
        if self._pool:
            self._pool.closeall()

    def _get_conn(self):
        if not self._pool:
            self._init_pool()
        try:
            return self._pool.getconn()
        except psycopg2.Error as e:
            raise DatabaseError(f"No se pudo obtener conexión del pool: {e}")

    def _put_conn(self, conn):
        if self._pool and conn:
            self._pool.putconn(conn)

    def execute_select(self, query: str, params=None):
        """
        Ejecuta SELECT y retorna una lista de diccionarios (columnas como claves).
        """
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                rows = cur.fetchall()
                return [dict(r) for r in rows]
        except psycopg2.Error as e:
            raise DatabaseError(f"Error en SELECT: {e}")
        finally:
            self._put_conn(conn)

    def execute_query(self, query: str, params=None) -> int:
        """
        Ejecuta INSERT/UPDATE/DELETE. Retorna rowcount.
        Maneja commit/rollback automáticamente.
        """
        conn = self._get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                affected = cur.rowcount
            conn.commit()
            return affected
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Error en DML: {e}")
        finally:
            self._put_conn(conn)

    def insert_and_return(self, query: str, params=None) -> dict:
        """
        Ejecuta un INSERT ... RETURNING ... y retorna la fila devuelta como dict.
        """
        conn = self._get_conn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                row = cur.fetchone()
            conn.commit()
            return dict(row) if row else {}
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Error en INSERT RETURNING: {e}")
        finally:
            self._put_conn(conn)
