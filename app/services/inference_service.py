from config import CONFIDENCE_THRESHOLD, IOU_THRESHOLD
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import base64
import io
import os

class InferenceService:
    def __init__(self):
        # Caminho para o modelo YOLOv8 treinado
        model_path = os.path.join(os.path.dirname(__file__), '..', 'egg_detection_yolov8n_final.pt')
        self.model = YOLO(model_path)

    def process_image(self, image_file):
        image = Image.open(image_file)
        
        # Executa inferência com YOLOv8
        results = self.model(image, conf=CONFIDENCE_THRESHOLD, iou=IOU_THRESHOLD)
        
        # Converte resultados do YOLOv8 para formato compatível
        predictions = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Extrai coordenadas e informações
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    # Converte para formato esperado (centro + largura/altura)
                    width = x2 - x1
                    height = y2 - y1
                    center_x = x1 + width / 2
                    center_y = y1 + height / 2
                    
                    # Mapeia class_id para nome da classe
                    class_name = self.model.names[class_id]
                    
                    # Mapeia as classes do modelo para nomes padronizados
                    if class_name == 'f':
                        class_name = 'fertile'
                    elif class_name == 'i':
                        class_name = 'infertile'
                    
                    predictions.append({
                        'x': center_x,
                        'y': center_y,
                        'width': width,
                        'height': height,
                        'confidence': confidence,
                        'class': class_name
                    })

        # Desenha as detecções na imagem
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        class_colors = {
            "fertile": "green",
            "infertile": "red",
        }

        for prediction in predictions:
            x = prediction['x']
            y = prediction['y']
            width = prediction['width']
            height = prediction['height']
            confidence = prediction['confidence']
            class_name = prediction['class']
            
            # Traduz nomes das classes para português para exibição
            display_name = class_name
            if class_name == "fertile":
                display_name = "fertil"
            elif class_name == "infertile":
                display_name = "infertil"
            
            label = f"{display_name} {confidence:.0%}"
            left = x - width / 2
            top = y - height / 2
            right = x + width / 2
            bottom = y + height / 2
            color = class_colors.get(prediction['class'], "blue")
            
            # Desenha retângulo
            draw.rectangle([left, top, right, bottom], outline=color, width=2)
            
            # Desenha label
            text_bbox = draw.textbbox((0, 0), label, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            draw.rectangle([left, top - text_height, left + text_width, top], fill=color)
            draw.text((left, top - text_height), label, fill="white", font=font)

        # Converte imagem para base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_with_detections_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return predictions, img_with_detections_str

