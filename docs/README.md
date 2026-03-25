# 📚 Documentación del Proyecto

Este directorio contiene toda la documentación técnica del proyecto.

## Archivos de Documentación

### `PROYECTO_STRUCTURE.md` ⭐️ EMPEZAR AQUÍ
Guía completa de la estructura del proyecto.

**Contenido:**
- Estructura de directorios visual
- Descripción de cada carpeta
- Flujo de trabajo (desarrollo local vs Docker)
- Variables de entorno
- Servicios en Docker Compose
- Troubleshooting

👉 **Si es la primera vez, lee esto primero.**

### `CONEXION_GUIDE.md`
Guía de conexión entre ambiente local y Docker.

**Problemas que resuelve:**
- Conexión rechazada entre local y Docker
- Timeout en requests gRPC
- Diagnóstico de puertos
- Context switching (Local vs Docker)
- Troubleshooting de healthchecks

**Incluye:**
- Diagrama de arquitectura
- Comandos de diagnóstico
- Pasos para resolver cada problema

### `IMPLEMENTACION.md`
Resumen de las 10 mejoras implementadas.

**Mejoras documentadas:**
1. Dockerfiles Multi-Stage
2. Validación de Entrada Robusta
3. Graceful Shutdown
4. Caché de Modelo (Singleton)
5. Configuración con Pydantic
6. Prometheus Metrics
7. Rate Limiting
8. Batch Processing
9. Distributed Tracing
10. Structured Logging JSON

**Para cada mejora:**
- Qué problema resolvía
- Cómo se implementó
- Cómo usarlo
- Impacto en performance

### `MEJORAS_POSIBLES.md`
Roadmap futuro del proyecto.

**Categorías:**
- **Alta Prioridad**: GPU support, CI/CD pipeline
- **Media Prioridad**: Kubernetes, monitoring dashboard
- **Baja Prioridad**: Features avanzadas

**Para ver:**
- Impacto estimado
- Esfuerzo requerido
- Dependencias

## 📖 Cómo Navegar la Documentación

### Soy nuevo en el proyecto
1. Lee [PROYECTO_STRUCTURE.md](PROYECTO_STRUCTURE.md)
2. Revisa [IMPLEMENTACION.md](IMPLEMENTACION.md) para ver qué características hay
3. Consulta [CONEXION_GUIDE.md](CONEXION_GUIDE.md) si tienes problemas

### Tengo problemas de conexión
→ Ve a [CONEXION_GUIDE.md](CONEXION_GUIDE.md)

### Quiero saber qué se mejoró
→ Ve a [IMPLEMENTACION.md](IMPLEMENTACION.md)

### Quiero contribuir con mejoras
→ Ve a [MEJORAS_POSIBLES.md](MEJORAS_POSIBLES.md)

## 🔗 Referencias Cruzadas

- **Código**: Ver `src/` en [PROYECTO_STRUCTURE.md](PROYECTO_STRUCTURE.md)
- **Scripts**: Ver `scripts/` en [PROYECTO_STRUCTURE.md](PROYECTO_STRUCTURE.md)
- **Config**: Ver `config/` en [PROYECTO_STRUCTURE.md](PROYECTO_STRUCTURE.md)
- **Tests**: Ver `tests/` en [PROYECTO_STRUCTURE.md](PROYECTO_STRUCTURE.md)

## 📝 Mantener la Documentación

Al realizar cambios:
1. Actualiza los archivos relevantes
2. Mantén ejemplos de código sincronizados
3. Actualiza la tabla de contenidos si es necesario
4. Revisa links internos

## 🚀 Inicio Rápido

```bash
# Desarrollo local
python scripts/descargar_modelo.py
streamlit run src/app.py

# Con Docker
cd config/
docker-compose up --build

# Diagnosticar problemas
python scripts/diagnose_connection.py
```

## 📞 Soporte

- 🐛 Problemas: Ver [CONEXION_GUIDE.md](CONEXION_GUIDE.md)
- 📋 Config: Ver [config/README.md](../config/README.md)
- 🧪 Tests: Ver [tests/README.md](../tests/README.md)
- 🔧 Scripts: Ver [scripts/README.md](../scripts/README.md)
