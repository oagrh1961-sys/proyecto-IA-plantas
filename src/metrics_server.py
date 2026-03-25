"""
Servidor HTTP para exponer métricas Prometheus.
Corre en puerto 9000 separado del servidor gRPC.
"""

import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from .metrics import get_metrics

logger = logging.getLogger(__name__)


class MetricsHandler(BaseHTTPRequestHandler):
    """Handler para requests a /metrics."""

    def do_GET(self):
        """Maneja GET requests."""
        if self.path == '/metrics':
            try:
                metrics = get_metrics()
                metrics_data = metrics.get_metrics()
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(metrics_data)
            except Exception as e:
                logger.error(f"Error generando métricas: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found\n')

    def log_message(self, format, *args):
        """Suprimir logs de HTTP por defecto."""
        pass


def start_metrics_server(host: str = "0.0.0.0", port: int = 9000):
    """Inicia servidor HTTP para métricas en un thread.
    
    Args:
        host: Host para el servidor
        port: Puerto para el servidor (default 9000)
    """
    try:
        server = HTTPServer((host, port), MetricsHandler)
        server_thread = threading.Thread(daemon=True, target=server.serve_forever)
        server_thread.start()
        logger.info(f"📊 Servidor de métricas Prometheus iniciado en http://{host}:{port}/metrics")
        return server
    except Exception as e:
        logger.error(f"❌ Error iniciando servidor de métricas: {e}")
        raise
