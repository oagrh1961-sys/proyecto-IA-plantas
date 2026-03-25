import os

from huggingface_hub import snapshot_download

folder = "./modelo_entrenado"

print("Iniciando la descarga del modelo...")
snapshot_download(
    repo_id="linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification",
    local_dir=folder,
)
print(f"Hecho! Archivos en: {os.path.abspath(folder)}")
