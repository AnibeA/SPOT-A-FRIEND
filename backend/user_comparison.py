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
    """Merge and normalize user data, map sub-genres, and prepare binary vectors for cosine similarity."""

    # ✅ Safe JSON decoding
    genres_1 = set(safe_json_loads(user1.top_genres))
    genres_2 = set(safe_json_loads(user2.top_genres))

    print("User1 Parsed Genres:", genres_1)
    print("User2 Parsed Genres:", genres_2)

    # Extract and merge sub-genres (before mapping)
    merged_sub_genres = list(genres_1 | genres_2)  # Unmapped sub-genres remain unchanged
    print("Merged Sub-Genres Before Mapping:", merged_sub_genres)

    # ✅ Map sub-genres to main genres
    mapped_genres = set()
    for genre in merged_sub_genres:
        mapped_genres.add(map_to_main_genre(genre))  # Ensure only main genres are collected

    print("Mapped Genres:", mapped_genres)

    # ✅ Create a unique set of all possible genres for binary vectorization
    all_possible_genres = list(mapped_genres)

    # ✅ Create binary vectors for cosine similarity (1 if a genre is present, 0 otherwise)
    user1_vector = [1 if genre in genres_1 else 0 for genre in all_possible_genres]
    user2_vector = [1 if genre in genres_2 else 0 for genre in all_possible_genres]

    print("User1 Binary Vector:", user1_vector)
    print("User2 Binary Vector:", user2_vector)

    # ✅ Extract and merge artists
    artists_1 = set(safe_json_loads(user1.top_artists))
    artists_2 = set(safe_json_loads(user2.top_artists))
    merged_artists = list(artists_1 | artists_2)

    # ✅ Get artist recommendations
    artist_recommendations = recommend_artists(user1, user2)

    return {
        "merged_artists": merged_artists,
        "merged_genres": list(mapped_genres),  # Ensure only main genres appear
        "merged_sub_genres": merged_sub_genres,  # Keep unmapped sub-genres
        "user1_vector": user1_vector,
        "user2_vector": user2_vector,
        "all_genres_list": all_possible_genres,  # Needed for cosine similarity
        "user1_recommended_artists": artist_recommendations["user1_recommended_artists"],
        "user2_recommended_artists": artist_recommendations["user2_recommended_artists"]
    }


def group_artists_by_subgenre(user):
    """Organize user's artists by their respective sub-genres."""
    user_artists = safe_json_loads(user.top_artists)
    user_genres = safe_json_loads(user.top_genres)

    artist_genre_map = {}
    for genre in user_genres:
        artist_genre_map[genre] = [artist for artist in user_artists]  # Map all artists under their genres
    
    return artist_genre_map

def recommend_artists(user1, user2):
    """Find artists that belong to common sub-genres but are unique to each user."""
    user1_artists_by_genre = group_artists_by_subgenre(user1)
    user2_artists_by_genre = group_artists_by_subgenre(user2)

    recommendations = {
        "user1_recommended_artists": set(),
        "user2_recommended_artists": set(),
    }

    common_subgenres = set(user1_artists_by_genre.keys()) & set(user2_artists_by_genre.keys())

    for genre in common_subgenres:
        user1_artists = set(user1_artists_by_genre.get(genre, []))
        user2_artists = set(user2_artists_by_genre.get(genre, []))

        # Artists to recommend to user1 (artists in user2 but not in user1)
        recommendations["user1_recommended_artists"].update(user2_artists - user1_artists)

        # Artists to recommend to user2 (artists in user1 but not in user2)
        recommendations["user2_recommended_artists"].update(user1_artists - user2_artists)

    return {
        "user1_recommended_artists": list(recommendations["user1_recommended_artists"]),
        "user2_recommended_artists": list(recommendations["user2_recommended_artists"]),
    }


@comparison.route("/compare-users", methods=["GET"])
def compare_users():
    """Compare two users' music tastes and return merged lists, binary vectors, and recommendations."""
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
