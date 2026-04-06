import uuid

from ..domain import (
    default_settings,
    default_teams,
    default_work_items,
    new_room,
    sanitize_points,
    sanitize_teams,
    sanitize_work_items,
)
from ..store import connections, rooms


def create_room(session_name):
    room_id = str(uuid.uuid4())[:6].upper()
    rooms[room_id] = new_room(session_name)
    return room_id


def resolve_team_id(room, requested_team_id):
    teams = room["settings"].get("teams", [])
    if not teams:
        teams = default_teams()
        room["settings"]["teams"] = teams

    valid_team_ids = {team["id"] for team in teams}
    if requested_team_id in valid_team_ids:
        return requested_team_id

    return teams[0]["id"]


def current_work_item(room):
    work_items = room.get("work_items") or default_work_items()
    index = room.get("current_work_item_index", 0)
    if index < 0 or index >= len(work_items):
        index = 0
        room["current_work_item_index"] = index
    return work_items[index]


def compute_group(room, team):
    team_id = team["id"]
    people = []
    for user_id, participant in room["participants"].items():
        if participant.get("participant_type") != "player":
            continue
        if participant.get("team") != team_id:
            continue

        vote_value = room["votes"].get(user_id, {}).get("vote")
        people.append({
            "user_id": user_id,
            "name": participant.get("name", "Anonymous"),
            "team": team_id,
            "team_name": team["name"],
            "participant_type": participant.get("participant_type", "player"),
            "has_voted": vote_value is not None,
            "vote": vote_value if room["revealed"] else None,
        })

    raw_votes = [person["vote"] for person in people if person["vote"] is not None]
    numeric_votes = []
    for vote in raw_votes:
        try:
            numeric_votes.append(float(vote))
        except (TypeError, ValueError):
            pass

    summary = {
        "count_voted": sum(1 for person in people if person["has_voted"]),
        "count_total": len(people),
        "average": round(sum(numeric_votes) / len(numeric_votes), 2) if numeric_votes else None,
        "min": min(numeric_votes) if numeric_votes else None,
        "max": max(numeric_votes) if numeric_votes else None,
        "consensus": None,
        "consensus_label": "No consensus yet",
    }

    if room["revealed"] and raw_votes:
        unique_votes = sorted(set(str(vote) for vote in raw_votes))
        if len(unique_votes) == 1:
            summary["consensus"] = unique_votes[0]
            summary["consensus_label"] = f"Consensus: {unique_votes[0]}"
        else:
            summary["consensus_label"] = "Split vote"

    return {
        "id": team_id,
        "name": team["name"],
        "participants": people,
        "summary": summary,
    }


def room_payload(room_id):
    room = rooms[room_id]
    teams = room["settings"].get("teams", default_teams())
    item = current_work_item(room)
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
        "story_title": item["title"],
        "story_description": item.get("description", ""),
        "revealed": room["revealed"],
        "settings": room["settings"],
        "work_items": room["work_items"],
        "current_work_item_index": room["current_work_item_index"],
        "current_work_item": item,
        "history": room["history"],
        "moderator_user_id": room["moderator_user_id"],
        "participants": participants,
        "teams": [compute_group(room, team) for team in teams],
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


def finalize_current_work_item(room):
    if not room["revealed"]:
        return

    item = current_work_item(room)
    team_results = []
    for team in room["settings"].get("teams", default_teams()):
        team_summary = compute_group(room, team)["summary"]
        team_results.append({
            "team_id": team["id"],
            "team_name": team["name"],
            "label": team_summary["consensus_label"],
        })

    room["history"].insert(0, {
        "work_item_id": item["id"],
        "work_item_number": room["current_work_item_index"] + 1,
        "work_item_title": item["title"] or f"Work Item {room['current_work_item_index'] + 1}",
        "work_item_description": item.get("description", ""),
        "team_results": team_results,
    })


def remove_participant(room_id, user_id, sid):
    room = rooms.get(room_id)
    if not room:
        return False

    participant = room["participants"].get(user_id)
    if participant and participant.get("sid") and participant.get("sid") != sid:
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
        else:
            rooms.pop(room_id, None)

    return True


def join_session(room_id, sid, data):
    room = rooms.setdefault(room_id, new_room())

    user_id = data["user_id"]
    is_first_join = len(room["participants"]) == 0
    participant_type = "observer" if is_first_join else data.get("participant_type", "player")
    requested_team = data.get("team")
    team = "" if participant_type == "observer" else resolve_team_id(room, requested_team)

    room["participants"][user_id] = {
        "user_id": user_id,
        "name": str(data.get("name", "Anonymous")).strip() or "Anonymous",
        "team": team,
        "participant_type": participant_type,
        "sid": sid,
    }

    if room["moderator_user_id"] is None:
        room["moderator_user_id"] = user_id

    connections[sid] = {"room_id": room_id, "user_id": user_id}
    return room_payload(room_id)


def update_presence(room_id, sid, data):
    room = rooms.get(room_id)
    if not room:
        return None

    user_id = data["user_id"]
    if user_id not in room["participants"]:
        return None

    if user_id == room.get("moderator_user_id"):
        participant_type = "observer"
        requested_team = ""
    else:
        participant_type = data.get("participant_type", room["participants"][user_id]["participant_type"])
        requested_team = resolve_team_id(
            room,
            data.get("team", room["participants"][user_id].get("team", "")),
        )

    room["participants"][user_id]["name"] = str(data.get("name", "Anonymous")).strip() or "Anonymous"
    room["participants"][user_id]["participant_type"] = participant_type
    room["participants"][user_id]["team"] = requested_team if participant_type == "player" else ""
    room["participants"][user_id]["sid"] = sid

    if participant_type != "player":
        room["votes"].pop(user_id, None)

    if room["moderator_user_id"] is None:
        room["moderator_user_id"] = user_id

    return room_payload(room_id)


def cast_vote(room_id, data):
    room = rooms.get(room_id)
    if not room:
        return None

    user_id = data["user_id"]
    participant = room["participants"].get(user_id)
    if not participant or participant.get("participant_type") != "player":
        return None

    room["votes"][user_id] = {"vote": str(data["value"])}
    return room_payload(room_id)


def reveal_votes(room_id, data):
    room = rooms.get(room_id)
    if not room:
        return None

    permissions = user_permissions(room, data.get("user_id"))
    if not permissions["can_show_votes"]:
        return None

    room["revealed"] = True
    return room_payload(room_id)


def reset_votes(room_id, data):
    room = rooms.get(room_id)
    if not room:
        return None

    permissions = user_permissions(room, data.get("user_id"))
    if not permissions["can_reset_votes"]:
        return None

    if room["revealed"]:
        finalize_current_work_item(room)

    room["votes"] = {}
    room["revealed"] = False
    return room_payload(room_id)


def update_story(room_id, data):
    room = rooms.get(room_id)
    if not room:
        return None

    requester_id = data.get("user_id")
    if requester_id != room.get("moderator_user_id"):
        return None

    room["session_name"] = str(data.get("session_name", room["session_name"])).strip() or room["session_name"]
    item = current_work_item(room)
    item["title"] = str(data.get("story_title", item["title"])).strip() or item["title"]
    item["description"] = str(data.get("story_description", item.get("description", ""))).strip()
    return room_payload(room_id)


def update_work_items(room_id, data):
    room = rooms.get(room_id)
    if not room:
        return None

    requester_id = data.get("user_id")
    if requester_id != room.get("moderator_user_id"):
        return None

    work_items = sanitize_work_items(data.get("work_items"))
    current_item_id = str(data.get("current_work_item_id", current_work_item(room)["id"]))
    room["work_items"] = work_items

    matched_index = next((index for index, item in enumerate(work_items) if item["id"] == current_item_id), None)
    requested_index = data.get("current_work_item_index")
    if matched_index is not None:
        room["current_work_item_index"] = matched_index
    elif isinstance(requested_index, int) and 0 <= requested_index < len(work_items):
        room["current_work_item_index"] = requested_index
    else:
        room["current_work_item_index"] = 0

    return room_payload(room_id)


def navigate_work_item(room_id, data):
    room = rooms.get(room_id)
    if not room:
        return None

    requester_id = data.get("user_id")
    if requester_id != room.get("moderator_user_id"):
        return None

    work_items = room.get("work_items") or default_work_items()
    current_index = room.get("current_work_item_index", 0)
    direction = str(data.get("direction", "next"))
    delta = -1 if direction == "previous" else 1
    next_index = current_index + delta
    if next_index < 0 or next_index >= len(work_items):
        return None

    if room["revealed"]:
        finalize_current_work_item(room)

    room["current_work_item_index"] = next_index
    room["votes"] = {}
    room["revealed"] = False
    return room_payload(room_id)


def update_settings(room_id, data):
    room = rooms.get(room_id)
    if not room:
        return None

    permissions = user_permissions(room, data.get("user_id"))
    if not permissions["can_edit_settings"]:
        return None

    incoming = data.get("settings", {})
    room["settings"]["show_story_description"] = bool(incoming.get("show_story_description", True))
    room["settings"]["show_history"] = bool(incoming.get("show_history", True))
    room["settings"]["show_team_boxes"] = bool(incoming.get("show_team_boxes", True))
    room["settings"]["allow_show_votes"] = {
        "players": bool(incoming.get("allow_show_votes", {}).get("players", False)),
        "observers": bool(incoming.get("allow_show_votes", {}).get("observers", True)),
    }
    room["settings"]["allow_reset_votes"] = {
        "players": bool(incoming.get("allow_reset_votes", {}).get("players", False)),
        "observers": bool(incoming.get("allow_reset_votes", {}).get("observers", True)),
    }
    room["settings"]["teams"] = sanitize_teams(incoming.get("teams"))
    room["settings"]["point_values"] = sanitize_points(incoming.get("point_values"))

    valid_team_ids = {team["id"] for team in room["settings"]["teams"]}
    fallback_team_id = room["settings"]["teams"][0]["id"]
    for participant in room["participants"].values():
        if participant.get("participant_type") != "player":
            participant["team"] = ""
            continue
        if participant.get("team") not in valid_team_ids:
            participant["team"] = fallback_team_id

    room["votes"] = {}
    room["revealed"] = False
    return room_payload(room_id)


def set_moderator(room_id, data):
    room = rooms.get(room_id)
    if not room:
        return None

    requester_id = data.get("requester_user_id")
    if requester_id != room.get("moderator_user_id"):
        return None

    target_id = data.get("target_user_id")
    target = room["participants"].get(target_id)
    if not target:
        return None

    room["moderator_user_id"] = target_id
    target["participant_type"] = "observer"
    target["team"] = ""
    room["votes"].pop(target_id, None)
    return room_payload(room_id)


def handle_disconnect(sid):
    connection = connections.pop(sid, None)
    if not connection:
        return None, None

    room_id = connection["room_id"]
    user_id = connection["user_id"]

    if remove_participant(room_id, user_id, sid) and room_id in rooms:
        return room_id, room_payload(room_id)

    return None, None
