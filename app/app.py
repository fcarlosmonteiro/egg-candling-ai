from flask import Flask, request, jsonify, render_template
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
from io import BytesIO

app = Flask(__name__)

MODEL_PATH = 'final_model.keras'
model = load_model(MODEL_PATH)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('egg_images')  # Isso assumirá que você pode enviar vários arquivos
        if not files:
            return jsonify({'error': 'Nenhum arquivo foi enviado.'}), 400
        results = []
        for file in files:
            if file:
                img_bytes = BytesIO(file.read())
                image = load_img(img_bytes, target_size=(64, 64))
                image_array = img_to_array(image)
                image_array = np.expand_dims(image_array, axis=0) / 255.0

                prediction = model.predict(image_array)
                result = "Fértil" if prediction[0][0] < 0.5 else "Infértil"
                results.append(result)
                print(result,prediction[0][0])

        return jsonify({'classificações': results})

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
