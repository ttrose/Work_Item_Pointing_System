from app import create_app
from app.extensions import socketio


app = create_app()


if __name__ == "__main__":
    socketio.run(
        app=app,
        host="0.0.0.0",
        port=app.config["PORT"],
        debug=app.config["FLASK_DEBUG"],
        allow_unsafe_werkzeug=False,
    )
