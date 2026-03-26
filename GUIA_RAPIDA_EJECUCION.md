# 🚀 GUÍA RÁPIDA DE EJECUCIÓN - Migración GitLab + CI/CD

**Sigue EXACTAMENTE estos pasos en este ORDEN. Tiempo total: ~20 minutos.**

---

## FASE 1: Preparación (5 minutos)

### ✅ Paso 1: Obtener Personal Access Token de GitLab

```
1. Ve a: https://gitlab.com/-/user_settings/personal_access_tokens
2. Haz clic en "Add new token"
3. Rellena:
   - Token name: "GitHub to GitLab Migration"
   - Scopes: 
     ✓ api
     ✓ read_repository
     ✓ write_repository
4. Clic en "Create personal access token"
5. COPIA el token (solo aparece UNA VEZ)
```

**Guarda el token aquí temporalmente:**
```
_____________________________________________
```

---

## FASE 2: Migración Automática (5 minutos)

### ✅ Paso 2: Ejecutar script de migración

**En PowerShell (como administrador):**

```powershell
# 1. Navega a tu proyecto
cd c:\Users\oagrh\proyecto_deteccion_plantas

# 2. Permite ejecutar scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# 3. Ejecuta el script de migración
.\scripts\migrate-to-gitlab.ps1

# 4. Cuando pida el token, pega el que obtuviste en el Paso 1
```

**Espera a que el script termine - debe decir:**
```
╔══════════════════════════════════════════════════════════════╗
║                   ✅ MIGRACIÓN EXITOSA                        ║
╚══════════════════════════════════════════════════════════════╝
```

---

## FASE 3: Configuración de Variables (8 minutos)

### ✅ Paso 3a: Obtener credenciales Docker Hub

**En el navegador:**

```
1. Ve a: https://hub.docker.com/settings/security
2. Haz clic en "New Access Token"
3. Nombre: "gitlab-cicd"
4. Clic en "Generate"
5. Copia el token
```

**Guarda aquí:**
```
DOCKER_PASSWORD: _____________________________________________
```

### ✅ Paso 3b: Obtener clave SSH en base64

**En PowerShell:**

```powershell
# Copiar clave SSH a portapapeles (codificada)
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$env:USERPROFILE\.ssh\id_rsa")) | Set-Clipboard
Write-Host "✅ Clave SSH copiada al portapapeles en base64"
```

**Pega aquí (primeros 50 caracteres para verificar):**
```
LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVk...
```

---

## FASE 4: Configurar Variables en GitLab (5 minutos)

### ✅ Paso 4: Ir a GitLab settings

**En el navegador:**

```
1. Ve a: https://gitlab.com/oagrh1961-sys/proyecto-deteccion-plantas
2. Haz clic en Settings (engranaje abajo a la izquierda)
3. En el menú izquierdo: CI/CD
4. Expande "Variables"
```

**URL directa:**
```
https://gitlab.com/oagrh1961-sys/proyecto-deteccion-plantas/-/settings/ci_cd
```

### ✅ Paso 5: Añadir cada variable

Haz clic en "Add Variable" y rellena EXACTAMENTE así:

#### Variable 1️⃣: DOCKER_USER
```
Key:         DOCKER_USER
Value:       oagrh1961
Masked:      ❌ (NO marcar)
Protected:   ❌ (NO marcar)
```
→ Haz clic en "Add variable"

#### Variable 2️⃣: DOCKER_PASSWORD ⭐ IMPORTANTE
```
Key:         DOCKER_PASSWORD
Value:       [pega el token de Docker Hub]
Masked:      ✅ (SÍ marcar)
Protected:   ✅ (SÍ marcar)
```
→ Haz clic en "Add variable"

#### Variable 3️⃣: SERVER_HOST
```
Key:         SERVER_HOST
Value:       [Tu IP de DigitalOcean, ej: 143.198.123.45]
Masked:      ❌ (NO marcar)
Protected:   ❌ (NO marcar)
```
→ Haz clic en "Add variable"

#### Variable 4️⃣: SSH_PRIVATE_KEY ⭐ IMPORTANTE
```
Key:         SSH_PRIVATE_KEY
Value:       [pega la clave SSH del Paso 3b - está en tu clipboard]
Masked:      ✅ (SÍ marcar)
Protected:   ✅ (SÍ marcar)
```
→ Haz clic en "Add variable"

---

## FASE 5: Verificación (2 minutos)

### ✅ Paso 6: Disparar el pipeline

**En PowerShell:**

```powershell
# Navega al proyecto
cd c:\Users\oagrh\proyecto_deteccion_plantas

# Crea un commit vacío para disparar el pipeline
git commit --allow-empty -m "test: trigger CI/CD pipeline"

# Empuja el commit
git push origin main
```

### ✅ Paso 7: Ver el pipeline en acción

**En el navegador:**

```
1. Ve a: https://gitlab.com/oagrh1961-sys/proyecto-deteccion-plantas/-/pipelines
2. Verás tu nuevo pipeline
3. Espera a que termine la etapa TEST (debe pasar en verde ✅)
```

**Estados esperados:**
```
✅ TEST stage          → Debe pasar automáticamente
✅ BUILD stage         → Debe pasar automáticamente (si TEST pasó)
🔘 DEPLOY stage        → Mostrado, pero requiere clic manual
```

---

## 🎉 ¡LISTO!

Si llegaste aquí y todo está en verde ✅, tu CI/CD está funcionando correctamente.

### Próximo: Configurar DigitalOcean (cuando estés listo)

Refer a: `docs/CI_CD_GITLAB_DIGITALOCEAN.md` - Sección 2: "DigitalOcean Setup"

---

## 🆘 Si algo falla

### Error 1: "Unauthorized" en DOCKER_PASSWORD
- ❌ El token de Docker es inválido o expirado
- ✅ Solución: genera un nuevo token y actualiza en Variables

### Error 2: "ssh: connect to host refused" en DEPLOY
- ❌ Aún no has creado el Droplet de DigitalOcean
- ✅ Solución: TEST y BUILD deben pasar sin problemas, DEPLOY falla hasta que tengas el servidor

### Error 3: "pytest: command not found" en TEST
- ❌ Falta pytest en dependencias
- ✅ Solución: añade pytest a `pyproject.toml` y haz push nuevamente

### Error 4: Clave SSH "Permission denied"
- ❌ La clave SSH en formato base64 está mal
- ✅ Solución: vuelve a generar usando el comando PowerShell del Paso 3b

---

## Checklist Final

- [ ] PAT de GitLab creado
- [ ] Script migrate-to-gitlab.ps1 ejecutado exitosamente
- [ ] Código en GitLab.com
- [ ] DOCKER_USER configurado en GitLab
- [ ] DOCKER_PASSWORD configurado y "Masked"
- [ ] SERVER_HOST configurado 
- [ ] SSH_PRIVATE_KEY configurado y "Masked"
- [ ] Pipeline TEST pasó ✅
- [ ] Pipeline BUILD pasó ✅
- [ ] Imagen visible en Docker Hub

---

**¿Dudas?** Lee completo en:
- `docs/CONFIGURACION_VARIABLES_GITLAB.md`
- `docs/CI_CD_GITLAB_DIGITALOCEAN.md`
