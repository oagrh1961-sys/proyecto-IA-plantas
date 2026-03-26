# ============================================
# SCRIPT: Migrar proyecto de GitHub a GitLab
# y configurar CI/CD
# ============================================

param(
    [string]$GitLabUsername = "oagrh1961-sys",
    [string]$ProjectName = "proyecto-deteccion-plantas",
    [string]$GitLabToken = ""
)

# Colores para output
$ErrorColor = "Red"
$SuccessColor = "Green"
$InfoColor = "Cyan"
$WarningColor = "Yellow"

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor $InfoColor
Write-Host "║  MIGRACIÓN DE GITHUB A GITLAB - PROYECTO DETECCIÓN PLANTAS   ║" -ForegroundColor $InfoColor
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor $InfoColor

# ============================================
# PASO 1: Verificar que estamos en el directorio correcto
# ============================================
Write-Host "`n[1/5] Verificando ubicación del proyecto..." -ForegroundColor $InfoColor
$currentDir = Get-Location
$gitDir = Join-Path $currentDir ".git"

if (-not (Test-Path $gitDir)) {
    Write-Host "❌ Error: No estamos en un repositorio Git" -ForegroundColor $ErrorColor
    Write-Host "   Ubicación actual: $currentDir" -ForegroundColor $WarningColor
    exit 1
}
Write-Host "✅ Repositorio Git encontrado" -ForegroundColor $SuccessColor

# ============================================
# PASO 2: Obtener token de GitLab si no está configurado
# ============================================
Write-Host "`n[2/5] Configurando autenticación GitLab..." -ForegroundColor $InfoColor

if ([string]::IsNullOrEmpty($GitLabToken)) {
    Write-Host "`n⚠️  Necesitas un Personal Access Token de GitLab" -ForegroundColor $WarningColor
    Write-Host "Pasos para obtenerlo:" -ForegroundColor $InfoColor
    Write-Host "  1. Ve a: https://gitlab.com/-/user_settings/personal_access_tokens" -ForegroundColor $InfoColor
    Write-Host "  2. Clic en 'Add new token'" -ForegroundColor $InfoColor
    Write-Host "  3. Nombre: 'GitHub to GitLab Migration'" -ForegroundColor $InfoColor
    Write-Host "  4. Scopes: api, read_repository, write_repository" -ForegroundColor $InfoColor
    Write-Host "  5. Expiration: 30 días (luego cámbialo)" -ForegroundColor $InfoColor
    Write-Host "  6. Clic en 'Create personal access token'" -ForegroundColor $InfoColor
    Write-Host "`nCopia el token (solo aparece una vez):" -ForegroundColor $WarningColor
    
    $GitLabToken = Read-Host "Token (deixar en blanco para usar HTTPS sin token)"
}

if ([string]::IsNullOrEmpty($GitLabToken)) {
    $useHttps = $true
    Write-Host "⚠️  Se usará HTTPS sin token (se pedirá contraseña en git push)" -ForegroundColor $WarningColor
} else {
    $useHttps = $false
    Write-Host "✅ Token configurado" -ForegroundColor $SuccessColor
}

# ============================================
# PASO 3: Configurar remoto de Git
# ============================================
Write-Host "`n[3/5] Configurando remoto Git hacia GitLab..." -ForegroundColor $InfoColor

$gitlabUrl = "https://gitlab.com/$GitLabUsername/$ProjectName.git"

if ($useHttps) {
    $gitRemoteUrl = $gitlabUrl
} else {
    # Construir URL con token incrustado (temporal, para push automatizado)
    $gitRemoteUrl = "https://oauth2:$GitLabToken@gitlab.com/$GitLabUsername/$ProjectName.git"
}

# Obtener remoto actual
$currentRemote = git remote get-url origin 2>$null
Write-Host "  Remote actual: $currentRemote" -ForegroundColor $InfoColor

# Cambiar remoto
git remote remove origin 2>$null
git remote add origin $gitRemoteUrl

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Remoto configurado: $gitlabUrl" -ForegroundColor $SuccessColor
} else {
    Write-Host "❌ Error configurando remoto Git" -ForegroundColor $ErrorColor
    exit 1
}

# ============================================
# PASO 4: Push a GitLab
# ============================================
Write-Host "`n[4/5] Empujando código a GitLab..." -ForegroundColor $InfoColor
Write-Host "  Esto puede tardar unos minutos (descargando historial completo)..." -ForegroundColor $WarningColor

$logOutput = git push -u origin main 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Código empujado exitosamente a GitLab" -ForegroundColor $SuccessColor
} else {
    # Intentar con master como fallback
    Write-Host "  Intentando con rama 'master'..." -ForegroundColor $InfoColor
    $logOutput = git push -u origin master 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Código empujado exitosamente a GitLab" -ForegroundColor $SuccessColor
    } else {
        Write-Host "❌ Error en git push:" -ForegroundColor $ErrorColor
        Write-Host $logOutput -ForegroundColor $ErrorColor
        Write-Host "`nTips:" -ForegroundColor $InfoColor
        Write-Host "  - ¿El proyecto existe en GitLab? (crear en https://gitlab.com/projects/new)" -ForegroundColor $InfoColor
        Write-Host "  - ¿El token tiene permisos 'write_repository'?" -ForegroundColor $InfoColor
        exit 1
    }
}

# ============================================
# PASO 5: Mostrar resumen y próximos pasos
# ============================================
Write-Host "`n[5/5] Configuración completada" -ForegroundColor $InfoColor

Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor $SuccessColor
Write-Host "║                   ✅ MIGRACIÓN EXITOSA                        ║" -ForegroundColor $SuccessColor
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor $SuccessColor

Write-Host "`n📍 Tu proyecto está en: https://gitlab.com/$GitLabUsername/$ProjectName" -ForegroundColor $SuccessColor

Write-Host "`n⚠️  PRÓXIMOS PASOS - Configurar Variables de CI/CD:" -ForegroundColor $WarningColor
Write-Host "`n1. Ve a GitLab:" -ForegroundColor $InfoColor
Write-Host "   https://gitlab.com/$GitLabUsername/$ProjectName/-/settings/ci_cd" -ForegroundColor $SuccessColor

Write-Host "`n2. Expande 'Variables' y añade estas variables secretas:" -ForegroundColor $InfoColor

$variables = @{
    "DOCKER_USER" = @{
        value = "oagrh1961"
        description = "Usuario de Docker Hub"
    }
    "DOCKER_PASSWORD" = @{
        value = "[Tu token/contraseña de Docker Hub]"
        description = "Token de Docker Hub (obtener en https://hub.docker.com/settings/security)"
    }
    "SERVER_HOST" = @{
        value = "[IP de tu Droplet de DigitalOcean]"
        description = "IP del servidor de producción"
    }
    "SSH_PRIVATE_KEY" = @{
        value = "[Tu clave privada SSH base64]"
        description = "SSH key para producción (en base64)"
    }
    "STAGING_SERVER_HOST" = @{
        value = "[IP de tu Droplet staging]"
        description = "IP del servidor de staging (opcional)"
    }
    "SSH_PRIVATE_KEY_STAGING" = @{
        value = "[Tu clave privada SSH base64]"
        description = "SSH key para staging (en base64, opcional)"
    }
}

foreach ($varName in $variables.Keys) {
    $var = $variables[$varName]
    Write-Host "`n   ▸ Variable name: $varName" -ForegroundColor $InfoColor
    Write-Host "     Value: $($var.value)" -ForegroundColor $WarningColor
    Write-Host "     Descripción: $($var.description)" -ForegroundColor $InfoColor
    
    if ($varName -like "*PASSWORD*" -or $varName -like "*KEY*") {
        Write-Host "     ⚠️  Marcar como 'Masked'" -ForegroundColor $WarningColor
    }
}

Write-Host "`n3. Para obtener SSH key en base64 (desde tu máquina):" -ForegroundColor $InfoColor
Write-Host "   powershell -Command `"[Convert]::ToBase64String([IO.File]::ReadAllBytes('`$env:USERPROFILE\.ssh\id_rsa'))`"" -ForegroundColor $SuccessColor

Write-Host "`n4. Luego que tengas todas las variables, haz un pequeño commit:" -ForegroundColor $InfoColor
Write-Host "   git add README.md && git commit -m 'trigger: CI/CD pipeline' && git push" -ForegroundColor $SuccessColor

Write-Host "`n5. Ve a la sección 'CI/CD' en GitLab para ver tu pipeline:" -ForegroundColor $InfoColor
Write-Host "   https://gitlab.com/$GitLabUsername/$ProjectName/-/pipelines" -ForegroundColor $SuccessColor

Write-Host "`n📚 Documentación disponible en tu proyecto:" -ForegroundColor $InfoColor
Write-Host "   - docs/CI_CD_GITLAB_DIGITALOCEAN.md" -ForegroundColor $SuccessColor
Write-Host "   - docs/VARIABLES_SECRETOS.md" -ForegroundColor $SuccessColor
Write-Host "   - docs/MAKEFILE_GUIDE.md" -ForegroundColor $SuccessColor

Write-Host "`n✅ ¡Todo listo! La migración y configuración están completas." -ForegroundColor $SuccessColor
