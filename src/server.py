import concurrent.futures
import logging
import os
import signal
import sys
import threading
import time
from io import BytesIO

import grpc
import mlflow
import torch
from PIL import Image
from transformers import MobileNetV2ForImageClassification, MobileNetV2ImageProcessor

from .config import get_server_config
from .image_classifier_pb2 import ImageRequest, ImageResponse
from .image_classifier_pb2_grpc import (
    ImageClassifierServicer,
    add_ImageClassifierServicer_to_server,
)
from .metrics import get_metrics
from .metrics_server import start_metrics_server
from .rate_limiter import get_rate_limiter
from .structured_logging import configure_structured_logging
from .tracer import get_tracer
from .validators import RequestValidator


class ModelHandler:
    """Maneja la carga y uso del modelo MobileNetV2.
    
    Singleton pattern con lazy loading:
    - Se carga solo cuando se necesita
    - Misma instancia para todas las requests
    - Reduce memoria y latencia
    """
    
    _instance = None
    _lock = __import__('threading').Lock()

    def __new__(cls, model_path: str = "./modelo_entrenado"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_path: str = "./modelo_entrenado"):
        if self._initialized:
            return  # Ya inicializado, no hacer nada
            
        self.model_path = model_path
        self.model = None
        self.processor = None
        self._initialized = True
        self._load_model()

    def _load_model(self):
        """Carga el modelo y procesador (lazy loading)."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Modelo no encontrado en {self.model_path}")
        
        logging.info("📦 Cargando modelo MobileNetV2...")
        start = time.time()
        
        self.model = MobileNetV2ForImageClassification.from_pretrained(self.model_path)
        self.processor = MobileNetV2ImageProcessor.from_pretrained(self.model_path)
        
        elapsed = time.time() - start
        logging.info(f"✅ Modelo cargado en {elapsed:.2f}s")

    def predict(self, image: Image.Image) -> tuple[str, float]:
        """Realiza predicción en la imagen."""
        if self.model is None or self.processor is None:
            raise RuntimeError("Modelo no inicializado")
        
        logging.debug("Iniciando procesamiento de imagen")
        inputs = self.processor(images=image, return_tensors="pt")
        logging.debug("Imagen procesada por el procesador")
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
        
        logging.debug("Inferencia completada")
        predicted_id = logits.argmax(-1).item()
        label = self.model.config.id2label[predicted_id]
        confidence = torch.softmax(logits, dim=-1)[0][predicted_id].item()
        logging.debug(f"Predicción obtenida: {label} con confianza {confidence}")
        
        return label, confidence


class MLflowTracker:
    """Maneja el tracking con MLflow."""

    def __init__(self, experiment_name: str = "Plant Disease Classification"):
        self.experiment_name = experiment_name
        mlflow.set_experiment(self.experiment_name)
        
        # Contadores para estadísticas
        self.prediction_count = 0
        self.error_count = 0
        self.total_latency = 0.0
        self.confidence_values = []
        self.label_counts = {}
        self.image_sizes = []
        
        self._log_startup()

    def _log_startup(self):
        """Registra el inicio del servicio."""
        with mlflow.start_run(run_name="Service Startup"):
            mlflow.log_param("service", "gRPC Plant Disease Classifier")
            mlflow.log_param("model_path", "./modelo_entrenado")
            mlflow.log_metric("initial_timestamp", time.time())
            logging.debug("MLflow tracking configurado")

    def log_prediction(self, label: str, confidence: float, latency: float, image_size: tuple[int, int]):
        """Registra una predicción con métricas adicionales."""
        self.prediction_count += 1
        self.total_latency += latency
        self.confidence_values.append(confidence)
        self.image_sizes.append(image_size)
        
        # Contar labels
        self.label_counts[label] = self.label_counts.get(label, 0) + 1
        
        with mlflow.start_run(run_name="Prediction"):
            mlflow.log_param("predicted_label", label)
            
            # Métricas básicas
            mlflow.log_metric("confidence", confidence)
            mlflow.log_metric("latency_ms", latency * 1000)
            
            # Información de imagen
            mlflow.log_param("image_width", image_size[0])
            mlflow.log_param("image_height", image_size[1])
            mlflow.log_metric("image_area_pixels", image_size[0] * image_size[1])
            
            if image_size[1] != 0:
                mlflow.log_metric("image_aspect_ratio", image_size[0] / image_size[1])
            
            # Estadísticas acumuladas
            mlflow.log_metric("total_predictions", self.prediction_count)
            mlflow.log_metric("average_latency_ms", (self.total_latency / self.prediction_count) * 1000)
            mlflow.log_metric("average_confidence", sum(self.confidence_values) / len(self.confidence_values))
            
            # Categorizar confianza
            if confidence < 0.5:
                mlflow.log_metric("low_confidence_prediction", 1)
            elif confidence > 0.95:
                mlflow.log_metric("high_confidence_prediction", 1)
            
            # Distribución de confianza
            if self.confidence_values:
                mlflow.log_metric("confidence_min", min(self.confidence_values))
                mlflow.log_metric("confidence_max", max(self.confidence_values))
                mlflow.log_metric("confidence_std", 
                    (sum((x - sum(self.confidence_values)/len(self.confidence_values))**2 
                     for x in self.confidence_values) / len(self.confidence_values))**0.5)

    def log_error(self, error_message: str, image_size: tuple[int, int] = None):
        """Registra un error."""
        self.error_count += 1
        
        with mlflow.start_run(run_name="Error"):
            mlflow.log_param("error", error_message)
            mlflow.log_metric("total_errors", self.error_count)
            
            if self.prediction_count + self.error_count > 0:
                error_rate = (self.error_count / (self.prediction_count + self.error_count)) * 100
                mlflow.log_metric("error_rate_percent", error_rate)
            
            if image_size:
                mlflow.log_param("image_width", image_size[0])
                mlflow.log_param("image_height", image_size[1])
            
            mlflow.set_tag("status", "error")
    
    def log_statistics(self):
        """Registra estadísticas agregadas del servicio."""
        if self.prediction_count == 0:
            return
        
        with mlflow.start_run(run_name="Service Statistics"):
            # Conteos
            mlflow.log_metric("total_predictions", self.prediction_count)
            mlflow.log_metric("total_errors", self.error_count)
            
            # Tasas
            total_requests = self.prediction_count + self.error_count
            if total_requests > 0:
                mlflow.log_metric("success_rate_percent", (self.prediction_count / total_requests) * 100)
                mlflow.log_metric("error_rate_percent", (self.error_count / total_requests) * 100)
            
            # Latencia
            mlflow.log_metric("average_latency_ms", (self.total_latency / self.prediction_count) * 1000)
            
            # Confianza
            if self.confidence_values:
                mlflow.log_metric("avg_confidence", sum(self.confidence_values) / len(self.confidence_values))
                mlflow.log_metric("min_confidence", min(self.confidence_values))
                mlflow.log_metric("max_confidence", max(self.confidence_values))
            
            # Top 5 labels
            top_labels = sorted(self.label_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for idx, (label, count) in enumerate(top_labels, 1):
                mlflow.log_param(f"top_{idx}_label", label)
                mlflow.log_metric(f"top_{idx}_count", count)
            
            # Imagen promedio
            if self.image_sizes:
                avg_width = sum(size[0] for size in self.image_sizes) / len(self.image_sizes)
                avg_height = sum(size[1] for size in self.image_sizes) / len(self.image_sizes)
                mlflow.log_metric("avg_image_width", avg_width)
                mlflow.log_metric("avg_image_height", avg_height)


def get_client_id(context) -> str:
    """Extrae el identificador del cliente desde el contexto gRPC.
    
    Args:
        context: Contexto gRPC del request
        
    Returns:
        String con el client ID (IP:port o "unknown")
    """
    try:
        peer = context.peer() if hasattr(context, 'peer') else None
        if peer:
            # Formato typical: "ipv4:127.0.0.1:54321"
            return peer.split(":")[-2] if ":" in peer else "unknown"
    except Exception as e:
        logging.debug(f"Error extrayendo client ID: {e}")
    
    return "unknown"


class PlantDiseaseClassifier(ImageClassifierServicer):
    """Servicio gRPC para clasificación de enfermedades en plantas."""

    def __init__(self, config=None):
        self.config = config or get_server_config()
        self.model_handler = ModelHandler(self.config.model_path)
        self.mlflow_tracker = MLflowTracker(self.config.mlflow_experiment_name)
        logging.info(f"✅ PlantDiseaseClassifier inicializado")

    def ClassifyImage(self, request: ImageRequest, context) -> ImageResponse:
        """Método gRPC para clasificar una imagen."""
        start_time = time.time()
        image_size = None
        metrics = get_metrics()
        client_id = get_client_id(context)
        
        # Chequear rate limiting
        limiter = get_rate_limiter()
        if not limiter.is_allowed(client_id):
            logging.warning(f"❌ Rate limit exceeded para {client_id}")
            metrics.record_error("RateLimitExceeded")
            context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
            context.set_details("Límite de requests excedido. Intenta más tarde.")
            return ImageResponse()
        
        try:
            # Validar request
            image, image_size = RequestValidator.validate_classify_image_request(request.image)

            # Realizar predicción
            label, confidence = self.model_handler.predict(image)

            # Calcular latencia
            latency = time.time() - start_time

            # Log con MLflow
            self.mlflow_tracker.log_prediction(label, confidence, latency, image_size)
            
            # Registrar en Prometheus
            metrics.record_prediction(label, confidence, latency, image_size, success=True)
            
            # Registrar estadísticas cada 10 predicciones
            if self.mlflow_tracker.prediction_count % 10 == 0:
                self.mlflow_tracker.log_statistics()

            logging.debug(f"Predicción: {label} (confianza: {confidence:.4f}, latencia: {latency:.4f}s) de {client_id}")
            return ImageResponse(label=label, confidence=confidence, latency_ms=latency * 1000)

        except ValueError as e:
            # Error de validación
            latency = time.time() - start_time
            logging.warning(f"❌ Validation error: {str(e)} (latencia: {latency:.4f}s)")
            self.mlflow_tracker.log_error(f"Validation: {str(e)}", image_size)
            metrics.record_error("ValidationError")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return ImageResponse()
            
        except Exception as e:
            # Error en clasificación
            latency = time.time() - start_time
            logging.error(f"❌ Classification error: {str(e)} (latencia: {latency:.4f}s)")
            self.mlflow_tracker.log_error(f"Classification: {str(e)}", image_size)
            metrics.record_error(type(e).__name__)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error procesando imagen: {str(e)}")
            return ImageResponse()


def serve():
    """Inicia el servidor gRPC con graceful shutdown y métricas Prometheus."""
    # Cargar configuración
    config = get_server_config()
    
    # Variables globales para graceful shutdown
    server_instance = None
    metrics_server = None
    
    def handle_shutdown(signum, frame):
        """Maneja señales de shutdown (SIGTERM, SIGINT)."""
        signal_name = signal.Signals(signum).name
        logging.info(f"🛑 Shutdown signal recibido: {signal_name}")
        
        if server_instance:
            logging.info("📋 Finalizando estadísticas de MLflow...")
            try:
                pass
            except Exception as e:
                logging.warning(f"Error finalizando MLflow: {e}")
            
            # Graceful shutdown del servidor gRPC
            grace = config.shutdown_grace_period_sec
            logging.info(f"⏳ Esperando {grace}s para finalizaciones en-vuelo...")
            server_instance.stop(grace)
            logging.info("✅ Servidor gRPC cerrado")
        
        sys.exit(0)
    
    # Registrar manejadores de señales
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)
    
    try:
        # Iniciar servidor de métricas Prometheus
        metrics_server = start_metrics_server(port=9000)
        
        # Crear servidor gRPC con opciones de config
        server_instance = grpc.server(
            concurrent.futures.ThreadPoolExecutor(max_workers=config.grpc_max_workers),
            options=[
                ('grpc.max_concurrent_streams', config.grpc_max_concurrent_streams),
                ('grpc.keepalive_time_ms', 30000),
                ('grpc.keepalive_timeout_ms', 10000),
            ]
        )
        
        # Agregar servicio
        classifier = PlantDiseaseClassifier(config)
        add_ImageClassifierServicer_to_server(classifier, server_instance)
        
        # Agregar puerto
        server_instance.add_insecure_port(f"{config.grpc_host}:{config.grpc_port}")
        
        # Iniciar servidor
        server_instance.start()
        logging.info(f"🚀 Servidor gRPC iniciado en {config.grpc_host}:{config.grpc_port}")
        logging.info("⏸️  Presiona Ctrl+C para detener")
        
        # Esperar indefinidamente
        server_instance.wait_for_termination()
        
    except KeyboardInterrupt:
        logging.info("Interrupción de teclado recibida")
        sys.exit(0)
    except Exception as e:
        logging.error(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Cargar configuración
    config = get_server_config()
    
    # Configurar structured logging
    configure_structured_logging(
        level=config.get_log_level(),
        use_json=True,  # Usar formato JSON
        log_file=None   # Opcional: log_file="/app/logs/server.json"
    )
    
    logging.info(f"📋 Nivel de logging: {config.log_level}")
    logging.info(str(config))
    
    # Iniciar servidor
    serve()
