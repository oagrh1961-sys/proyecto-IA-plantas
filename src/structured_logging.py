"""
Logging centralizado con structured logging (JSON).
Compatible con ELK Stack, Datadog, CloudWatch, etc.
"""

import json
import logging
import sys
import time
from logging import LogRecord


class StructuredLogFormatter(logging.Formatter):
    """Formatea logs como JSON para logging centralizado."""

    def format(self, record: LogRecord) -> str:
        """Convierte un log record a JSON.
        
        Args:
            record: Log record de logging
            
        Returns:
            JSON string con el log
        """
        log_data = {
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Agregar información de excepción si existe
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Agregar campos adicionales si están en extra
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        return json.dumps(log_data, ensure_ascii=False)


class StructuredLogger(logging.Logger):
    """Logger customizado que soporta structured logging."""

    def log_with_context(self, level: int, message: str, **context):
        """Registra un log con contexto adicional.
        
        Args:
            level: Nivel de logging
            message: Mensaje
            **context: Campos adicionales para JSON
        """
        extra = {"extra": context}
        self.log(level, message, extra=extra)

    def debug_structured(self, message: str, **context):
        """Debug con contexto."""
        self.log_with_context(logging.DEBUG, message, **context)

    def info_structured(self, message: str, **context):
        """Info con contexto."""
        self.log_with_context(logging.INFO, message, **context)

    def warning_structured(self, message: str, **context):
        """Warning con contexto."""
        self.log_with_context(logging.WARNING, message, **context)

    def error_structured(self, message: str, **context):
        """Error con contexto."""
        self.log_with_context(logging.ERROR, message, **context)


def configure_structured_logging(
    level: int = logging.INFO,
    use_json: bool = True,
    log_file: str = None
):
    """Configura logging centralizado con structured logs.
    
    Args:
        level: Nivel de logging
        use_json: Si usar formato JSON (True) o texto (False)
        log_file: Opcional, fichero para guardar logs
    """
    # Cambiar logger default
    logging.setLoggerClass(StructuredLogger)
    
    # Crear handler para stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    if use_json:
        formatter = StructuredLogFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()  # Limpiar handlers existentes
    root_logger.addHandler(console_handler)
    
    # Opcionalmente, agregar file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        root_logger.info(f"📝 Logging a archivo: {log_file}")
    
    # Suprimir logs de librerías
    for lib in ["transformers", "PIL", "torch", "mlflow", "grpc"]:
        logging.getLogger(lib).setLevel(logging.WARNING)
    
    return root_logger


def get_structured_logger(name: str) -> StructuredLogger:
    """Obtiene un logger structurado.
    
    Args:
        name: Nombre del logger
        
    Returns:
        StructuredLogger instance
    """
    return logging.getLogger(name)
