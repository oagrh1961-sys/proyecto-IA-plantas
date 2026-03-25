#!/bin/bash

# ============================================================
# Script de Instalación Automática de GitLab Runner
# Para: DigitalOcean Droplet (Ubuntu 24.04 LTS)
#
# Uso:
#   ssh -i key.pem root@droplet-ip
#   curl -fsSL https://raw.githubusercontent.com/... | bash
#   O descargar y ejecutar: bash setup-runner.sh
# ============================================================

set -e  # Salir si hay error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# ============================================================
# 1. VALIDACIONES PREVIAS
# ============================================================

log_info "Validando requisitos del sistema..."

# Verificar que es Linux
if [[ ! "$OSTYPE" == "linux-gnu"* ]]; then
    log_error "Este script solo funciona en Linux"
    exit 1
fi

# Verificar que es root
if [[ $EUID -ne 0 ]]; then
    log_error "Este script debe ejecutarse como root (sudo)"
    exit 1
fi

# Verificar conexión a internet
if ! ping -c 1 8.8.8.8 &> /dev/null; then
    log_error "No hay conexión a internet"
    exit 1
fi

log_success "Sistema válido (Linux, root, internet OK)"

# ============================================================
# 2. ACTUALIZAR SISTEMA
# ============================================================

log_info "Actualizando sistema operativo..."
apt-get update -qq
apt-get upgrade -y -qq
log_success "Sistema actualizado"

# ============================================================
# 3. INSTALAR DEPENDENCIAS BÁSICAS
# ============================================================

log_info "Instalando dependencias..."
apt-get install -y -qq \
    curl \
    wget \
    git \
    ssh \
    openssh-server \
    ca-certificates \
    gnupg \
    lsb-release \
    ubuntu-keyring

log_success "Dependencias instaladas"

# ============================================================
# 4. VERIFICAR/INSTALAR DOCKER
# ============================================================

if command -v docker &> /dev/null; then
    log_success "Docker ya está instalado"
    docker --version
else
    log_info "Instalando Docker..."
    
    # Agregar repositorio oficial de Docker
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Iniciar Docker
    systemctl start docker
    systemctl enable docker
    
    log_success "Docker instalado"
    docker --version
fi

# ============================================================
# 5. INSTALAR DOCKER COMPOSE (si no viene con plugin)
# ============================================================

if ! command -v docker-compose &> /dev/null; then
    log_info "Instalando Docker Compose..."
    
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d'"' -f4)
    
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    
    chmod +x /usr/local/bin/docker-compose
    
    log_success "Docker Compose instalado"
    docker-compose --version
fi

# ============================================================
# 6. CREAR USUARIO PARA LA APP
# ============================================================

log_info "Configurando usuario no-root..."

if id "appuser" &>/dev/null; then
    log_warning "Usuario 'appuser' ya existe"
else
    useradd -m -s /bin/bash appuser
    log_success "Usuario 'appuser' creado"
fi

# Agregar a grupo docker
usermod -aG docker appuser

# ============================================================
# 7. CREAR DIRECTORIOS DE LA APP
# ============================================================

log_info "Creando estructura de directorios..."

mkdir -p /app/proyecto_deteccion_plantas/{config,src,scripts,docs,tests,modelo_entrenado,mlruns}

chown -R appuser:appuser /app/proyecto_deteccion_plantas
chmod -R 755 /app/proyecto_deteccion_plantas

log_success "Directorios creados en /app/proyecto_deteccion_plantas"

# ============================================================
# 8. INSTALAR GITLAB RUNNER
# ============================================================

log_info "Instalando GitLab Runner..."

# Agregar repositorio de GitLab
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh -o /tmp/runner-install.sh
bash /tmp/runner-install.sh

# Instalar
apt-get install -y -qq gitlab-runner

# Verificar instalación
gitlab-runner --version
log_success "GitLab Runner instalado"

# Agregar gitlab-runner al grupo docker
usermod -aG docker gitlab-runner

# ============================================================
# 9. CREAR ARCHIVO DE CONFIGURACIÓN
# ============================================================

log_info "Preparando configuración de GitLab Runner..."

cat > /etc/gitlab-runner/config.toml << 'EOF'
concurrent = 2
check_interval = 0

[session_server]
  session_timeout = 1800
EOF

log_success "Configuración de runner preparada"

# ============================================================
# 10. CREAR SCRIPT PARA REGISTRO FÁCIL
# ============================================================

cat > /tmp/register-runner.sh << 'SCRIPT'
#!/bin/bash

echo ""
echo "======================================"
echo "  Registro de GitLab Runner"
echo "======================================"
echo ""
echo "Por favor proporciona los siguientes datos:"
echo ""

read -p "GitLab URL (https://gitlab.com): " GITLAB_URL
GITLAB_URL=${GITLAB_URL:-https://gitlab.com}

read -p "GitLab registration token: " GITLAB_TOKEN

read -p "Descripción del runner (ej: proyecto-plantas-runner): " RUNNER_DESCRIPTION
RUNNER_DESCRIPTION=${RUNNER_DESCRIPTION:-project-runner}

read -p "Tags (separados por coma, ej: production,docker): " RUNNER_TAGS
RUNNER_TAGS=${RUNNER_TAGS:-docker}

read -p "Docker image (docker:latest): " DOCKER_IMAGE
DOCKER_IMAGE=${DOCKER_IMAGE:-docker:latest}

echo ""
echo "Registrando runner..."
echo ""

gitlab-runner register \
    --non-interactive \
    --url "$GITLAB_URL" \
    --registration-token "$GITLAB_TOKEN" \
    --executor docker \
    --docker-image "$DOCKER_IMAGE" \
    --docker-tlsverify=false \
    --docker-volumes /var/run/docker.sock:/var/run/docker.sock \
    --Docker-privileged \
    --description "$RUNNER_DESCRIPTION" \
    --tag-list "$RUNNER_TAGS" \
    --docker-pull-policy if-not-present

echo ""
echo "✅ Runner registrado exitosamente!"
echo ""
echo "Próximos pasos:"
echo "1. Ir a GitLab → Tu Proyecto → Settings → CI/CD → Runners"
echo "2. Verificar que el runner aparece como ✅ activo"
echo "3. Hacer un push para triggear el pipeline"
echo ""

SCRIPT

chmod +x /tmp/register-runner.sh
log_success "Script de registro creado"

# ============================================================
# 11. LIMPIAR
# ============================================================

rm -f /tmp/runner-install.sh

# ============================================================
# 12. VERIFICACIÓN FINAL
# ============================================================

log_info "Verificando instalación..."

echo ""
echo "Sistema:"
lsb_release -d

echo ""
echo "Docker:"
docker --version

echo ""
echo "Docker Compose:"
docker-compose --version

echo ""
echo "GitLab Runner:"
gitlab-runner --version

# ============================================================
# 13. INSTRUCCIONES FINALES
# ============================================================

log_success "✨ Instalación completada exitosamente"

cat << 'INFO'

====================================
  Próximos Pasos
====================================

1️⃣  REGISTRAR EL RUNNER:
   bash /tmp/register-runner.sh
   
   O manualmente:
   gitlab-runner register

   Detalles para el registro:
   • URL: https://gitlab.com
   • Token: (obtener de GitLab →  Settings → CI/CD → Runners)
   • Executor: docker
   • Docker Image: docker:latest
   • Tags: production,docker

2️⃣  INICIAR EL RUNNER:
   systemctl start gitlab-runner
   systemctl enable gitlab-runner

3️⃣  VERIFICAR ESTADO:
   gitlab-runner verify
   gitlab-runner list

4️⃣  VER LOGS:
   journalctl -u gitlab-runner -f

5️⃣  DESCARGAR CODE:
   cd /app/proyecto_deteccion_plantas
   git clone https://gitlab.com/tu-usuario/proyecto-deteccion-plantas.git .

6️⃣  CONFIGURAR CREDENCIALES DE DOCKER:
   docker login
   Username: tu-usuario-docker
   Password: tu-token-docker

====================================

ℹ️  Documentación:
   • GitLab Runner: https://docs.gitlab.com/runner/
   • Troubleshooting: /docs/CI_CD_GITLAB_DIGITALOCEAN.md

ℹ️  Ubicaciones importantes:
   • App: /app/proyecto_deteccion_plantas
   • Config Runner: /etc/gitlab-runner/config.toml
   • Logs: journalctl -u gitlab-runner

¡Tu servidor está listo para CI/CD! 🚀

====================================

INFO

echo ""
log_success "Server setup completado correctamente"

