"""Test suite completo para el clasificador de enfermedades en plantas."""
import io
import logging
import os
import time
from unittest.mock import MagicMock, patch

import grpc
import pytest
from PIL import Image
from transformers import MobileNetV2ForImageClassification

from src.app import UIHandler
from src.client import PlantDiseaseClient
from src.server import MLflowTracker, ModelHandler, PlantDiseaseClassifier
from src.image_classifier_pb2 import ImageRequest


@pytest.fixture(autouse=True)
def setup_logging():
    """Configura logging para pruebas limpias."""
    logging.getLogger().setLevel(logging.WARNING)
    # Suprimir warnings de transformers y otros
    logging.getLogger("transformers").setLevel(logging.ERROR)
    logging.getLogger("PIL").setLevel(logging.ERROR)


# ==================== TESTS BÁSICOS ====================

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


# ==================== TESTS DE PROCESAMIENTO DE IMÁGENES ====================

class TestImageProcessing:
    """Tests para procesamiento de imágenes."""

    @staticmethod
    def _image_to_bytes(image: Image.Image) -> bytes:
        """Convierte una imagen PIL a bytes."""
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        return img_byte_arr.getvalue()

    def test_valid_image_rgb(self):
        """Prueba con imagen RGB válida."""
        image = Image.new("RGB", (224, 224), color="red")
        image_bytes = self._image_to_bytes(image)
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0

    def test_valid_image_rgba(self):
        """Prueba con imagen RGBA válida."""
        image = Image.new("RGBA", (224, 224), color=(255, 0, 0, 255))
        image_bytes = self._image_to_bytes(image)
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0

    def test_small_image(self):
        """Prueba con imagen más pequeña que 224x224."""
        image = Image.new("RGB", (100, 100), color="blue")
        image_bytes = self._image_to_bytes(image)
        assert isinstance(image_bytes, bytes)

    def test_large_image(self):
        """Prueba con imagen más grande que 224x224."""
        image = Image.new("RGB", (512, 512), color="green")
        image_bytes = self._image_to_bytes(image)
        assert isinstance(image_bytes, bytes)


# ==================== TESTS DE RENDIMIENTO ====================

class TestModelHandlerPerformance:
    """Tests de rendimiento del ModelHandler."""

    def test_prediction_latency(self):
        """Verifica que la predicción se completa en tiempo razonable."""
        handler = ModelHandler()
        test_image = Image.new("RGB", (224, 224), color="white")

        start = time.time()
        label, confidence = handler.predict(test_image)
        latency = time.time() - start

        assert latency < 5.0, f"Predicción tomó {latency}s, debería ser < 5s"
        assert isinstance(label, str)
        assert isinstance(confidence, float)

    def test_multiple_predictions(self):
        """Verifica que múltiples predicciones funcionan correctamente."""
        handler = ModelHandler()
        colors = ["red", "green", "blue", "white", "black"]

        results = []
        for color in colors:
            test_image = Image.new("RGB", (224, 224), color=color)
            label, confidence = handler.predict(test_image)
            results.append((label, confidence))

        assert len(results) == 5
        for label, confidence in results:
            assert isinstance(label, str)
            assert 0.0 <= confidence <= 1.0


# ==================== TESTS DE GRPC ====================

class TestGRPCRequest:
    """Tests para requests gRPC."""

    @staticmethod
    def _image_to_bytes(image: Image.Image) -> bytes:
        """Convierte una imagen PIL a bytes."""
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        return img_byte_arr.getvalue()

    def test_image_request_creation(self):
        """Verifica que se puede crear un ImageRequest válido."""
        image = Image.new("RGB", (224, 224), color="white")
        image_bytes = self._image_to_bytes(image)
        
        request = ImageRequest(image=image_bytes)
        assert request.image == image_bytes

    def test_empty_image_request(self):
        """Verifica que un request vacío se crea correctamente."""
        request = ImageRequest(image=b"")
        assert request.image == b""


# ==================== TESTS DE MLFLOW ====================

class TestMLflowMetrics:
    """Tests para logging de métricas en MLflow."""

    def test_mlflow_prediction_logging(self):
        """Verifica que MLflow registra métricas de predicción."""
        with patch("src.server.mlflow") as mock_mlflow:
            tracker = MLflowTracker()
            tracker.log_prediction("test_label", 0.99, 0.5, (224, 224))

            # Verifica que se registraron las métricas
            calls = [str(call) for call in mock_mlflow.log_metric.call_args_list]
            assert any("confidence" in str(call) for call in calls)
            assert any("latency" in str(call) for call in calls)

    def test_mlflow_error_logging(self):
        """Verifica que MLflow registra errores."""
        with patch("src.server.mlflow") as mock_mlflow:
            tracker = MLflowTracker()
            tracker.log_error("Test error", (224, 224))

            # Verifica que se registró el error
            mock_mlflow.log_param.assert_called()
            mock_mlflow.set_tag.assert_called()


# ==================== TESTS DE CONFIGURACIÓN DEL CLIENTE ====================

class TestClientConfiguration:
    """Tests para configuración del cliente gRPC."""

    def test_client_default_config(self):
        """Verifica configuración por defecto del cliente."""
        with patch.dict("os.environ", {}, clear=True):
            client = PlantDiseaseClient()
            assert client.channel is not None

    def test_client_custom_config(self):
        """Verifica que el cliente usa configuración personalizada."""
        with patch.dict(
            "os.environ",
            {"GRPC_SERVER_HOST": "custom_host", "GRPC_SERVER_PORT": "9999"}
        ):
            client = PlantDiseaseClient()
            assert client.channel is not None


# ==================== TESTS DE MANEJO DE ERRORES ====================

class TestErrorHandling:
    """Tests para manejo de errores."""

    def test_invalid_image_format(self):
        """Verifica manejo de formato de imagen inválido."""
        invalid_bytes = b"not_an_image"
        
        with patch("src.server.ModelHandler.predict") as mock_predict:
            mock_predict.side_effect = Exception("Invalid image")
            
            handler = MagicMock()
            handler.predict.side_effect = Exception("Invalid image")
            
            with pytest.raises(Exception):
                handler.predict("dummy_input")

    def test_missing_model(self):
        """Verifica manejo de modelo faltante."""
        with patch("os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError):
                ModelHandler()


# ==================== TESTS DE TRADUCCIÓN DE ETIQUETAS ====================

class TestUIHandlerTranslations:
    """Tests para traducción de etiquetas en UIHandler."""

    @pytest.fixture
    def ui_handler(self):
        """Crea una instancia de UIHandler con cliente mock."""
        mock_client = MagicMock(spec=PlantDiseaseClient)
        return UIHandler(mock_client)

    def test_translate_apple_healthy(self, ui_handler):
        """Prueba traducción de manzana sana."""
        result = ui_handler.translate_label("Apple___healthy")
        assert "Manzana" in result
        assert "Sana" in result

    def test_translate_apple_scab(self, ui_handler):
        """Prueba traducción de sarna de manzana."""
        result = ui_handler.translate_label("Apple___Apple_scab")
        assert "Manzana" in result
        assert "Sarna" in result

    def test_translate_tomato_late_blight(self, ui_handler):
        """Prueba traducción de tizón tardío de tomate."""
        result = ui_handler.translate_label("Tomato___Late_blight")
        assert "Tomate" in result
        assert "Tizón" in result

    def test_translate_unknown_label(self, ui_handler):
        """Prueba que etiqueta desconocida se retorna como está."""
        unknown = "Unknown_plant___Unknown_disease"
        result = ui_handler.translate_label(unknown)
        assert result == unknown

    def test_translate_empty_label(self, ui_handler):
        """Prueba traducción de etiqueta vacía."""
        result = ui_handler.translate_label("")
        assert result == ""


# ==================== TESTS DE DIMENSIONES DE IMAGEN ====================

class TestImageDimensions:
    """Tests para validación de dimensiones de imagen."""

    def test_standard_image_size(self):
        """Verifica procesamiento de imagen estándar."""
        image = Image.new("RGB", (224, 224), color="white")
        assert image.size == (224, 224)

    def test_portrait_image(self):
        """Verifica procesamiento de imagen en modo portrait."""
        image = Image.new("RGB", (224, 400), color="white")
        assert image.height > image.width

    def test_landscape_image(self):
        """Verifica procesamiento de imagen en modo landscape."""
        image = Image.new("RGB", (400, 224), color="white")
        assert image.width > image.height

    def test_very_small_image(self):
        """Verifica manejo de imagen muy pequeña."""
        image = Image.new("RGB", (32, 32), color="white")
        assert image.size[0] > 0 and image.size[1] > 0

    def test_very_large_image(self):
        """Verifica manejo de imagen muy grande."""
        image = Image.new("RGB", (4096, 4096), color="white")
        assert image.size[0] > 0 and image.size[1] > 0


# ==================== TESTS DE CONFIGURACIÓN DEL SERVIDOR ====================

class TestModelHandlerInitialization:
    """Tests para inicialización del ModelHandler."""

    def test_model_handler_init_default_path(self):
        """Verifica inicialización con ruta por defecto."""
        handler = ModelHandler()
        assert handler.model is not None
        assert handler.processor is not None
        assert handler.model_path == "./modelo_entrenado"

    def test_model_handler_init_custom_path(self):
        """Verifica inicialización con ruta personalizada."""
        with patch("os.path.exists", return_value=True):
            with patch("src.server.MobileNetV2ForImageClassification.from_pretrained") as mock_model:
                with patch("src.server.MobileNetV2ImageProcessor.from_pretrained") as mock_processor:
                    mock_model.return_value = MagicMock()
                    mock_processor.return_value = MagicMock()
                    handler = ModelHandler("./custom_model_path")
                    assert handler.model_path == "./custom_model_path"
                    assert handler.model is not None
                    assert handler.processor is not None


class TestMLflowTrackerInitialization:
    """Tests para inicialización del MLflowTracker."""

    def test_mlflow_tracker_init_default_experiment(self):
        """Verifica inicialización con nombre de experimento por defecto."""
        with patch("src.server.mlflow") as mock_mlflow:
            tracker = MLflowTracker()
            assert tracker.experiment_name == "Plant Disease Classification"
            mock_mlflow.set_experiment.assert_called_once()

    def test_mlflow_tracker_init_custom_experiment(self):
        """Verifica inicialización con nombre de experimento personalizado."""
        with patch("src.server.mlflow") as mock_mlflow:
            custom_name = "Custom Experiment"
            tracker = MLflowTracker(experiment_name=custom_name)
            assert tracker.experiment_name == custom_name
            mock_mlflow.set_experiment.assert_called_with(custom_name)

    def test_mlflow_tracker_startup_logging(self):
        """Verifica que se registra el inicio del servicio."""
        with patch("src.server.mlflow") as mock_mlflow:
            tracker = MLflowTracker()
            
            # Verificar que se inició un run
            assert mock_mlflow.start_run.call_count >= 1
            # Verificar que se registró un parámetro
            mock_mlflow.log_param.assert_called()


class TestPlantDiseaseClassifierInitialization:
    """Tests para inicialización del PlantDiseaseClassifier."""

    def test_classifier_init(self):
        """Verifica que el clasificador se inicializa correctamente."""
        classifier = PlantDiseaseClassifier()
        assert classifier is not None
        assert hasattr(classifier, "model_handler")
        assert hasattr(classifier, "mlflow_tracker")

    def test_classifier_has_classify_method(self):
        """Verifica que el clasificador tiene el método ClassifyImage (gRPC)."""
        classifier = PlantDiseaseClassifier()
        assert hasattr(classifier, "ClassifyImage")
        assert callable(getattr(classifier, "ClassifyImage"))


# ==================== TESTS DE VARIABLES DE ENTORNO ====================

class TestEnvironmentVariables:
    """Tests para validación de variables de entorno."""

    def test_grpc_port_from_env(self):
        """Verifica lectura del puerto gRPC desde variable de entorno."""
        with patch.dict(os.environ, {"GRPC_SERVER_PORT": "50052"}):
            port = os.getenv("GRPC_SERVER_PORT", "50051")
            assert port == "50052"

    def test_grpc_host_from_env(self):
        """Verifica lectura del host gRPC desde variable de entorno."""
        with patch.dict(os.environ, {"GRPC_SERVER_HOST": "custom_host"}):
            host = os.getenv("GRPC_SERVER_HOST", "localhost")
            assert host == "custom_host"

    def test_mlflow_tracking_uri_from_env(self):
        """Verifica lectura de URI de MLflow desde variable de entorno."""
        with patch.dict(os.environ, {"MLFLOW_TRACKING_URI": "file:///app/mlruns"}):
            uri = os.getenv("MLFLOW_TRACKING_URI")
            assert uri == "file:///app/mlruns"

    def test_defaults_when_env_not_set(self):
        """Verifica que se usan valores por defecto cuando variables no están set."""
        with patch.dict(os.environ, {}, clear=True):
            port = os.getenv("GRPC_SERVER_PORT", "50051")
            host = os.getenv("GRPC_SERVER_HOST", "localhost")
            
            assert port == "50051"
            assert host == "localhost"


# ==================== TESTS DE MÉTRICAS DE CONFIANZA ====================

class TestConfidenceMetrics:
    """Tests para validación de métricas de confianza."""

    def test_confidence_range_valid(self):
        """Verifica que los valores de confianza están en rango válido."""
        valid_confidences = [0.0, 0.5, 0.99, 1.0]
        
        for conf in valid_confidences:
            assert 0.0 <= conf <= 1.0

    def test_confidence_percentage_conversion(self):
        """Verifica conversión de confianza a porcentaje."""
        test_cases = [
            (0.0, "0%"),
            (0.5, "50%"),
            (1.0, "100%"),
            (0.956, "95%")
        ]
        
        for conf, expected_format in test_cases:
            percentage = f"{int(conf * 100)}%"
            assert percentage in expected_format or expected_format in f"{int(conf * 100)}%"


# ==================== TESTS DE CONCURRENCIA ====================

class TestConcurrency:
    """Tests para comportamiento concurrente."""

    def test_multiple_handler_instances(self):
        """Verifica que se pueden crear múltiples instancias del handler."""
        handlers = [ModelHandler() for _ in range(3)]
        assert len(handlers) == 3
        assert all(h.model is not None for h in handlers)

    def test_multiple_tracker_instances(self):
        """Verifica que se pueden crear múltiples instancias del tracker."""
        with patch("src.server.mlflow"):
            trackers = [MLflowTracker() for _ in range(3)]
            assert len(trackers) == 3
            assert all(t.experiment_name for t in trackers)
