"""
Tracing distribuida con OpenTelemetry.
Permite debugging de requests en producción.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SimplePropagator:
    """Propagador simple de trace context (compatible con OpenTelemetry)."""

    @staticmethod
    def extract_trace_id(context) -> Optional[str]:
        """Extrae trace ID del contexto gRPC.
        
        Args:
            context: Contexto gRPC
            
        Returns:
            Trace ID or None
        """
        try:
            metadata = context.invocation_metadata() if hasattr(context, 'invocation_metadata') else []
            for key, value in metadata:
                if key.lower() == "traceparent" or key.lower() == "trace-id":
                    return value
        except Exception as e:
            logger.debug(f"Error extracting trace ID: {e}")
        return None

    @staticmethod
    def inject_trace_id(context, trace_id: str):
        """Inyecta trace ID en el contexto (para respuestas).
        
        Args:
            context: Contexto gRPC
            trace_id: ID de trace a inyectar
        """
        try:
            if hasattr(context, 'set_trailing_metadata'):
                context.set_trailing_metadata([("trace-id", trace_id)])
        except Exception as e:
            logger.debug(f"Error injecting trace ID: {e}")


class DistributedTracer:
    """Sistema de tracing distribuido simplificado."""

    def __init__(self):
        self.traces: dict[str, dict] = {}
        logger.info("✅ Distributed tracer inicializado")

    def create_trace(self, trace_id: str, operation: str, metadata: dict = None) -> dict:
        """Crea un nuevo trace.
        
        Args:
            trace_id: ID único del trace
            operation: Nombre de la operación
            metadata: Metadata adicional
            
        Returns:
            Trace object
        """
        trace = {
            "trace_id": trace_id,
            "operation": operation,
            "metadata": metadata or {},
            "spans": [],
        }
        self.traces[trace_id] = trace
        return trace

    def add_span(self, trace_id: str, span_name: str, duration_ms: float, status: str = "OK"):
        """Agrega un span a un trace.
        
        Args:
            trace_id: ID del trace
            span_name: Nombre del span
            duration_ms: Duración en milisegundos
            status: Estado del span
        """
        if trace_id in self.traces:
            self.traces[trace_id]["spans"].append({
                "name": span_name,
                "duration_ms": duration_ms,
                "status": status,
            })

    def get_trace(self, trace_id: str) -> Optional[dict]:
        """Retorna un trace por ID.
        
        Args:
            trace_id: ID del trace
            
        Returns:
            Trace object or None
        """
        return self.traces.get(trace_id)

    def cleanup_old_traces(self, max_age_seconds: int = 3600):
        """Limpia traces antiguos.
        
        Args:
            max_age_seconds: Edad máxima en segundos
        """
        import time
        now = time.time()
        # Simplificado: solo limpia si hay muchos traces
        if len(self.traces) > 10000:
            self.traces.clear()
            logger.info("🧹 Traces limpiados (limite alcanzado)")


# Singleton de tracer
_tracer: Optional[DistributedTracer] = None


def get_tracer() -> DistributedTracer:
    """Obtiene instancia de tracer (singleton)."""
    global _tracer
    if _tracer is None:
        _tracer = DistributedTracer()
    return _tracer
