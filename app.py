from flask import Flask, render_template, request
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input
import keras
from io import BytesIO
import base64

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Cargar el modelo
model = keras.models.load_model('coso_clasi.keras')

# Nombres de clases
class_names = ["black-spot", "citrus-canker"]

# Asegurar que la carpeta de subida exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files['file']
        if file:
            # Leer la imagen directamente en memoria
            file_stream = BytesIO(file.read())
            
            # Preprocesar la imagen exactamente como en el entrenamiento
            img = image.load_img(file_stream, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            
            # Aplicar el preprocesamiento de VGG16
            img_array = preprocess_input(img_array)

            # Hacer la predicción
            predictions = model.predict(img_array)
            print("\n=== Detalles de la Predicción ===")
            print("Shape del array de predicciones:", predictions.shape)
            print("Predicciones brutas:", predictions)
            print("\nValores de predicción por clase:")
            for i, prob in enumerate(predictions[0]):
                print(f"Clase {i} ({class_names[i]}): {prob:.4f} ({prob*100:.2f}%)")
            
            class_idx = np.argmax(predictions)
            predicted_probability = predictions[0][class_idx]
            class_label = class_names[class_idx]
            
            print(f"\nResultados finales:")
            print(f"Índice de la clase con mayor probabilidad: {class_idx}")
            print(f"Nombre de la clase predicha: {class_label}")
            print(f"Probabilidad de la predicción: {predicted_probability:.4f} ({predicted_probability*100:.2f}%)")
            
            if predicted_probability < 0.5:
                print("⚠️ ADVERTENCIA: Baja confianza en la predicción")
            
            print("================================\n")

            # Convertir la imagen original a base64 para mostrarla
            file_stream.seek(0)
            img_base64 = tf.keras.utils.img_to_array(img)
            img_base64 = tf.keras.preprocessing.image.array_to_img(img_base64)
            import io
            img_buffer = io.BytesIO()
            img_base64.save(img_buffer, format='PNG')
            img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

            return render_template("index.html", 
                                img_data=f"data:image/png;base64,{img_str}", 
                                label=class_label,
                                probability=predicted_probability)
    
    return render_template("index.html", img_data=None, label=None, probability=None)

if __name__ == "__main__":
    app.run(debug=True)