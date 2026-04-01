from flask import jsonify, render_template, request
from flask_cors import CORS

from config import INFERENCE_SERVICE_URL
from services.inference_remote import RemoteInferenceClient

_remote_client = None


def _get_remote_client():
    global _remote_client
    if _remote_client is None:
        _remote_client = RemoteInferenceClient(INFERENCE_SERVICE_URL)
    return _remote_client


def setup_routes(app):
    CORS(app)

    @app.route("/")
    def index():
        return render_template("home.html")

    @app.route("/app")
    def app_page():
        return render_template("app.html")

    @app.route("/infer", methods=["POST"])
    def infer():
        if "image" not in request.files:
            return jsonify({"error": "Nenhum arquivo de imagem fornecido"}), 400

        image_file = request.files["image"]
        if image_file.filename == "":
            return jsonify({"error": "Nenhum arquivo selecionado"}), 400

        try:
            return jsonify(_get_remote_client().infer(image_file))
        except RuntimeError as e:
            return jsonify({"error": str(e)}), 502
        except Exception as e:
            return jsonify({"error": str(e)}), 500
