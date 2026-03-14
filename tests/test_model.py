import os
import logging
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image
from transformers import MobileNetV2ForImageClassification

from src.app import UIHandler
from src.client import PlantDiseaseClient
from src.server import MLflowTracker, ModelHandler


@pytest.fixture(autouse=True)
def setup_logging():
    """Configura logging para pruebas limpias."""
    logging.getLogger().setLevel(logging.WARNING)
    # Suprimir warnings de transformers y otros
    logging.getLogger("transformers").setLevel(logging.ERROR)
    logging.getLogger("PIL").setLevel(logging.ERROR)


def test_model_loading():
    """Verifica que los archivos del modelo existan y sean cargables."""
    path = "./modelo_entrenado"
    assert os.path.exists(path), "La carpeta del modelo no existe"

    model = MobileNetV2ForImageClassification.from_pretrained(path)
    assert model is not None
    assert hasattr(model, "config")


def test_model_handler():
    """Prueba la clase ModelHandler para carga y predicción."""
    handler = ModelHandler()
    assert handler.model is not None
    assert handler.processor is not None

    # Crear imagen de prueba (blanca)
    test_image = Image.new("RGB", (224, 224), color="white")
    label, confidence = handler.predict(test_image)
    assert isinstance(label, str)
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0


def test_mlflow_tracker():
    """Prueba la clase MLflowTracker."""
    with patch("src.server.mlflow") as mock_mlflow:
        tracker = MLflowTracker()
        mock_mlflow.set_experiment.assert_called_once()
        mock_mlflow.start_run.assert_called()

        # Probar log_prediction con nuevos parámetros
        tracker.log_prediction("test_label", 0.95, 1.23, (224, 224))
        assert mock_mlflow.start_run.call_count == 2  # Una para init, una para log

        # Probar log_error
        tracker.log_error("Test error message", (224, 224))
        assert mock_mlflow.start_run.call_count == 3  # Una más para error


def test_ui_handler_translate():
    """Prueba la traducción de etiquetas en UIHandler."""
    mock_client = MagicMock(spec=PlantDiseaseClient)
    handler = UIHandler(mock_client)

    # Probar traducción existente
    assert handler.translate_label("Apple___healthy") == "Manzana - Sana ✅"

    # Probar etiqueta no existente
    assert handler.translate_label("unknown_label") == "unknown_label"


def test_plant_disease_client_init():
    """Prueba la inicialización del cliente gRPC."""
    with patch.dict(
        os.environ, {"GRPC_SERVER_HOST": "test_host", "GRPC_SERVER_PORT": "1234"}
    ):
        client = PlantDiseaseClient()
        assert client.channel is not None
        assert client.stub is not None
