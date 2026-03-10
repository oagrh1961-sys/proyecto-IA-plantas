import streamlit as st
import torch
from PIL import Image
from transformers import MobileNetV2ForImageClassification, MobileNetV2ImageProcessor

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

st.set_page_config(page_title="Detector de Enfermedades", page_icon="🌿")

st.title("🌿 Diagnóstico de Salud Vegetal")
st.write("Sube una foto de la hoja para obtener un diagnóstico en español.")


@st.cache_resource
def load_model():
    path = "./modelo_entrenado"
    model = MobileNetV2ForImageClassification.from_pretrained(path)
    processor = MobileNetV2ImageProcessor.from_pretrained(path)
    return model, processor


model, processor = load_model()

uploaded_file = st.file_uploader(
    "Selecciona una imagen...", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Imagen seleccionada", use_container_width=True)

    if st.button("Iniciar Diagnóstico"):
        with st.spinner("Analizando tejido vegetal..."):
            inputs = processor(images=image, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                predicted_label = logits.argmax(-1).item()

            # Obtener etiqueta original
            label_original = model.config.id2label[predicted_label]

            # Buscar traducción o dejar la original si no está en el diccionario
            resultado_es = TRADUCCIONES.get(label_original, label_original)

            st.markdown("---")
            st.subheader("Resultado del Análisis:")
            st.success(f"**{resultado_es}**")

            # Recomendación rápida
            if "sana" in resultado_es.lower() or "✅" in resultado_es:
                st.balloons()
                st.info("Sugerencia: Mantén el ciclo de riego actual.")
            else:
                st.warning(
                    "Sugerencia: Aísla la planta y aplica un tratamiento fungicida."
                )
