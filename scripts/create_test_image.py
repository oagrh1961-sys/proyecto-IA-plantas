from PIL import Image
import numpy as np

# Crear una imagen aleatoria de 224x224
img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
img = Image.fromarray(img_array)
img.save('test_image.jpg')
print("Imagen de prueba creada: test_image.jpg")