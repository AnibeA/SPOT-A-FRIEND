import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode
from flask import Blueprint, redirect, request, session, jsonify
from backend.config import Config
from backend.models import db, User

# ✅ Create a Blueprint for authentication-related routes
auth = Blueprint("auth", __name__)

# ✅ Spotify API URLs and required scopes for authentication
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1/"
SCOPE = "user-read-recently-played user-top-read user-library-read user-read-private"
FRONTEND_REDIRECT_URI = "http://127.0.0.1:3000/dashboard"

# ----------------------------------------------
# ✅ ROUTE: /login - Redirects user to Spotify for authentication
# ----------------------------------------------
@auth.route("/login")
def login():
    """Redirect user to Spotify authorization page (forces login)."""
    params = {
        "client_id": Config.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": Config.SPOTIFY_REDIRECT_URI,
        "scope": SCOPE,
        "show_dialog": "true",  # ✅ Forces Spotify to ask for login every time
    }
    auth_url = f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)


# ----------------------------------------------
# ✅ ROUTE: /callback - Handles Spotify OAuth callback & saves user data
# ----------------------------------------------
@auth.route("/callback")
def callback():
    """Handle the Spotify OAuth callback and save user data."""
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Authorization failed"}), 400

    # Exchange authorization code for access token
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": Config.SPOTIFY_REDIRECT_URI,
        "client_id": Config.SPOTIFY_CLIENT_ID,
        "client_secret": Config.SPOTIFY_CLIENT_SECRET,
    }

    response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
    
    try:
        token_info = response.json()
    except requests.exceptions.JSONDecodeError:
        return jsonify({"error": "Failed to retrieve access token from Spotify"}), 400

    if "access_token" not in token_info:
        return jsonify({"error": "Failed to retrieve access token"}), 400

    access_token = token_info["access_token"]
    refresh_token = token_info.get("refresh_token")
    expires_in = token_info.get("expires_in", 3600)

    headers = {"Authorization": f"Bearer {access_token}"}

    # ✅ Fetch user's Spotify profile
    user_response = requests.get(f"{SPOTIFY_API_BASE_URL}me", headers=headers)
    
    try:
        user_data = user_response.json()
    except requests.exceptions.JSONDecodeError:
        return jsonify({"error": "Failed to retrieve Spotify user data. Check your Spotify Developer settings."}), 400

    spotify_id = user_data.get("id")
    if not spotify_id:
        return jsonify({"error": "Failed to retrieve Spotify user data"}), 400

    # ✅ Fetch additional listening data (short-term = last 4 weeks)
    top_artists_response = requests.get(f"{SPOTIFY_API_BASE_URL}me/top/artists?limit=10&time_range=short_term", headers=headers)
    top_tracks_response = requests.get(f"{SPOTIFY_API_BASE_URL}me/top/tracks?limit=10&time_range=short_term", headers=headers)
    top_genres_response = requests.get(f"{SPOTIFY_API_BASE_URL}me/top/artists?limit=10&time_range=short_term", headers=headers)


    # ✅ Extract relevant data
    top_artists = [artist["name"] for artist in top_artists_response.json().get("items", [])]
    top_tracks = [track["name"] for track in top_tracks_response.json().get("items", [])]
    
    genre_list = []
    for artist in top_genres_response.json().get("items", []):
        genre_list.extend(artist.get("genres", []))
    top_genres = list(set(genre_list))  # Remove duplicates

    # ✅ Check if user exists
    user = User.query.filter_by(spotify_id=spotify_id).first()

    if not user:
        user = User(
            spotify_id=spotify_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
            top_artists=str(top_artists),
            top_tracks=str(top_tracks),
            top_genres=str(top_genres)
        )
        db.session.add(user)
    else:
        user.access_token = access_token
        user.refresh_token = refresh_token
        user.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        user.update_listening_data(str(top_artists), str(top_tracks), str(top_genres))

    db.session.commit()

    session["spotify_id"] = spotify_id
    session["access_token"] = access_token
    session["refresh_token"] = refresh_token

    return redirect(f"{FRONTEND_REDIRECT_URI}?spotify_id={spotify_id}")


# ✅ ROUTES TO FETCH DATA
@auth.route("/recently-played", methods=["GET"])
def recently_played():
    return fetch_spotify_data("me/player/recently-played")


@auth.route("/top-artists", methods=["GET"])
def top_artists():
    return fetch_spotify_data("me/top/artists")


@auth.route("/top-tracks", methods=["GET"])
def top_tracks():
    return fetch_spotify_data("me/top/tracks")


@auth.route("/top-genres", methods=["GET"])
def top_genres():
    response = fetch_spotify_data("me/top/artists")
    if isinstance(response, tuple):  # ✅ Handles error responses properly
        return response

    artist_data = response.get_json()
    genre_list = []
    for artist in artist_data.get("items", []):
        genre_list.extend(artist.get("genres", []))

    unique_genres = list(set(genre_list))  # Remove duplicates
    return jsonify({"top_genres": unique_genres})


# ✅ FUNCTION TO FETCH SPOTIFY DATA
def fetch_spotify_data(endpoint):
    spotify_id = request.args.get("spotify_id")

    if not spotify_id:
        return jsonify({"error": "Missing spotify_id"}), 400

    user = User.query.filter_by(spotify_id=spotify_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    access_token = refresh_access_token(user)

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{SPOTIFY_API_BASE_URL}{endpoint}?limit=10", headers=headers)

    if response.status_code != 200:
        return jsonify({"error": f"Failed to fetch {endpoint}"}), response.status_code

    return jsonify(response.json())


# ✅ FUNCTION TO REFRESH ACCESS TOKEN
def refresh_access_token(user):
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
    
    try:
        token_info = response.json()
    except requests.exceptions.JSONDecodeError:
        return jsonify({"error": "Failed to refresh access token"}), 400

    if "access_token" not in token_info:
        return jsonify({"error": "Failed to refresh access token"}), 400

    user.access_token = token_info["access_token"]
    user.expires_at = datetime.utcnow() + timedelta(seconds=3600)
    db.session.commit()

    return user.access_token



@auth.route("/logout")
def logout():
    """Logs out the current user by clearing session data."""
    session.clear()
    return jsonify({"message": "User logged out successfully!"}), 200