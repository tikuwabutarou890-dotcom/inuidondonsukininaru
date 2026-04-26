 # ▼ __init__.py
from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")

    # ▼ DB 初期化（絶対必要）
    from .database import init_db
    init_db()

    # ▼ main ルート
    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    # ▼ schedule API（これがないと 404）
    from .schedule import bp as schedule_bp
    app.register_blueprint(schedule_bp)

    return app

app = create_app()
