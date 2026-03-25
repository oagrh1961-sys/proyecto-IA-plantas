import logging
import os
from io import BytesIO

import grpc
import streamlit as st
from PIL import Image

from .client import PlantDiseaseClient

# Configurar logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class UIHandler:
    """Maneja la interfaz de usuario de Streamlit."""

    def __init__(self, client: PlantDiseaseClient):
        self.client = client
        self.translations = {
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

    def translate_label(self, label: str) -> str:
        """Traduce la etiqueta técnica a español."""
        return self.translations.get(label, label)

    def run(self):
        """Ejecuta la aplicación Streamlit."""
        st.set_page_config(page_title="Detector de Enfermedades", page_icon="🌿")
        st.title("🌿 Diagnóstico de Salud Vegetal")
        
        # Mostrar contexto de conexión
        context = self.client.context
        host = self.client.host
        st.caption(f"🔗 Conectado [{context}]: {host}:{self.client.port}")
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
                    buffer = BytesIO()
                    image.save(buffer, format="JPEG")
                    image_bytes = buffer.getvalue()
                    logger.info(f"Enviando imagen ({len(image_bytes)} bytes) para clasificación...")

                    # Enviar al servidor gRPC con mejor manejo de errores
                    try:
                        label_original, confidence, latency_ms = self.client.classify_image(
                            image_bytes
                        )
                        resultado_es = self.translate_label(label_original)

                        st.markdown("---")
                        st.subheader("Resultado del Análisis:")
                        st.success(f"**{resultado_es}**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.info(f"Confianza: {confidence:.2%}")
                        with col2:
                            st.metric("Latencia", f"{latency_ms:.2f}ms")
                        with col3:
                            st.metric("Tamaño", f"{len(image_bytes)/1024:.1f}KB")

                        # Recomendación rápida
                        if "sana" in resultado_es.lower() or "✅" in resultado_es:
                            st.balloons()
                            st.info("✅ Sugerencia: Mantén el ciclo de riego actual.")
                        else:
                            st.warning(
                                "⚠️ Sugerencia: Aísla la planta y aplica un "
                                "tratamiento fungicida."
                            )
                        logger.info(f"✅ Clasificación exitosa: {label_original}")
                        
                    except grpc.RpcError as e:
                        error_code = e.code().name if hasattr(e, 'code') else 'UNKNOWN'
                        error_msg = e.details() if hasattr(e, 'details') else str(e)
                        logger.error(f"Error gRPC [{error_code}]: {error_msg}")
                        
                        st.error(f"❌ Error en el servidor ({error_code})")
                        st.error(f"Detalles: {error_msg}")
                        
                        # Mostrar instrucciones según el contexto
                        if self.client.is_docker:
                            st.info(
                                "**En Docker:**\\n"
                                "1. Verifica que el container del servidor esté corriendo: `docker ps`\\n"
                                "2. Revisa los logs: `docker-compose logs server`\\n"
                                "3. Reinicia los servicios: `docker-compose restart server`"
                            )
                        else:
                            st.info(
                                "**En Local:**\\n"
                                "1. Verifica que el servidor gRPC esté ejecutándose\\n"
                                f"2. Confirma que pueda conectarse a {self.client.host}:{self.client.port}\\n"
                                "3. Revisa los logs del servidor"
                            )
                    except Exception as e:
                        logger.exception(f"Error inesperado: {e}")
                        st.error(f"❌ Error inesperado: {str(e)[:100]}...")
                        st.info("Revisa los logs para más información.")


# Inicializar y ejecutar la aplicación
@st.cache_resource
def init_client():
    """Inicializa el cliente gRPC (cacheado en Streamlit)."""
    try:
        logger.info("Inicializando cliente gRPC...")
        client = PlantDiseaseClient()
        logger.info(f"✅ Cliente inicializado correctamente [{client.context}]")
        return client
    except Exception as e:
        logger.error(f"Error al inicializar cliente: {e}")
        raise

try:
    client = init_client()
    ui_handler = UIHandler(client)
    ui_handler.run()
except Exception as e:
    st.error(f"❌ Error crítico al inicializar la aplicación: {e}")
    st.stop()
