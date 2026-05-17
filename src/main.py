import sys
import json
from pathlib import Path
from datetime import datetime
import time

sys.path.insert(0, str(Path(__file__).parent))

from src.config.loader import ConfigLoader, EnvironmentConfig
from src.database.query_executor import ServerExecutor
from src.logging_config.logger import get_logger
from src.utils.models import ExecutionReport


def main():
    logger = get_logger()

    logger.info("="*80)
    logger.info("INICIANDO GENERACIÓN DE INFORMES SQL SERVER")
    logger.info("="*80)

    start_time = time.time()

    try:
        logger.info("\n[1/5] Cargando configuración...")

        config_loader = ConfigLoader()

        try:
            servers = config_loader.load_servers("servers.json")
        except FileNotFoundError:
            logger.error("❌ No encontrado: config/servers.json")
            logger.info("📋 Copiar: config/servers.example.json → config/servers.json")
            logger.info("✏️  Editar con tus servidores SQL")
            return False

        queries = config_loader.load_queries()
        EnvironmentConfig.load_env_file()

        logger.info(f"✓ Configuración cargada: {len(servers)} servidores, {len(queries)} queries")
        for i, server in enumerate(servers[:3], 1):
            logger.info(f"  {i}. {server.server}\\{server.instance} ({server.auth_type.value})")
        if len(servers) > 3:
            logger.info(f"  ... y {len(servers) - 3} más")

        logger.info("\n[2/5] Validando configuración de servidores...")

        valid_servers = []
        for server in servers:
            from src.authentication.authenticator import Authenticator
            is_valid, error = Authenticator.validate_credentials(server)
            if is_valid:
                valid_servers.append(server)
            else:
                logger.warning(f"⚠️  Servidor inválido {server.server}: {error}")

        if not valid_servers:
            logger.error("❌ No hay servidores válidos para procesar")
            return False

        logger.info(f"✓ {len(valid_servers)} servidores válidos para procesar")

        logger.info("\n[3/5] Conectando a servidores y recopilando datos...")
        logger.info("⏳ Esto puede tomar varios minutos...")

        executor = ServerExecutor(queries, max_workers=10)
        all_servers_data = executor.execute_servers(valid_servers)

        successful = sum(1 for s in all_servers_data if s.is_success)
        partial = sum(1 for s in all_servers_data if s.status.value == "partial")
        failed = sum(1 for s in all_servers_data if s.is_failed)

        logger.info(f"\n✓ Recopilación completada:")
        logger.info(f"  ✓ Exitosos: {successful}")
        if partial > 0:
            logger.info(f"  ⚠️  Parciales: {partial}")
        if failed > 0:
            logger.info(f"  ✗ Fallidos: {failed}")

        logger.info("\n[4/5] Generando reporte de ejecución...")

        report = ExecutionReport(
            informe_id="MVP_DEMO",
            client_name="ACEROS_AREQUIPA",
            invoice_month=datetime.now().strftime("%B %Y"),
            servers_total=len(all_servers_data),
            servers_successful=successful,
            servers_partial=partial,
            servers_failed=failed,
        )
        report.finished_at = datetime.now()

        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)

        metadata_file = output_dir / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                "informe_id": report.informe_id,
                "cliente": report.client_name,
                "mes": report.invoice_month,
                "fecha": report.started_at.isoformat(),
                "duracion_segundos": report.duration_seconds,
                "servidores": {
                    "total": report.servers_total,
                    "exitosos": report.servers_successful,
                    "parciales": report.servers_partial,
                    "fallidos": report.servers_failed,
                    "tasa_exito": f"{report.success_rate:.1f}%"
                },
                "errores": report.errors
            }, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Metadata guardado: {metadata_file}")

        logger.info("\n[5/5] Preparando generación de documento Word...")

        from src.document.template_handler import TemplateHandler

        templates_dir = Path(__file__).parent / "templates"
        if not (templates_dir / "INFORME_TEMPLATE.docx").exists():
            logger.warning("⚠️  No encontrado: templates/INFORME_TEMPLATE.docx")
            logger.info("📋 Copiar tu template Word a: templates/INFORME_TEMPLATE.docx")
            logger.info("⏭️  Para MVP, saltando generación de documento")
        else:
            try:
                template_handler = TemplateHandler()
                template_handler.load_template()

                replacements = template_handler.replace_placeholder(
                    "{{FECHA}}",
                    datetime.now().strftime("%d de %B de %Y")
                )

                output_file = output_dir / "informes" / f"INFORME_{report.informe_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
                output_file.parent.mkdir(parents=True, exist_ok=True)

                template_handler.save_document(output_file)

                logger.info(f"✓ Documento generado: {output_file}")
                report.document_path = str(output_file)

            except Exception as e:
                logger.error(f"✗ Error generando documento: {e}")

        duration = time.time() - start_time

        logger.info("\n" + "="*80)
        logger.info("✓ GENERACIÓN DE INFORMES COMPLETADA")
        logger.info("="*80)
        logger.info(f"⏱️  Tiempo total: {duration:.1f} segundos")
        logger.info(f"📊 Servidores procesados: {len(all_servers_data)}")
        logger.info(f"📁 Output: {output_dir}")
        logger.info(f"📋 Metadata: {metadata_file}")
        logger.info(f"📄 Informes: {output_dir / 'informes'}")
        logger.info(f"📝 Logs: {logger.log_dir}")
        logger.info("="*80)

        return True

    except Exception as e:
        logger.critical(f"ERROR CRÍTICO: {e}", exc_info=True)
        return False


def print_help():
    """Mostrar ayuda"""
    help_text = """
    ╔════════════════════════════════════════════════════════════════╗
    ║  Sistema de Generación de Informes SQL Server                  ║
    ╚════════════════════════════════════════════════════════════════╝
    
    USO RÁPIDO:
    
    1. Instalar dependencias:
       pip install -r requirements.txt
    
    2. Configurar servidores:
       copy config/servers.example.json config/servers.json
       # Editar con tus servidores SQL
    
    3. Configurar credenciales:
       copy .env.example .env
       # Llenar con passwords
    
    4. Copiar template Word:
       copy tu_template.docx templates/INFORME_TEMPLATE.docx
    
    5. Ejecutar:
       python src/main.py
    
    DOCUMENTACIÓN:
    - README.md: Guía completa
    - ARQUITECTURA.md: Diseño del sistema
    - config/servers.example.json: Ejemplo de configuración
    
    PROBLEMAS:
    - Revisar output/logs/
    - Verificar conectividad a servidores SQL
    - Validar archivo .env con credenciales
    """
    print(help_text)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        print_help()
    else:
        success = main()
        sys.exit(0 if success else 1)

