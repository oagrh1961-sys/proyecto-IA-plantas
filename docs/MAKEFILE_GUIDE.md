# 🏭 Documentación de Makefile

Guía rápida de los comandos disponibles en tu `Makefile`.

## 🚀 Inicio Rápido

```bash
# Ver todos los comandos disponibles
make help

# Instalar dependencias
make install

# Ejecutar tests
make test

# Construir imagen Docker
make docker-build

# Iniciar contenedores
make docker-up
```

---

## 📋 Comandos Disponibles

### 📦 Instalación y Setup

#### `make install`
Instala todas las dependencias del proyecto.

```bash
make install
```

**Qué hace:**
- ✅ Detecta si tienes UV o pip
- ✅ Instala dependencias desde `pyproject.toml`
- ✅ Crea archivo `.venv` (virtual environment)

**Cuándo usar:**
- Primera vez que clonas el proyecto
- Después de cambios en `pyproject.toml`

#### `make setup`
Setup completo del proyecto (install + pre-commit).

```bash
make setup
```

---

### 🧪 Testing

#### `make test`
Ejecutar tests rápidamente.

```bash
make test
```

**Salida esperada:**
```
🧪 Ejecutando tests...

tests/test_model.py::test_model_loads PASSED
tests/test_model.py::test_prediction PASSED

✅ Tests completados
```

#### `make test-verbose`
Tests con output detallado.

```bash
make test-verbose
```

**Mostrará:**
- Cada test ejecutándose
- Tiempo de ejecución
- Detalles de errores

#### `make coverage`
Tests con reporte de cobertura de código.

```bash
make coverage
```

**Genera:**
- `htmlcov/index.html` - Reporte visual
- `coverage.xml` - formato de GitLab
- Output en terminal

**Qué mira:**
- Qué porcentaje del código está cubierto por tests
- Qué líneas no tienen test

---

### 🐳 Docker

#### `make docker-build`
Construir imagen Docker.

```bash
make docker-build
```

**Equivalente a:**
```bash
docker build -t proyecto-deteccion-plantas:latest .
```

**Tiempo:** 5-10 min (primera vez), <1 min (con cache)

#### `make docker-up`
Iniciar todos los contenedores.

```bash
make docker-up
```

**Inicia:**
- Servidor gRPC (puerto 50052)
- App Streamlit (puerto 8501)
- MLflow UI (puerto 5000)

**Acceso a servicios:**
```
App:           http://localhost:8501
Métricas:      http://localhost:9000/metrics
MLflow:        http://localhost:5000
gRPC:          localhost:50052
```

#### `make docker-down`
Detener contenedores.

```bash
make docker-down
```

#### `make docker-logs`
Ver logs en vivo de los contenedores.

```bash
make docker-logs
```

**Ctrl+C** para salir

#### `make docker-clean`
Limpiar imágenes y contenedores completamente.

```bash
make docker-clean
```

**⚠️ Advertencia:** Elimina todo, incluso datos en volúmenes

---

### 💻 Desarrollo

#### `make run`
Ejecutar servidor gRPC localmente.

```bash
make run
```

**Inicia:**
- Servidor en puerto 50052
- Métricas en puerto 9000
- Logs en consola

**Ctrl+C** para detener

#### `make app`
Ejecutar interfaz Streamlit.

```bash
make app
```

**Abre automáticamente:**
- http://localhost:8501

**Ctrl+C** para detener

#### `make cli`
Ejecutar interfaz de línea de comandos.

```bash
make cli
```

---

### 🔍 Code Quality

#### `make lint`
Verificar código con ruff.

```bash
make lint
```

**Verifica:**
- Errores de sintaxis
- Imports no usados
- Estilos no recomendados

#### `make format`
Formatear código automáticamente.

```bash
make format
```

**Cambia:**
- Indentación inconsistente
- Espacios extra
- Líneas muy largas

#### `make format-check`
Verificar si el código está formateado.

```bash
make format-check
```

**No modifica**, solo reporta

---

### 🧹 Limpieza

#### `make clean`
Limpiar archivos temporales.

```bash
make clean
```

**Elimina:**
- `__pycache__/` directorios
- `.pytest_cache/`
- `.coverage` reportes
- `*.pyc` archivos

**No toca:**
- Tu código
- Datos

---

### 📊 Información

#### `make info`
Mostrar información del proyecto.

```bash
make info
```

**Muestra:**
- Versión de Python
- Docker version
- Rama Git actual
- Cambios sin commit

---

## 🔄 Flujos Típicos

### Desarrollo Local

```bash
# 1. Setup inicial
make install

# 2. Hacer cambios...

# 3. Verificar código
make lint
make format

# 4. Ejecutar tests
make test

# 5. Probar en Docker
make docker-build
make docker-up

# 6. Ver logs
make docker-logs

# 7. Cuando termines
make docker-down
make clean
```

### Antes de Hacer Commit

```bash
# 1. Lint y format
make lint
make format

# 2. Tests deben pasar
make test

# 3. Coverage > 80%
make coverage

# 4. Limpiar
make clean

# 5. Commit
git add .
git commit -m "mensaje"
git push
```

### CI/CD (GitLab Pipeline)

El `.gitlab-ci.yml` usa estos targets automáticamente:

```yaml
test:
  script:
    - make test        # Corre make test

build:
  script:
    - make docker-build  # Corre make docker-build
```

---

## ⚡ Atajos Útiles

### Crear alias en bash/zsh

```bash
# Agregar a ~/.bashrc o ~/.zshrc
alias mt="make test"
alias mb="make docker-build"
alias mu="make docker-up"
alias md="make docker-down"
alias clean="make clean"

# Recargar terminal
source ~/.bashrc
```

Luego puedes usar:
```bash
mt      # en lugar de: make test
mb      # en lugar de: make docker-build
mu      # en lugar de: make docker-up
```

---

## 🆘 Troubleshooting

### Error: "make: command not found"

**Windows:**
```bash
# Instalar Make
choco install make  # Si tienes Chocolatey
# O descargar desde: https://gnuwin32.sourceforge.net/packages/make.htm
```

**Mac:**
```bash
brew install make
```

**Linux:**
```bash
apt-get install make  # Debian/Ubuntu
yum install make      # RedHat/CentOS
```

### Error: "docker: command not found"

```bash
# Instalar Docker
# Linux: https://docs.docker.com/engine/install/
# Mac/Windows: descargar Docker Desktop
```

### Tests failing

```bash
# 1. Verificar dependencias
make install

# 2. Limpiar cache
make clean

# 3. Ejecutar tests con más detalles
make test-verbose

# 4. Ver coverage
make coverage
```

### Docker no build

```bash
# 1. Limpiar imágenes viejas
make docker-clean

# 2. Recontrabilidad
make docker-build

# 3. Ver logs
docker build -t proyecto-deteccion-plantas .
```

---

## 📚 Referencias

- [GNU Make Manual](https://www.gnu.org/software/make/manual/)
- [Docker Documentation](https://docs.docker.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Ruff Code Formatter](https://github.com/astral-sh/ruff)

---

¡Haz productiva tu línea de comandos! 💪
