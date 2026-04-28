from copy import deepcopy
from time import time


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

DEFAULT_TEAMS = [
    {"id": "team-1", "name": "Team 1"},
]

DEFAULT_WORK_ITEMS = [
    {"id": "work-item-1", "title": "Work Item 1", "description": "", "elapsed_ms": 0, "timer_started_at": None},
]


def now_ms():
    return int(time() * 1000)


def default_teams():
    return deepcopy(DEFAULT_TEAMS)


def default_work_items():
    return deepcopy(DEFAULT_WORK_ITEMS)


def default_settings():
    return {
        "show_story_description": True,
        "show_history": True,
        "show_team_boxes": True,
        "allow_observer_moderator_permissions": False,
        "allow_show_votes": {"players": False, "observers": True},
        "allow_reset_votes": {"players": False, "observers": True},
        "teams": default_teams(),
        "point_values": deepcopy(DEFAULT_POINT_VALUES),
    }


def new_room(name="Untitled Session"):
    return {
        "session_name": name,
        "revealed": False,
        "votes": {},
        "participants": {},
        "settings": default_settings(),
        "work_items": default_work_items(),
        "current_work_item_index": 0,
        "history": [],
        "team_change_requests": [],
        "moderator_user_id": None,
    }


def sanitize_points(items):
    cleaned = []
    for item in items or []:
        label = str(item.get("label", "")).strip()
        value = str(item.get("value", "")).strip()
        if label and value:
            cleaned.append({"label": label, "value": value})
    return cleaned or deepcopy(DEFAULT_POINT_VALUES)


def sanitize_teams(items):
    cleaned = []
    seen_ids = set()

    for index, item in enumerate(items or []):
        team_id = str(item.get("id", "")).strip() or f"team-{index + 1}"
        team_name = str(item.get("name", "")).strip()
        if not team_name or team_id in seen_ids:
            continue
        seen_ids.add(team_id)
        cleaned.append({"id": team_id, "name": team_name})

    return cleaned or default_teams()


def sanitize_work_items(items):
    cleaned = []

    for index, item in enumerate(items or []):
        item_id = str(item.get("id", "")).strip() or f"work-item-{index + 1}"
        title = str(item.get("title", "")).strip()
        description = str(item.get("description", "")).strip()
        if not title:
            continue
        cleaned.append({
            "id": item_id,
            "title": title,
            "description": description,
            "elapsed_ms": 0,
            "timer_started_at": None,
        })

    return cleaned or default_work_items()
