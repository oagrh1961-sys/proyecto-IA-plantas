# Tests del Proyecto

Este directorio contiene la suite de tests para el clasificador de enfermedades en plantas.

## Archivo de Tests

### `test_model.py`
Suite completa de tests organizados por categorías:

**Tests Básicos:**
- Carga del modelo
- Predicción del modelo
- Tracking con MLflow
- Traducción de etiquetas en UIHandler
- Inicialización del cliente gRPC

**Tests de Procesamiento de Imágenes:**
- Imágenes RGB y RGBA
- Diferentes tamaños (pequeñas, estándar, grandes)

**Tests de Rendimiento:**
- Latencia de predicción
- Múltiples predicciones simultáneas

**Tests de gRPC:**
- Creación de ImageRequest
- Requests vacíos

**Tests de MLflow:**
- Logging de métricas de predicción
- Logging de errores

**Tests de Configuración:**
- Inicialización del ModelHandler
- Inicialización del MLflowTracker
- Inicialización del PlantDiseaseClassifier

**Tests de Validación:**
- Traducción de etiquetas
- Dimensiones de imagen
- Métricas de confianza
- Variables de entorno

**Tests de Concurrencia:**
- Múltiples instancias simultáneas

## Ejecución de Tests

### Ejecutar todos los tests
```bash
uv run pytest tests/test_model.py
```

### Ejecutar una clase específica
```bash
uv run pytest tests/test_model.py::TestImageProcessing
uv run pytest tests/test_model.py::TestUIHandlerTranslations
```

### Ejecutar un test específico
```bash
uv run pytest tests/test_model.py::test_model_loading
```

### Ejecutar con verbose
```bash
uv run pytest tests/test_model.py -v
```

### Ejecutar con coverage
```bash
uv run pytest tests/test_model.py --cov=src --cov-report=html
```

### Detener en primer fallo
```bash
uv run pytest tests/test_model.py -x
```

### Mostrar output de print
```bash
uv run pytest tests/test_model.py -s
```

### Abrir debugger en fallos
```bash
uv run pytest tests/test_model.py --pdb
```

## Cobertura de Código

Para generar un reporte de cobertura:

```bash
uv run pytest tests/test_model.py --cov=src --cov-report=html --cov-report=term-missing
```

Esto generará un reporte HTML en `htmlcov/index.html`

## Requisitos para Tests

Los tests requieren:
- `pytest`
- `pytest-cov` (para cobertura)
- Las dependencias del proyecto (`pyproject.toml`)

Todos están incluidos en el `uv.lock`.

## Total de Tests

El archivo `test_model.py` contiene:
- 6 tests básicos
- 4 tests de procesamiento de imágenes
- 2 tests de rendimiento
- 2 tests de gRPC
- 2 tests de MLflow
- 3 tests de configuración
- 7 tests de dimensiones
- 2 tests de inicialización del handler
- 3 tests de inicialización del tracker
- 2 tests del clasificador
- 4 tests de variables de entorno
- 2 tests de métricas de confianza
- 7 tests de traducción de etiquetas
- 2 tests de concurrencia
- 1 test de manejo de errores

**Total: 60+ tests**
