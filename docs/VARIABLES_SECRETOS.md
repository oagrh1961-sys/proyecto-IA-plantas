# 🔐 Gestión de Variables de Entorno y Secretos

Guía completa para manejar credenciales y configuración sensible de forma segura en tu pipeline CI/CD.

## 📋 Tabla de Contenidos

1. [Tipos de Variables](#tipos-de-variables)
2. [Variables Necesarias](#variables-necesarias)
3. [Cómo Crear Variables en GitLab](#cómo-crear-variables-en-gitlab)
4. [Mejores Prácticas de Seguridad](#mejores-prácticas-de-seguridad)
5. [Debugging de Variables](#debugging-de-variables)

---

## Tipos de Variables

### 1. Variable (texto simple)
- Usada para: URLs, nombres de usuario, configuración general
- Visible en logs del pipeline
- Ejemplo: `DOCKER_USER`

### 2. File (archivo)
- Usada para: SSH keys, certificados, tokens largos
- Guardada como archivo temporal durante execution
- Mejor para: `SSH_PRIVATE_KEY`

### 3. Protected
- Solo se usa en ramas/tags protegidos (main)
- Adicional: Masked (oculta en logs)

### 4. Group Variable
- Compartida entre múltiples proyectos del grupo

---

## Variables Necesarias

### Variables de GitLab CI/CD

Agregar en: **GitLab → Tu Proyecto → Settings → CI/CD → Variables**

```yaml
# ============================================
# DOCKER REGISTRY
# ============================================
DOCKER_USER
  Type: Variable
  Scope: All
  Protected: ✅
  Masked: ❌
  Valor: tu-usuario-docker
  
DOCKER_PASSWORD
  Type: File (mejor que Variable)
  Scope: All
  Protected: ✅
  Masked: ✅
  Valor: token-de-docker-hub
  
DOCKER_REGISTRY
  Type: Variable
  Valor: docker.io

# ============================================
# SERVIDOR PRODUCCIÓN
# ============================================
SERVER_HOST
  Type: Variable
  Scope: All
  Protected: ✅
  Masked: ❌
  Valor: IP-o-dominio-del-droplet (ej: 123.45.67.89)
  
SERVER_PORT
  Type: Variable
  Valor: 22
  
SSH_PRIVATE_KEY
  Type: File
  Scope: All
  Protected: ✅
  Masked: ✅
  Valor: contenido base64 de gitlab-runner.pem

# ============================================
# SERVIDOR STAGING (opcional)
# ============================================
STAGING_SERVER_HOST
  Type: Variable
  Valor: ip-staging

SSH_PRIVATE_KEY_STAGING
  Type: File
  Protected: ✅
  Masked: ✅

# ============================================
# CONFIGURACIÓN DE LA APP
# ============================================
LOG_LEVEL
  Type: Variable
  Valor: INFO
  
# Para acceder a estas en el pipeline:
# echo $LOG_LEVEL
```

---

## Cómo Crear Variables en GitLab

### Paso 1: Acceder a Configuración

```
GitLab → Tu Proyecto
        → Settings (⚙️)
        → CI/CD
        → Variables
        → Click "Add variable"
```

### Paso 2: Completar Formulario

**Sin Scopes (disponible para todos):**

```
Key: DOCKER_USER
Value: mi-usuario-docker
Type: Variable
Protected: ✅ (solo en main/protected branches)
Masked: ❌ (es público)
Scope: All (o especificar ramas)
```

**Para Variables Sensibles:**

```
Key: DOCKER_PASSWORD
Value: [pegar token de Docker Hub]
Type: File
Protected: ✅
Masked: ✅ (no mostrar en logs)
```

### Paso 3: Ver Variables Creadas

```
GitLab → Tu Proyecto → Settings → CI/CD → Variables
```

Cada variable mostrará con un icono:
- 🔒 Protected (solo ramas seguras)
- 👁️ Masked (oculto en logs)
- 📄 File (guardado como archivo)

---

## Mejores Prácticas de Seguridad

### ✅ QUÉ DEBES HACER

#### 1. Usar SSH Keys en lugar de Passwords

**Crear SSH key para GitLab Runner:**

```bash
# En tu máquina local
ssh-keygen -t ed25519 -C "gitlab-runner" -f ~/.ssh/gitlab-runner

# IMPORTANTE: Sin passphrase (dejar vacío)
# Archivo privado: ~/.ssh/gitlab-runner
# Archivo público: ~/.ssh/gitlab-runner.pub
```

**Agregar a DigitalOcean:**

```bash
# Ver contenido de la clave pública
cat ~/.ssh/gitlab-runner.pub

# Copiar salida
# DigitalOcean → Settings → Security → SSH Keys → Add Key
# Pegar contenido público
```

**Codificar para GitLab:**

```bash
# Base64 encode la clave privada
cat ~/.ssh/gitlab-runner | base64 | tr -d '\n' | pbcopy

# En Windows PowerShell
[convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes(
  (Get-Content -Raw ~/.ssh/gitlab-runner)
)) | Set-Clipboard
```

#### 2. Usar Tokens en lugar de Passwords

**Para Docker Hub:**

```
1. Login en Docker Hub
2. Settings → Security
3. New Access Token
4. Nombre: gitlab-ci
5. Permissions: Read & Write
6. Copiar token (similar a ghp_XXXXX)
7. No guardar este token en ningún lado excepto en GitLab
```

#### 3. Rotación de Secretos

Cada 3-6 meses:

```bash
# 1. Generar nuevo token/key
# 2. Actualizar variable en GitLab
# 3. Esperar a que se use
# 4. Revocar token antiguo
```

#### 4. Limpieza de SSH Keys después del Deploy

En el `.gitlab-ci.yml`, siempre limpiar:

```yaml
after_script:
  - rm -f ~/.ssh/id_rsa
  - rm -f ~/.ssh/id_rsa.pub
  - docker logout || true
```

### ❌ QUÉ NO DEBES HACER

| ❌ NO HAGAS | ✅ USA EN LUGAR |
|-----------|----------------|
| Cometer .env con valores reales | Variables de GitLab CI/CD |
| Usar passwords directos | SSH keys o tokens |
| Compartir SSH keys en chat | Agregarlo solo a GitLab |
| Dejar credenciales en logs | Marcar como "Masked" |
| Usar variables globales en .gitlab-ci.yml | Definir en GitLab UI |
| Git push credenciales | Git commit .gitignore |

---

## Debugging de Variables

### Ver qué variables están disponibles

En el pipeline, añade (solo para debugging):

```yaml
debug_variables:
  stage: test
  script:
    - echo "Variables disponibles:"
    - env | grep -E "^(DOCKER|SERVER|SSH)" || echo "Sin match"
    - echo "Runner info:"
    - gitlab-runner --version
  only:
    - merge_requests
```

**⚠️ ADVERTENCIA:** Esto mostrará valores sensibles en logs si no están "Masked"

### Verificar que una variable está siendo usada

```yaml
script:
  - echo "Using Docker User: $DOCKER_USER"  # Mostrará valor
  - echo "SSH Key length: ${#SSH_PRIVATE_KEY}"  # Mostrará *** si está masked
```

### Probar SSH key localmente

```bash
# Extraer key de base64
echo "$SSH_PRIVATE_KEY" | base64 -d > /tmp/test_key.pem
chmod 600 /tmp/test_key.pem

# Intentar conexión
ssh -i /tmp/test_key.pem -o ConnectTimeout=5 root@$SERVER_HOST "echo OK"

# Limpiar
rm /tmp/test_key.pem
```

---

## Configuración en DigitalOcean

### Variables de Entorno en la App

Crear `config/.env.example` (sin secretos):

```env
# Ejemplo seguro sin valores reales

# Servidor gRPC
GRPC_HOST=0.0.0.0
GRPC_PORT=50052

# Modelo
MODEL_PATH=/app/modelo_entrenado

# MLflow
MLFLOW_TRACKING_URI=file:///app/mlruns
MLFLOW_EXPERIMENT_NAME=plant-disease

# Logging
LOG_LEVEL=INFO

# Redis (si la usas)
# REDIS_URL=redis://localhost:6379

# Base de datos
# DATABASE_URL=postgresql://user:pass@host:5432/db
```

### En el Servidor DigitalOcean

**Crear archivo `.env` real:**

```bash
ssh -i ~/.ssh/gitlab-runner.pem root@$SERVER_HOST

cd /app/proyecto_deteccion_plantas

# Copiar desde ejemplo
cp config/.env.example config/.env

# Editar valores específicos del servidor
nano config/.env

# Salvar y cerrar (Ctrl+X, Yes, Enter)
```

---

## Flujo de Variables Completo

```
┌─ Local Development
│  ├─ .env (gitignored)
│  └─ .env.example (versionado)
│
├─ GitHub/GitLab
│  ├─ .gitlab-ci.yml
│  └─ Settings → CI/CD → Variables
│     (valores sensibles aquí)
│
└─ DigitalOcean Droplet
   ├─ .env (creado en deployment)
   └─ docker-compose.yml
      (lee desde .env)
```

---

## Checklista de Seguridad

- [ ] SSH private key codificada en base64
- [ ] Docker password marcado como "Masked"
- [ ] SSH key no tiene passphrase
- [ ] .env nunca commit a git
- [ ] .env.example existe (sin valores reales)
- [ ] Todas las credenciales están en GitLab CI/CD
- [ ] after_script limpia archivos temporales
- [ ] rotación de tokens configurada (reminder)
- [ ] SSH keys solo en repos privados
- [ ] Logs de deploy no muestran secretos

---

## Referencias

- [GitLab CI/CD Variables Docs](https://docs.gitlab.com/ee/ci/variables/)
- [SSH Key Generation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
- [Docker Hub Authentication](https://docs.docker.com/docker-hub/access-tokens/)
- [Base64 Encoding Guide](https://www.base64encode.org/)

---

¡Tu secretos están seguros! 🔒
