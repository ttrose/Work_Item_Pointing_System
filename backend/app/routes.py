from flask import Blueprint, jsonify, request

from .services.session_service import create_room


api_bp = Blueprint("api", __name__)


@api_bp.get("/health")
def health():
    return jsonify({"ok": True})


@api_bp.post("/create")
def create_session():
    payload = request.get_json(silent=True) or {}
    session_name = str(payload.get("session_name", "Untitled Session")).strip() or "Untitled Session"
    room_id = create_room(session_name)
    return jsonify({"room": room_id})
