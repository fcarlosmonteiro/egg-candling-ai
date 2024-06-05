from flask import request, jsonify, render_template
from inference_sdk import InferenceHTTPClient
import base64
from PIL import Image, ImageDraw, ImageFont
import io

API_URL = "https://detect.roboflow.com"
API_KEY = "wC7iFMlWHPTgTSCUd2fy" 
MODEL_ID = "egg-detection-ud1ys/13"  
client = InferenceHTTPClient(
    api_url=API_URL,
    api_key=API_KEY
)

def setup_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/infer', methods=['POST'])
    def infer():
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        image = Image.open(image_file)
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        try:
            result = client.infer(img_str, model_id=MODEL_ID)  
            
            draw = ImageDraw.Draw(image)
            font = ImageFont.load_default()
            for prediction in result['predictions']:
                x = prediction['x']
                y = prediction['y']
                width = prediction['width']
                height = prediction['height']
                confidence = prediction['confidence']
                label = f"{prediction['class']} {confidence:.0%}"
                left = x - width / 2
                top = y - height / 2
                right = x + width / 2
                bottom = y + height / 2
                draw.rectangle([left, top, right, bottom], outline="red", width=2)
                text_bbox = draw.textbbox((0, 0), label, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                draw.rectangle([left, top - text_height, left + text_width, top], fill="red")
                draw.text((left, top - text_height), label, fill="white", font=font)

            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_with_detections_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            return render_template('index.html', results=result['predictions'], image_data=img_with_detections_str)

        except Exception as e:
            return jsonify({'error': str(e)}), 500
