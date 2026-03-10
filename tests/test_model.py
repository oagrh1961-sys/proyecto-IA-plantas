import os

from transformers import MobileNetV2ForImageClassification


def test_model_loading():
    """Verifica que los archivos del modelo existan y sean cargables."""
    path = "./modelo_entrenado"
    assert os.path.exists(path), "La carpeta del modelo no existe"

    model = MobileNetV2ForImageClassification.from_pretrained(path)
    assert model is not None
    assert hasattr(model, "config")
