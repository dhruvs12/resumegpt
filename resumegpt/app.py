from flask import Flask
from flask_cors import CORS
from .services.api_handler import api as api_blueprint

def create_app():
    app = Flask(__name__)
    
    # Enable CORS properly
    CORS(app, resources={
        r"/api/*": {
            "origins": ["chrome-extension://*", "http://localhost:*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    app.register_blueprint(api_blueprint, url_prefix='/api')
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True) 