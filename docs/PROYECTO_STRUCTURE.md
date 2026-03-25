# 📁 Estructura del Proyecto

Este documento describe la organización de archivos y directorios del proyecto de detección de fitopatologías.

## 🏗️ Estructura General

```
proyecto_deteccion_plantas/
│
├── 📂 src/                          # Código principal de la aplicación
│   ├── __init__.py
│   ├── app.py                       # Interfaz Streamlit
│   ├── server.py                    # Servidor gRPC
│   ├── client.py                    # Cliente gRPC
│   ├── predictor.py                 # Lógica de predicción
│   ├── cli.py                       # Interfaz CLI
│   │
│   ├── config.py                    # Configuración con Pydantic
│   ├── validators.py                # Validación de entrada
│   ├── metrics.py                   # Métricas Prometheus
│   ├── metrics_server.py            # Servidor HTTP de métricas
│   ├── rate_limiter.py              # Limitador de tasa
│   ├── batch_processor.py           # Procesamiento en batch
│   ├── tracer.py                    # Tracing distribuido
│   ├── structured_logging.py        # Logging estructurado JSON
│   │
│   ├── image_classifier.proto       # Definición protobuf
│   ├── image_classifier_pb2.py      # Generado: clases protobuf
│   └── image_classifier_pb2_grpc.py # Generado: stubs gRPC
│
├── 📂 scripts/                       # Scripts de utilidad
│   ├── create_test_image.py        # Generar imagen de prueba
│   ├── descargar_modelo.py         # Descargar modelo HuggingFace
│   └── diagnose_connection.py      # Diagnóstico de conexión
│
├── 📂 config/                        # Archivos de configuración
│   ├── .env                        # Variables de entorno
│   ├── docker-compose.yml          # Orquestación de contenedores
│   └── .dockerignore               # Exclusiones para Docker
│
├── 📂 docs/                          # Documentación del proyecto
│   ├── PROYECTO_STRUCTURE.md       # Este archivo
│   ├── CONEXION_GUIDE.md           # Guía de conexión local/Docker
│   ├── IMPLEMENTACION.md           # Resumen de implementaciones
│   └── MEJORAS_POSIBLES.md         # Roadmap de mejoras futuras
│
├── 📂 tests/                         # Tests y fixtures
│   ├── __init__.py
│   ├── test_model.py
│   ├── README.md
│   └── 📂 fixtures/                 # Datos de prueba
│       └── test_image.jpg
│
├── 📂 modelo_entrenado/              # Modelo ML descargado (gitignored)
├── 📂 mlruns/                        # Artefactos MLflow (gitignored)
│
├── 🐳 Dockerfile.app                 # Docker app Streamlit
├── 🐳 Dockerfile.server              # Docker servidor gRPC
├── pyproject.toml                    # Dependencias y configuración del proyecto
├── pytest.ini                        # Configuración de pytest
├── README.md                         # Documentación principal
├── .gitignore                        # Exclusiones de git
└── uv.lock                           # Lock file de dependencias
```

## 📋 Descripción de Directorios

### `src/` - Código Principal
Contiene toda la lógica de la aplicación:
- **Core**: `app.py`, `server.py`, `client.py`, `predictor.py`
- **Infraestructura**: `config.py`, `validators.py`, `structured_logging.py`
- **Observabilidad**: `metrics.py`, `metrics_server.py`, `tracer.py`
- **Performance**: `rate_limiter.py`, `batch_processor.py`
- **gRPC**: Definiciones protobuf y código generado

### `scripts/` - Utilidades
Scripts de uso ocasional:
- `descargar_modelo.py` - Descarga el modelo del repositorio HuggingFace
- `create_test_image.py` - Crea una imagen para testing
- `diagnose_connection.py` - Diagnostica problemas de conexión

### `config/` - Configuración
Archivos de configuración centralizada:
- `.env` - Variables de entorno (puerto, host, credenciales, etc.)
- `docker-compose.yml` - Orquestación y redirección de puertos
- `.dockerignore` - Optimización de construcción de Docker

### `docs/` - Documentación
Documentación técnica detallada:
- `CONEXION_GUIDE.md` - Cómo resolver problemas de conexión local/Docker
- `IMPLEMENTACION.md` - Qué mejoras se implementaron y cómo usarlas
- `MEJORAS_POSIBLES.md` - Roadmap de mejoras futuras
- `PROYECTO_STRUCTURE.md` - Esta guía

### `tests/` - Tests y Fixtures
Tests unitarios e integración:
- `test_model.py` - Tests del modelo
- `fixtures/` - Datos de prueba compartidos

## 🚀 Flujo de Trabajo

### Desarrollo Local
```bash
# 1. Copiar .env de config/ a raíz (opcional)
# 2. Instalar dependencias
pip install -e .

# 3. Descargar modelo
python scripts/descargar_modelo.py

# 4. Iniciar servidor
python -m src.server

# 5. En otra terminal, iniciar app
streamlit run src/app.py
```

### Con Docker
```bash
# 1. Ir a config/
cd config/

# 2. Construir e iniciar
docker-compose up --build

# 3. Acceder a servicios
# - App: http://localhost:8501
# - Métricas: http://localhost:9000/metrics
# - MLflow: http://localhost:5000
```

## 🔧 Configuración

### Variables de Entorno (config/.env)
```
# Servidor gRPC
GRPC_HOST=0.0.0.0
GRPC_PORT=50052

# Modelo
MODEL_PATH=./modelo_entrenado

# MLflow
MLFLOW_TRACKING_URI=file:///app/mlruns
MLFLOW_EXPERIMENT_NAME=plant-disease

# Validación
MAX_IMAGE_SIZE_MB=10
MIN_IMAGE_DIMENSION=32
MAX_IMAGE_DIMENSION=2048

# Logging
LOG_LEVEL=INFO
```

## 📦 Dependencias Principales

- **gRPC**: `grpcio`, `grpcio-tools`
- **ML**: `torch`, `transformers`, `huggingface-hub`
- **UI**: `streamlit`
- **Métricas**: `prometheus-client`
- **Config**: `pydantic`, `pydantic-settings`
- **MLOps**: `mlflow`

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=src

# Test específico
pytest tests/test_model.py::test_prediction
```

## 📊 Servicios en Docker Compose

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| `server` | 50052 | Servidor gRPC |
| `app` | 8501 | Interfaz Streamlit |
| `mlflow` | 5000 | Dashboard de experimentos |
| `metrics` | 9000 | Endpoint Prometheus (via server) |

## 🔍 Troubleshooting

Ver [CONEXION_GUIDE.md](CONEXION_GUIDE.md) para resolver problemas de conexión.

## 📚 Más Información

- [CONEXION_GUIDE.md](CONEXION_GUIDE.md) - Diagrama y guía de conexión
- [IMPLEMENTACION.md](IMPLEMENTACION.md) - Detalles de las 10 mejoras implementadas
- [MEJORAS_POSIBLES.md](MEJORAS_POSIBLES.md) - Roadmap de futuras mejoras
- [README.md](../README.md) - Información general del proyecto
