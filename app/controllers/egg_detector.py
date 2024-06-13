from flask import request, jsonify, render_template
from services.inference_service import InferenceService

inference_service = InferenceService()

def setup_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/infer', methods=['POST'])
    def infer():
        if 'image' not in request.files:
            return jsonify({'error': 'Nenhum arquivo de imagem fornecido'}), 400
        
        image_file = request.files['image']
        try:
            results, img_with_detections_str = inference_service.process_image(image_file)
            return render_template('index.html', results=results, image_data=img_with_detections_str)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
