# 🔐 Configuración de Variables CI/CD en GitLab

**Este documento te guía paso a paso para configurar las variables secretas necesarias para que el pipeline funcione correctamente.**

---

## Tabla Rápida de Acceso

| Paso | Acción | Tiempo |
|------|--------|--------|
| 1 | Obtener datos de DigitalOcean | 2 min |
| 2 | Obtener token de Docker Hub | 2 min |
| 3 | Generar clave SSH en base64 | 3 min |
| 4 | Configurar variables en GitLab | 5 min |
| 5 | Verificar pipeline | 2 min |

---

## Paso 1: Información de DigitalOcean

### Obtener IP del servidor

```bash
# En DigitalOcean Dashboard:
# 1. Ve a "Droplets"
# 2. Haz clic en tu Droplet
# 3. Copia la IPv4 address (ej: 143.198.123.45)
```

**Variable para GitLab:**
```
SERVER_HOST = 143.198.123.45
```

---

## Paso 2: Autenticación Docker Hub

### Opción A: Usar token (RECOMENDADO)

```bash
# 1. Ve a: https://hub.docker.com/settings/security
# 2. Haz clic en "New Access Token"
# 3. Nombre: "gitlab-cicd" 
# 4. Clic en "Generate"
# 5. Copia el token
```

**Variables para GitLab:**
```
DOCKER_USER = oagrh1961
DOCKER_PASSWORD = dckr_pat_xxxxxxxxxxxxx
```

### Opción B: Usar contraseña de Docker Hub

```bash
DOCKER_USER = oagrh1961
DOCKER_PASSWORD = tu-contraseña-docker
```

> ⚠️ **Seguridad**: Los tokens son más seguros que contraseñas.

---

## Paso 3: Clave SSH para Servidor

### Generar o usar clave existente

#### 3a) Si YA TIENES una clave SSH en tu máquina:

**En PowerShell (Windows):**
```powershell
# Mostrar la clave actual (sin codificar - solo para ver)
Get-Content $env:USERPROFILE\.ssh\id_rsa

# Codificar en base64:
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$env:USERPROFILE\.ssh\id_rsa")) | Set-Clipboard
Write-Host "✅ Clave copiada al portapapeles en base64"
```

#### 3b) Si NO TIENES una clave SSH:

**Crear nueva clave SSH:**
```bash
# En PowerShell o terminal Git Bash:
ssh-keygen -t rsa -b 4096 -f $env:USERPROFILE\.ssh\id_rsa -N ""

# Luego usar el comando del punto 3a para codificar
```

**Variable para GitLab:**
```
SSH_PRIVATE_KEY = [pegar código base64 aquí]
```

---

## Paso 4: Configurar Variables en GitLab

### 4.1 Acceder a Variables CI/CD

```
Tu proyecto en GitLab
  ↓
Settings (Engranaje) 
  ↓
CI/CD 
  ↓
Variables (expandir)
```

**URL directa:** 
```
https://gitlab.com/oagrh1961-sys/proyecto-deteccion-plantas/-/settings/ci_cd
```

### 4.2 Añadir cada variable

**Variable 1: DOCKER_USER**
- **Key:** `DOCKER_USER`
- **Value:** `oagrh1961`
- **Write protect branch:** NO
- **Masked:** NO
- **Expand variables:** SÍ

**Variable 2: DOCKER_PASSWORD** ⭐
- **Key:** `DOCKER_PASSWORD`
- **Value:** `[tu token de Docker Hub]`
- **Write protect branch:** SÍ (recomendado)
- **Masked:** ✅ **SÍ (IMPORTANTE)**
- **Expand variables:** SÍ

**Variable 3: SERVER_HOST**
- **Key:** `SERVER_HOST`
- **Value:** `143.198.123.45` (reemplazar con tu IP)
- **Write protect branch:** NO
- **Masked:** NO
- **Expand variables:** SÍ

**Variable 4: SSH_PRIVATE_KEY** ⭐
- **Key:** `SSH_PRIVATE_KEY`
- **Value:** `[código base64 de tu clave SSH]`
- **Write protect branch:** SÍ (recomendado)
- **Masked:** ✅ **SÍ (IMPORTANTE)**
- **Expand variables:** SÍ

### 4.3 Variables Opcionales (para staging)

Si planeas usar staging (rama develop):

**Variable 5: STAGING_SERVER_HOST**
- **Key:** `STAGING_SERVER_HOST`
- **Value:** `[IP de tu servidor staging]`
- **Masked:** NO

**Variable 6: SSH_PRIVATE_KEY_STAGING**
- **Key:** `SSH_PRIVATE_KEY_STAGING`
- **Value:** `[código base64 en staging]`
- **Masked:** ✅ **SÍ**

---

## Paso 5: Verificar la Configuración

### 5.1 Trigger del Pipeline

Haz un pequeño commit para disparar el pipeline:

```bash
# Opción A: Modificar un archivo existente
echo "# Pipeline test" >> README.md
git add README.md
git commit -m "test: trigger CI/CD pipeline"
git push origin main

# Opción B: Crear un commit vacío
git commit --allow-empty -m "test: trigger CI/CD pipeline"
git push origin main
```

### 5.2 Ver estado del pipeline

```
GitLab → Tu proyecto
  ↓
CI/CD 
  ↓
Pipelines
```

**URL directa:**
```
https://gitlab.com/oagrh1961-sys/proyecto-deteccion-plantas/-/pipelines
```

### 5.3 Verificación por etapa

#### Etapa TEST (Automática)
- ✅ Debe correr automáticamente
- ❌ Si falla: revisar output, probablemente falta alguna dependencia en pyproject.toml

#### Etapa BUILD (Automática si TEST pasa)
- ✅ Debe empujar imagen a Docker Hub
- ⚠️ Tarda ~3-5 minutos
- ❌ Si falla: revisar DOCKER_USER y DOCKER_PASSWORD

#### Etapa DEPLOY (Manual)
- 🔘 Requiere clic en botón "Deploy" en GitLab
- ⚠️ Tarda ~2 minutos
- ❌ Si falla: revisar SERVER_HOST y SSH_PRIVATE_KEY

---

## Checklist de Verificación

- [ ] GitLab PAT creado y repositorio migrado
- [ ] DOCKER_USER configurado
- [ ] DOCKER_PASSWORD configurado y marcado como "Masked"
- [ ] SERVER_HOST añadido (IP de DigitalOcean)
- [ ] SSH_PRIVATE_KEY configurado en base64 y marcado como "Masked"
- [ ] Pipeline intentado (commit + push a main)
- [ ] Stage TEST completado exitosamente
- [ ] Stage BUILD completado exitosamente
- [ ] Imagen visible en Docker Hub
- [ ] Stage DEPLOY manualmente ejecutado

---

## 🆘 Troubleshooting

### Error: "DOCKER_PASSWORD is masked and cannot be printed"
- ✅ Normal, significa que está bien configurado
- Revisa los logs para ver si falla la autenticación

### Error en TEST: "pytest: command not found"
- Falta instalar pytest en pyproject.toml
- Añade en la sección [tool.uv] o [tool.poetry]

### Error en BUILD: "unauthorized: authentication required"
- DOCKER_PASSWORD es incorrecto o expirado
- Genera un nuevo token en Docker Hub

### Error en DEPLOY: "ssh: connect to host ... port 22: Connection refused"
- SSH_PRIVATE_KEY no es válida
- Verificar que se generó correctamente en base64
- Verificar que la clave pública está en el servidor

### Error en DEPLOY: "docker-compose: command not found"
- Docker Compose no está instalado en el servidor
- Ejecutar: `curl -s https://raw.githubusercontent.com/...` en el servidor

---

## 📚 Recursos Adicionales

- [GitLab CI/CD Variables](https://docs.gitlab.com/ee/ci/variables/)
- [Docker Hub Security](https://docs.gitlab.com/ee/ci/variables/)
- [SSH Key Management](https://docs.gitlab.com/ee/user/ssh.html)

---

**¿Problemas?** Revisa:
1. `docs/CI_CD_GITLAB_DIGITALOCEAN.md` (guía completa)
2. Los logs del pipeline en GitLab
3. `docs/EMERGENCY_DEPLOYMENT.md` para troubleshooting avanzado
