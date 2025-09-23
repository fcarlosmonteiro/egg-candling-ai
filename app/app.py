from flask import Flask
from controllers.egg_detector import setup_routes

app = Flask(__name__)
setup_routes(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
