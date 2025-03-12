import json
from collections import Counter
from flask import Blueprint, request, jsonify
from backend.models import User  # Import User model

# 🔹 Create a Flask Blueprint for user comparison
comparison = Blueprint("comparison", __name__)

def normalize_genre(genre):
    """Normalize similar genres to reduce redundancy."""
    genre_mapping = {
        "afrobeat": "afrobeats",
        "afropop": "afrobeats",
        "boom bap": "hip hop",
        "jazz rap": "hip hop",
        "west coast hip hop": "hip hop",
        "rage rap": "trap",
        "melodic rap": "rap",
    }
    return genre_mapping.get(genre.lower(), genre.lower())

def merge_user_data(user1, user2):
    """Merge and normalize two users' music data."""
    
    # 🔹 Convert stored JSON strings back into Python lists
    user1_top_artists = json.loads(user1["top_artists"]) if isinstance(user1["top_artists"], str) else user1["top_artists"]
    user2_top_artists = json.loads(user2["top_artists"]) if isinstance(user2["top_artists"], str) else user2["top_artists"]

    user1_top_genres = json.loads(user1["top_genres"]) if isinstance(user1["top_genres"], str) else user1["top_genres"]
    user2_top_genres = json.loads(user2["top_genres"]) if isinstance(user2["top_genres"], str) else user2["top_genres"]

    # 🔹 Extract and combine genres, then remove duplicates
    genres_1 = set(normalize_genre(g) for g in user1_top_genres)
    genres_2 = set(normalize_genre(g) for g in user2_top_genres)
    combined_genres = list(genres_1 | genres_2)  # Union of both sets

    # 🔹 Extract and combine artist names, then remove duplicates
    artists_1 = set(artist for artist in user1_top_artists)
    artists_2 = set(artist for artist in user2_top_artists)
    combined_artists = list(artists_1 | artists_2)

    return {
        "merged_genres": combined_genres,
        "merged_artists": combined_artists,
    }

# ----------------------------------------------
# ✅ ROUTE: /compare-users - Compares two users' music preferences
# ----------------------------------------------
@comparison.route("/compare-users", methods=["GET"])
def compare_users():
    """API endpoint to compare two users' music preferences."""

    # Get two Spotify IDs from query parameters
    user1_spotify_id = request.args.get("user1")
    user2_spotify_id = request.args.get("user2")

    if not user1_spotify_id or not user2_spotify_id:
        return jsonify({"error": "Both user1 and user2 Spotify IDs are required"}), 400

    # Fetch users from database
    user1 = User.query.filter_by(spotify_id=user1_spotify_id).first()
    user2 = User.query.filter_by(spotify_id=user2_spotify_id).first()

    if not user1 or not user2:
        return jsonify({"error": "One or both users not found"}), 404

    # Convert stored string data back into lists
    user1_data = {
        "top_genres": eval(user1.top_genres),  # Convert stored string back to list
        "top_artists": eval(user1.top_artists)
    }
    user2_data = {
        "top_genres": eval(user2.top_genres),
        "top_artists": eval(user2.top_artists)
    }

    # Merge and compare user data
    comparison_result = merge_user_data(user1_data, user2_data)

    return jsonify(comparison_result)
