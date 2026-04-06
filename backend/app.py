from copy import deepcopy
import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "fusion-planning-poker"
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

rooms = {}
connections = {}

DEFAULT_POINT_VALUES = [
    {"label": "0 points", "value": "0"},
    {"label": "½ point", "value": "0.5"},
    {"label": "1 point", "value": "1"},
    {"label": "2 points", "value": "2"},
    {"label": "3 points", "value": "3"},
    {"label": "5 points", "value": "5"},
    {"label": "8 points", "value": "8"},
    {"label": "13 points", "value": "13"},
    {"label": "20 points", "value": "20"},
    {"label": "40 points", "value": "40"},
    {"label": "100 points", "value": "100"},
    {"label": "?", "value": "?"},
]

def default_settings():
    return {
        "show_story_description": True,
        "show_history": True,
        "allow_show_votes": {"players": False, "observers": True},
        "allow_reset_votes": {"players": False, "observers": True},
        "point_values": deepcopy(DEFAULT_POINT_VALUES),
    }

def new_room(name="Untitled Session"):
    return {
        "session_name": name,
        "story_title": "",
        "story_description": "",
        "revealed": False,
        "votes": {},
        "participants": {},
        "settings": default_settings(),
        "history": [],
        "moderator_user_id": None,
    }

def remove_participant(room_id, user_id):
    room = rooms.get(room_id)
    if not room:
        return False

    participant = room["participants"].get(user_id)
    if participant and participant.get("sid") and participant.get("sid") != request.sid:
        return False

    removed = room["participants"].pop(user_id, None)
    room["votes"].pop(user_id, None)

    if removed is None:
        return False

    if room["moderator_user_id"] == user_id:
        remaining_ids = list(room["participants"].keys())
        room["moderator_user_id"] = remaining_ids[0] if remaining_ids else None
        if room["moderator_user_id"]:
            new_moderator = room["participants"][room["moderator_user_id"]]
            new_moderator["participant_type"] = "observer"
            new_moderator["team"] = ""
            room["votes"].pop(room["moderator_user_id"], None)

    return True

def sanitize_points(items):
    cleaned = []
    for item in items or []:
        label = str(item.get("label", "")).strip()
        value = str(item.get("value", "")).strip()
        if label and value:
            cleaned.append({"label": label, "value": value})
    return cleaned or deepcopy(DEFAULT_POINT_VALUES)

def compute_group(room, team_name):
    people = []
    for user_id, participant in room["participants"].items():
        if participant.get("participant_type") != "player":
            continue
        if participant.get("team") != team_name:
            continue

        vote_value = room["votes"].get(user_id, {}).get("vote")
        people.append({
            "user_id": user_id,
            "name": participant.get("name", "Anonymous"),
            "team": team_name,
            "participant_type": participant.get("participant_type", "player"),
            "has_voted": vote_value is not None,
            "vote": vote_value if room["revealed"] else None,
        })

    raw_votes = [p["vote"] for p in people if p["vote"] is not None]
    numeric_votes = []
    for vote in raw_votes:
        try:
            numeric_votes.append(float(vote))
        except (TypeError, ValueError):
            pass

    summary = {
        "count_voted": sum(1 for p in people if p["has_voted"]),
        "count_total": len(people),
        "average": round(sum(numeric_votes) / len(numeric_votes), 2) if numeric_votes else None,
        "min": min(numeric_votes) if numeric_votes else None,
        "max": max(numeric_votes) if numeric_votes else None,
        "consensus": None,
        "consensus_label": "No consensus yet",
    }

    if room["revealed"] and raw_votes:
        unique_votes = sorted(set(str(v) for v in raw_votes))
        if len(unique_votes) == 1:
            summary["consensus"] = unique_votes[0]
            summary["consensus_label"] = f"Consensus: {unique_votes[0]}"
        else:
            summary["consensus_label"] = "Split vote"

    return {"participants": people, "summary": summary}

def room_payload(room_id):
    room = rooms[room_id]
    participants = []
    for participant in room["participants"].values():
        participants.append({
            "user_id": participant.get("user_id"),
            "name": participant.get("name", "Anonymous"),
            "team": participant.get("team", ""),
            "participant_type": participant.get("participant_type", "player"),
        })

    return {
        "room_id": room_id,
        "session_name": room["session_name"],
        "story_title": room["story_title"],
        "story_description": room["story_description"],
        "revealed": room["revealed"],
        "settings": room["settings"],
        "history": room["history"],
        "moderator_user_id": room["moderator_user_id"],
        "participants": participants,
        "dev": compute_group(room, "DEV"),
        "qa": compute_group(room, "QA"),
    }

def user_permissions(room, user_id):
    participant_type = room["participants"].get(user_id, {}).get("participant_type", "player")
    is_player = participant_type == "player"
    key = "players" if is_player else "observers"
    return {
        "can_vote": is_player,
        "can_show_votes": bool(room["settings"]["allow_show_votes"].get(key)),
        "can_reset_votes": bool(room["settings"]["allow_reset_votes"].get(key)),
        "can_edit_settings": user_id == room.get("moderator_user_id"),
    }

@app.get("/health")
def health():
    return jsonify({"ok": True})

@app.post("/create")
def create_session():
    payload = request.get_json(silent=True) or {}
    room_id = str(uuid.uuid4())[:6].upper()
    session_name = str(payload.get("session_name", "Untitled Session")).strip() or "Untitled Session"
    rooms[room_id] = new_room(session_name)
    return jsonify({"room": room_id})

@socketio.on("join")
def on_join(data):
    room_id = data["room"]
    room = rooms.setdefault(room_id, new_room())

    user_id = data["user_id"]
    is_first_join = len(room["participants"]) == 0
    participant_type = "observer" if is_first_join else data.get("participant_type", "player")
    team = "" if participant_type == "observer" else data.get("team", "DEV")

    room["participants"][user_id] = {
        "user_id": user_id,
        "name": str(data.get("name", "Anonymous")).strip() or "Anonymous",
        "team": team,
        "participant_type": participant_type,
        "sid": request.sid,
    }

    if room["moderator_user_id"] is None:
        room["moderator_user_id"] = user_id

    join_room(room_id)
    connections[request.sid] = {"room_id": room_id, "user_id": user_id}
    emit("state", room_payload(room_id), room=room_id)

@socketio.on("update_presence")
def on_update_presence(data):
    room_id = data["room"]
    room = rooms.get(room_id)
    if not room:
        return

    user_id = data["user_id"]
    if user_id not in room["participants"]:
        return

    if user_id == room.get("moderator_user_id"):
        participant_type = "observer"
        requested_team = ""
    else:
        participant_type = data.get("participant_type", room["participants"][user_id]["participant_type"])
        requested_team = data.get("team", room["participants"][user_id].get("team", "DEV"))

    room["participants"][user_id]["name"] = str(data.get("name", "Anonymous")).strip() or "Anonymous"
    room["participants"][user_id]["participant_type"] = participant_type
    room["participants"][user_id]["team"] = requested_team if participant_type == "player" else ""
    room["participants"][user_id]["sid"] = request.sid

    if participant_type != "player":
        room["votes"].pop(user_id, None)

    if room["moderator_user_id"] is None:
        room["moderator_user_id"] = user_id

    emit("state", room_payload(room_id), room=room_id)

@socketio.on("vote")
def on_vote(data):
    room_id = data["room"]
    room = rooms.get(room_id)
    if not room:
        return

    user_id = data["user_id"]
    participant = room["participants"].get(user_id)
    if not participant or participant.get("participant_type") != "player":
        return

    room["votes"][user_id] = {"vote": str(data["value"])}
    emit("state", room_payload(room_id), room=room_id)

@socketio.on("reveal")
def on_reveal(data):
    room_id = data["room"]
    room = rooms.get(room_id)
    if not room:
        return

    permissions = user_permissions(room, data.get("user_id"))
    if not permissions["can_show_votes"]:
        return

    room["revealed"] = True
    emit("state", room_payload(room_id), room=room_id)

@socketio.on("reset_votes")
def on_reset_votes(data):
    room_id = data["room"]
    room = rooms.get(room_id)
    if not room:
        return

    permissions = user_permissions(room, data.get("user_id"))
    if not permissions["can_reset_votes"]:
        return

    if room["revealed"]:
        dev_summary = compute_group(room, "DEV")["summary"]
        qa_summary = compute_group(room, "QA")["summary"]
        room["history"].insert(0, {
            "story_title": room["story_title"] or "Untitled Story",
            "dev_label": dev_summary["consensus_label"],
            "qa_label": qa_summary["consensus_label"],
        })
        room["history"] = room["history"][:20]

    room["votes"] = {}
    room["revealed"] = False
    emit("state", room_payload(room_id), room=room_id)

@socketio.on("update_story")
def on_update_story(data):
    room_id = data["room"]
    room = rooms.get(room_id)
    if not room:
        return

    requester_id = data.get("user_id")
    if requester_id != room.get("moderator_user_id"):
        return

    room["session_name"] = str(data.get("session_name", room["session_name"])).strip() or room["session_name"]
    room["story_title"] = str(data.get("story_title", room["story_title"])).strip()
    room["story_description"] = str(data.get("story_description", room["story_description"])).strip()
    emit("state", room_payload(room_id), room=room_id)

@socketio.on("update_settings")
def on_update_settings(data):
    room_id = data["room"]
    room = rooms.get(room_id)
    if not room:
        return

    permissions = user_permissions(room, data.get("user_id"))
    if not permissions["can_edit_settings"]:
        return

    incoming = data.get("settings", {})
    room["settings"]["show_story_description"] = bool(incoming.get("show_story_description", True))
    room["settings"]["show_history"] = bool(incoming.get("show_history", True))
    room["settings"]["allow_show_votes"] = {
        "players": bool(incoming.get("allow_show_votes", {}).get("players", False)),
        "observers": bool(incoming.get("allow_show_votes", {}).get("observers", True)),
    }
    room["settings"]["allow_reset_votes"] = {
        "players": bool(incoming.get("allow_reset_votes", {}).get("players", False)),
        "observers": bool(incoming.get("allow_reset_votes", {}).get("observers", True)),
    }
    room["settings"]["point_values"] = sanitize_points(incoming.get("point_values"))
    room["votes"] = {}
    room["revealed"] = False

    emit("state", room_payload(room_id), room=room_id)

@socketio.on("set_moderator")
def on_set_moderator(data):
    room_id = data["room"]
    room = rooms.get(room_id)
    if not room:
        return

    requester_id = data.get("requester_user_id")
    if requester_id != room.get("moderator_user_id"):
        return

    target_id = data.get("target_user_id")
    target = room["participants"].get(target_id)
    if not target:
        return

    room["moderator_user_id"] = target_id
    target["participant_type"] = "observer"
    target["team"] = ""
    room["votes"].pop(target_id, None)
    emit("state", room_payload(room_id), room=room_id)

@socketio.on("disconnect")
def on_disconnect():
    connection = connections.pop(request.sid, None)
    if not connection:
        return

    room_id = connection["room_id"]
    user_id = connection["user_id"]

    if remove_participant(room_id, user_id):
        emit("state", room_payload(room_id), room=room_id)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
