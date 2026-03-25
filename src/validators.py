"""
Módulo de validación para imágenes gRPC.
Valida tamaño, tipo MIME, dimensiones y contenido.
"""

import logging
from io import BytesIO
from typing import Tuple

from PIL import Image

logger = logging.getLogger(__name__)


class ValidationConfig:
    """Configuración de validación de imágenes."""
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MIN_DIMENSION = 32
    MAX_DIMENSION = 2048
    ALLOWED_FORMATS = {"JPEG", "PNG", "RGB", "RGBA"}


class ImageValidator:
    """Valida imágenes antes de procesarlas."""

    @staticmethod
    def validate_size(image_bytes: bytes) -> None:
        """Valida que la imagen no exceda el tamaño máximo.
        
        Args:
            image_bytes: Bytes de la imagen
            
        Raises:
            ValueError: Si la imagen es demasiado grande
        """
        size_mb = len(image_bytes) / (1024 * 1024)
        if len(image_bytes) > ValidationConfig.MAX_IMAGE_SIZE:
            raise ValueError(
                f"Imagen demasiado grande: {size_mb:.2f}MB "
                f"(máximo: {ValidationConfig.MAX_IMAGE_SIZE / (1024 * 1024):.0f}MB)"
            )
        logger.debug(f"✅ Size validation passed: {size_mb:.2f}MB")

    @staticmethod
    def validate_format(image: Image.Image) -> None:
        """Valida el formato de la imagen.
        
        Args:
            image: Objeto PIL Image
            
        Raises:
            ValueError: Si el formato no es soportado
        """
        if image.format not in ValidationConfig.ALLOWED_FORMATS and image.mode not in ValidationConfig.ALLOWED_FORMATS:
            raise ValueError(
                f"Formato no soportado: {image.format} (modo: {image.mode}). "
                f"Permitidos: {ValidationConfig.ALLOWED_FORMATS}"
            )
        logger.debug(f"✅ Format validation passed: {image.format} ({image.mode})")

    @staticmethod
    def validate_dimensions(image: Image.Image) -> None:
        """Valida las dimensiones de la imagen.
        
        Args:
            image: Objeto PIL Image
            
        Raises:
            ValueError: Si las dimensiones no están permitidas
        """
        width, height = image.size
        
        if width < ValidationConfig.MIN_DIMENSION or height < ValidationConfig.MIN_DIMENSION:
            raise ValueError(
                f"Imagen demasiado pequeña: {width}x{height} "
                f"(mínimo: {ValidationConfig.MIN_DIMENSION}x{ValidationConfig.MIN_DIMENSION})"
            )
        
        if width > ValidationConfig.MAX_DIMENSION or height > ValidationConfig.MAX_DIMENSION:
            raise ValueError(
                f"Imagen demasiado grande: {width}x{height} "
                f"(máximo: {ValidationConfig.MAX_DIMENSION}x{ValidationConfig.MAX_DIMENSION})"
            )
        
        logger.debug(f"✅ Dimension validation passed: {width}x{height}")

    @staticmethod
    def validate_image_content(image_bytes: bytes) -> Tuple[Image.Image, str]:
        """Valida el contenido completo de la imagen.
        
        Args:
            image_bytes: Bytes de la imagen
            
        Returns:
            Tupla (imagen PIL convertida a RGB, tamaño original)
            
        Raises:
            ValueError: Si la imagen no es válida
            IOError: Si hay error al leer la imagen
        """
        try:
            # Validar tamaño
            ImageValidator.validate_size(image_bytes)
            
            # Intentar abrir como PIL Image
            try:
                image = Image.open(BytesIO(image_bytes))
            except Exception as e:
                raise IOError(f"Error al abrir imagen: {str(e)}")
            
            # Validar formato
            ImageValidator.validate_format(image)
            
            # Validar dimensiones
            ImageValidator.validate_dimensions(image)
            
            # Convertir a RGB si es necesario
            if image.mode != "RGB":
                image = image.convert("RGB")
            
            logger.info(f"✅ Image validation passed: {image.size} {image.mode}")
            return image, image.size
            
        except (ValueError, IOError) as e:
            logger.error(f"❌ Image validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected validation error: {str(e)}")
            raise ValueError(f"Error inesperado en validación: {str(e)}")


class RequestValidator:
    """Valida requests gRPC completos."""

    @staticmethod
    def validate_classify_image_request(image_bytes: bytes) -> Tuple[Image.Image, Tuple[int, int]]:
        """Valida un request de ClassifyImage.
        
        Args:
            image_bytes: Bytes de la imagen del request
            
        Returns:
            Tupla (imagen validated, original_size)
            
        Raises:
            ValueError: Si el request es inválido
        """
        if not image_bytes:
            raise ValueError("ImageRequest.image no puede estar vacío")
        
        image, size = ImageValidator.validate_image_content(image_bytes)
        return image, size
