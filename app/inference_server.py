"""
Microserviço HTTP só para inferência YOLO (deploy e monitoramento isolados).

  cd app && python inference_server.py

Variáveis: MODEL_PATH, INFERENCE_SERVER_PORT (padrão 5002).

A app web encaminha POST /infer para esta API (INFERENCE_SERVICE_URL na app).
"""
import os

from flask import Flask, jsonify, request

from config import INFERENCE_SERVER_PORT
from services.inference_service import InferenceService

app = Flask(__name__)

_svc = None


def get_inference():
    global _svc
    if _svc is None:
        _svc = InferenceService()
    return _svc


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "inference"})


@app.route("/infer", methods=["POST"])
def infer():
    if "image" not in request.files:
        return jsonify({"error": "Nenhum arquivo de imagem fornecido"}), 400
    image_file = request.files["image"]
    if not image_file.filename:
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
    try:
        svc = get_inference()
        predictions, img_b64 = svc.process_image(image_file)
        return jsonify(InferenceService.build_response(predictions, img_b64))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("INFERENCE_SERVER_PORT", str(INFERENCE_SERVER_PORT)))
    get_inference()
    app.run(
        debug=True,
        use_reloader=False,
        threaded=True,
        host="0.0.0.0",
        port=port,
    )
