import argparse
import logging
import os
import warnings

# Configurar entorno para streamlit antes de importar (aunque no importemos)
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

from client import PlantDiseaseClient


def main():
    # Configurar logging para ejecución limpia
    logging.getLogger().setLevel(logging.WARNING)
    logging.getLogger("streamlit").setLevel(logging.ERROR)

    parser = argparse.ArgumentParser(
        description="Analiza una imagen usando el servidor gRPC de detección de enfermedades."  # noqa: E501
    )
    parser.add_argument(
        "--image", "-i", required=True, help="Ruta local de la imagen a analizar."
    )
    args = parser.parse_args()

    client = PlantDiseaseClient()
    with open(args.image, "rb") as f:
        image_bytes = f.read()

    label, confidence = client.classify_image(image_bytes)
    print(f"Etiqueta: {label}")
    print(f"Confianza: {confidence:.2%}")


if __name__ == "__main__":
    main()
