# Dockerfile para la aplicación Streamlit
FROM python:3.11-slim

# Instalar uv
RUN pip install uv

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración
COPY pyproject.toml uv.lock ./

# Instalar dependencias
RUN uv sync --frozen --no-install-project

# Copiar código fuente
COPY src/ ./src/

# Exponer puerto Streamlit
EXPOSE 8501

# Comando para ejecutar la app
CMD ["uv", "run", "streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]