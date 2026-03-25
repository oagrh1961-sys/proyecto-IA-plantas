# 🔧 Scripts de Utilidad

Colección de scripts auxiliares para configuración, diagnóstico y deployment.

## Archivos

### `setup-gitlab-runner.sh` ⭐ NUEVO
Script automático para instalar y configurar GitLab Runner en DigitalOcean.

```bash
# Ejecutar en el Droplet
bash setup-gitlab-runner.sh
```

**Qué hace:**
- ✅ Actualiza el sistema operativo
- ✅ Instala Docker y Docker Compose
- ✅ Instala GitLab Runner automáticamente
- ✅ Configura usuario no-root
- ✅ Crea directorios de la app
- ✅ Genera script interactivo de registro

**Cuándo usarlo:**
- Primavera vez que configuras un Droplet en DigitalOcean
- Después de crear una nueva instancia

**Resultado:**
```
$ bash setup-gitlab-runner.sh

✅ Sistema válido
✅ Sistema actualizado
✅ Docker instalado
✅ Docker Compose instalado
✅ GitLab Runner instalado
✅ Instalación completada exitosamente

Próximos pasos:
1. Ejecutar: bash /tmp/register-runner.sh
2. Proporcionar token de GitLab
3. Hacer push para triggear pipeline
```

---

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

**Requisitos:**
- Conexión a internet
- ~500MB de espacio disponible
- Dependencias de HuggingFace

---

### `create_test_image.py`
Genera una imagen aleatoria para testing.

```bash
python scripts/create_test_image.py
```

**Qué hace:**
- Crea `tests/fixtures/test_image.jpg` (imagen 224x224 RGB)
- Útil para testing rápido sin datos reales
- Genera nuevas imágenes cada vez

**Cuándo usarlo:**
- Testing durante desarrollo
- Validar pipeline sin modelos reales
- Debugging de validaciones de imagen

---

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
- Verificación de .env

**Salida esperada:**
```
====== Diagnóstico de Conexión ======
✓ Servidor gRPC accesible en localhost:50052
✓ Latencia: 2ms
✓ Contexto: Local
✓ Configuración cargada correctamente
✓ Modelo disponible: ./modelo_entrenado
```

**Qué revisar si falla:**
- Server no está corriendo → `make run` o `docker-compose up`
- Puerto en uso → Ver qué lo ocupa
- Contexto incorrecto → Revisar .env
- Modelo no existe → `python scripts/descargar_modelo.py`

---

## 🏃 Ejecutar Todos los Scripts

```bash
# 1. Descargar modelo (necesario una sola vez)
python scripts/descargar_modelo.py

# 2. Crear imagen de prueba
python scripts/create_test_image.py

# 3. Diagnosticar conexión
python scripts/diagnose_connection.py
```

## 🔐 Setup en DigitalOcean

Para servidor remoto, ejecutar después de SSH:

```bash
# 1. Descargar script
wget https://raw.githubusercontent.com/oagrh1961-sys/proyecto-IA-plantas/main/scripts/setup-gitlab-runner.sh

# 2. Ejecutar
bash setup-gitlab-runner.sh

# 3. Registrar runner (se genera automáticamente)
bash /tmp/register-runner.sh
```

O copiar manualmente el archivo.

---

## 📝 Notas

- Los scripts pueden ejecutarse en cualquier orden (excepto descargar_modelo.py primero)
- La mayoría requieren las dependencias de `pyproject.toml`
- Para Docker, ejecutar scripts dentro del contenedor:
  ```bash
  docker exec -it proyecto-app bash
  python scripts/diagnose_connection.py
  ```

---

## 📚 Referencias

- AutoSetup del Server: [setup-gitlab-runner.sh](setup-gitlab-runner.sh)
- CI/CD Completo: [CI_CD_GITLAB_DIGITALOCEAN.md](../docs/CI_CD_GITLAB_DIGITALOCEAN.md)
- Variables de Entorno: [VARIABLES_SECRETOS.md](../docs/VARIABLES_SECRETOS.md)
- Emergency Deployment: [EMERGENCY_DEPLOYMENT.md](../docs/EMERGENCY_DEPLOYMENT.md)
