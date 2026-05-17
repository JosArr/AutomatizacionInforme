# src/database/connector.py
"""Conector a SQL Server con manejo de conexiones"""

import pyodbc
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
import threading

from src.utils.models import ServerConfig
from src.authentication.authenticator import Authenticator, CredentialManager
from src.logging_config.logger import get_logger


logger = get_logger()


class ConnectionPool:
    """Pool simple de conexiones SQL Server"""

    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections: Dict[str, List[pyodbc.Connection]] = {}
        self.lock = threading.RLock()

    def get_connection(self, connection_string: str) -> pyodbc.Connection:
        """Obtener una conexión del pool o crear una nueva"""
        with self.lock:
            if connection_string not in self.connections:
                self.connections[connection_string] = []

            if self.connections[connection_string]:
                conn = self.connections[connection_string].pop()
                try:
                    conn.execute("SELECT 1")
                    return conn
                except Exception:
                    pass

            try:
                conn = pyodbc.connect(connection_string, autocommit=True)
                conn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
                conn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
                conn.setencoding(encoding='utf-8')
                return conn
            except Exception as e:
                logger.error(f"Error creando conexión: {e}")
                raise

    def return_connection(self, connection_string: str, conn: pyodbc.Connection):
        """Devolver una conexión al pool"""

        with self.lock:
            if connection_string not in self.connections:
                self.connections[connection_string] = []

            if len(self.connections[connection_string]) < self.max_connections:
                self.connections[connection_string].append(conn)
            else:
                conn.close()

    def close_all(self):
        """Cerrar todas las conexiones del pool"""

        with self.lock:
            for connections in self.connections.values():
                for conn in connections:
                    try:
                        conn.close()
                    except Exception:
                        pass
            self.connections.clear()


class SQLServerConnector:
    """Conector a SQL Server"""

    # Pool global
    _pool = ConnectionPool(max_connections=20)

    def __init__(self, config: ServerConfig):
        self.config = config
        self.conn: Optional[pyodbc.Connection] = None
        self.connection_string: Optional[str] = None
        self.connected = False
        self.connect_time: Optional[datetime] = None

    def connect(self) -> bool:
        """Conectar al servidor SQL"""
        try:
            config = CredentialManager.fill_credentials(self.config)
            is_valid, error_msg = Authenticator.validate_credentials(config)
            if not is_valid:
                logger.error(f"Credenciales inválidas para {config.server}: {error_msg}")
                return False

            self.connection_string = Authenticator.get_connection_string(config)
            start_time = time.time()
            last_error = None

            for attempt in range(config.retries):
                try:
                    self.conn = self._pool.get_connection(self.connection_string)
                    self.connected = True
                    self.connect_time = datetime.now()

                    duration = time.time() - start_time
                    logger.info(
                        f"Conectado a {config.server}\\{config.instance}",
                        server=config.server,
                        duration=duration
                    )
                    return True
                except pyodbc.OperationalError as e:
                    last_error = str(e)
                    if attempt < config.retries - 1:
                        time.sleep(2 ** attempt)
                    continue

            logger.error(
                f"No se pudo conectar a {config.server} después de {config.retries} intentos: {last_error}",
                server=config.server
            )
            return False

        except Exception as e:
            logger.error(f"Error conectando a {self.config.server}: {e}", server=self.config.server)
            return False

    def disconnect(self):
        """Desconectar del servidor"""
        if self.conn:
            try:
                self._pool.return_connection(self.connection_string, self.conn)
            except Exception:
                pass
        self.connected = False
        self.conn = None

    def execute_query(self, query: str) -> Optional[List[tuple]]:
        """Ejecutar una query y retornar resultados"""
        if not self.connected or not self.conn:
            raise RuntimeError("No hay conexión activa")

        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            columns = [description[0] for description in cursor.description] if cursor.description else []
            results = cursor.fetchall()
            cursor.close()
            return results, columns

        except pyodbc.ProgrammingError as e:
            logger.error(f"Error SQL: {e}", query=query)
            raise
        except Exception as e:
            logger.error(f"Error ejecutando query: {e}", query=query)
            raise

    def execute_dict_query(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Ejecutar query y retornar resultados como lista de dictionaries"""
        results, columns = self.execute_query(query)
        dict_results = []
        for row in results:
            row_dict = dict(zip(columns, row))
            dict_results.append(row_dict)

        return dict_results

    def execute_scalar(self, query: str) -> Any:
        """Ejecutar query que devuelve un único valor"""
        results, _ = self.execute_query(query)
        if results and len(results) > 0 and len(results[0]) > 0:
            return results[0][0]

        return None

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

    def __del__(self):
        """Context manager cleanup"""
        try:
            self.disconnect()
        except Exception:
            pass


@staticmethod
def close_all_pools():
    """Cerrar todos los pools de conexión"""
    SQLServerConnector._pool.close_all()
