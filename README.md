# 🌿 Detección de Enfermedades en Cultivos con IA

## Descripción
Sistema de clasificación de imágenes basado en **MobileNetV2** para la identificación temprana de patologías en hojas de plantas. Desarrollado para la materia "Desarrollo de Proyectos de IA".

## Arquitectura
El proyecto utiliza una arquitectura **gRPC** distribuida:
- **Servidor gRPC** (`server.py`): Carga el modelo MobileNetV2 y realiza inferencias, con tracking MLflow.
- **Cliente Streamlit** (`app.py`): Interfaz web que envía imágenes al servidor para clasificación.
- **Protocol Buffers**: Define el contrato de comunicación entre cliente y servidor.

##  Requisitos e Instalación
Este proyecto utiliza `uv` para la gestión de dependencias.
```bash
uv sync
```

##  Uso

### Opción 1: Ejecutar con Docker (Recomendado)
```bash
# Construir y ejecutar ambos servicios
docker-compose up --build
```

Accede a la aplicación en: http://localhost:8501

### Opción 2: Ejecutar localmente
Para ejecutar el proyecto sin Docker, necesitas dos terminales:

1. **Iniciar el servidor gRPC:**
   ```bash
   uv run python src/server.py
   ```

2. **Lanzar la interfaz de usuario:**
   ```bash
   uv run streamlit run src/app.py
   ```

##  Calidad y Pruebas
Ejecutar linter (Clase 5):

```bash
uv run ruff check
```

Ejecutar pruebas unitarias (Clase 2):

```bash
uv run pytest
```
**Cobertura de Pruebas:**
-  Carga del modelo MobileNetV2
-  Funcionalidad de ModelHandler (predicción)
-  Tracking con MLflowTracker
-  Traducción de etiquetas en UIHandler
-  Inicialización del cliente gRPC

## Logging y Ejecuciones Limpias
El proyecto está configurado para ejecuciones limpias con control de verbosidad:

- **Por defecto**: Nivel WARNING (solo errores y warnings importantes)
- **Configurable**: Usa la variable `LOG_LEVEL` para controlar la verbosidad

```bash
# Ejecutar con logs detallados
LOG_LEVEL=INFO uv run python src/server.py

# Ejecutar con logs de debug (muy verboso)
LOG_LEVEL=DEBUG uv run python src/server.py

# Ejecutar limpio (por defecto)
uv run python src/server.py
```

Niveles disponibles: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

## CLI: Análisis desde Docker o local
Si quieres analizar imágenes directamente (sin abrir Streamlit), puedes usar el CLI:

```bash

uv run python src/cli.py --image rutas/mi_imagen.jpg
```

Si usas Docker:

```bash
docker compose run --rm app python src/cli.py --image /path/to/mi_imagen.jpg
```

##  Docker
El proyecto incluye configuración Docker para facilitar el despliegue:

- `Dockerfile.server`: Contenedor para el servidor gRPC con el modelo ML.
- `Dockerfile.app`: Contenedor para la aplicación Streamlit.
- `docker-compose.yml`: Orquesta ambos servicios en una red compartida.

### Requisitos para Docker
- Docker instalado y ejecutándose.
- Docker Compose.

### Ejecutar con Docker
```bash
docker-compose up --build
```

Esto iniciará:
- Servidor gRPC en puerto 50051
- Aplicación web en http://localhost:8501
- Interfaz de MLflow en http://localhost:5000
##  Tablero Kanban
El proyecto utiliza un tablero Kanban para la gestión ágil del desarrollo. Puedes acceder al tablero aquí: [GitHub Projects - Plant Disease Detection](https://trello.com/invite/proyectoia31/ATTIa0ebcc94e9d42792058f219cfc7aac1dED1F85E9}) 

El tablero incluye columnas para:
- **Backlog**: Tareas pendientes.
- **In Progress**: Trabajo en desarrollo.
- **Review**: Código bajo revisión.
- **Done**: Tareas completadas.
##  Licencia
Este proyecto se distribuye bajo la licencia MIT.