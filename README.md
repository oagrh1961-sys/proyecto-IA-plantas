# 🌿 Detección de Enfermedades en Cultivos con IA

## Descripción
Sistema de clasificación de imágenes basado en **MobileNetV2** para la identificación temprana de patologías en hojas de plantas. Desarrollado para la materia "Desarrollo de Proyectos de IA".

## 🏗️ Arquitectura
El proyecto utiliza una arquitectura **gRPC** distribuida con resiliencia mejorada:

- **Servidor gRPC** (`server.py`): Carga el modelo MobileNetV2 y realiza inferencias con tracking MLflow
- **Cliente Streamlit** (`app.py`): Interfaz web con reconexión automática y manejo robusto de errores
- **Protocol Buffers**: Define el contrato de comunicación entre cliente y servidor
- **MLflow UI**: Dashboard de seguimiento de métricas y experimentos

### 🔄 Características de Resiliencia
- ✅ Retry automático (hasta 3 intentos)
- ✅ Backoff exponencial (1s, 2s, 4s)
- ✅ Timeouts configurables
- ✅ Reconstrucción automática de canales
- ✅ Detección de contexto (Local vs Docker)
- ✅ Logs detallados para debugging
- ✅ Healthcheck automático en Docker

##  Requisitos e Instalación
Este proyecto utiliza `uv` para la gestión de dependencias.
```bash
uv sync
```

##  Uso

### Opción 1: Ejecutar con Docker (Recomendado) 🐳
```bash
# Construir y ejecutar los 3 servicios (server, app, mlflow)
docker-compose up --build
```

Accede a:
- 🌐 **Streamlit**: http://localhost:8501
- 📊 **MLflow UI**: http://localhost:5000
- 🔧 **gRPC Server**: server:50052 (interno)

### Opción 2: Ejecutar localmente 💻
Para ejecutar sin Docker, necesitas 2 terminales (en carpeta del proyecto):

**Terminal 1 - Servidor gRPC:**
```bash
uv run python -m src.server
```

**Terminal 2 - Interfaz Streamlit:**
```bash
uv run streamlit run src/app.py
```

Accede a: http://localhost:8501

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

## 🔧 Troubleshooting & Diagnóstico

### Problema: "Error conectando al servidor"

**Ejecutar diagnóstico automático:**
```bash
# Para conexión Local
python diagnose_connection.py

# Para conexión Docker
python diagnose_connection.py --docker
```

**Para Local:**
- ✅ Verifica que ambos servicios estén corriendo en 2 terminales diferentes
- ✅ Confirma que el puerto 50052 esté libre: `netstat -ano | findstr :50052` (Windows)
- ✅ Revisa los logs del servidor para errores

**Para Docker:**
```bash
# Ver estado de contenedores
docker ps

# Ver logs del servidor
docker-compose logs server

# Reiniciar servicios
docker-compose restart server

# Full reset
docker-compose down -v --remove-orphans
docker-compose up --build
```

### Contexto de Conexión
La app detecta automáticamente si está corriendo en:
- **[Local]**: Conecta a `localhost:50052`
- **[Docker]**: Conecta a `server:50052` (nombre del servicio)

Este contexto se muestra en la UI de Streamlit: 🔗 Conectado [Local/Docker]: host:port

Ver [`CONEXION_GUIDE.md`](CONEXION_GUIDE.md) para documentación detallada.

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

## Variables de Entorno

Crea un archivo `.env` para configuración personalizada:
```env
GRPC_SERVER_HOST=localhost     # Cambiar a 'server' si usas Docker
GRPC_SERVER_PORT=50052
GRPC_SERVER_TIMEOUT=10
LOG_LEVEL=INFO
MLFLOW_TRACKING_URI=file:///app/mlruns
```

## CLI: Análisis desde Docker o local
Si quieres analizar imágenes directamente (sin abrir Streamlit), puedes usar el CLI:

```bash

uv run python src/cli.py --image rutas/mi_imagen.jpg
```

Si usas Docker:

```bash
docker compose run --rm app python src/cli.py --image /path/to/mi_imagen.jpg
```

## 🚀 CI/CD con GitLab y DigitalOcean

El proyecto incluye un pipeline **CI/CD profesional** que automatiza:
- ✅ Pruebas automáticas (pytest)
- ✅ Construcción de imagen Docker
- ✅ Despliegue automático a producción

### � ¡NUEVO! Guía Rápida de Ejecución
**→ [GUIA_RAPIDA_EJECUCION.md](GUIA_RAPIDA_EJECUCION.md)** ⭐ **(Comienza here - 20 minutos)**
- 5 fases con instrucciones paso a paso
- Script PowerShell automatizado
- Migración GitHub → GitLab

### 📚 Documentación Completa
- **[CI_CD_GITLAB_DIGITALOCEAN.md](docs/CI_CD_GITLAB_DIGITALOCEAN.md)** - Guía completa (6 secciones)
- **[CONFIGURACION_VARIABLES_GITLAB.md](docs/CONFIGURACION_VARIABLES_GITLAB.md)** - Setup de variables de CI/CD
- **[.gitlab-ci.yml](.gitlab-ci.yml)** - Pipeline YAML (3 stages)
- **[VARIABLES_SECRETOS.md](docs/VARIABLES_SECRETOS.md)** - Gestión segura de credenciales
- **[MAKEFILE_GUIDE.md](docs/MAKEFILE_GUIDE.md)** - Comandos disponibles
- **[EMERGENCY_DEPLOYMENT.md](docs/EMERGENCY_DEPLOYMENT.md)** - Deployment manual y troubleshooting

### 🏗️ Etapas del Pipeline
```
Test (pytest)
   ↓
Build (Docker)
   ↓
Deploy (DigitalOcean - Manual)
```

**Ver estado:** GitLab → Tu Proyecto → CI/CD → Pipelines

##  Docker
El proyecto incluye configuración Docker para facilitar el despliegue:

- `Dockerfile.server`: Contenedor para el servidor gRPC con el modelo ML.
- `Dockerfile.app`: Contenedor para la aplicación Streamlit.
- `config/docker-compose.yml`: Orquesta ambos servicios en una red compartida.

### Requisitos para Docker
- Docker instalado y ejecutándose.
- Docker Compose.

### Ejecutar con Docker
```bash
docker-compose up --build
```

Esto iniciará:
- Servidor gRPC en puerto 50052
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