# 🚀 Guía Completa de CI/CD con GitLab y DigitalOcean

Esta guía te llevará paso a paso por la configuración de un pipeline CI/CD profesional para desplegar tu aplicación de IA en producción.

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Paso 1: Preparar en Local](#paso-1-preparar-en-local)
3. [Paso 2: Configurar GitLab](#paso-2-configurar-gitlab)
4. [Paso 3: Crear Infraestructura en DigitalOcean](#paso-3-crear-infraestructura-en-digitalocean)
5. [Paso 4: Instalar GitLab Runner](#paso-4-instalar-gitlab-runner)
6. [Paso 5: Configurar Variables de Entorno](#paso-5-configurar-variables-de-entorno)
7. [Paso 6: Validar el Pipeline](#paso-6-validar-el-pipeline)
8. [Mantenimiento y Troubleshooting](#mantenimiento-y-troubleshooting)

---

## Requisitos Previos

### Cuentas necesarias:
- ✅ GitLab (gratis en gitlab.com)
- ✅ DigitalOcean (registro: $5 USD/mes mínimo)
- ✅ Docker Hub (para almacenar imágenes del container)

### Software en Local:
```bash
git --version
docker --version
```

---

## Paso 1: Preparar en Local

### 1.1 Verificar que Makefile existe

Tu `Makefile` debe tener un target `test`:

```bash
# Ver targets disponibles
make help

# Ejecutar tests localmente
make test
```

Si no existe, crea `Makefile` en la raiz:

```makefile
.PHONY: test build help

test:
	@echo "Ejecutando tests..."
	pytest -v

build:
	@echo "Construyendo imagen Docker..."
	docker build -t proyecto-deteccion-plantas .

help:
	@echo "Targets disponibles:"
	@echo "  make test    - Ejecutar tests"
	@echo "  make build   - Construir imagen Docker"
```

### 1.2 Crear archivo .env.example

En `config/` crea `.env.example` (sin valores sensibles):

```bash
cp config/.env config/.env.example
```

Edita `config/.env.example`:

```env
# Servidor gRPC
GRPC_HOST=0.0.0.0
GRPC_PORT=50052

# Modelo ML
MODEL_PATH=/app/modelo_entrenado

# MLflow
MLFLOW_TRACKING_URI=file:///app/mlruns
MLFLOW_EXPERIMENT_NAME=plant-disease

# Logging
LOG_LEVEL=INFO
```

### 1.3 Verificar código en GitHub (si aún no está en GitLab)

```bash
git remote -v
# Output: origin  https://github.com/tu-usuario/proyecto-IA-plantas.git

# Tu código ya está en GitHub 👍
```

---

## Paso 2: Configurar GitLab

### 2.1 Crear Proyecto en GitLab

1. Ve a https://gitlab.com
2. Click en "New project"
3. Selecciona "Create blank project"
4. Llena los datos:
   - Project name: `proyecto-deteccion-plantas`
   - Visibility: `Public` (para nuestros propósitos)
   - Click "Create project"

### 2.2 Migrar Repositorio desde GitHub a GitLab

```bash
cd proyecto_deteccion_plantas

# Cambiar remote de GitHub a GitLab
git remote remove origin
git remote add origin https://gitlab.com/tu-usuario/proyecto-deteccion-plantas.git

# Pushear a GitLab
git branch -M main
git push -u origin main
```

**Nota:** Te pedirá credenciales de GitLab. Usa un "Personal Access Token":
1. GitLab → Settings → Access Tokens
2. Crea token con scope `api, read_repository, write_repository`
3. Usa este token como contraseña

### 2.3 Verifica en GitLab

```
https://gitlab.com/tu-usuario/proyecto-deteccion-plantas
```

Deberías ver tu código subido ✅

### 2.4 Crear Deploy Token para Docker

```
GitLab → Settings → CI/CD → Deploy Tokens
Crea token con nombre: "docker-runner"
Permisos: "write_registry"
Copia el nombre de usuario y contraseña
```

---

## Paso 3: Crear Infraestructura en DigitalOcean

### 3.1 Crear Cuenta DigitalOcean

1. Ve a https://www.digitalocean.com
2. Sign up con email
3. Verifica email
4. Agrega método de pago

### 3.2 Crear Droplet (Servidor)

#### Configuración Recomendada:

```
Choose an image:
├─ Marketplace → Docker on Ubuntu 24.04 LTS
   (ya viene con Docker instalado)

Choose a size:
├─ CPU/Memory: 2 vCPU, 2GB RAM ($12/mes)
├─ Storage: SSD 50GB

Choose a region:
├─ Selecciona cercano: Miami (iad3), México (mexico1)

Choose authentication:
├─ ✅ SSH Key (seguro)
│   → Generate new
│   → Nombre: "gitlab-runner"
│   → Download (.pem)
│   → Guardar en: ~/.ssh/gitlab-runner.pem
│
├─ ⚠️ O Password (menos seguro)
│   → Recibirás contraseña por email

Hostname: proyecto-plantas-prod

Backups: ✅ Activar (protección)
```

**IMPORTANTE:** Después de crear:
1. Anota IP del Droplet (ej: `123.45.67.89`)
2. Guarda la SSH key en `~/.ssh/`

### 3.3 Conectar al Droplet

```bash
# Linux/Mac
chmod 600 ~/.ssh/gitlab-runner.pem
ssh -i ~/.ssh/gitlab-runner.pem root@123.45.67.89

# Windows PowerShell
# ... usar PuTTY o Windows Subsystem for Linux
```

### 3.4 Configurar Droplet

```bash
# Una vez dentro del servidor:

## Actualizar sistema
apt-get update
apt-get upgrade -y

## Docker ya está instalado, verificar:
docker --version
docker run hello-world

## Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
docker-compose --version

## Crear directorio para la app
mkdir -p /app/proyecto_deteccion_plantas
cd /app/proyecto_deteccion_plantas

## Crear usuario no-root para seguridad
useradd -m -s /bin/bash appuser
usermod -aG docker appuser

## Configurar permisos
chown -R appuser:appuser /app/proyecto_deteccion_plantas
```

---

## Paso 4: Instalar GitLab Runner

### 4.1 En el Droplet, Instalar GitLab Runner

```bash
# Conectarse al Droplet
ssh -i ~/.ssh/gitlab-runner.pem root@IP_DEL_DROPLET

# Descargar e instalar GitLab Runner
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | bash
apt-get install gitlab-runner

# Verificar instalación
gitlab-runner --version
```

### 4.2 Registrar Runner con GitLab

En el Droplet:

```bash
gitlab-runner register
```

**Responder a las preguntas:**

```
GitLab instance URL: https://gitlab.com/
GitLab registration token: [VER ABAJO]
Enter description: proyecto-plantas-runner
Enter tags (comma separated): production,docker
Enter maintenance note: Runner principal para prod

Enter an executor: docker

Enter the default Docker image: docker:latest

Register runner as paused?: no
```

**¿Dónde obtener el Registration Token?**

```
1. GitLab → Tu Proyecto → Settings → CI/CD → Runners
2. Click "New instance runner"
3. Selecciona tags: "docker"
4. Copia el token mostrado
5. Pegalo en la terminal cuando pida
```

### 4.3 Verificar Runner Registrado

```bash
# En GitLab:
GitLab → Tu Proyecto → Settings → CI/CD → Runners
```

Deberías ver el runner listado con estado ✅ verde

---

## Paso 5: Configurar Variables de Entorno

### 5.1 Variables en GitLab (Secrets)

```
GitLab → Tu Proyecto → Settings → CI/CD → Variables
```

**Agregar estas variables:**

| Variable | Valor | Tipo |
|----------|-------|------|
| `DOCKER_USER` | tu-usuario-docker | Variable |
| `DOCKER_PASSWORD` | token-docker-hub | File (Masked) |
| `SERVER_HOST` | IP-de-tu-droplet | Variable |
| `SSH_PRIVATE_KEY` | contenido de gitlab-runner.pem | File (Masked) |
| `GITLAB_CI_SKIP_DEFAULT_CHECKOUT` | "false" | Variable |

**Cómo obtener cada una:**

#### DOCKER_USER y DOCKER_PASSWORD:
```bash
# En Docker Hub (https://hub.docker.com):
1. Login
2. Account Settings → Security → New Access Token
3. Nombre: "gitlab-ci"
4. Permiso: "Read & Write"
5. Copia el token
```

#### SSH_PRIVATE_KEY (Base64 encoded):
```bash
# En tu máquina local:
cat ~/.ssh/gitlab-runner.pem | base64 | tr -d '\n'
# Copia todo el output
# Pégalo en la variable (es muy larga)
```

#### SERVER_HOST:
```
Es la IP del Droplet que anotaste (ej: 123.45.67.89)
```

### 5.2 Variables en el Droplet

En el servidor, agregar credenciales de Docker:

```bash
ssh -i ~/.ssh/gitlab-runner.pem root@IP_DEL_DROPLET

# Login a Docker Hub
docker login
# Username: tu-usuario-docker
# Password: tu-token-docker
# (Las credenciales se guardan en ~/.docker/config.json)
```

---

## Paso 6: Validar el Pipeline

### 6.1 Hacer un commit para activar el pipeline

```bash
# En tu local:
cd proyecto_deteccion_plantas

# Crear rama feature
git checkout -b feature/ci-cd

# Realizar un cambio pequeño
echo "# CI/CD configurado" >> README.md

# Commit y push
git add .
git commit -m "feat: agregar pipeline CI/CD"
git push -u origin feature/ci-cd
```

### 6.2 Monitorear el Pipeline

```
1. GitLab → Tu Proyecto → CI/CD → Pipelines
2. Verás tu commit con el pipeline ejecutándose
3. Click en el commit para ver detalles

Etapas (stages):
├─ test         (ejecuta pytest)
├─ build        (construye imagen Docker)
└─ deploy       (despliegue opcional)
```

### 6.3 Crear Merge Request y Mergear a Main

```
1. GitLab → Merge Requests → Create MR
2. From branch: feature/ci-cd
3. To branch: main
4. Después que pasen todos los tests:
   Click "Merge"
```

**Esto triggereará el build automático** ✅

### 6.4 Desplegar a Producción (Manual)

```
1. GitLab → CI/CD → Pipelines
2. En el pipeline de main:
   Click en "deploy_to_production"
   Click "Play" (▶️)
```

Esto ejecutará el deployment automaticamente.

---

## Mantenimiento y Troubleshooting

### Ver Logs del Pipeline

```
GitLab → CI/CD → Pipelines → Click en job → "Logs"
```

### Errores Comunes

#### ❌ "Pipeline failed: docker: permission denied"
```bash
# En el droplet:
usermod -aG docker gitlab-runner
systemctl restart gitlab-runner
```

#### ❌ "Failed to pull image"
```bash
# Verificar credenciales Docker:
docker login
# Si falla, regenerar token en Docker Hub
```

#### ❌ "SSH connection refused"
```bash
# Verificar SSH key está correctamente encoded:
cat ~/.ssh/gitlab-runner.pem | base64 | wc -c
# Debe ser ~2000+ caracteres
```

### Ver estado del Runner

```bash
ssh -i ~/.ssh/gitlab-runner.pem root@IP_DEL_DROPLET

# Ver procesos del runner
gitlab-runner list
gitlab-runner verify

# Ver logs del runner
journalctl -u gitlab-runner -f
```

### Actualizar código en producción manualmente

```bash
ssh -i ~/.ssh/gitlab-runner.pem root@IP_DEL_DROPLET

cd /app/proyecto_deteccion_plantas
git pull origin main
docker-compose -f config/docker-compose.yml down
docker-compose -f config/docker-compose.yml up -d
```

---

## Resumen del Flujo Completo

```
1️⃣ Haces commit y push a GitLab
   ↓
2️⃣ GitLab triggerea el pipeline automáticamente
   ├─ Test: ejecuta pytest
   ├─ Build: construye imagen Docker y la pushea
   └─ Deploy: (opcional) despliegue manual
   ↓
3️⃣ Si todo pasó, la imagen está en Docker Hub
   ↓
4️⃣ Para desplegar a producción:
   └─ Click "Play" en el job "deploy_to_production"
   ↓
5️⃣ El Droplet:
   ├─ Descarga la imagen
   ├─ Detiene contenedores antiguos
   ├─ Inicia contenedores nuevos
   └─ Tu app se actualiza en vivo ✅
```

---

## Referencias

- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [GitLab Runner Installation](https://docs.gitlab.com/runner/install/)
- [DigitalOcean Droplets Docs](https://docs.digitalocean.com/products/droplets/)
- [Docker Hub Authentication](https://docs.docker.com/docker-hub/access-tokens/)

---

¡Tu proyecto está listo para producción! 🚀
