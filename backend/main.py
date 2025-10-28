from flask import Flask
from flask_cors import CORS
from backend.api.routes import bp
import os

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.secret_key = os.getenv("APP_SESSION_SECRET", "supersecretkey")
    CORS(app, supports_credentials=True)

    app.register_blueprint(bp)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
