# src/authentication/authenticator.py
"""Módulo de autenticación para conexiones SQL Server"""

import os
from typing import Optional
from src.utils.models import ServerConfig, AuthType


class Authenticator:
    """Autenticador para conexiones SQL Server"""

    @staticmethod
    def get_connection_string(config: ServerConfig) -> str:
        """Genera el string de conexión según el tipo de autenticación"""
        if config.auth_type == AuthType.SQL:
            return Authenticator._sql_authentication(config)
        elif config.auth_type == AuthType.WINDOWS:
            return Authenticator._windows_authentication(config)
        else:
            raise ValueError(f"Tipo de autenticación no soportado: {config.auth_type}")

    @staticmethod
    def _sql_authentication(config: ServerConfig) -> str:
        """SQL Authentication (usuario local SQL Server)"""
        if not config.username or not config.password:
            raise ValueError(f"SQL Authentication requiere username y password para {config.server}")

        connection_string = (
            f"Driver={{ODBC Driver 17 for SQL Server}};"
            f"Server={config.server},{config.port};"
            f"Database=master;"
            f"UID={config.username};"
            f"PWD={config.password};"
            f"Connection Timeout={config.timeout};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=yes;"
        )

        return connection_string

    @staticmethod
    def _windows_authentication(config: ServerConfig) -> str:
        """Windows Authentication (con y sin credenciales específicas)"""
        if not config.username and not config.password:
            connection_string = (
                f"Driver={{ODBC Driver 17 for SQL Server}};"
                f"Server={config.server},{config.port};"
                f"Database=master;"
                f"Trusted_Connection=yes;"
                f"Connection Timeout={config.timeout};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=yes;"
            )
        else:
            if not config.username or not config.password:
                raise ValueError(f"Windows Authentication requiere username y password juntos para {config.server}")

            if config.domain:
                user_spec = f"{config.domain}\\{config.username}"
            else:
                user_spec = config.username

            connection_string = (
                f"Driver={{ODBC Driver 17 for SQL Server}};"
                f"Server={config.server},{config.port};"
                f"Database=master;"
                f"UID={user_spec};"
                f"PWD={config.password};"
                f"Connection Timeout={config.timeout};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=yes;"
            )

        return connection_string

    @staticmethod
    def validate_credentials(config: ServerConfig) -> tuple[bool, Optional[str]]:
        """Validar que las credenciales sean válidas"""
        if not config.server:
            return False, "Servidor requerido"

        if config.auth_type == AuthType.SQL:
            if not config.username:
                return False, "SQL Auth requiere username"
            if not config.password:
                return False, "SQL Auth requiere password"

        if config.port < 1 or config.port > 65535:
            return False, f"Puerto inválido: {config.port}"

        if config.timeout < 1:
            return False, f"Timeout debe ser positivo: {config.timeout}"

        return True, None


class CredentialManager:
    """Gestor de credenciales desde variables de entorno"""

    @staticmethod
    def get_password(server: str, instance: str = "") -> Optional[str]:
        """Obtener password desde variables de entorno"""
        if instance:
            env_var = f"SQLSERVER_{server.upper()}_{instance.upper()}_PASSWORD"
            pwd = os.getenv(env_var)
            if pwd:
                return pwd

        env_var = f"SQLSERVER_{server.upper()}_PASSWORD"
        return os.getenv(env_var)

    @staticmethod
    def get_username(server: str, instance: str = "") -> Optional[str]:
        """Obtener username desde variables de entorno"""
        if instance:
            env_var = f"SQLSERVER_{server.upper()}_{instance.upper()}_USER"
            user = os.getenv(env_var)
            if user:
                return user

        env_var = f"SQLSERVER_{server.upper()}_USER"
        return os.getenv(env_var)

    @staticmethod
    def fill_credentials(config: ServerConfig) -> ServerConfig:
        """Llenar credenciales faltantes desde variables de entorno"""
        if config.auth_type == AuthType.SQL:
            if not config.password:
                config.password = CredentialManager.get_password(config.server, config.instance)
            if not config.username:
                config.username = CredentialManager.get_username(config.server, config.instance)

        return config
