# 📊 Sistema de Generación Automatizado de Informes SQL Server

Sistema enterprise-grade en Python para automatizar la generación de informes mensuales desde múltiples servidores Microsoft SQL Server hacia documentos Word (.docx) con formato preservado.

## ✨ Características

### ✅ Autenticación Flexible
- **SQL Authentication** (usuario/contraseña SQL Server)
- **Windows Authentication** (Integrated Security)
- **Windows con Credenciales de Dominio**
- **Gestor de Credenciales** desde variables de entorno
- Reintentos automáticos con backoff exponencial

### ✅ Conexión a SQL Server
- Pool de conexiones optimizado
- Manejo de timeouts
- Reintentos automáticos
- Soporta múltiples instancias
- Conexiones paralelas

### ✅ Recolección de Datos
- **15+ queries T-SQL** predefinidas
- Ejecución de queries en paralelo
- Manejo robusto de errores
- Validación de datos
- Logs detallados

### ✅ Datos Recolectados
- Versión, edición, build de SQL Server
- Memoria y CPU del servidor
- Información de bases de datos
- Espacio en discos
- Servicios SQL Server
- Usuarios con rol sysadmin
- Backups y sus características
- Jobs fallidos
- Top queries pesadas
- Tablas con mayor tamaño
- Recuentos de registros

### ✅ Generación de Documentos
- Preserva 100% del template original
- Mantiene formatos y estilos
- Preserva imágenes y logos
- Preserva header/footer
- Rellenadodinámico de tablas
- Duplication de secciones por servidor

### ✅ Seguridad
- Nunca hardcodea passwords
- Credenciales en variables de entorno
- Soporte para .env (python-dotenv)
- No registra credenciales en logs
- Preparado para Azure KeyVault

### ✅ Logging y Monitoreo
- Logs estructurados en JSON
- Archivo general de logs
- Archivo específico de errores
- Console output formateado
- Estadísticas de ejecución
- Metadata de informe

### ✅ Manejo de Errores
- Tolerante a fallos parciales
- Un servidor falla → continúa con los demás
- Una query falla → continúa con las demás
- Warnings y errores registrados
- Reporte final detallado

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Clonar o descargar el proyecto
cd AutomatizacionInforme

# Crear ambiente virtual
python -m venv .venv

# Activar ambiente virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Instalar dependencias
pip install -r requirements.txt

# Instalar ODBC Driver (si no lo tienes)
# Windows: Descargar de Microsoft
# macOS: brew install mssql-tools
# Linux: apt-get install unixodbc msodbcsql17
```

### 2. Configuración

```bash
# Copiar archivo de ejemplo
copy config\servers.example.json config\servers.json

# Editar con tus servidores
notepad config\servers.json
```

**Respuesta configuración`config/servers.json`:**

```json
[
  {
    "server": "172.16.4.166",
    "instance": "SACVDB",
    "port": 1433,
    "auth_type": "sql",
    "username": "sa",
    "timeout": 30,
    "retries": 3,
    "tags": ["producción", "cliente_a"]
  },
  {
    "server": "172.25.91.69",
    "instance": "MSSQLSERVER",
    "port": 1433,
    "auth_type": "windows",
    "timeout": 30,
    "retries": 3,
    "tags": ["producción", "cliente_b"]
  }
]
```

### 3. Credenciales Seguras

**Crear archivo `.env`:**

```bash
copy .env.example .env
notepad .env
```

**Contenido de `.env`:**

```
SQLSERVER_172.16.4.166_SACVDB_PASSWORD=tu_password_aqui
SQLSERVER_172.25.91.69_MSSQLSERVER_PASSWORD=otro_password_aqui
```

### 4. Template Word

Copiatutemplate al directorio:

```bash
copy "tu_template.docx" "templates/INFORME_TEMPLATE.docx"
```

### 5. Ejecutar

```bash
python src/main.py
```

Salida esperada:

```
2026-05-11 09:00:00 - informe - INFO - Iniciando generación de informes
2026-05-11 09:00:00 - informe - INFO - Cargada configuración: 19 servidores
2026-05-11 09:00:05 - informe - INFO - Conectado a 172.16.4.166\SACVDB
2026-05-11 09:00:12 - informe - INFO - Conectado a 172.25.91.69\MSSQLSERVER
...
2026-05-11 09:03:30 - informe - INFO - ✓ Informe generado exitosamente
2026-05-11 09:03:30 - informe - INFO - 📁 Archivo: output/informes/INFORME_ACEROS_AREQUIPA_MAYO_2026.docx
```

## 📁 Estructura del Proyecto

```
AutomatizacionInforme/
├── src/                              # Código fuente
│   ├── main.py                      # Entrada principal
│   ├── config/
│   │   └── loader.py                # Cargador de configuraciones
│   ├── authentication/
│   │   └── authenticator.py         # Gestión de autenticación
│   ├── database/
│   │   ├── connector.py             # Conexión a SQL Server
│   │   └── query_executor.py        # Ejecución de queries
│   ├── data/
│   │   └── transformer.py           # Transformación de datos
│   ├── document/
│   │   └── template_handler.py      # Manejo de templates Word
│   ├── logging_config/
│   │   └── logger.py                # Logger centralizado
│   └── utils/
│       └── models.py                # Definición de dataclasses
├── config/
│   ├── servers.json                 # Configuración de servidores
│   └── queries.json                 # Queries T-SQL disponibles
├── templates/
│   └── INFORME_TEMPLATE.docx        # Template Word base
├── output/
│   ├── informes/                    # Informes generados
│   └── logs/                        # Logs y estadísticas
├── requirements.txt                 # Dependencias
├── .env.example                     # Exemplo de variables de entorno
└── README.md                        # Este archivo
```

## 🔧 Configuración Avanzada

### SQL Authentication

```json
{
  "server": "172.16.4.166",
  "instance": "SACVDB",
  "port": 1433,
  "auth_type": "sql",
  "username": "sa",
  "password": null,
  "timeout": 30,
  "retries": 3
}
```

Las contraseñas se obtienen de variables de entorno:`SQLSERVER_172.16.4.166_SACVDB_PASSWORD`

### Windows Authentication Integrada

```json
{
  "server": "172.25.91.69",
  "instance": "MSSQLSERVER",
  "port": 1433,
  "auth_type": "windows",
  "timeout": 30,
  "retries": 3
}
```

Usa las credenciales del usuario que ejecuta el programa.

### Windows con Dominio

```json
{
  "server": "sql-prod.empresa.local",
  "instance": "MSSQLSERVER",
  "port": 1433,
  "auth_type": "windows",
  "domain": "EMPRESA",
  "username": "sql_admin",
  "password": null,
  "timeout": 30,
  "retries": 3
}
```

Contraseña desde: `SQLSERVER_SQL-PROD.EMPRESA.LOCAL_MSSQLSERVER_PASSWORD`

### Timeouts y Reintentos

```json
{
  "server": "slow-server.com",
  "instance": "MSSQLSERVER",
  "port": 1433,
  "auth_type": "windows",
  "timeout": 60,
  "retries": 5
}
```

- `timeout`: Segundos de espera máximo (default: 30)
- `retries`: Número de reintentos (default: 3)

### Tags para Filtrado

```json
{
  "server": "prod-db",
  "instance": "MSSQLSERVER",
  "tags": ["producción", "crítico", "cliente_a", "region_norte"]
}
```

## 🔐 Seguridad

### ❌ Nunca Hagas Esto:

```json
{
  "server": "172.16.4.166",
  "username": "sa",
  "password": "MiPasswordSeguro123!"
}
```

### ✅ Haz Esto Instead

**1. Variables de Entorno (`.env`)**

```
SQLSERVER_172.16.4.166_PASSWORD=MiPasswordSeguro123!
```

**2. Desde archivo en memoria**

El programa carga passwords desde variables de entorno automáticamente.

**3. Para CI/CD**

Usa GitHub Secrets o Azure KeyVault:

```python
import os
password = os.getenv('SQLSERVER_PASSWORD')
```

## 📊 Ejemplos de Uso

### Ejemplo 1: Informe Básico

```python
from src.config.loader import ConfigLoader
from src.database.query_executor import ServerExecutor
from src.logging_config.logger import get_logger

# Cargar configuración
loader = ConfigLoader()
servers = loader.load_servers()
queries = loader.load_queries()

# Ejecutar
executor = ServerExecutor(queries, max_workers=10)
results = executor.execute_servers(servers)

# Procesar resultados
for server_data in results:
    print(f"{server_data.server_config.server}: {server_data.status}")
```

### Ejemplo 2: Filtrar Servidores

```python
# Ejecutar solo servidores de producción
prod_servers = [s for s in servers if "producción" in s.tags]
results = executor.execute_servers(prod_servers)
```

### Ejemplo 3: Consultar Variables de Entorno

```python
from src.authentication.authenticator import CredentialManager

# Obtener password desde env
password = CredentialManager.get_password("172.16.4.166", "SACVDB")
```

## 📋 Queries Disponibles

Las queries se definen en `config/queries.json` y pueden customizarse:

- **version**: Versión de SQL Server
- **server_name**: Nombre de la instancia
- **edition**: Edición (Express, Standard, Enterprise)
- **memory_total**: Memoria física total
- **databases**: Lista de bases de datos
- **users_sysadmin**: Usuarios con rol sysadmin
- **failed_jobs**: Jobs that failed
- **backups**: Información de backups
- **top_queries**: Queries pesadas
- **tables_by_size**: Tablas más grandes
- **disk_space**: Espacio en discos

## 🎯 Performance

### Benchmarks Típicos (20 servidores)

| Operación | Tiempo |
|-----------|--------|
| Conexión por servidor | 0.5-2s |
| Queries ejecutadas (paralelas) | 5-10s |
| Transformación de datos | 1s |
| Generación documento | 5-15s |
| **Total** | **~2-3 minutos** |

### Optimizaciones

- Connection pooling automático
- Queries ejecutadas en paralelo (max 5 por servidor)
- Servidores procesados en paralelo (max 10)
- Caching de conexiones
- Threading sin GIL para I/O bound

## 📝 Logs

Tres archivos de log se generan automáticamente:

### 1. Archivo General

`output/logs/2026-05-11_090000_informe.log`

```
2026-05-11 09:00:00 - informe - INFO - Cargada configuración: 19 servidores
2026-05-11 09:00:05 - informe - INFO - Conectado a 172.16.4.166\SACVDB
2026-05-11 09:00:12 - informe - DEBUG - Query 'version' ejecutada en 0.50s
```

### 2. Errors Only

`output/logs/2026-05-11_090000_informe_errors.log`

```
2026-05-11 09:00:30 - informe - ERROR - Error conectando a old-server: Timeout
```

### 3. Structured (JSON)

`output/logs/2026-05-11_090000_informe_structured.json`

```json
{"timestamp": "2026-05-11T09:00:05", "level": "INFO", "message": "Conectado a 172.16.4.166\\SACVDB", "server": "172.16.4.166", "duration_seconds": 1.5}
```

## 🐛 Troubleshooting

### Error: "ODBC driver not found"

```bash
# Windows
# Descargar e instalar de: https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server

# macOS
brew install mssql-tools

# Linux (Ubuntu)
apt-get install unixodbc msodbcsql17
```

### Error: "Login failed for user"

```
✗ Verifica credenciales en .env
✗ Asegúrate de que el usuario existe en SQL Server
✗ Comprueba permisos de usuario
```

### Error: "Connection timeout"

```
✗ Aumenta timeout en config: "timeout": 60
✗ Verifica conectividad: ping -c 1 servidor.com
✗ Verifica puerto: telnet servidor.com 1433
```

### Error: "Permission denied"

```
✗ El usuario SQL requiere permisos VIEW SERVER STATE
✗ Para backups: acceso a msdb
✗ Para queries: acceso a sys.*
```

## 🚦 Estados de Ejecución

Cada servidor tiene un estado:

- **SUCCESS**: Todas las queries ejecutadas exitosamente
- **PARTIAL**: Algunas queries ejecutadas, otras fallaron
- **FAILED**: No se pudo conectar o error crítico
- **TIMEOUT**: Superó tiempo máximo de ejecución

## 📈 Reporte Final

Se genera `output/metadata.json` con estadísticas:

```json
{
  "informe_id": "ACEROS_AREQUIPA_MAYO_2026",
  "fecha_inicio": "2026-05-11T09:00:00Z",
  "fecha_fin": "2026-05-11T09:03:30Z",
  "duracion_segundos": 210,
  "servidores": {
    "total": 19,
    "exitosos": 18,
    "fallidos": 1,
    "parciales": 0
  },
  "documento": {
    "path": "output/informes/INFORME_ACEROS_AREQUIPA_MAYO_2026.docx",
    "tamaño_bytes": 1250000
  }
}
```

## 🛠️ Desarrollo

### Estructura de Módulos

- **src/config/**: Carga y gestión de configuración
- **src/authentication/**: Estrategias de autenticación
- **src/database/**: Conexiones y queries SQL
- **src/data/**: Transformación de datos
- **src/document/**: Generación de documentos Word
- **src/logging_config/**: Sistema de logs
- **src/utils/**: Utilitarios y modelos de datos

### Agregar Nueva Query

1. Editar `config/queries.json`:
```json
{
  "mi_nueva_query": "SELECT ... FROM ..."
}
```

2. Agregar transformador en `src/data/transformer.py`
3. Agregar campo al template Word
4. Ejecutar

### Agregar Nueva Métrica

1. Definir en `src/utils/models.py`
2. Crear transformer en `src/data/transformer.py`
3. Ejecutar query en `config/queries.json`
4. Renderizar en documento Word

## 📦 Build/Distribución

### Como Ejecutable EXE

```bash
pip install pyinstaller
pyinstaller --onefile --windowed src/main.py
```

### Como Paquete pip

```bash
python -m build
twine upload dist/*
```

## 📞 Soporte

Para problemas o preguntas:

1. Revisar logs en `output/logs/`
2. Ejecutar con `--debug` para más verbosidad
3. Verificar conectividad a servidores SQL
4. Validar archivo de configuración JSON

## 📄 Licencia

Privado - Solo uso autorizado

---

**Versión**: 1.0.0  
**Última actualización**: Mayo 2026  
**Autor**: DBA Team

