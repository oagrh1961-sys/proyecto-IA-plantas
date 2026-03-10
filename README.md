# 🌿 Detección de Enfermedades en Cultivos con IA

## Descripción
Sistema de clasificación de imágenes basado en **MobileNetV2** para la identificación temprana de patologías en hojas de plantas. Desarrollado para la materia "Desarrollo de Proyectos de IA".

## 🛠️ Requisitos e Instalación
Este proyecto utiliza `uv` para la gestión de dependencias.
```bash
uv sync
```

## 🚀 Uso
Para lanzar la interfaz de usuario:

```bash
uv run streamlit run src/app.py
```

## 🧪 Calidad y Pruebas
Ejecutar linter (Clase 5):

```bash
uv run ruff check
```

Ejecutar pruebas unitarias (Clase 2):

```bash
uv run pytest
```

## 📄 Licencia
Este proyecto se distribuye bajo la licencia MIT.