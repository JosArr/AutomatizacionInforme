# src/utils/models.py
"""Modelos de datos para el sistema de informes"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AuthType(str, Enum):
    """Tipos de autenticación soportados"""
    SQL = "sql"
    WINDOWS = "windows"


class ServerStatus(str, Enum):
    """Estados posibles del servidor"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class ServerConfig:
    """Configuración de conexión a un servidor SQL Server"""
    server: str
    instance: str
    port: int = 1433
    auth_type: AuthType = AuthType.SQL
    username: Optional[str] = None
    password: Optional[str] = None
    domain: Optional[str] = None
    timeout: int = 30
    retries: int = 3
    tags: List[str] = field(default_factory=list)

    def get_connection_string(self) -> str:
        """Genera el string de conexión según el tipo de autenticación"""
        base = f"Driver={{ODBC Driver 17 for SQL Server}};Server={self.server},{self.port};Database=master;Connection Timeout={self.timeout};"

        if self.auth_type == AuthType.SQL:
            return f"{base}UID={self.username};PWD={self.password};"
        elif self.auth_type == AuthType.WINDOWS:
            if self.domain:
                return f"{base}UID={self.domain}\\{self.username};PWD={self.password};"
            else:
                return f"{base}Trusted_Connection=yes;"

        return base


@dataclass
class DatabaseInfo:
    """Información de una base de datos"""
    name: str
    size_mb: float
    created_date: datetime
    owner: str
    status: str
    recovery_model: str
    rows_count: int = 0
    data_file_size_mb: float = 0.0
    log_file_size_mb: float = 0.0


@dataclass
class DiskSpace:
    """Información de espacio en disco"""
    drive_letter: str
    total_mb: float
    used_mb: float
    free_mb: float
    percent_used: float

    @property
    def percent_free(self) -> float:
        return 100 - self.percent_used


@dataclass
class ServiceStatus:
    """Estado de un servicio SQL Server"""
    service_name: str
    display_name: str
    status: str           # Running, Stopped, Paused, etc
    start_type: str      # Auto, Manual, Disabled


@dataclass
class UserInfo:
    """Información de usuario SQL Server"""
    login_name: str
    user_type: str       # SQL_LOGIN, WINDOWS_LOGIN, etc
    is_sysadmin: bool
    create_date: datetime
    last_login: Optional[datetime]


@dataclass
class BackupInfo:
    """Información de backup"""
    database_name: str
    backup_type: str    # D (Full), I (Differential), L (Log)
    backup_start_date: datetime
    backup_finish_date: datetime
    expiration_date: datetime
    backup_size_mb: float
    media_set_id: int


@dataclass
class JobInfo:
    """Información de un SQL Agent Job"""
    job_name: str
    last_run_outcome: int  # 0 = Failed, 1 = Succeeded, 3 = Canceled, 4 = In Progress
    last_run_date: Optional[datetime]
    last_run_duration: int  # segundos
    enabled: bool


@dataclass
class QueryInfo:
    """Información de query pesada"""
    query_hash: str
    statement_text: str
    execution_count: int
    total_elapsed_time_ms: float
    avg_elapsed_time_ms: float
    cpu_time_ms: float
    logical_reads: int


@dataclass
class TableInfo:
    """Información de tablas grandes"""
    schema_name: str
    table_name: str
    row_count: int
    size_mb: float
    data_space_mb: float
    index_space_mb: float
    reserved_mb: float

    @property
    def full_name(self) -> str:
        return f"{self.schema_name}.{self.table_name}"


@dataclass
class MemoryUsage:
    """Información de uso de memoria"""
    component: str
    allocated_mb: float
    used_mb: float
    free_mb: float


@dataclass
class ServerMetrics:
    """Métricas generales del servidor"""
    version: str
    edition: str
    instance_name: str
    collation: str
    memory_total_mb: int
    cpu_count: int
    max_memory_mb: int
    build_number: str


@dataclass
class ServerData:
    """Datos completos recolectados de un servidor"""
    server_config: ServerConfig
    metrics: Optional[ServerMetrics] = None
    databases: List[DatabaseInfo] = field(default_factory=list)
    disk_spaces: List[DiskSpace] = field(default_factory=list)
    services: List[ServiceStatus] = field(default_factory=list)
    sysadmin_users: List[UserInfo] = field(default_factory=list)
    failed_jobs: List[JobInfo] = field(default_factory=list)
    backups: List[BackupInfo] = field(default_factory=list)
    top_queries: List[QueryInfo] = field(default_factory=list)
    tables_by_size: List[TableInfo] = field(default_factory=list)
    memory_usage: List[MemoryUsage] = field(default_factory=list)

    created_datetime: datetime = field(default_factory=datetime.now)
    query_execution_time_sec: float = 0.0
    status: ServerStatus = ServerStatus.FAILED
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return self.status == ServerStatus.SUCCESS

    @property
    def is_failed(self) -> bool:
        return self.status == ServerStatus.FAILED


@dataclass
class ExecutionReport:
    """Reporte de ejecución general"""
    informe_id: str
    client_name: str
    invoice_month: str

    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None

    servers_total: int = 0
    servers_successful: int = 0
    servers_partial: int = 0
    servers_failed: int = 0

    queries_executed: int = 0
    queries_failed: int = 0

    document_path: Optional[str] = None
    document_size_bytes: int = 0

    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, server: str, error: str, severity: str = "ERROR"):
        """Añade un error al reporte"""
        self.errors.append({
            "timestamp": datetime.now().isoformat(),
            "server": server,
            "error": error,
            "severity": severity
        })

    @property
    def duration_seconds(self) -> float:
        if self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return 0.0

    @property
    def success_rate(self) -> float:
        if self.servers_total == 0:
            return 0.0
        return (self.servers_successful / self.servers_total) * 100
