"""
Configuración centralizada con Pydantic v2.
Valida automáticamente variables de entorno al startup.
"""

import logging
from typing import Literal

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class ServerSettings(BaseSettings):
    """Configuración del servidor gRPC."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Servidor
    grpc_host: str = Field(default="0.0.0.0", description="Host del servidor gRPC")
    grpc_port: int = Field(default=50052, description="Puerto del servidor gRPC")
    grpc_max_workers: int = Field(default=10, description="Max workers en ThreadPoolExecutor")
    grpc_max_concurrent_streams: int = Field(default=100, description="Max streams concurrentes")
    
    # Modelo
    model_path: str = Field(default="./modelo_entrenado", description="Path al modelo entrenado")
    
    # MLflow
    mlflow_tracking_uri: str = Field(
        default="file:///app/mlruns",
        description="URI de tracking de MLflow"
    )
    mlflow_experiment_name: str = Field(
        default="Plant Disease Classification",
        description="Nombre del experimento en MLflow"
    )
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="WARNING",
        description="Nivel de logging"
    )
    
    # Validación de imágenes
    max_image_size_mb: int = Field(default=10, description="Tamaño máximo de imagen en MB")
    min_image_dimension: int = Field(default=32, description="Dimensión mínima de imagen")
    max_image_dimension: int = Field(default=2048, description="Dimensión máxima de imagen")
    
    # Graceful shutdown
    shutdown_grace_period_sec: int = Field(
        default=5,
        description="Segundos para finalizar requests en-vuelo"
    )
    
    def get_log_level(self) -> int:
        """Retorna el nivel de logging como int."""
        return getattr(logging, self.log_level)
    
    def get_max_image_bytes(self) -> int:
        """Retorna tamaño máximo en bytes."""
        return self.max_image_size_mb * 1024 * 1024
    
    def __str__(self) -> str:
        """Representación legible de la configuración."""
        return f"""
=== Configuración del Servidor ===
🔧 gRPC: {self.grpc_host}:{self.grpc_port}
  - Workers: {self.grpc_max_workers}
  - Max streams: {self.grpc_max_concurrent_streams}
📦 Modelo: {self.model_path}
📊 MLflow: {self.mlflow_tracking_uri}
📝 Logging: {self.log_level}
🖼️  Imágenes: {self.max_image_size_mb}MB, {self.min_image_dimension}x{self.min_image_dimension} a {self.max_image_dimension}x{self.max_image_dimension}
"""


class ClientSettings(BaseSettings):
    """Configuración del cliente gRPC."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Conexión
    grpc_server_host: str = Field(default="localhost", description="Host del servidor gRPC")
    grpc_server_port: int = Field(default=50052, description="Puerto del servidor gRPC")
    grpc_server_timeout: int = Field(default=10, description="Timeout en segundos")
    
    # Retry
    max_retries: int = Field(default=3, description="Máximo de reintentos")
    retry_delay_sec: float = Field(default=1.0, description="Delay inicial de reintento")
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="WARNING",
        description="Nivel de logging"
    )


def load_server_config() -> ServerSettings:
    """Carga y valida configuración del servidor.
    
    Returns:
        ServerSettings: Configuración validada
        
    Raises:
        ValidationError: Si hay errores en la configuración
    """
    try:
        config = ServerSettings()
        logger.info(str(config))
        return config
    except ValidationError as e:
        logger.error("❌ Error en configuración:")
        for error in e.errors():
            logger.error(f"  - {error['loc'][0]}: {error['msg']}")
        raise


def load_client_config() -> ClientSettings:
    """Carga y valida configuración del cliente.
    
    Returns:
        ClientSettings: Configuración validada
        
    Raises:
        ValidationError: Si hay errores en la configuración
    """
    try:
        config = ClientSettings()
        return config
    except ValidationError as e:
        logger.error("❌ Error en configuración del cliente:")
        for error in e.errors():
            logger.error(f"  - {error['loc'][0]}: {error['msg']}")
        raise


# Singleton: Cargar configuración una sola vez
_server_config: ServerSettings = None


def get_server_config() -> ServerSettings:
    """Obtiene la configuración del servidor (singleton)."""
    global _server_config
    if _server_config is None:
        _server_config = load_server_config()
    return _server_config
