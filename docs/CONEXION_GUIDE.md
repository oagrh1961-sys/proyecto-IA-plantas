# Guía de Conexión Local vs Docker

## 🎯 Contextos de Ejecución

### Local (Desarrollo)
```bash
# Terminal 1: Inicia el servidor gRPC
python -m src.server

# Terminal 2: Inicia la app Streamlit
streamlit run src/app.py
```

**Configuración automática:**
- `GRPC_SERVER_HOST=localhost` (por defecto)
- `GRPC_SERVER_PORT=50052` (por defecto)
- UI mostrará: 🔗 Conectado [Local]: localhost:50052

---

### Docker (Producción)
```bash
# Inicia todos los servicios
docker-compose up --build

# Acceso:
# - Streamlit: http://localhost:8501
# - MLflow: http://localhost:5000
# - gRPC Server: server:50052 (interno)
```

**Configuración automática:**
- Container app: `GRPC_SERVER_HOST=server` (nombre del servicio)
- Container mlflow: `GRPC_SERVER_HOST=server`
- UI mostrará: 🔗 Conectado [Docker]: server:50052

---

## 📊 Diferencias Técnicas

| Aspecto | Local | Docker |
|--------|-------|--------|
| Hostname | `localhost` | `server` (nombre del servicio) |
| Puerto | `50052` (expuesto) | `50052` (interno) |
| Network | Host system | `plant-disease-net` bridge |
| Volúmenes | Direct path | `/app/mlruns` mounted |
| Restart | Manual | Automático con `on-failure:3` |
| Healthcheck | N/A | Verificación de puerto cada 30s |
| Logs | Terminal | `docker-compose logs` |

---

## 🔧 Troubleshooting

### Problema: "Error conectando al servidor"

**1. Verifica el contexto:**
```bash
# Local - Ver si el servidor está corriendo
python -m src.server

# Docker - Ver estado de contenedores
docker ps
docker-compose logs server
```

**2. Diagnóstico automático:**
```bash
# Para Local
python diagnose_connection.py

# Para Docker
python diagnose_connection.py --docker
```

**3. Problemas comunes:**

#### En Local:
```bash
# ❌ "Connection refused" → Servidor no está corriendo
python -m src.server

# ❌ Puerto 50052 ya en uso
netstat -ano | findstr :50052  # Windows
lsof -i :50052                  # Mac/Linux
```

#### En Docker:
```bash
# ❌ Container no inicia
docker-compose logs server

# ❌ Network issues
docker network ls
docker inspect plant-disease-net

# ❌ Servicio unhealthy
docker ps  # Revisa el status

# Reinicia
docker-compose restart server
```

---

## 🚀 Variables de Entorno

Crear archivo `.env`:
```env
GRPC_SERVER_HOST=localhost      # Cambiar a 'server' para Docker
GRPC_SERVER_PORT=50052
GRPC_SERVER_TIMEOUT=10
LOG_LEVEL=INFO
MLFLOW_TRACKING_URI=file:///app/mlruns
```

---

## 📈 Características de Resiliencia

El cliente gRPC mejorado incluye:

1. **Retry automático** (hasta 3 intentos)
2. **Backoff exponencial** (1s, 2s, 4s)
3. **Timeouts configurables** (10s por defecto)
4. **Reconstrucción de channel** en primer fallo
5. **Logs detallados** para debugging
6. **Detección automática de contexto** (Local vs Docker)

```python
# Uso en código
from src.client import PlantDiseaseClient

try:
    client = PlantDiseaseClient(timeout=10)  # Custom timeout
    label, confidence, latency = client.classify_image(image_bytes)
except grpc.RpcError as e:
    print(f"Error: {e.code().name} - {e.details()}")
```

---

## 🐳 Docker Compose Mejorado

El `docker-compose.yml` ahora incluye:

- **Healthcheck**: Verifica que el puerto 50052 esté abierto
- **Restart policy**: Reinicia automáticamente en fallos
- **Depends on**: El app espera a que el server esté healthy
- **Container names**: Nombres consistentes para debugging
- **Logging**: PYTHONUNBUFFERED para logs en tiempo real

---

## 📝 Comandos Útiles

```bash
# Ver estado de servicios
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f server
docker-compose logs -f app
docker-compose logs -f mlflow

# Ejecutar comando en container
docker-compose exec server python -c "import grpc; print('gRPC OK')"

# Rebuild y reinicia
docker-compose down -v
docker-compose up --build

# Limpiar todo y empezar
docker-compose down -v --remove-orphans
docker system prune -a
```

---

## ✅ Verificación de Éxito

### Local:
```
✅ Conexión exitosa al servidor [Local]: localhost:50052
```

### Docker:
```
✅ Conectado [Docker]: server:50052
Container proyecto-server: healthy
Container proyecto-app: running
Container proyecto-mlflow: running
```
