from config import CONFIDENCE_THRESHOLD, IOU_THRESHOLD
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import base64
import io
import os

_MODEL_FILENAME = "egg_detection_yolov8n_final.pt"


def resolve_model_path():
    env = (os.environ.get("MODEL_PATH") or "").strip()
    if env and os.path.isfile(env):
        return os.path.abspath(env)
    services_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.dirname(services_dir)
    repo_root = os.path.dirname(app_dir)
    for candidate in (
        os.path.join(services_dir, _MODEL_FILENAME),
        os.path.join(app_dir, _MODEL_FILENAME),
        os.path.join(repo_root, _MODEL_FILENAME),
    ):
        if os.path.isfile(candidate):
            return candidate
    raise FileNotFoundError(
        f"Modelo não encontrado ({_MODEL_FILENAME}). "
        "Coloque o arquivo em app/services/, app/ ou na raiz do repositório, "
        "ou defina MODEL_PATH com o caminho absoluto."
    )


class InferenceService:
    def __init__(self):
        model_path = resolve_model_path()
        self.model = YOLO(model_path)

    def process_image(self, image_file):
        image = Image.open(image_file)
        if image.mode != "RGB":
            image = image.convert("RGB")

        results = self.model(
            image,
            conf=CONFIDENCE_THRESHOLD,
            iou=IOU_THRESHOLD,
            verbose=False,
        )

        predictions = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())

                    width = x2 - x1
                    height = y2 - y1
                    center_x = x1 + width / 2
                    center_y = y1 + height / 2

                    class_name = self.model.names[class_id]

                    if class_name == "f":
                        class_name = "fertile"
                    elif class_name == "i":
                        class_name = "infertile"

                    predictions.append(
                        {
                            "x": center_x,
                            "y": center_y,
                            "width": width,
                            "height": height,
                            "confidence": confidence,
                            "class": class_name,
                        }
                    )

        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        class_colors = {
            "fertile": "green",
            "infertile": "red",
        }

        for prediction in predictions:
            x = prediction["x"]
            y = prediction["y"]
            width = prediction["width"]
            height = prediction["height"]
            confidence = prediction["confidence"]
            class_name = prediction["class"]

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
            color = class_colors.get(prediction["class"], "blue")

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

    @staticmethod
    def build_response(predictions, img_with_detections_str):
        detections = []
        for prediction in predictions:
            detections.append(
                {
                    "class": prediction["class"],
                    "confidence": float(round(prediction["confidence"], 3)),
                    "bbox": {
                        "x": float(round(prediction["x"], 2)),
                        "y": float(round(prediction["y"], 2)),
                        "width": float(round(prediction["width"], 2)),
                        "height": float(round(prediction["height"], 2)),
                    },
                }
            )
        return {
            "success": True,
            "detections": detections,
            "total_detections": len(detections),
            "image_with_detections": img_with_detections_str,
        }
