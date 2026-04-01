import os

# Parâmetros YOLO (usados apenas pelo microserviço inference_server + inference_service)
CONFIDENCE_THRESHOLD = 0.6
IOU_THRESHOLD = 0.3

# App web: URL base do microserviço. Se vazio, usa localhost (dev sem export).
_DEFAULT_INFERENCE_URL = "http://127.0.0.1:5002"
_raw_infer_url = (os.environ.get("INFERENCE_SERVICE_URL") or "").strip().rstrip("/")
INFERENCE_SERVICE_URL = _raw_infer_url or _DEFAULT_INFERENCE_URL
INFERENCE_REQUEST_TIMEOUT = int(os.environ.get("INFERENCE_REQUEST_TIMEOUT", "120"))

# Porta padrão do inference_server.py
INFERENCE_SERVER_PORT = int(os.environ.get("INFERENCE_SERVER_PORT", "5002"))
