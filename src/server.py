import concurrent.futures
import logging
import os
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


class PlantDiseaseClassifier(ImageClassifierServicer):
    """Servicio gRPC para clasificación de enfermedades en plantas
    usando MobileNetV2."""

    def __init__(self, model_path: str = "./modelo_entrenado"):
        self.model_path = model_path
        self.model = None
        self.processor = None
        self._load_model()
        self._setup_mlflow()

    def _load_model(self):
        """Carga el modelo y procesador desde el path especificado."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Modelo no encontrado en {self.model_path}")

        self.model = MobileNetV2ForImageClassification.from_pretrained(self.model_path)
        self.processor = MobileNetV2ImageProcessor.from_pretrained(self.model_path)
        logging.info("Modelo MobileNetV2 cargado exitosamente")

    def _setup_mlflow(self):
        """Configura MLflow para tracking."""
        mlflow.set_experiment("Plant Disease Classification")
        with mlflow.start_run(run_name="Service Startup"):
            mlflow.log_param("model_type", "MobileNetV2")
            mlflow.log_param("model_path", self.model_path)
            mlflow.log_param("service", "gRPC Plant Disease Classifier")
            logging.info("MLflow tracking configurado")

    def ClassifyImage(self, request: ImageRequest, context) -> ImageResponse:
        """Método gRPC para clasificar una imagen."""
        try:
            # Convertir bytes a imagen
            image = Image.open(BytesIO(request.image)).convert("RGB")

            # Procesar imagen
            inputs = self.processor(images=image, return_tensors="pt")

            # Realizar inferencia
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits

            # Obtener predicción
            predicted_id = logits.argmax(-1).item()
            label = self.model.config.id2label[predicted_id]
            confidence = torch.softmax(logits, dim=-1)[0][predicted_id].item()

            # Log con MLflow
            with mlflow.start_run(run_name="Prediction"):
                mlflow.log_param("predicted_label", label)
                mlflow.log_metric("confidence", confidence)

            logging.info(f"Predicción: {label} (confianza: {confidence:.4f})")
            return ImageResponse(label=label, confidence=confidence)

        except Exception as e:
            logging.error(f"Error en clasificación: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error procesando imagen: {str(e)}")
            return ImageResponse()


def serve():
    """Inicia el servidor gRPC."""
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    add_ImageClassifierServicer_to_server(PlantDiseaseClassifier(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    logging.info("Servidor gRPC iniciado en puerto 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()
