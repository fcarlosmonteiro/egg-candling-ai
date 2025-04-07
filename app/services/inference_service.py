from config import API_URL, API_KEY, MODEL_ID, CONFIDENCE_THRESHOLD, IOU_THRESHOLD
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw, ImageFont
import base64
import io

class InferenceService:
    def __init__(self):
        self.client = InferenceHTTPClient(api_url=API_URL, api_key=API_KEY)

    def process_image(self, image_file):
        image = Image.open(image_file)
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        result = self.client.infer(img_str, model_id=MODEL_ID)

        predictions = [p for p in result['predictions'] if p['confidence'] >= CONFIDENCE_THRESHOLD]
        predictions = self.non_max_suppression(predictions, IOU_THRESHOLD)

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
            if class_name == "fertile":
                class_name = "fertil"
            elif class_name == "infertile":
                class_name = "infertil"
            label = f"{class_name} {confidence:.0%}"
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

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_with_detections_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return predictions, img_with_detections_str

    def non_max_suppression(self, predictions, iou_threshold):
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
                iou = self.compute_iou(boxes[current], boxes[idx])
                if iou > iou_threshold:
                    remove.append(idx)
            indices = [idx for idx in indices if idx not in remove]

        return [predictions[idx] for idx in keep]

    def compute_iou(self, box1, box2):
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
