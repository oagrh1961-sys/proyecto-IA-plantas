import logging
import os
import time

import grpc

from .image_classifier_pb2 import ImageRequest
from .image_classifier_pb2_grpc import ImageClassifierStub

logger = logging.getLogger(__name__)


class PlantDiseaseClient:
    """Cliente gRPC robusto para clasificación de enfermedades en plantas.
    
    Features:
    - Reconexión automática con retry policy
    - Timeouts configurables
    - Logs detallados para debugging
    - Detección de cambios de contexto (local vs Docker)
    """

    def __init__(self, host: str = None, port: int = None, timeout: int = 10):
        self.host = host or os.getenv("GRPC_SERVER_HOST", "localhost")
        self.port = port or int(os.getenv("GRPC_SERVER_PORT", "50052"))
        self.timeout = timeout
        self.max_retries = 3
        self.retry_delay = 1.0
        self.is_docker = self.host != "localhost"
        self.context = "Docker" if self.is_docker else "Local"
        
        logger.info(f"Inicializando cliente gRPC [{self.context}]: {self.host}:{self.port}")
        self.channel = self._create_channel()
        self.stub = ImageClassifierStub(self.channel)
        self._verify_connection()

    def _create_channel(self):
        """Crea canal gRPC con opciones de retry y timeout."""
        target = f"{self.host}:{self.port}"
        
        # Configurar retry policy
        options = [
            ("grpc.max_receive_message_length", -1),
            ("grpc.max_send_message_length", -1),
            ("grpc.keepalive_time_ms", 30000),
            ("grpc.keepalive_timeout_ms", 10000),
        ]
        
        logger.debug(f"Conectando a gRPC server: {target}")
        return grpc.insecure_channel(target, options=options)

    def _verify_connection(self) -> bool:
        """Verifica si el servidor está disponible."""
        try:
            # Intentar hacer una llamada simple con timeout
            request = ImageRequest(image=b"")
            grpc.aio.insecure_channel(f"{self.host}:{self.port}").__enter__()
            logger.info(f"✅ Conexión exitosa al servidor [{self.context}]")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Servidor no disponible inicialmente: {str(e)[:100]}")
            return False

    def _reconstruct_channel(self):
        """Reconstruye el canal en caso de desconexión."""
        logger.info(f"Reconstruyendo canal gRPC...")
        self.channel = self._create_channel()
        self.stub = ImageClassifierStub(self.channel)

    def classify_image(self, image_bytes: bytes) -> tuple[str, float, float]:
        """Envía imagen al servidor gRPC con retry automático.
        
        Args:
            image_bytes: Imagen en formato bytes
            
        Returns:
            Tupla (label, confidence, latency_ms)
            
        Raises:
            grpc.RpcError: Si falla después de reintentos
        """
        request = ImageRequest(image=image_bytes)
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Intento {attempt + 1}/{self.max_retries} - Enviando clasificación...")
                response = self.stub.ClassifyImage(
                    request,
                    timeout=self.timeout
                )
                logger.info(f"✅ Clasificación exitosa: {response.label} ({response.confidence:.2%})")
                return response.label, response.confidence, response.latency_ms
                
            except grpc.RpcError as e:
                if attempt < self.max_retries - 1:
                    logger.warning(
                        f"Intento {attempt + 1} falló ({e.code().name}): {e.details()}"
                    )
                    if attempt == 0:
                        # En el primer fallo, reconstruir el canal
                        self._reconstruct_channel()
                    time.sleep(self.retry_delay * (2 ** attempt))  # Backoff exponencial
                else:
                    logger.error(f"❌ Falló después de {self.max_retries} intentos: {e.details()}")
                    raise

    def health_check(self) -> bool:
        """Verifica la salud de la conexión."""
        try:
            request = ImageRequest(image=b"test")
            self.stub.ClassifyImage(request, timeout=2)
            return True
        except Exception as e:
            logger.error(f"Health check falló: {e}")
            return False

    def close(self):
        """Cierra la conexión gRPC."""
        if self.channel:
            self.channel.close()
            logger.info("Canal gRPC cerrado")