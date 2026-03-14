import concurrent.futures
import logging
import os
import time
from io import BytesIO

import grpc
import mlflow
import torch
from PIL import Image
from transformers import MobileNetV2ForImageClassification, MobileNetV2ImageProcessor

from image_classifier_pb2 import ImageRequest, ImageResponse
from image_classifier_pb2_grpc import (
    ImageClassifierServicer,
    add_ImageClassifierServicer_to_server,
)
from grpc.health.v1 import health_pb2, health_pb2_grpc


class ModelHandler:
    """Maneja la carga y uso del modelo MobileNetV2."""

    def __init__(self, model_path: str = "./modelo_entrenado"):
        self.model_path = model_path
        self.model = None
        self.processor = None
        self._load_model()

    def _load_model(self):
        """Carga el modelo y procesador."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Modelo no encontrado en {self.model_path}")
        self.model = MobileNetV2ForImageClassification.from_pretrained(self.model_path)
        self.processor = MobileNetV2ImageProcessor.from_pretrained(self.model_path)
        logging.debug("Modelo MobileNetV2 cargado exitosamente")

    def predict(self, image: Image.Image) -> tuple[str, float]:
        """Realiza predicción en la imagen."""
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
        self._log_startup()

    def _log_startup(self):
        """Registra el inicio del servicio."""
        with mlflow.start_run(run_name="Service Startup"):
            mlflow.log_param("service", "gRPC Plant Disease Classifier")
            logging.debug("MLflow tracking configurado")

    def log_prediction(self, label: str, confidence: float, latency: float, image_size: tuple[int, int]):
        """Registra una predicción con métricas adicionales."""
        with mlflow.start_run(run_name="Prediction"):
            mlflow.log_param("predicted_label", label)
            mlflow.log_metric("confidence", confidence)
            mlflow.log_metric("latency_ms", latency * 1000)  # Convertir a ms
            mlflow.log_param("image_width", image_size[0])
            mlflow.log_param("image_height", image_size[1])

    def log_error(self, error_message: str, image_size: tuple[int, int] = None):
        """Registra un error."""
        with mlflow.start_run(run_name="Error"):
            mlflow.log_param("error", error_message)
            if image_size:
                mlflow.log_param("image_width", image_size[0])
                mlflow.log_param("image_height", image_size[1])
            mlflow.set_tag("status", "error")


class PlantDiseaseClassifier(ImageClassifierServicer):
    """Servicio gRPC para clasificación de enfermedades en plantas."""

    def __init__(self, model_path: str = "./modelo_entrenado"):
        self.model_handler = ModelHandler(model_path)
        self.mlflow_tracker = MLflowTracker()

    def ClassifyImage(self, request: ImageRequest, context) -> ImageResponse:
        """Método gRPC para clasificar una imagen."""
        start_time = time.time()
        try:
            # Convertir bytes a imagen
            image = Image.open(BytesIO(request.image)).convert("RGB")
            image_size = image.size

            # Realizar predicción
            label, confidence = self.model_handler.predict(image)

            # Calcular latencia
            latency = time.time() - start_time

            # Log con MLflow
            self.mlflow_tracker.log_prediction(label, confidence, latency, image_size)

            logging.debug(f"Predicción: {label} (confianza: {confidence:.4f}, latencia: {latency:.4f}s)")
            return ImageResponse(label=label, confidence=confidence)

        except Exception as e:
            latency = time.time() - start_time
            logging.debug(f"Error en clasificación: {str(e)} (latencia: {latency:.4f}s)")
            # Log error en MLflow
            try:
                image_size = image.size if 'image' in locals() else None
                self.mlflow_tracker.log_error(str(e), image_size)
            except:
                self.mlflow_tracker.log_error(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error procesando imagen: {str(e)}")
            return ImageResponse()


def serve():
    """Inicia el servidor gRPC."""
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    add_ImageClassifierServicer_to_server(PlantDiseaseClassifier(), server)
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    logging.info("Servidor gRPC iniciado en puerto 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    # Configurar logging limpio
    log_level = os.getenv("LOG_LEVEL", "WARNING").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.WARNING),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    # Suprimir logs de transformers y otros durante carga
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)

    serve()
