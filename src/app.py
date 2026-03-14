import os

import grpc
import streamlit as st
from PIL import Image

from image_classifier_pb2 import ImageRequest
from image_classifier_pb2_grpc import ImageClassifierStub

# 1. Diccionario de traducción (ajusta según las clases que veas en tu modelo)
TRADUCCIONES = {
    "Apple___Apple_scab": "Manzana - Sarna del manzano",
    "Apple___Black_rot": "Manzana - Podredumbre negra",
    "Apple___Cedar_apple_rust": "Manzana - Roya del manzano",
    "Apple___healthy": "Manzana - Sana ✅",
    "Corn_(maize)___Common_rust_": "Maíz - Roya común",
    "Corn_(maize)___healthy": "Maíz - Sano ✅",
    "Grape___Black_rot": "Uva - Podredumbre negra",
    "Grape___healthy": "Uva - Sana ✅",
    "Potato___Early_blight": "Papa - Tizón temprano",
    "Potato___Late_blight": "Papa - Tizón tardío",
    "Potato___healthy": "Papa - Sana ✅",
    "Tomato___Early_blight": "Tomate - Tizón temprano",
    "Tomato___Late_blight": "Tomate - Tizón tardío",
    "Tomato___healthy": "Tomate - Sano ✅",
    "healthy": "Sana ✅",
}


class PlantDiseaseClient:
    """Cliente gRPC para el servicio de clasificación de enfermedades en plantas."""

    def __init__(self, host: str = None, port: int = None):
        if host is None:
            host = os.getenv("GRPC_SERVER_HOST", "localhost")
        if port is None:
            port = int(os.getenv("GRPC_SERVER_PORT", "50051"))
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = ImageClassifierStub(self.channel)

    def classify_image(self, image_bytes: bytes) -> tuple[str, float]:
        """Envía la imagen al servidor gRPC y recibe la predicción."""
        request = ImageRequest(image=image_bytes)
        response = self.stub.ClassifyImage(request)
        return response.label, response.confidence


# Inicializar cliente
client = PlantDiseaseClient()

st.set_page_config(page_title="Detector de Enfermedades", page_icon="🌿")

st.title("🌿 Diagnóstico de Salud Vegetal")
st.write("Sube una foto de la hoja para obtener un diagnóstico en español.")

uploaded_file = st.file_uploader(
    "Selecciona una imagen...", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Imagen seleccionada", use_container_width=True)

    if st.button("Iniciar Diagnóstico"):
        with st.spinner("Analizando tejido vegetal..."):
            # Convertir imagen a bytes
            from io import BytesIO

            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            image_bytes = buffer.getvalue()

            # Enviar al servidor gRPC
            try:
                label_original, confidence = client.classify_image(image_bytes)

                # Buscar traducción o dejar la original si no está en el diccionario
                resultado_es = TRADUCCIONES.get(label_original, label_original)

                st.markdown("---")
                st.subheader("Resultado del Análisis:")
                st.success(f"**{resultado_es}**")
                st.info(f"Confianza: {confidence:.2%}")

                # Recomendación rápida
                if "sana" in resultado_es.lower() or "✅" in resultado_es:
                    st.balloons()
                    st.info("Sugerencia: Mantén el ciclo de riego actual.")
                else:
                    st.warning(
                        "Sugerencia: Aísla la planta y aplica un tratamiento fungicida."
                    )
            except grpc.RpcError as e:
                st.error(f"Error conectando al servidor: {e.details()}")
                st.info("Asegúrate de que el servidor gRPC esté ejecutándose.")
