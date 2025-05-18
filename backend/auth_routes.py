import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode
from flask import Blueprint, redirect, request, session, jsonify
from backend.config import Config
from backend.models import db, User
import json
from flask import make_response


auth = Blueprint("auth", __name__)

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1/"
SCOPE = "user-read-recently-played user-top-read user-library-read user-read-private"
FRONTEND_REDIRECT_URI = "http://127.0.0.1:3000/dashboard"

@auth.route("/login")
def login():
    params = {
        "client_id": Config.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": Config.SPOTIFY_REDIRECT_URI,
        "scope": SCOPE,
        "show_dialog": "true",
    }
    return redirect(f"{SPOTIFY_AUTH_URL}?{urlencode(params)}")

@auth.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Authorization failed"}), 400

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

    # Get user profile
    user_response = requests.get(f"{SPOTIFY_API_BASE_URL}me", headers=headers)
    user_data = user_response.json()
    spotify_id = user_data.get("id")
    if not spotify_id:
        return jsonify({"error": "Spotify ID not found"}), 400

    # Fetch top artists and tracks
    top_artists_res = requests.get(f"{SPOTIFY_API_BASE_URL}me/top/artists?limit=10&time_range=short_term", headers=headers)
    top_tracks_res = requests.get(f"{SPOTIFY_API_BASE_URL}me/top/tracks?limit=10&time_range=short_term", headers=headers)

    # Process top artists
    artist_items = top_artists_res.json().get("items", [])
    top_artists = []
    top_genres = set()

    for artist in artist_items:
        top_artists.append({
            "name": artist["name"],
            "genres": artist.get("genres", []),
            "images": artist.get("images", []),
            "external_urls": artist.get("external_urls", {})
        })
        top_genres.update(artist.get("genres", []))

    top_tracks = [track["name"] for track in top_tracks_res.json().get("items", [])]

    # Store or update user in DB
    user = User.query.filter_by(spotify_id=spotify_id).first()
    if not user:
        user = User(
            spotify_id=spotify_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
            top_artists=json.dumps(top_artists),
            top_tracks=json.dumps(top_tracks),
            top_genres=json.dumps(list(top_genres))
        )
        db.session.add(user)
    else:
        user.access_token = access_token
        user.refresh_token = refresh_token
        user.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        user.top_artists = json.dumps(top_artists)
        user.top_tracks = json.dumps(top_tracks)
        user.top_genres = json.dumps(list(top_genres))

    db.session.commit()

    session["spotify_id"] = spotify_id
    session["access_token"] = access_token
    session["refresh_token"] = refresh_token

    return redirect(f"{FRONTEND_REDIRECT_URI}?spotify_id={spotify_id}")

@auth.route("/recently-played", methods=["GET"])
def recently_played():
    return fetch_spotify_data("me/player/recently-played")

@auth.route("/top-artists", methods=["GET"])
def top_artists():
    spotify_id = request.args.get("spotify_id")
    if not spotify_id:
        return jsonify({"error": "Missing spotify_id"}), 400
    user = User.query.filter_by(spotify_id=spotify_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return fetch_spotify_data("me/top/artists", user)

@auth.route("/top-tracks", methods=["GET"])
def top_tracks():
    spotify_id = request.args.get("spotify_id")
    if not spotify_id:
        return jsonify({"error": "Missing spotify_id"}), 400
    user = User.query.filter_by(spotify_id=spotify_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return fetch_spotify_data("me/top/tracks", user)

@auth.route("/top-genres", methods=["GET"])
def top_genres():
    spotify_id = request.args.get("spotify_id")
    if not spotify_id:
        return jsonify({"error": "Missing spotify_id"}), 400
    user = User.query.filter_by(spotify_id=spotify_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    response = fetch_spotify_data("me/top/artists", user)
    if isinstance(response, tuple):
        return response

    artist_data = response.get_json()
    genre_list = []
    for artist in artist_data.get("items", []):
        genre_list.extend(artist.get("genres", []))

    return jsonify({"top_genres": list(set(genre_list))})

def fetch_spotify_data(endpoint, user):
    access_token = refresh_access_token(user)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{SPOTIFY_API_BASE_URL}{endpoint}?limit=10", headers=headers)

    if response.status_code != 200:
        return jsonify({"error": f"Failed to fetch {endpoint}"}), response.status_code

    data = response.json()

    if "top/artists" in endpoint:
        top_artists = []
        genres = set()
        for artist in data.get("items", []):
            top_artists.append({
                "name": artist["name"],
                "genres": artist.get("genres", []),
                "images": artist.get("images", []),
                "external_urls": artist.get("external_urls", {})
            })
            genres.update(artist.get("genres", []))
        user.top_artists = json.dumps(top_artists)
        user.top_genres = json.dumps(list(genres))

    elif "top/tracks" in endpoint:
        user.top_tracks = json.dumps([track["name"] for track in data.get("items", [])])

    db.session.commit()
    return jsonify(data)

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
    token_info = response.json()
    if "access_token" not in token_info:
        return jsonify({"error": "Failed to refresh access token"}), 400

    user.access_token = token_info["access_token"]
    user.expires_at = datetime.utcnow() + timedelta(seconds=3600)
    db.session.commit()

    return user.access_token

@auth.route("/logout")
def logout():
    session.clear()
    response = make_response(jsonify({"message": "User logged out successfully!"}))
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
