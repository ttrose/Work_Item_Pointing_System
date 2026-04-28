import os


def parse_allowed_origins():
    raw = os.getenv("CORS_ORIGIN", "*")
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or ["*"]


def build_config():
    return {
        "SECRET_KEY": os.getenv("SECRET_KEY", "dev-only-change-me"),
        "ALLOWED_ORIGINS": parse_allowed_origins(),
        "PORT": int(os.getenv("PORT", "5000")),
        "FLASK_DEBUG": os.getenv("FLASK_DEBUG", "true").lower() == "true",
    }
