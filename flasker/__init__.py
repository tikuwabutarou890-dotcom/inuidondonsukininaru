from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()  # ← .env を読み込む

    app = Flask(__name__)

    # セッション用の secret_key
    app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")

    # Blueprint 読み込み
    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    return app

