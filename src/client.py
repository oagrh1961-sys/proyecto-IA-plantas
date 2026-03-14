import os

import grpc

from image_classifier_pb2 import ImageRequest
from image_classifier_pb2_grpc import ImageClassifierStub


class PlantDiseaseClient:
    """Cliente gRPC para el servicio de clasificación de enfermedades en plantas."""

    def __init__(self, host: str = None, port: int = None):
        if host is None:
            host = os.getenv("GRPC_SERVER_HOST", "localhost")
        if port is None:
            port = int(os.getenv("GRPC_SERVER_PORT", "50051"))
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = ImageClassifierStub(self.channel)

    def classify_image(self, image_bytes: bytes) -> tuple[str, float]:
        """Envía la imagen al servidor gRPC y recibe la predicción."""
        request = ImageRequest(image=image_bytes)
        response = self.stub.ClassifyImage(request)
        return response.label, response.confidence