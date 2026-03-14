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
##  Línea de Tiempo del Proyecto

### 📅 Evolución del Desarrollo

| Fecha | Hito | Descripción |
|-------|------|-------------|
| **2026-10-14** | Entrega Final Completa | Arquitectura gRPC completa con MLflow tracking, Docker containerization, CLI limpio, pruebas unitarias y ejecuciones limpias |
| **2026-10-13** | Arquitectura MLOps | Implementación de servidor gRPC separado, cliente distribuido, tracking MLflow con métricas de latencia y errores |
| **2026-11-12** | Containerización | Configuración Docker completa con docker-compose, servicios orquestados y volúmenes optimizados |
| **2026-13-11** | Calidad de Código | Pruebas unitarias completas, logging configurable, ejecuciones limpias sin output innecesario |
| **2026-13-10** | Documentación | README completo con instrucciones de instalación, uso, Docker y control de logging |
| **2026-13-07** | Entrega Inicial | Proyecto base con MobileNetV2, Streamlit UI y modelo entrenado funcional |

### 📊 Métricas del Proyecto
- **Arquitectura**: gRPC distribuida con Protocol Buffers
- **Modelo**: MobileNetV2 fine-tuned para clasificación de enfermedades en plantas
- **Cobertura de Pruebas**: 5/5 pruebas unitarias ✅
- **Containerización**: Docker + Docker Compose ✅
- **MLOps**: MLflow tracking con latencia y errores ✅
- **Líneas de Código**: ~506 líneas agregadas en la evolución final

### 🎯 Hitos Técnicos Alcanzados
1. **Microservicios gRPC** - Separación clara entre servidor de inferencia y cliente UI
2. **MLflow Integration** - Tracking completo de predicciones, latencia y errores
3. **Docker Production-Ready** - Contenedores optimizados con healthchecks y volúmenes
4. **CLI Tool** - Análisis de imágenes sin interfaz gráfica
5. **Clean Code** - Logging configurable, pruebas unitarias, código linted
6. **Documentación Completa** - Instrucciones para desarrollo y producción

##  Tablero Kanban
El proyecto utiliza un tablero Kanban para la gestión ágil del desarrollo. Puedes acceder al tablero aquí: [GitHub Projects - Plant Disease Detection](https://trello.com/invite/proyectoia31/ATTIa0ebcc94e9d42792058f219cfc7aac1dED1F85E9}) 

El tablero incluye columnas para:
- **Backlog**: Tareas pendientes.
- **In Progress**: Trabajo en desarrollo.
- **Review**: Código bajo revisión.
- **Done**: Tareas completadas.
##  Licencia
Este proyecto se distribuye bajo la licencia MIT.