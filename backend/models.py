import requests
from datetime import datetime, timedelta
from flask import jsonify
from backend.extensions import db
from backend.config import Config

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

class User(db.Model):
    """
    Database model to store Spotify user authentication details and listening data.
    """
    id = db.Column(db.Integer, primary_key=True)  # Unique user ID
    spotify_id = db.Column(db.String(80), unique=True, nullable=False)  # ✅ Unique Spotify User ID
    access_token = db.Column(db.String(500), nullable=False)  # Spotify Access Token
    refresh_token = db.Column(db.String(500), nullable=True)  # Spotify Refresh Token
    expires_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(seconds=3600))  

    # ✅ New Columns for Listening Data
    top_artists = db.Column(db.Text, nullable=True)  # JSON-encoded list of top artists
    top_tracks = db.Column(db.Text, nullable=True)  # JSON-encoded list of top tracks
    top_genres = db.Column(db.Text, nullable=True)  # JSON-encoded list of top genres

    def __repr__(self):
        return f"<User {self.spotify_id}>"

    def is_token_expired(self):
        """Check if the user's Spotify access token is expired."""
        return datetime.utcnow() > self.expires_at

    def update_tokens(self, new_access_token, expires_in=3600):
        """Update the user's access token and refreshes expiration time."""
        self.access_token = new_access_token
        self.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        db.session.commit()

    def update_listening_data(self, artists, tracks, genres):
        """Update user's top artists, top tracks, and top genres."""
        self.top_artists = artists
        self.top_tracks = tracks
        self.top_genres = genres
        db.session.commit()

def refresh_access_token(user):
    """Refresh the user's Spotify access token if expired."""
    if not user.is_token_expired():
        return user.access_token  

    if not user.refresh_token:
        return jsonify({"error": "No refresh token available"}), 400

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": user.refresh_token,
        "client_id": Config.SPOTIFY_CLIENT_ID,
        "client_secret": Config.SPOTIFY_CLIENT_SECRET,
    }

    response = requests.post(SPOTIFY_TOKEN_URL, data=payload)
    token_info = response.json()

    if "access_token" not in token_info:
        return jsonify({"error": "Failed to refresh access token"}), 400

    user.access_token = token_info["access_token"]
    user.expires_at = datetime.utcnow() + timedelta(seconds=3600)
    db.session.commit()

    return user.access_token
