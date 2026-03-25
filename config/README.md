# ⚙️ Configuración del Proyecto

Este directorio contiene todos los archivos de configuración del proyecto.

## Archivos

### `.env`
Variables de entorno para la aplicación.

**Secciones principales:**

**Servidor gRPC:**
```env
GRPC_HOST=0.0.0.0
GRPC_PORT=50052
GRPC_MAX_WORKERS=10
GRPC_MAX_CONCURRENT_STREAMS=100
```

**Modelo ML:**
```env
MODEL_PATH=./modelo_entrenado
```

**MLflow:**
```env
MLFLOW_TRACKING_URI=file:///app/mlruns
MLFLOW_EXPERIMENT_NAME=plant-disease
```

**Validación:**
```env
MAX_IMAGE_SIZE_MB=10
MIN_IMAGE_DIMENSION=32
MAX_IMAGE_DIMENSION=2048
```

**Logging:**
```env
LOG_LEVEL=INFO
```

**Cliente gRPC:**
```env
GRPC_SERVER_HOST=localhost
GRPC_SERVER_PORT=50052
GRPC_SERVER_TIMEOUT=10
MAX_RETRIES=3
RETRY_DELAY_SEC=1
```

### `docker-compose.yml`
Orquestación de contenedores Docker.

**Servicios:**
- `server` - Servidor gRPC (puerto 50052)
- `app` - Interfaz Streamlit (puerto 8501)
- `mlflow` - Dashboard MLflow (puerto 5000)

**Uso:**
```bash
# Desde este directorio (config/)
docker-compose up --build

# O desde la raíz del proyecto
cd ..
docker-compose -f config/docker-compose.yml up --build
```

### `.dockerignore`
Archivos excluidos del contexto de build de Docker.

**Excluye:**
- `__pycache__/`, `*.pyc`
- `.git/`, `.gitignore`
- `tests/`, `.pytest_cache/`
- `modelo_entrenado/`, `mlruns/` (muy grandes)
- `venv/`, `.venv/`, `.venv-1/`
- IDE configs (`.vscode/`, `.idea/`)

**Beneficio:** Reduce el tamaño del contexto de build (~60% de reducción)

## 🔧 Configurar el Proyecto

### Primera vez (Local)

```bash
# 1. Crear .env si no existe
cp .env.example .env  # O copiar manualmente

# 2. Editar variables específicas de tu entorno
vim .env

# 3. Verificar configuración
python -c "from src.config import get_server_config; print(get_server_config())"
```

### Con Docker

```bash
# El .env en config/ se carga automáticamente en docker-compose.yml
cd config/
docker-compose up --build
```

## 📋 Validación

El archivo `.env` se valida automáticamente al iniciar:
- ✓ Tipos de datos correctos
- ✓ Valores dentro de rangos válidos
- ✓ Puertos disponibles
- ✓ Rutas existentes

Si hay errores, se mostrarán al iniciar la aplicación.

## 🔐 Seguridad

**Importante:**
- ⚠️ `.env` contiene configuración sensible (no commits)
- ✓ Ya está en `.gitignore`
- 📋 Usar `.env.example` para proporcionar template

## 📝 Soporte

Para problemas de configuración:
1. Ver [docs/CONEXION_GUIDE.md](../docs/CONEXION_GUIDE.md)
2. Ejecutar: `python scripts/diagnose_connection.py`
3. Revisar logs: `grep ERROR src/structured_logging.log`
