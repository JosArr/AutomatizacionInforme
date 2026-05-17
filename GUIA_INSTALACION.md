# 📦 Guía de Instalación y Configuración

## ⚙️ Pre-requisitos

### Windows 10+
- Python 3.12 o superior
- PowerShell o CMD
- Acceso a servidores SQL Server
- Microsoft ODBC Driver 17 for SQL Server

### macOS / Linux
- Python 3.12 o superior
- Terminal
- ODBC driver para SQL Server

---

## 🔧 PASO 1: Instalar Python 3.12+

### Windows
1. Descargar de: https://www.python.org/downloads/
2. Ejecutar instalador
3. ✅ Marcar "Add Python to PATH"
4. Continuar con la instalación
5. Verificar:
```bash
python --version
# Python 3.12.0 o superior
```

### macOS
```bash
brew install python@3.12
python3.12 --version
```

### Linux (Ubuntu)
```bash
sudo apt-get update
sudo apt-get install python3.12 python3.12-venv
python3.12 --version
```

---

## 🛠️ PASO 2: Instalar ODBC Driver

### Windows
1. Descargar: https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server
2. Ejecutar MSI installer
3. Completar instalación
4. Reiniciar (opcional)

### macOS
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew install mssql-tools
```

### Linux (Ubuntu)
```bash
sudo apt install -y msodbcsql17 unixodbc
```

---

## 📁 PASO 3: Clonar/Descargar el Proyecto

### Opción A: Git
```bash
git clone <repository-url>
cd AutomatizacionInforme
```

### Opción B: Descargar ZIP
1. Descargar ZIP desde repositorio
2. Extraer carpeta
3. Abrir terminal en esa carpeta

---

## 🐍 PASO 4: Crear Ambiente Virtual

### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Windows (CMD)
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### macOS / Linux
```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Verificar (debe mostrar `(.venv)` en el prompt):
```bash
pip --version
# pip 24.x.x from /path/to/.venv/lib/...
```

---

## 📦 PASO 5: Instalar Dependencias

```bash
# Actualizar pip (opcional pero recomendado)
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

Esto instalará:
- pyodbc (conexión SQL)
- python-docx (manipulación Word)
- pandas (análisis de datos)
- pydantic (validación)
- python-dotenv (variables de entorno)
- pyyaml (soporte YAML)
- Y más...

Verificar instalación:
```bash
python -c "import pyodbc; print(f'pyodbc {pyodbc.__version__}')"
```

---

## ⚙️ PASO 6: Configurar Servidores SQL

### 6.1 Copiar archivo de ejemplo

**Windows:**
```powershell
copy config\servers.example.json config\servers.json
```

**macOS/Linux:**
```bash
cp config/servers.example.json config/servers.json
```

### 6.2 Editar `config/servers.json`

**Windows (Notepad++):**
```powershell
notepad++ config\servers.json
```

**Windows (Notepad simple):**
```powershell
notepad config\servers.json
```

**macOS/Linux (VS Code):**
```bash
code config/servers.json
```

**macOS/Linux (Vi):**
```bash
vi config/servers.json
```

### 6.3 Ejemplo de Configuración

Editar el archivo con tus servidores SQL:

```json
[
  {
    "server": "172.16.4.166",
    "instance": "SACVDB",
    "port": 1433,
    "auth_type": "sql",
    "username": "sa",
    "password": null,
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
  },
  {
    "server": "sql-backup.empresa.local",
    "instance": "BACKUP",
    "port": 1433,
    "auth_type": "windows",
    "domain": "EMPRESA",
    "username": "sql_backup",
    "password": null,
    "timeout": 60,
    "retries": 5,
    "tags": ["backup"]
  }
]
```

### Campos Obligatorios
- `server`: IP o hostname del servidor
- `instance`: Nombre de la instancia SQL
- `port`: Puerto TCP (1433 es default)
- `auth_type`: "sql" o "windows"

### Campos Condicionales
- `username` / `password`: Requeridos para SQL Auth
- `domain`: Opcional para Windows con dominio

---

## 🔐 PASO 7: Configurar Credenciales

### 7.1 Copiar archivo .env

**Windows:**
```powershell
copy .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

### 7.2 Editar `.env` con Credenciales

⚠️ **IMPORTANTE**: Este archivo NO debe committerse a Git

**Windows:**
```powershell
notepad .env
```

### 7.3 Formato de Variables

```env
# Formato: SQLSERVER_{SERVIDOR}_{INSTANCIA}_PASSWORD=contraseña
# o: SQLSERVER_{SERVIDOR}_PASSWORD=contraseña

SQLSERVER_172.16.4.166_SACVDB_PASSWORD=tu_password_aqui
SQLSERVER_172.25.91.69_MSSQLSERVER_PASSWORD=otro_password_aqui
SQLSERVER_SQL-BACKUP_EMPRESA_LOCAL_BACKUP_PASSWORD=backup_password_aqui
```

### ✅ Verificación

El programa cargará automáticamente desde `.env`:
1. Lee `.env` al iniciar
2. Carga passwords en memoria
3. Borra variables de memoria después de usar
4. ✅ Nunca registra passwords en logs

---

## 📄 PASO 8: Copiar Template Word

### 8.1 Copiar tu template actual

Tu archivo Word actual con formato:

**Windows:**
```powershell
copy "C:\Path\To\Template.docx" templates\INFORME_TEMPLATE.docx
```

**macOS/Linux:**
```bash
cp "/Path/To/Template.docx" templates/INFORME_TEMPLATE.docx
```

### 8.2 Copiar template de ejemplo (si no tienes)

Si tienes un template de ejemplo:

```bash
# El proyecto ya contiene ejemplos en template_extracted/
```

---

## ✅ PASO 9: Verificar Conectividad

### 9.1 Probar conexión a servidores

**Desde PowerShell:**
```powershell
Test-NetConnection 172.16.4.166 -Port 1433
# Debería mostrar: TcpTestSucceeded : True
```

**Desde Terminal (Linux/macOS):**
```bash
nc -zv 172.16.4.166 1433
# nc: Connection successful
```

### 9.2 Verificar ODBC Driver

**Windows (PowerShell):**
```powershell
Get-OdbcDriver | Where-Object { $_.Name -like "*SQL Server*" }
# Debe mostrar: ODBC Driver 17 for SQL Server
```

**Linux/macOS:**
```bash
odbcinst -q -d -n "ODBC Driver 17 for SQL Server"
# Debe mostrar la ruta del driver
```

---

## 🚀 PASO 10: Ejecutar Prueba MVP

### 10.1 Ejecutar el programa

```bash
python src/main.py
```

### 10.2 Salida Esperada

```
================================================================================
INICIANDO GENERACIÓN DE INFORMES SQL SERVER
================================================================================

[1/5] Cargando configuración...
✓ Configuración cargada: 3 servidores, 15 queries
  1. 172.16.4.166\SACVDB (sql)
  2. 172.25.91.69\MSSQLSERVER (windows)
  3. sql-backup.empresa.local\BACKUP (windows)

[2/5] Validando configuración de servidores...
✓ 3 servidores válidos para procesar

[3/5] Conectando a servidores y recopilando datos...
⏳ Esto puede tomar varios minutos...

✓ Conectado a 172.16.4.166\SACVDB
✓ Conectado a 172.25.91.69\MSSQLSERVER
✓ Conectado a sql-backup.empresa.local\BACKUP

✓ Recopilación completada:
  ✓ Exitosos: 3
  ⚠️  Parciales: 0
  ✗ Fallidos: 0

[4/5] Generando reporte de ejecución...
✓ Metadata guardado: output/metadata.json

[5/5] Preparando generación de documento Word...
✓ Documento generado: output/informes/INFORME_MVP_DEMO_20260511_090330.docx

================================================================================
✓ GENERACIÓN DE INFORMES COMPLETADA
================================================================================
⏱️  Tiempo total: 45.3 segundos
📊 Servidores procesados: 3
📁 Output: output
📋 Metadata: output/metadata.json
📄 Documentos: output/informes
📝 Logs: output/logs
================================================================================
```

---

## 📊 PASO 11: Revisar Resultados

### 11.1 Ver logs

**Windows:**
```powershell
Get-Content output/logs/*informe.log -Head 50
```

**macOS/Linux:**
```bash
head -50 output/logs/*informe.log
```

### 11.2 Ver metadata

```bash
type output/metadata.json  # Windows
cat output/metadata.json   # macOS/Linux
```

### 11.3 Ver documento generado

```bash
# Abrir con Word/LibreOffice
output/informes/INFORME_*.docx
```

---

## 🎯 ESTRUCTURA TRAS INSTALACIÓN

```
AutomatizacionInforme/
├── .venv/                              ← Ambiente virtual
├── src/
│   ├── main.py
│   └── ... (módulos)
├── config/
│   ├── servers.json                    ← ✏️ EDITADO por ti
│   └── queries.json
├── templates/
│   └── INFORME_TEMPLATE.docx           ← ✏️  Tu template
├── output/
│   ├── informes/
│   │   └── INFORME_*.docx              ← Documentos generados
│   └── logs/
│       └── YYYYMMDD_*.log              ← Archivos de log
├── .env                                ← ✏️ TU CONFIGURACIÓN (secreto)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚠️ PROBLEMAS COMUNES

### "ODBC Driver not found"

```
❌ Error: ('01000', '[01000] [unixODBC][Driver Manager]Can't open lib 'ODBC Driver 17 for SQL Server'')
```

**Solución:**
- Instalar ODBC Driver 17 (ver PASO 2)
- Reiniciar terminal
- Verificar ruta: `odbcinst -j`

### "Login failed for user 'sa'"

```
❌ Error: ('28000', "[28000] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Login failed")
```

**Solución:**
- Verificar password en `.env`
- Verificar usuario existe en SQL Server
- Verificar credenciales SQL son correctas

### "Connection timeout"

```
❌ Error: ('08S01', '[08S01] [Microsoft][ODBC Driver 17 for SQL Server]Communication link failure')
```

**Solución:**
- Verificar conectividad: `ping 172.16.4.166`
- Verificar puerto: `telnet 172.16.4.166 1433` (Windows)
- Aumentar timeout en `config/servers.json`: `"timeout": 60`
- Verificar firewall

### "File not found: config/servers.json"

```
❌ Error: FileNotFoundError: Archivo de configuración no encontrado: config/servers.json
```

**Solución:**
- Copiar ejemplo: `copy config\servers.example.json config\servers.json`
- Editar con tus servidores

### "Template not found"

```
⚠️  No encontrado: templates/INFORME_TEMPLATE.docx
```

**Solución:**
- Copiar tu template: `copy tu_template.docx templates\INFORME_TEMPLATE.docx`
- Para MVP, saltará la generación de documento

---

## 🎓 Próximos Pasos Tras Instalación

1. ✅ Ejecutar MVP
2. ✅ Revisar logs en `output/logs/`
3. ✅ Ir a GUIA_PROXIMOS_PASOS.md para FASE 2
4. ✅ Customizar queries en `config/queries.json`
5. ✅ Rellenar template Word con placeholders

---

## 📞 Soporte

Si tienes problemas:

1. Revisar `README.md` (Troubleshooting)
2. Revisar logs en `output/logs/`
3. Ejecutar con `--help`: `python src/main.py --help`
4. Revisar `ARQUITECTURA.md` para entender flujo

---

**¡Instalación completada! Ahora está listo para customizar.**

