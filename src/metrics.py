"""
Instrumentación Prometheus para gRPC server.
Métricas: latencia, errores, throughput, etc.
"""

import logging
import time
from functools import wraps
from typing import Callable

from prometheus_client import Counter, Gauge, Histogram, generate_latest
from prometheus_client.registry import REGISTRY

logger = logging.getLogger(__name__)


class PrometheusMetrics:
    """Métricas Prometheus para el servicio de clasificación."""

    def __init__(self):
        # Contadores
        self.predictions_total = Counter(
            'plant_disease_predictions_total',
            'Total de predicciones procesadas',
            ['label', 'success']
        )
        
        self.errors_total = Counter(
            'plant_disease_errors_total',
            'Total de errores',
            ['error_type']
        )
        
        # Histogramas (latencia)
        self.prediction_latency = Histogram(
            'plant_disease_prediction_latency_seconds',
            'Latencia de predicción en segundos',
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0)
        )
        
        # Gauges (última lectura)
        self.confidence_last = Gauge(
            'plant_disease_confidence_last',
            'Confianza de última predicción'
        )
        
        self.model_load_time = Gauge(
            'plant_disease_model_load_time_seconds',
            'Tiempo de carga del modelo'
        )
        
        # Valores acumulados
        self.uptime_seconds = Gauge(
            'plant_disease_uptime_seconds',
            'Tiempo que lleva corriendo el servicio'
        )
        
        self.prediction_count = Gauge(
            'plant_disease_prediction_count_total',
            'Total acumulado de predicciones'
        )
        
        self.error_count = Gauge(
            'plant_disease_error_count_total',
            'Total acumulado de errores'
        )
        
        # Distribuciones de labels
        self.label_distribution = Gauge(
            'plant_disease_label_distribution',
            'Distribución de labels predichos',
            ['label']
        )
        
        # Image stats
        self.image_size_bytes = Histogram(
            'plant_disease_image_size_bytes',
            'Tamaño de imagen en bytes',
            buckets=(10000, 100000, 1000000, 5000000, 10000000)
        )
        
        self.image_width = Histogram(
            'plant_disease_image_width_pixels',
            'Ancho de imagen en píxeles',
            buckets=(32, 64, 128, 224, 256, 512, 1024, 2048)
        )
        
        self.confidence_distribution = Histogram(
            'plant_disease_confidence',
            'Distribución de confianza',
            buckets=(0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0)
        )
        
        logger.info("✅ Prometheus metrics inicializadas")

    def record_prediction(self, label: str, confidence: float, latency: float, 
                         image_size: tuple[int, int], success: bool = True):
        """Registra una predicción exitosa."""
        self.predictions_total.labels(label=label, success='1' if success else '0').inc()
        self.prediction_latency.observe(latency)
        self.confidence_last.set(confidence)
        self.confidence_distribution.observe(confidence)
        self.prediction_count.inc()
        self.label_distribution.labels(label=label).inc()
        
        # Image stats
        if image_size:
            width, height = image_size
            self.image_width.observe(width)

    def record_error(self, error_type: str):
        """Registra un error."""
        self.errors_total.labels(error_type=error_type).inc()
        self.error_count.inc()

    def record_model_load_time(self, load_time_seconds: float):
        """Registra tiempo de carga del modelo."""
        self.model_load_time.set(load_time_seconds)

    def record_uptime(self, uptime_seconds: float):
        """Actualiza uptime."""
        self.uptime_seconds.set(uptime_seconds)

    def get_metrics(self) -> bytes:
        """Retorna toda las métricas en formato Prometheus."""
        return generate_latest(REGISTRY)


# Singleton de métricas
_metrics_instance = None


def get_metrics() -> PrometheusMetrics:
    """Obtiene instancia de métricas (singleton)."""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = PrometheusMetrics()
    return _metrics_instance


def track_prediction(func: Callable) -> Callable:
    """Decorator para tracking de predicciones."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            latency = time.time() - start_time
            metrics = get_metrics()
            
            # Extraer datos si están disponibles
            if isinstance(result, tuple) and len(result) >= 2:
                label, confidence = result[0], result[1]
                metrics.record_prediction(label, confidence, latency, None, success=True)
            
            return result
        except Exception as e:
            metrics = get_metrics()
            metrics.record_error(type(e).__name__)
            raise
    
    return wrapper
