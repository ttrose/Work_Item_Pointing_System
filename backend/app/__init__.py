from flask import Flask
from flask_cors import CORS

from .config import build_config
from .extensions import socketio
from .routes import api_bp
from .sockets import register_socket_handlers


def create_app():
    config = build_config()

    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=config["SECRET_KEY"],
        PORT=config["PORT"],
        FLASK_DEBUG=config["FLASK_DEBUG"],
        ALLOWED_ORIGINS=config["ALLOWED_ORIGINS"],
    )

    CORS(app, resources={r"/*": {"origins": app.config["ALLOWED_ORIGINS"]}})
    socketio.init_app(
        app,
        cors_allowed_origins=app.config["ALLOWED_ORIGINS"],
        async_mode="threading",
    )

    app.register_blueprint(api_bp)
    register_socket_handlers(socketio)

    return app
