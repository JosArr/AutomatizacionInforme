# src/logging_config/logger.py
"""Logger centralizado para el sistema de informes"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import json


class JsonFormatter(logging.Formatter):
    """Formateador JSON para logs estructurados"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if hasattr(record, "server"):
            log_data["server"] = record.server
        if hasattr(record, "duration"):
            log_data["duration_seconds"] = record.duration
        if hasattr(record, "query"):
            log_data["query"] = record.query

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class ReporteLogger:
    """Logger personalizado para el sistema de informes"""

    _instance: Optional['ReporteLogger'] = None

    def __init__(self, log_dir: Path = None, log_name: str = "informe"):
        if log_dir is None:
            log_dir = Path(__file__).parent.parent.parent / "output" / "logs"

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_name = log_name
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.logger = logging.getLogger("informe")
        self.logger.setLevel(logging.DEBUG)

        self.logger.handlers.clear()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        log_file = self.log_dir / f"{self.timestamp}_{log_name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10_000_000,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(console_formatter)
        self.logger.addHandler(file_handler)

        # Handler para archivo JSON (DEBUG y superior)
        json_file = self.log_dir / f"{self.timestamp}_{log_name}_structured.json"
        json_handler = logging.handlers.RotatingFileHandler(
            json_file,
            maxBytes=10_000_000,
            backupCount=5,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(json_handler)

        # Handler para archivo de errores (ERROR y superior)
        error_file = self.log_dir / f"{self.timestamp}_{log_name}_errors.log"
        error_handler = logging.FileHandler(
            error_file,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(console_formatter)
        self.logger.addHandler(error_handler)

        self.logger.debug("Logger inicializado correctamente")

    @classmethod
    def get_instance(cls, log_dir: Path = None, log_name: str = "informe") -> "ReporteLogger":
        """Obtener instancia global del logger (singleton)"""
        if cls._instance is None:
            cls._instance = cls(log_dir, log_name)
        return cls._instance

    def info(self, message: str, **kwargs):
        """Log INFO"""
        self.logger.info(message, extra=kwargs)

    def debug(self, message: str, **kwargs):
        """Log DEBUG"""
        self.logger.debug(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log WARNING"""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """Log ERROR"""
        self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs):
        """Log CRITICAL"""
        self.logger.critical(message, extra=kwargs)

    def log_server_connection(self, server: str, status: str, duration: float, error: str = None):
        """Log de conexión a servidor"""
        if error:
            self.error(
                f"Error conectando a {server}: {error}",
                server=server,
                duration=duration
            )
        else:
            self.info(
                f"Conectado a {server}: {status}",
                server=server,
                duration=duration
            )

    def log_query_execution(self, server: str, query_name: str, duration: float, error: str = None):
        """Log de ejecución de query"""
        if error:
            self.error(
                f"Error ejecutando {query_name} en {server}: {error}",
                server=server,
                query=query_name,
                duration=duration
            )
        else:
            self.debug(
                f"Query {query_name} en {server} completada",
                server=server,
                query=query_name,
                duration=duration
            )

    def get_log_files(self) -> dict:
        """Obtener paths de los archivos de log"""
        return {
            "general": self.log_dir / f"{self.timestamp}_{self.log_name}.log",
            "errors": self.log_dir / f"{self.timestamp}_{self.log_name}_errors.log",
            "structured": self.log_dir / f"{self.timestamp}_{self.log_name}_structured.json",
        }


# Función de conveniencia global
def get_logger(log_dir: Path = None, log_name: str = "informe") -> ReporteLogger:
    """Obtener instancia del logger"""
    return ReporteLogger.get_instance(log_dir, log_name)

