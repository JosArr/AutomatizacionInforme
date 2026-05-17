# src/database/query_executor.py
"""Ejecutor de queries paralelas"""

import time
from typing import Dict, Any, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
from datetime import datetime
import traceback

from src.utils.models import ServerConfig, ServerData, ServerStatus
from src.database.connector import SQLServerConnector
from src.data.transformer import DataTransformer
from src.logging_config.logger import get_logger


logger = get_logger()


class QueryExecutor:
    """Ejecutor de múltiples queries en paralelo"""

    def __init__(self, config: ServerConfig, queries: Dict[str, str], max_workers: int = 5):
        self.config = config
        self.queries = queries
        self.max_workers = max_workers
        self.transformer = DataTransformer()

    def execute_all_queries(self) -> ServerData:
        """Ejecutar todas las queries para un servidor"""
        server_data = ServerData(server_config=self.config)
        start_time = time.time()

        try:
            with SQLServerConnector(self.config) as connector:
                if not connector.connected:
                    server_data.status = ServerStatus.FAILED
                    server_data.error_message = "No se pudo establecer conexión"
                    return server_data

                results = self._execute_parallel_queries(connector)
                server_data = self.transformer.transform_server_data(
                    self.config,
                    results,
                    server_data
                )
                server_data.status = ServerStatus.SUCCESS
        except Exception as e:
            logger.error(f"Error ejecutando queries en {self.config.server}: {e}")
            server_data.status = ServerStatus.FAILED
            server_data.error_message = str(e)

        finally:
            server_data.query_execution_time_sec = time.time() - start_time

        return server_data

    def _execute_parallel_queries(self, connector: SQLServerConnector) -> Dict[str, Any]:
        """Ejecutar queries en paralelo"""
        results = {}
        failed_queries = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_query = {
                executor.submit(
                    self._execute_single_query,
                    connector,
                    query_name,
                    query
                ): query_name
                for query_name, query in self.queries.items()
            }

            for future in as_completed(future_to_query, timeout=self.config.timeout * 2):
                query_name = future_to_query[future]

                try:
                    query_result = future.result(timeout=self.config.timeout)
                    results[query_name] = query_result
                except FuturesTimeoutError:
                    logger.warning(
                        f"Timeout ejecutando query '{query_name}' en {self.config.server}",
                        server=self.config.server,
                        query=query_name
                    )
                    failed_queries.append(query_name)
                    results[query_name] = None

                except Exception as e:
                    logger.error(
                        f"Error en query '{query_name}' en {self.config.server}: {e}",
                        server=self.config.server,
                        query=query_name
                    )
                    failed_queries.append(query_name)
                    results[query_name] = None

        if failed_queries:
            logger.warning(
                f"{len(failed_queries)} queries fallidas en {self.config.server}: {failed_queries}",
                server=self.config.server
            )

        return results

    @staticmethod
    def _execute_single_query(connector: SQLServerConnector, query_name: str, query: str) -> Optional[List[Dict[str, Any]]]:
        """Ejecutar una query individual"""

        try:
            start_time = time.time()
            result = connector.execute_dict_query(query)
            duration = time.time() - start_time

            logger.debug(
                f"Query '{query_name}' completada en {duration:.2f}s",
                query=query_name,
                duration=duration
            )

            return result

        except Exception as e:
            logger.error(f"Error ejecutando query '{query_name}': {e}")
            raise


class ServerExecutor:
    """Ejecutor de queries para múltiples servidores en paralelo"""

    def __init__(self, queries: Dict[str, str], max_workers: int = 10):
        self.queries = queries
        self.max_workers = max_workers

    def execute_servers(self, configs: List[ServerConfig]) -> List[ServerData]:
        """Ejecutar queries en múltiples servidores en paralelo"""
        all_results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_config = {
                executor.submit(self._execute_server, config): config
                for config in configs
            }

            for future in as_completed(future_to_config):
                config = future_to_config[future]

                try:
                    server_data = future.result()
                    all_results.append(server_data)

                    if server_data.status == ServerStatus.SUCCESS:
                        logger.info(f"✓ {config.server} completado con éxito")
                    else:
                        logger.warning(f"⚠ {config.server} completado con estado: {server_data.status}")
                except Exception as e:
                    logger.error(f"✗ Error procesando {config.server}: {e}")
                    server_data = ServerData(server_config=config)
                    server_data.status = ServerStatus.FAILED
                    server_data.error_message = str(e)
                    all_results.append(server_data)

        return all_results

    def _execute_server(self, config: ServerConfig) -> ServerData:
        """Ejecutar queries para un servidor individual"""

        executor = QueryExecutor(config, self.queries, max_workers=5)
        return executor.execute_all_queries()

