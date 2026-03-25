# Makefile para proyecto_deteccion_plantas
# Targets: test, build, run, clean, help

.PHONY: help install test build run docker-build docker-up docker-down clean lint format

# Variables
PYTHON := python
PIP := pip
DOCKER_IMAGE := proyecto-deteccion-plantas
DOCKER_TAG := latest

# ============================================
# 📚 HELP - Mostrar todos los targets
# ============================================
help:
	@echo "======================================"
	@echo "  Proyecto Detección de Plantas"
	@echo "======================================"
	@echo ""
	@echo "📦 Instalación y Setup:"
	@echo "  make install        - Instalar dependencias"
	@echo "  make setup         - Setup completo (install + pre-commit)"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test          - Ejecutar tests con pytest"
	@echo "  make test-verbose  - Tests con output detallado"
	@echo "  make coverage      - Tests con reporte de cobertura"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-build  - Construir imagen Docker"
	@echo "  make docker-up     - Iniciar contenedores"
	@echo "  make docker-down   - Detener contenedores"
	@echo "  make docker-logs   - Ver logs de contenedores"
	@echo ""
	@echo "💻 Desarrollo:"
	@echo "  make run           - Ejecutar servidor localmente"
	@echo "  make app           - Ejecutar app Streamlit"
	@echo "  make lint          - Verificar código con ruff"
	@echo "  make format        - Formatear código (ruff)"
	@echo ""
	@echo "🧹 Limpieza:"
	@echo "  make clean         - Limpiar archivos temporales"
	@echo "  make clean-docker  - Limpiar imágenes/contenedores Docker"
	@echo ""

# ============================================
# 📦 INSTALL - Instalar dependencias
# ============================================
install:
	@echo "📦 Instalando dependencias..."
	@if command -v uv > /dev/null; then \
		echo "✓ Usando UV como gestor de paquetes"; \
		uv sync; \
	else \
		echo "✓ Usando pip como gestor de paquetes"; \
		$(PIP) install -q -e .; \
	fi
	@echo "✅ Dependencias instaladas"

setup: install
	@echo "🔧 Setup completo..."
	@echo "✅ Setup completado"

# ============================================
# 🧪 TEST - Ejecutar tests
# ============================================
test:
	@echo "🧪 Ejecutando tests..."
	@echo ""
	pytest tests/ -q --tb=short
	@echo ""
	@echo "✅ Tests completados"

test-verbose:
	@echo "🧪 Ejecutando tests (verbose)..."
	@echo ""
	pytest tests/ -v --tb=short
	@echo ""

coverage:
	@echo "📊 Ejecutando tests con cobertura..."
	@echo ""
	pytest tests/ \
		--cov=src \
		--cov-report=html \
		--cov-report=term-missing \
		--cov-report=xml
	@echo ""
	@echo "📈 Reporte de cobertura generado en htmlcov/index.html"
	@echo "✅ Coverage completado"

# ============================================
# 🐳 DOCKER - Construir y ejecutar contenedores
# ============================================
docker-build:
	@echo "🐳 Construyendo imagen Docker..."
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	@echo "✅ Imagen construida: $(DOCKER_IMAGE):$(DOCKER_TAG)"

docker-up:
	@echo "🚀 Iniciando contenedores..."
	cd config && docker-compose up -d
	@echo ""
	@echo "📍 Servicios disponibles:"
	@echo "  - App (Streamlit): http://localhost:8501"
	@echo "  - Servidor gRPC: localhost:50052"
	@echo "  - MLflow UI: http://localhost:5000"
	@echo "  - Métricas Prometheus: http://localhost:9000/metrics"
	@echo ""
	@echo "✅ Contenedores iniciados"

docker-down:
	@echo "⛔ Deteniendo contenedores..."
	cd config && docker-compose down
	@echo "✅ Contenedores detenidos"

docker-logs:
	@echo "📋 Logs de contenedores..."
	cd config && docker-compose logs -f

docker-clean:
	@echo "🧹 Limpiando imágenes y contenedores..."
	docker-compose -f config/docker-compose.yml down -v
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) || true
	@echo "✅ Limpieza completada"

# ============================================
# 💻 DEVELOPMENT - Ejecutar en modo desarrollo
# ============================================
run:
	@echo "🚀 Ejecutando servidor gRPC..."
	python -m src.server

app:
	@echo "🎨 Ejecutando app Streamlit..."
	streamlit run src/app.py

cli:
	@echo "💻 Ejecutando CLI..."
	python -m src.cli

# ============================================
# 🔍 CODE QUALITY - Lint y Format
# ============================================
lint:
	@echo "🔍 Verificando código con ruff..."
	ruff check src/ tests/
	@echo "✅ Lint completado"

format:
	@echo "✨ Formateando código..."
	ruff format src/ tests/
	@echo "✅ Formato completado"

format-check:
	@echo "🔍 Verificando formato..."
	ruff format --check src/ tests/

# ============================================
# 🧹 CLEAN - Limpiar archivos temporales
# ============================================
clean:
	@echo "🧹 Limpiando archivos temporales..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .coverage -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	@echo "✅ Limpieza completada"

# ============================================
# CI/CD - Targets para GitLab CI/CD
# ============================================
.PHONY: ci-test ci-build

ci-test: clean install test
	@echo "✅ CI Test pipeline completado"

ci-build: docker-build
	@echo "✅ CI Build pipeline completado"

# ============================================
# 🔗 GIT - Utilidades de git
# ============================================
.PHONY: git-status git-log

git-status:
	@git status

git-log:
	@git log --oneline -10

# ============================================
# 📊 INFO - Mostrar información del proyecto
# ============================================
.PHONY: info

info:
	@echo ""
	@echo "======================================"
	@echo "  Información del Proyecto"
	@echo "======================================"
	@echo ""
	@echo "Python:"
	@$(PYTHON) --version
	@echo ""
	@echo "Docker:"
	@docker --version
	@echo ""
	@echo "Docker Compose:"
	@docker-compose --version
	@echo ""
	@echo "Git:"
	@git --version
	@echo ""
	@echo "Rama actual:"
	@git branch --show-current
	@echo ""
	@echo "Cambios sin commit:"
	@git status --short || echo "Clean"
	@echo ""
