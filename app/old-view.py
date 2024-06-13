API_KEY = "wC7iFMlWHPTgTSCUd2fy"  # Certifique-se de substituir pela sua chave de API correta

from flask import request, jsonify, render_template
from inference_sdk import InferenceHTTPClient
import base64
from PIL import Image, ImageDraw, ImageFont
import io

# Configurações da API do Roboflow
API_URL = "https://detect.roboflow.com"
MODEL_ID = "egg-detection-ud1ys/13"  # Substitua pelo seu model_id correto

client = InferenceHTTPClient(
    api_url=API_URL,
    api_key=API_KEY
)

CONFIDENCE_THRESHOLD = 0.7  # Limite de confiança
IOU_THRESHOLD = 0.3  # Limite de Interseção sobre União (IoU)

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
            result = client.infer(img_str, model_id=MODEL_ID)  # Envia a string codificada em base64

            # Filtrar as previsões com base no limite de confiança
            predictions = [p for p in result['predictions'] if p['confidence'] >= CONFIDENCE_THRESHOLD]

            # Aplicar supressão não-máxima
            predictions = non_max_suppression(predictions, IOU_THRESHOLD)

            # Desenhar as caixas de detecção na imagem
            draw = ImageDraw.Draw(image)
            font = ImageFont.load_default()
            class_colors = {
                "FE": "green",
                "UF": "red",
                "DE": "purple"
            }

            for prediction in predictions:
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
                color = class_colors.get(prediction['class'], "blue")
                draw.rectangle([left, top, right, bottom], outline=color, width=2)
                text_bbox = draw.textbbox((0, 0), label, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                draw.rectangle([left, top - text_height, left + text_width, top], fill=color)
                draw.text((left, top - text_height), label, fill="white", font=font)

            # Converter a imagem com as detecções de volta para base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_with_detections_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            return render_template('index.html', results=predictions, image_data=img_with_detections_str)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

def non_max_suppression(predictions, iou_threshold):
    if len(predictions) == 0:
        return []

    boxes = [(p['x'] - p['width'] / 2, p['y'] - p['height'] / 2, p['x'] + p['width'] / 2, p['y'] + p['height'] / 2) for p in predictions]
    scores = [p['confidence'] for p in predictions]
    indices = sorted(range(len(scores)), key=lambda k: scores[k], reverse=True)

    keep = []
    while len(indices) > 0:
        current = indices.pop(0)
        keep.append(current)
        remove = []
        for idx in indices:
            iou = compute_iou(boxes[current], boxes[idx])
            if iou > iou_threshold:
                remove.append(idx)
        indices = [idx for idx in indices if idx not in remove]

    return [predictions[idx] for idx in keep]

def compute_iou(box1, box2):
    x1, y1, x2, y2 = box1
    x1_, y1_, x2_, y2_ = box2

    inter_x1 = max(x1, x1_)
    inter_y1 = max(y1, y1_)
    inter_x2 = min(x2, x2_)
    inter_y2 = min(y2, y2_)

    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
    box1_area = (x2 - x1) * (y2 - y1)
    box2_area = (x2_ - x1_) * (y2_ - y1_)

    iou = inter_area / float(box1_area + box2_area - inter_area)
    return iou
