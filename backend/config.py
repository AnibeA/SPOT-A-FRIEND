import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "supersecretkey"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"  # ✅ Ensure this is set
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "a5c36a62868e4920af2a80e69c24506a")
    SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "19dc1fb765e84ea8bed946735948acfc")
    SPOTIFY_REDIRECT_URI = "http://127.0.0.1:5000/callback"
