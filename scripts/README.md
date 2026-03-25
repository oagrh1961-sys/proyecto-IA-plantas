# 🔧 Scripts de Utilidad

Colección de scripts auxiliares para configuración y diagnóstico.

## Archivos

### `descargar_modelo.py`
Descarga el modelo entrenado desde Hugging Face.

```bash
python scripts/descargar_modelo.py
```

**Qué hace:**
- Descarga el modelo MobileNetV2 desde `linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification`
- Lo guarda en `modelo_entrenado/`
- Crea configuración y archivos de tokens

**Cuándo usarlo:**
- Primera instalación del proyecto
- Si el directorio `modelo_entrenado/` se borra accidentalmente

### `create_test_image.py`
Genera una imagen aleatoria para testing.

```bash
python scripts/create_test_image.py
```

**Qué hace:**
- Crea `tests/fixtures/test_image.jpg` (imagen 224x224 aleatoria)
- Útil para testing rápido sin datos reales

### `diagnose_connection.py`
Diagnostica problemas de conexión local/Docker.

```bash
python scripts/diagnose_connection.py
```

**Diagnósticos que realiza:**
- Conectividad al servidor gRPC
- Latencia de red
- Contexto (Local vs Docker)
- Estado de los puertos
- Información de configuración

**Salida esperada:**
```
✓ Servidor gRPC accesible
✓ Latencia: 2ms
✓ Contexto: Local
✓ Configuración cargada correctamente
```

## 🏃 Ejecutar Todos los Scripts

```bash
# 1. Descargar modelo
python scripts/descargar_modelo.py

# 2. Crear imagen de prueba
python scripts/create_test_image.py

# 3. Diagnosticar conexión
python scripts/diagnose_connection.py
```

## 📝 Notas

- Los scripts pueden ejecutarse en cualquier orden (excepto descargar_modelo.py primero)
- La mayoría requieren las dependencias de `pyproject.toml`
- Para Docker, ejecutar desde dentro del contenedor
