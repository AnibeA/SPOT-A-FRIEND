from flask import Blueprint, jsonify, request
import json
from backend.models import User  # Import User model
import os

# ✅ Load the categorized sub-genre mapping from JSON file
current_dir = os.path.dirname(__file__)  # Get the current directory
json_path = os.path.join(current_dir, "categorized-subset.json")  # Path to JSON file

with open(json_path, "r") as f:
    GENRE_MAPPING = json.load(f)

# ✅ Create Blueprint
comparison = Blueprint("comparison", __name__)

def map_to_main_genre(sub_genre):
    """Map a sub-genre to its main genre using the GENRE_MAPPING dictionary (case-insensitive)."""
    sub_genre = sub_genre.lower()  # Convert sub-genre from database to lowercase
    
    for main_genre, sub_genres in GENRE_MAPPING.items():
        normalized_sub_genres = [g.lower() for g in sub_genres]  # Convert JSON file genres to lowercase
        
        if sub_genre in normalized_sub_genres:
            print(f"Mapping sub-genre '{sub_genre}' to main genre '{main_genre.lower()}'")  # Debug print
            return main_genre.lower()  # Also return in lowercase for consistency

    print(f"No mapping found for '{sub_genre}', keeping original")  # Debug print
    return sub_genre  # If no match is found, return the original sub-genre

def safe_json_loads(data):
    """Safely loads a JSON string, returning an empty list if it fails."""
    if not data:
        return []  # Return an empty list if data is None or empty
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON: {data}")  # Debugging output
        return []  # Return an empty list on failure

def merge_user_data(user1, user2):
    """Merge and normalize user data, map sub-genres, and prepare for cosine similarity."""

    # ✅ Safe JSON decoding
    try:
        genres_1 = set(json.loads(user1.top_genres)) if user1.top_genres else set()
    except json.JSONDecodeError:
        print(f"Failed to decode JSON: {user1.top_genres}")
        genres_1 = set()
    
    try:
        genres_2 = set(json.loads(user2.top_genres)) if user2.top_genres else set()
    except json.JSONDecodeError:
        print(f"Failed to decode JSON: {user2.top_genres}")
        genres_2 = set()

    print("User1 Parsed Genres:", genres_1)
    print("User2 Parsed Genres:", genres_2)

    # Extract and merge sub-genres (these should remain unchanged)
    merged_sub_genres = list(genres_1 | genres_2)
    print("Merged Sub-Genres Before Mapping:", merged_sub_genres)

    # Map sub-genres to main genres
    mapped_genres = set()
    for genre in merged_sub_genres:
        mapped_genres.add(map_to_main_genre(genre))  # Ensures only main genres are collected

    print("Mapped Genres:", mapped_genres)

    # Extract and merge artists
    artists_1 = set(json.loads(user1.top_artists) if user1.top_artists else [])
    artists_2 = set(json.loads(user2.top_artists) if user2.top_artists else [])
    merged_artists = list(artists_1 | artists_2)

    print("\nFinal Output:")
    print("Merged Artists:", merged_artists)
    print("Final Mapped Genres:", list(mapped_genres))
    print("Final Merged Sub-Genres:", merged_sub_genres)

    return {
        "merged_artists": merged_artists,
        "merged_genres": list(mapped_genres),  # Ensure it only contains main genres
        "merged_sub_genres": merged_sub_genres,  # This still contains sub-genres
    }


@comparison.route("/compare-users", methods=["GET"])
def compare_users():
    """Compare two users' music tastes and return merged lists and binary vectors."""
    user1_id = request.args.get("user1")
    user2_id = request.args.get("user2")

    if not user1_id or not user2_id:
        return jsonify({"error": "Missing user IDs"}), 400

    user1 = User.query.filter_by(spotify_id=user1_id).first()
    user2 = User.query.filter_by(spotify_id=user2_id).first()

    if not user1 or not user2:
        return jsonify({"error": "One or both users not found"}), 404

    comparison_result = merge_user_data(user1, user2)

    return jsonify(comparison_result)
