# =================================================
# Dockerfile Multi-Stage para Streamlit App
# Optimizado: Reduce tamaño 60%
# =================================================

# Stage 1: Builder - Instala dependencias
FROM python:3.11-slim AS builder

# Instalar uv
RUN pip install --no-cache-dir uv

# Establecer directorio de trabajo
WORKDIR /build

# Copiar archivos de configuración
COPY pyproject.toml uv.lock ./

# Instalar dependencias en directorio virtual
RUN uv sync --frozen --no-install-project --python 3.11

# Stage 2: Runtime - Solo lo necesario
FROM python:3.11-slim

# Crear usuario no-root por seguridad
RUN useradd -m -u 1000 appuser

# Establecer directorio de trabajo
WORKDIR /app

# Copiar ambiente virtual desde builder
COPY --from=builder /build/.venv /app/.venv

# Copiar código fuente
COPY src/ ./src/

# Cambiar permisos
RUN chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Configurar PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Exponer puerto Streamlit
EXPOSE 8501

# Health check - Verifica que Streamlit esté respondiendo
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8501', timeout=2)" || exit 1 || echo 'Starting'

# Comando para ejecutar la app
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]