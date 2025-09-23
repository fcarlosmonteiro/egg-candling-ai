from flask import request, jsonify, render_template
from flask_cors import CORS
from services.inference_service import InferenceService

inference_service = InferenceService()

def setup_routes(app):
    CORS(app)
    
    @app.route('/')
    def index():
        return render_template('home.html')
    
    @app.route('/app')
    def app_page():
        return render_template('app.html')

    @app.route('/infer', methods=['POST'])
    def infer():
        if 'image' not in request.files:
            return jsonify({'error': 'Nenhum arquivo de imagem fornecido'}), 400
        
        image_file = request.files['image']
        
        # Validação básica do arquivo
        if image_file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        try:
            results, img_with_detections_str = inference_service.process_image(image_file)
            
            # Converte resultados para formato JSON
            detections = []
            for prediction in results:
                detections.append({
                    'class': prediction['class'],
                    'confidence': float(round(prediction['confidence'], 3)),
                    'bbox': {
                        'x': float(round(prediction['x'], 2)),
                        'y': float(round(prediction['y'], 2)),
                        'width': float(round(prediction['width'], 2)),
                        'height': float(round(prediction['height'], 2))
                    }
                })
            
            return jsonify({
                'success': True,
                'detections': detections,
                'total_detections': len(detections),
                'image_with_detections': img_with_detections_str
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
