#!/usr/bin/env python
"""
Script de diagnóstico para problemas de conexión gRPC
Uso: python diagnose_connection.py [--docker] [--host HOST] [--port PORT]
"""

import argparse
import logging
import os
import socket
import sys
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def check_port_open(host: str, port: int, timeout: int = 2) -> bool:
    """Verifica si un puerto está abierto."""
    try:
        socket.create_connection((host, port), timeout=timeout)
        logger.info(f"✅ Puerto {port} en {host} está ABIERTO")
        return True
    except (socket.timeout, socket.error) as e:
        logger.error(f"❌ Puerto {port} en {host} está CERRADO: {e}")
        return False

def check_grpc_connection(host: str, port: int, timeout: int = 2) -> bool:
    """Verifica conexión gRPC."""
    try:
        import grpc
        channel = grpc.insecure_channel(f"{host}:{port}")
        logger.info(f"✅ Canal gRPC creado: {host}:{port}")
        channel.close()
        return True
    except Exception as e:
        logger.error(f"❌ Error al crear canal gRPC: {e}")
        return False

def check_environment():
    """Verifica variables de entorno."""
    logger.info("\\n📋 Variables de entorno:")
    env_vars = {
        "GRPC_SERVER_HOST": os.getenv("GRPC_SERVER_HOST", "localhost"),
        "GRPC_SERVER_PORT": os.getenv("GRPC_SERVER_PORT", "50052"),
        "MLFLOW_TRACKING_URI": os.getenv("MLFLOW_TRACKING_URI", "N/A"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    }
    for key, value in env_vars.items():
        logger.info(f"  {key}: {value}")

def check_docker_containers():
    """Verifica contenedores Docker."""
    try:
        import subprocess
        logger.info("\\n🐳 Contenedores Docker:")
        result = subprocess.run(["docker", "ps", "--format", "table {{.Names}}\\t{{.Status}}"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(result.stdout)
        else:
            logger.warning("No se pudo ejecutar 'docker ps'")
    except Exception as e:
        logger.warning(f"Docker no disponible: {e}")

def check_python_imports():
    """Verifica imports necesarios."""
    logger.info("\\n📦 Verificando imports:")
    imports = ["grpc", "streamlit", "PIL", "mlflow", "torch", "transformers"]
    for module in imports:
        try:
            __import__(module)
            logger.info(f"  ✅ {module}")
        except ImportError:
            logger.error(f"  ❌ {module} - NO INSTALADO")

def run_diagnostics(is_docker: bool = False, host: str = None, port: int = None):
    """Ejecuta todos los diagnósticos."""
    
    if host is None:
        host = "server" if is_docker else "localhost"
    if port is None:
        port = 50052
    
    context = "Docker" if is_docker else "Local"
    logger.info(f"\\n🔍 DIAGNÓSTICO DE CONEXIÓN [{context}]")
    logger.info("=" * 50)
    
    check_environment()
    check_python_imports()
    
    if is_docker:
        check_docker_containers()
    
    logger.info(f"\\n🌐 Probando conexión a {host}:{port}:")
    logger.info("-" * 50)
    
    # Intentar 3 veces con espera
    for attempt in range(3):
        if attempt > 0:
            logger.info(f"\\nIntento {attempt + 1}/3...")
            time.sleep(2)
        
        port_ok = check_port_open(host, port)
        grpc_ok = check_grpc_connection(host, port) if port_ok else False
        
        if port_ok and grpc_ok:
            logger.info("\\n" + "=" * 50)
            logger.info("✅ ¡CONEXIÓN EXITOSA!")
            logger.info("=" * 50)
            return True
    
    logger.info("\\n" + "=" * 50)
    logger.error("❌ NO SE PUDO ESTABLECER CONEXIÓN")
    logger.info("=" * 50)
    
    if is_docker:
        logger.info("\\n💡 Sugerencias para Docker:")
        logger.info("  1. Verifica: docker ps")
        logger.info("  2. Revisa logs: docker-compose logs server")
        logger.info("  3. Reinicia: docker-compose restart server")
    else:
        logger.info("\\n💡 Sugerencias para Local:")
        logger.info(f"  1. Verifica que el servidor esté corriendo en {host}:{port}")
        logger.info("  2. Revisa los logs del servidor")
        logger.info("  3. Intenta: python -m src.server")
    
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Diagnóstico de conexión gRPC")
    parser.add_argument("--docker", action="store_true", help="Ejecutar en modo Docker")
    parser.add_argument("--host", help="Hostname del servidor gRPC")
    parser.add_argument("--port", type=int, help="Puerto del servidor gRPC")
    
    args = parser.parse_args()
    
    success = run_diagnostics(
        is_docker=args.docker,
        host=args.host,
        port=args.port
    )
    
    sys.exit(0 if success else 1)
