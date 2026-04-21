from flask import Blueprint, jsonify, request

from .services.session_service import create_room, get_room_payload


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


@api_bp.get("/rooms/<room_id>")
def get_room(room_id):
    payload = get_room_payload(room_id)
    if payload is None:
        return jsonify({"error": "Room not found"}), 404
    return jsonify(payload)
