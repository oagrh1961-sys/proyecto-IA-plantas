import os

import torch
from PIL import Image
from transformers import MobileNetV2ForImageClassification, MobileNetV2ImageProcessor

# Ruta donde descargamos el modelo
PATH_MODELO = "./modelo_entrenado"

print("Cargando modelo y procesador específicos para MobileNetV2...")
# Forzamos las clases específicas para evitar el ValueError
model = MobileNetV2ForImageClassification.from_pretrained(PATH_MODELO)
processor = MobileNetV2ImageProcessor.from_pretrained(PATH_MODELO)


def predecir(ruta_imagen):
    if not os.path.exists(ruta_imagen):
        print(f"\n❌ Error: No encontré la imagen '{ruta_imagen}' en la carpeta.")
        print("Asegúrate de que el nombre sea idéntico (ej: imagen.jpg)")
        return

    # Abrir y procesar la imagen
    image = Image.open(ruta_imagen).convert("RGB")

    # El procesador redimensiona y normaliza la imagen automáticamente
    inputs = processor(images=image, return_tensors="pt")

    # Inferencia (predicción)
    print("Analizando imagen...")
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    # Obtener la etiqueta con mayor probabilidad
    predicted_label = logits.argmax(-1).item()

    # Mapear el ID numérico al nombre de la enfermedad
    resultado = model.config.id2label[predicted_label]

    print("\n" + "=" * 40)
    print("🌿 RESULTADO DEL DIAGNÓSTICO:")
    print(f" >> {resultado} <<")
    print("=" * 40 + "\n")


# --- PRUEBA AQUÍ ---
# 1. Pon una imagen en tu carpeta (ejemplo: 'hoja_enferma.jpg')
# 2. Escribe el nombre exacto aquí abajo:
nombre_de_tu_archivo = "test.jpg"

if __name__ == "__main__":
    predecir(nombre_de_tu_archivo)
