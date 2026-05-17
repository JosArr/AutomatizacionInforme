# src/data/transformer.py
"""Transformación de datos desde SQL Server a objetos Python"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

from src.utils.models import (
    ServerConfig, ServerData, ServerMetrics, DatabaseInfo,
    DiskSpace, ServiceStatus, UserInfo, BackupInfo, JobInfo,
    QueryInfo, TableInfo, MemoryUsage, ServerStatus
)
from src.logging_config.logger import get_logger


logger = get_logger()


class DataTransformer:
    """Transformador de resultados SQL a objetos Python"""

    def transform_server_data(
        self,
        config: ServerConfig,
        query_results: Dict[str, List[Dict[str, Any]]],
        server_data: ServerData
    ) -> ServerData:
        """Transformar resultados de queries en ServerData"""
        server_data.server_config = config

        try:
            if query_results.get('version'):
                server_data.metrics = self._extract_server_metrics(
                    query_results['version'],
                    query_results
                )

            if query_results.get('databases'):
                server_data.databases = self._extract_databases(query_results['databases'])

            if query_results.get('disk_space'):
                server_data.disk_spaces = self._extract_disk_spaces(query_results['disk_space'])

            if query_results.get('services'):
                server_data.services = self._extract_services(query_results['services'])

            if query_results.get('users_sysadmin'):
                server_data.sysadmin_users = self._extract_sysadmin_users(
                    query_results['users_sysadmin']
                )

            if query_results.get('failed_jobs'):
                server_data.failed_jobs = self._extract_failed_jobs(query_results['failed_jobs'])

            if query_results.get('backups'):
                server_data.backups = self._extract_backups(query_results['backups'])

            if query_results.get('top_queries'):
                server_data.top_queries = self._extract_top_queries(query_results['top_queries'])

            if query_results.get('tables_by_size'):
                server_data.tables_by_size = self._extract_tables(query_results['tables_by_size'])

            return server_data

        except Exception as e:
            logger.error(f"Error transformando datos para {config.server}: {e}")
            raise

    @staticmethod
    def _extract_server_metrics(version_result: List[Dict], all_results: Dict) -> ServerMetrics:
        """Extraer métricas generales del servidor"""

        try:
            version_text = version_result[0].get('') if version_result else ""

            edition = ""
            instance_name = ""
            cpu_count = 0
            max_memory_mb = 0
            memory_total_mb = 0
            collation = ""
            build_number = ""

            # Buscar valores en otros resultados
            if all_results.get('edition'):
                edition = all_results['edition'][0].get('')  if all_results['edition'] else ""

            if all_results.get('instance_name'):
                instance_name = all_results['instance_name'][0].get('') if all_results['instance_name'] else "MSSQLSERVER"

            if all_results.get('cpu_count'):
                try:
                    cpu_count = int(all_results['cpu_count'][0].get('cpu_count', 0) or 0)
                except (ValueError, TypeError):
                    cpu_count = 0

            if all_results.get('max_memory'):
                try:
                    max_memory_mb = int(all_results['max_memory'][0].get('max_memory_mb', 0) or 0)
                except (ValueError, TypeError):
                    max_memory_mb = 0

            if all_results.get('memory_total'):
                try:
                    memory_total_mb = int(all_results['memory_total'][0].get('memory_total_mb', 0) or 0)
                except (ValueError, TypeError):
                    memory_total_mb = 0

            if all_results.get('collation'):
                collation = all_results['collation'][0].get('') if all_results['collation'] else ""

            if all_results.get('build_number'):
                build_number = all_results['build_number'][0].get('') if all_results['build_number'] else ""

            return ServerMetrics(
                version=version_text[:50],
                edition=edition[:50],
                instance_name=instance_name or "MSSQLSERVER",
                collation=collation[:50],
                memory_total_mb=memory_total_mb,
                cpu_count=cpu_count,
                max_memory_mb=max_memory_mb,
                build_number=build_number[:50]
            )

        except Exception as e:
            logger.warning(f"Error extrayendo métricas del servidor: {e}")
            return ServerMetrics(
                version="",
                edition="",
                instance_name="",
                collation="",
                memory_total_mb=0,
                cpu_count=0,
                max_memory_mb=0,
                build_number=""
            )

    @staticmethod
    def _extract_databases(db_result: List[Dict]) -> List[DatabaseInfo]:
        """Extraer información de bases de datos"""

        databases = []

        for row in db_result:
            try:
                name = row.get('name', 'Unknown')
                size_mb = float(row.get('size_mb', 0) or 0)
                created_date = row.get('create_date', datetime.now())
                if isinstance(created_date, str):
                    created_date = datetime.fromisoformat(created_date)

                owner = row.get('owner', '')
                status = row.get('state_desc', 'Unknown')
                recovery_model = row.get('recovery_model_desc', 'Unknown')

                databases.append(DatabaseInfo(
                    name=name,
                    size_mb=size_mb,
                    created_date=created_date,
                    owner=owner,
                    status=status,
                    recovery_model=recovery_model
                ))

            except Exception as e:
                logger.warning(f"Error procesando base de datos: {e}")
                continue

        return databases

    @staticmethod
    def _extract_disk_spaces(disk_result: List[Dict]) -> List[DiskSpace]:
        """Extraer información de espacios en disco"""
        disk_spaces = []

        for row in disk_result:
            try:
                drive = row.get('drive', '')
                mb_free = float(row.get('mb_free', 0) or 0)

                total_mb = mb_free * 2
                used_mb = max(0, total_mb - mb_free)
                percent_used = (used_mb / total_mb * 100) if total_mb > 0 else 0

                disk_spaces.append(DiskSpace(
                    drive_letter=drive,
                    total_mb=total_mb,
                    used_mb=used_mb,
                    free_mb=mb_free,
                    percent_used=percent_used
                ))

            except Exception as e:
                logger.warning(f"Error procesando disco: {e}")
                continue

        return disk_spaces

    @staticmethod
    def _extract_services(services_result: List[Dict]) -> List[ServiceStatus]:
        """Extraer información de servicios"""

        services = []

        for row in services_result:
            try:
                service_name = row.get('servicename', '')
                status = row.get('status', '')
                start_type = row.get('startup_type', '')

                services.append(ServiceStatus(
                    service_name=service_name,
                    display_name=service_name,
                    status=status,
                    start_type=start_type
                ))

            except Exception as e:
                logger.warning(f"Error procesando servicio: {e}")
                continue

        return services

    @staticmethod
    def _extract_sysadmin_users(users_result: List[Dict]) -> List[UserInfo]:
        """Extraer usuarios con rol sysadmin"""
        users = []

        for row in users_result:
            try:
                name = row.get('name', '')

                users.append(UserInfo(
                    login_name=name,
                    user_type='SYSADMIN',
                    is_sysadmin=True,
                    create_date=datetime.now(),
                    last_login=None
                ))

            except Exception as e:
                logger.warning(f"Error procesando usuario: {e}")
                continue

        return users

    @staticmethod
    def _extract_failed_jobs(jobs_result: List[Dict]) -> List[JobInfo]:
        """Extraer trabajos fallidos"""
        jobs = []

        for row in jobs_result:
            try:
                job_name = row.get('job_name', '')
                last_status = row.get('last_status', 'Unknown')
                run_date = row.get('run_date')

                if run_date and isinstance(run_date, str):
                    run_date = datetime.fromisoformat(run_date)

                jobs.append(JobInfo(
                    job_name=job_name,
                    last_run_outcome=0 if 'Failed' in last_status else 1,
                    last_run_date=run_date,
                    last_run_duration=row.get('run_duration', 0) or 0,
                    enabled=True
                ))

            except Exception as e:
                logger.warning(f"Error procesando job: {e}")
                continue

        return jobs

    @staticmethod
    def _extract_backups(backups_result: List[Dict]) -> List[BackupInfo]:
        """Extraer información de backups"""

        backups = []

        for row in backups_result:
            try:
                database_name = row.get('database_name', '')
                backup_type = row.get('backup_type', 'U')
                start_date = row.get('backup_start_date', datetime.now())
                finish_date = row.get('backup_finish_date', datetime.now())
                size_mb = float(row.get('backup_size_mb', 0) or 0)

                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date)
                if isinstance(finish_date, str):
                    finish_date = datetime.fromisoformat(finish_date)

                backups.append(BackupInfo(
                    database_name=database_name,
                    backup_type=backup_type,
                    backup_start_date=start_date,
                    backup_finish_date=finish_date,
                    expiration_date=datetime.now(),
                    backup_size_mb=size_mb,
                    media_set_id=0
                ))

            except Exception as e:
                logger.warning(f"Error procesando backup: {e}")
                continue

        return backups

    @staticmethod
    def _extract_top_queries(queries_result: List[Dict]) -> List[QueryInfo]:
        """Extraer top queries pesadas"""

        queries = []

        for row in queries_result:
            try:
                query_hash = str(row.get('query_hash', ''))
                statement = row.get('statement_text', '')[:500]
                exec_count = int(row.get('execution_count', 0) or 0)
                total_time_ms = float(row.get('total_elapsed_time_sec', 0) or 0) * 1000
                avg_time_ms = float(row.get('avg_elapsed_time_ms', 0) or 0)
                cpu_time = float(row.get('cpu_time_ms', 0) or 0)
                log_reads = int(row.get('logical_reads', 0) or 0)

                queries.append(QueryInfo(
                    query_hash=query_hash,
                    statement_text=statement,
                    execution_count=exec_count,
                    total_elapsed_time_ms=total_time_ms,
                    avg_elapsed_time_ms=avg_time_ms,
                    cpu_time_ms=cpu_time,
                    logical_reads=log_reads
                ))

            except Exception as e:
                logger.warning(f"Error procesando query: {e}")
                continue

        return queries

    @staticmethod
    def _extract_tables(tables_result: List[Dict]) -> List[TableInfo]:
        """Extraer tablas más pesadas"""
        tables = []

        for row in tables_result:
            try:
                schema_name = row.get('schema_name', 'dbo')
                table_name = row.get('table_name', '')
                row_count = int(row.get('row_count', 0) or 0)
                size_mb = float(row.get('size_mb', 0) or 0)

                tables.append(TableInfo(
                    schema_name=schema_name,
                    table_name=table_name,
                    row_count=row_count,
                    size_mb=size_mb,
                    data_space_mb=size_mb * 0.8,
                    index_space_mb=size_mb * 0.2,
                    reserved_mb=size_mb
                ))

            except Exception as e:
                logger.warning(f"Error procesando tabla: {e}")
                continue

        return tables
