# src/config/loader.py
"""Cargador de configuración desde JSON/YAML"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

from src.utils.models import ServerConfig, AuthType


class ConfigLoader:
    """Cargador de configuración del proyecto"""

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent / "config"

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_servers(self, filename: str = "servers.json") -> List[ServerConfig]:
        """Cargar configuración de servidores desde JSON o YAML"""
        config_path = self.config_dir / filename

        if not config_path.exists():
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")

        try:
            if filename.endswith('.json'):
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif filename.endswith(('.yaml', '.yml')):
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
            else:
                raise ValueError(f"Formato de archivo no soportado: {filename}")

            if isinstance(data, list):
                servers_data = data
            elif isinstance(data, dict) and 'servers' in data:
                servers_data = data['servers']
            else:
                raise ValueError("Formato de configuración inválido. Debe ser lista o dict con key 'servers'")

            servers = []
            for server_data in servers_data:
                server = self._parse_server_config(server_data)
                servers.append(server)

            return servers

        except json.JSONDecodeError as e:
            raise ValueError(f"Error decodificando JSON: {e}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error decodificando YAML: {e}")

    @staticmethod
    def _parse_server_config(data: Dict[str, Any]) -> ServerConfig:
        """Parsear un diccionario a ServerConfig garantizando validación"""
        server = data.get('server')
        if not server:
            raise ValueError("Campo 'server' es obligatorio")

        instance = data.get('instance', 'MSSQLSERVER')
        auth_type_str = data.get('auth_type', 'sql').lower()

        try:
            auth_type = AuthType(auth_type_str)
        except ValueError:
            raise ValueError(f"auth_type debe ser 'sql' o 'windows', recibido: {auth_type_str}")

        username = data.get('username')
        password = data.get('password')

        if auth_type == AuthType.SQL:
            if not username or not password:
                raise ValueError(f"SQL Authentication requiere 'username' y 'password' para {server}")
        elif auth_type == AuthType.WINDOWS:
            if not username and not password:
                pass
            elif username and not password:
                raise ValueError(f"Si se especifica username en Windows Auth, se requiere password para {server}")

        return ServerConfig(
            server=server,
            instance=instance,
            port=data.get('port', 1433),
            auth_type=auth_type,
            username=username,
            password=password,
            domain=data.get('domain'),
            timeout=data.get('timeout', 30),
            retries=data.get('retries', 3),
            tags=data.get('tags', [])
        )

    def load_queries(self, filename: str = "queries.json") -> Dict[str, str]:
        """Cargar queries T-SQL desde archivo"""
        config_path = self.config_dir / filename

        if not config_path.exists():
            raise FileNotFoundError(f"Archivo de queries no encontrado: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            if filename.endswith('.json'):
                queries = json.load(f)
            else:
                queries = yaml.safe_load(f)

        return queries

    def save_servers(self, servers: List[ServerConfig], filename: str = "servers.json"):
        """Guardar configuración de servidores (sin passwords!)"""
        config_path = self.config_dir / filename
        servers_data = []

        for server in servers:
            servers_data.append({
                "server": server.server,
                "instance": server.instance,
                "port": server.port,
                "auth_type": server.auth_type.value,
                "domain": server.domain,
                "timeout": server.timeout,
                "retries": server.retries,
                "tags": server.tags,
            })

        with open(config_path, 'w', encoding='utf-8') as f:
            if filename.endswith('.json'):
                json.dump(servers_data, f, indent=2, ensure_ascii=False)
            else:
                yaml.dump(servers_data, f, default_flow_style=False, allow_unicode=True)


class EnvironmentConfig:
    """Gestor de variables de entorno"""

    @staticmethod
    def get_password(server_name: str) -> Optional[str]:
        """Obtener password desde variables de entorno"""
        env_var = f"SQLSERVER_{server_name}_PASSWORD"
        return os.getenv(env_var)

    @staticmethod
    def get_all_passwords() -> Dict[str, str]:
        """Obtener todos los passwords desde variables de entorno"""
        passwords = {}
        for key, value in os.environ.items():
            if key.startswith("SQLSERVER_") and key.endswith("_PASSWORD"):
                server = key.replace("SQLSERVER_", "").replace("_PASSWORD", "")
                passwords[server] = value
        return passwords

    @staticmethod
    def load_env_file(env_file: Path = None):
        """Cargar archivo .env"""
        if env_file is None:
            env_file = Path(__file__).parent.parent.parent / ".env"

        if env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)
