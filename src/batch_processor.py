"""
Batch processing para múltiples imágenes.
Procesa hasta 50 imágenes en paralelo para mejor throughput.
"""

import concurrent.futures
import logging
from typing import List, Tuple

from .server import ModelHandler

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Procesa múltiples imágenes en paralelo."""

    def __init__(self, max_workers: int = 8, max_batch_size: int = 50):
        """
        Args:
            max_workers: Número de threads para procesamiento paralelo
            max_batch_size: Máximo número de imágenes por batch
        """
        self.max_workers = max_workers
        self.max_batch_size = max_batch_size
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        logger.info(f"✅ Batch processor inicializado: {max_workers} workers, max batch {max_batch_size}")

    def process_batch(self, images_bytes: List[bytes], model_handler: ModelHandler) -> List[Tuple[str, float]]:
        """Procesa un batch de imágenes en paralelo.
        
        Args:
            images_bytes: Lista de imágenes en bytes
            model_handler: Handler del modelo
            
        Returns:
            Lista de tuplas (label, confidence) para cada imagen
        """
        if len(images_bytes) > self.max_batch_size:
            raise ValueError(f"Batch size excede máximo ({len(images_bytes)} > {self.max_batch_size})")
        
        from PIL import Image
        from io import BytesIO
        from .validators import ImageValidator
        
        def predict_single(image_bytes: bytes) -> Tuple[str, float]:
            """Procesa una imagen individual."""
            try:
                image, _ = ImageValidator.validate_image_content(image_bytes)
                label, confidence = model_handler.predict(image)
                return label, confidence
            except Exception as e:
                logger.error(f"Error procesando imagen en batch: {e}")
                return "ERROR", 0.0
        
        # Procesar en paralelo
        futures = [
            self.executor.submit(predict_single, img_bytes)
            for img_bytes in images_bytes
        ]
        
        # Recolectar resultados
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result(timeout=30)
                results.append(result)
            except Exception as e:
                logger.error(f"Error en batch processing: {e}")
                results.append(("ERROR", 0.0))
        
        return results

    def shutdown(self):
        """Detiene el executor."""
        self.executor.shutdown(wait=True)
