from flask_socketio import emit, join_room
from flask import request

from .services.session_service import (
    cast_vote,
    claim_moderator,
    handle_disconnect,
    join_session,
    navigate_work_item,
    request_team_change,
    reset_votes,
    reveal_votes,
    respond_team_change_request,
    set_current_work_item,
    set_moderator,
    update_presence,
    update_settings,
    update_story,
    update_work_items,
)


def emit_if_payload(room_id, payload):
    if payload is not None:
        emit("state", payload, room=room_id)


def register_socket_handlers(socketio):
    @socketio.on("join")
    def on_join(data):
        room_id = data["room"]
        payload = join_session(room_id, request.sid, data)
        join_room(room_id)
        emit_if_payload(room_id, payload)

    @socketio.on("update_presence")
    def on_update_presence(data):
        room_id = data["room"]
        payload = update_presence(room_id, request.sid, data)
        emit_if_payload(room_id, payload)

    @socketio.on("vote")
    def on_vote(data):
        room_id = data["room"]
        payload = cast_vote(room_id, data)
        emit_if_payload(room_id, payload)

    @socketio.on("reveal")
    def on_reveal(data):
        room_id = data["room"]
        payload = reveal_votes(room_id, data)
        emit_if_payload(room_id, payload)

    @socketio.on("reset_votes")
    def on_reset_votes(data):
        room_id = data["room"]
        payload = reset_votes(room_id, data)
        emit_if_payload(room_id, payload)

    @socketio.on("request_team_change")
    def on_request_team_change(data):
        room_id = data["room"]
        payload = request_team_change(room_id, data)
        emit_if_payload(room_id, payload)

    @socketio.on("respond_team_change_request")
    def on_respond_team_change_request(data):
        room_id = data["room"]
        payload = respond_team_change_request(room_id, data)
        emit_if_payload(room_id, payload)

    @socketio.on("update_story")
    def on_update_story(data):
        room_id = data["room"]
        payload = update_story(room_id, data)
        emit_if_payload(room_id, payload)

    @socketio.on("update_settings")
    def on_update_settings(data):
        room_id = data["room"]
        payload = update_settings(room_id, data)
        emit_if_payload(room_id, payload)

    @socketio.on("update_work_items")
    def on_update_work_items(data):
        room_id = data["room"]
        payload = update_work_items(room_id, data)
        emit_if_payload(room_id, payload)

    @socketio.on("navigate_work_item")
    def on_navigate_work_item(data):
        room_id = data["room"]
        payload = navigate_work_item(room_id, data)
        emit_if_payload(room_id, payload)

    @socketio.on("set_current_work_item")
    def on_set_current_work_item(data):
        room_id = data["room"]
        payload = set_current_work_item(room_id, data)
        emit_if_payload(room_id, payload)

    @socketio.on("set_moderator")
    def on_set_moderator(data):
        room_id = data["room"]
        payload = set_moderator(room_id, data)
        emit_if_payload(room_id, payload)

    @socketio.on("claim_moderator")
    def on_claim_moderator(data):
        room_id = data["room"]
        payload = claim_moderator(room_id, data)
        emit_if_payload(room_id, payload)

    @socketio.on("disconnect")
    def on_disconnect():
        room_id, payload = handle_disconnect(request.sid)
        emit_if_payload(room_id, payload)
