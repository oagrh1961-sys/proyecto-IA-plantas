"""
Rate limiting para proteger el servidor gRPC.
Implementa Token Bucket algorithm por IP/cliente.
"""

import logging
import time
from collections import defaultdict
from threading import Lock
from typing import Optional

logger = logging.getLogger(__name__)


class TokenBucket:
    """Token bucket para rate limiting."""

    def __init__(self, capacity: float, refill_rate: float):
        """
        Args:
            capacity: Máximo número de tokens
            refill_rate: Tokens por segundo
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = Lock()

    def _refill(self):
        """Recarga tokens basado en el tiempo elapsed."""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def consume(self, tokens: float = 1.0) -> bool:
        """Intenta consumir tokens.
        
        Args:
            tokens: Número de tokens a consumir (default 1)
            
        Returns:
            True si hay suficientes tokens, False otherwise
        """
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def get_available(self) -> float:
        """Retorna tokens disponibles."""
        with self.lock:
            self._refill()
            return self.tokens


class RateLimiter:
    """Rate limiter por cliente usando token bucket."""

    def __init__(self, requests_per_second: float = 100, burst_size: float = 10):
        """
        Args:
            requests_per_second: Tasa sostenida de requests
            burst_size: Máximo burst permitido
        """
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.buckets: dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(self.burst_size, self.requests_per_second)
        )
        self.lock = Lock()
        logger.info(
            f"✅ Rate limiter inicializado: {requests_per_second} req/s, "
            f"burst size: {burst_size}"
        )

    def is_allowed(self, client_id: str, tokens: float = 1.0) -> bool:
        """Chequea si un cliente puede hacer una request.
        
        Args:
            client_id: Identificador del cliente (e.g., IP address)
            tokens: Tokens a consumir
            
        Returns:
            True si está permitido, False si está rate-limited
        """
        bucket = self.buckets[client_id]
        allowed = bucket.consume(tokens)
        
        if not allowed:
            available = bucket.get_available()
            logger.warning(
                f"⚠️  Rate limit exceeded for {client_id} "
                f"(available: {available:.2f})"
            )
        
        return allowed

    def get_status(self, client_id: str) -> dict:
        """Retorna estado del rate limiter para un cliente.
        
        Args:
            client_id: Identificador del cliente
            
        Returns:
            Dict con tokens disponibles y tasa configurada
        """
        bucket = self.buckets[client_id]
        return {
            "available_tokens": bucket.get_available(),
            "capacity": bucket.capacity,
            "refill_rate": bucket.refill_rate,
        }


class AdaptiveRateLimiter:
    """Rate limiter adaptativo que ajusta basado en carga."""

    def __init__(
        self,
        base_rate: float = 100,
        min_rate: float = 10,
        max_rate: float = 1000,
        cpu_threshold: float = 80.0
    ):
        """
        Args:
            base_rate: Tasa base de requests/segundo
            min_rate: Mínima tasa permitida
            max_rate: Máxima tasa permitida
            cpu_threshold: Umbral de CPU para reducir rate (%)
        """
        self.base_rate = base_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.cpu_threshold = cpu_threshold
        self.limiter = RateLimiter(base_rate)
        self.current_rate = base_rate
        logger.info(f"✅ Adaptive rate limiter inicializado (base: {base_rate} req/s)")

    def adjust_rate(self, cpu_usage: float):
        """Ajusta la tasa basada en uso de CPU.
        
        Args:
            cpu_usage: Uso de CPU en porcentaje (0-100)
        """
        if cpu_usage > self.cpu_threshold:
            # Reducir tasa cuando CPU está alta
            self.current_rate = max(
                self.min_rate,
                self.base_rate * (1 - (cpu_usage - self.cpu_threshold) / 100)
            )
            logger.warning(
                f"⚠️  CPU alta ({cpu_usage:.1f}%), reduciendo rate a {self.current_rate:.0f} req/s"
            )
        else:
            # Restaurar tasa cuando CPU está baja
            self.current_rate = min(self.base_rate, self.current_rate * 1.1)

        self.limiter = RateLimiter(self.current_rate)

    def is_allowed(self, client_id: str) -> bool:
        """Chequea si un cliente puede hacer una request."""
        return self.limiter.is_allowed(client_id)


# Singleton de rate limiter
_limiter: Optional[RateLimiter] = None


def get_rate_limiter(
    requests_per_second: float = 100,
    burst_size: float = 10
) -> RateLimiter:
    """Obtiene instancia de rate limiter (singleton)."""
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter(requests_per_second, burst_size)
    return _limiter
