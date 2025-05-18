from flask import Blueprint, jsonify, request
import json
from backend.models import User
import os
import math

comparison = Blueprint("comparison", __name__)

# Load sub-genre-to-main-genre mapping
current_dir = os.path.dirname(__file__)
json_path = os.path.join(current_dir, "categorized-subset.json")
with open(json_path, "r") as f:
    GENRE_MAPPING = json.load(f)

def safe_json_loads(data):
    """Load JSON safely from a stringified object in the DB."""
    if not data:
        return []
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON: {data}")
        return []

def map_to_main_genre(sub_genre):
    """Maps a given sub-genre to a main genre from the JSON mapping."""
    sub_genre = sub_genre.lower()
    for main_genre, sub_genres in GENRE_MAPPING.items():
        if sub_genre in [g.lower() for g in sub_genres]:
            return main_genre.lower()
    return sub_genre

def cosine_similarity(vec1, vec2):
    """Standard cosine similarity calculation."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

def organize_artists_by_genre(artists):
    """
    From list of artist objects, return a dictionary of genre → [artist dicts]
    """
    genre_to_artists = {}
    for artist in artists:
        for genre in artist.get("genres", []):
            genre = map_to_main_genre(genre)
            genre_to_artists.setdefault(genre, []).append(artist)
    return genre_to_artists

def merge_user_data(user1, user2):
    """Main logic: compares, maps, and recommends artists."""

    # 🎧 Load top genres & artists
    genres_1 = set(safe_json_loads(user1.top_genres))
    genres_2 = set(safe_json_loads(user2.top_genres))
    user1_artists = safe_json_loads(user1.top_artists)
    user2_artists = safe_json_loads(user2.top_artists)

    # 📚 All genres and mapped versions
    all_subgenres = list(genres_1 | genres_2)
    mapped_genres = set(map_to_main_genre(g) for g in all_subgenres)
    user1_mapped = set(map_to_main_genre(g) for g in genres_1)
    user2_mapped = set(map_to_main_genre(g) for g in genres_2)

    shared_genres = user1_mapped & user2_mapped
    print("Shared Genres:", shared_genres)

    # 🎨 Organize each user's artists by genre
    u1_by_genre = organize_artists_by_genre(user1_artists)
    u2_by_genre = organize_artists_by_genre(user2_artists)

    # 🎯 Recommendation logic
    user1_recommended = set()
    user2_recommended = set()

    for genre in shared_genres:
        u1_artists_in_genre = {a["name"] for a in u1_by_genre.get(genre, [])}
        u2_artists_in_genre = {a["name"] for a in u2_by_genre.get(genre, [])}

        # Recommend artists user2 knows but user1 doesn't
        user1_recommended.update(
            a["name"] for a in u2_by_genre.get(genre, [])
            if a["name"] not in u1_artists_in_genre
        )

        # Recommend artists user1 knows but user2 doesn't
        user2_recommended.update(
            a["name"] for a in u1_by_genre.get(genre, [])
            if a["name"] not in u2_artists_in_genre
        )

    # 🧮 Vectors for cosine similarity
    all_genres = list(mapped_genres)
    u1_vector = [1 if g in user1_mapped else 0 for g in all_genres]
    u2_vector = [1 if g in user2_mapped else 0 for g in all_genres]

    return {
        "merged_sub_genres": all_subgenres,
        "merged_genres": list(mapped_genres),
        "user1_vector": u1_vector,
        "user2_vector": u2_vector,
        "cosine_similarity": cosine_similarity(u1_vector, u2_vector),
        "user1_recommended_artists": list(user1_recommended),
        "user2_recommended_artists": list(user2_recommended),
    }

@comparison.route("/compare-users", methods=["GET"])
def compare_users():
    """Compare users based on genre overlap and return recommendations."""
    user1_id = request.args.get("user1")
    user2_id = request.args.get("user2")

    if not user1_id or not user2_id:
        return jsonify({"error": "Missing user IDs"}), 400

    user1 = User.query.filter_by(spotify_id=user1_id).first()
    user2 = User.query.filter_by(spotify_id=user2_id).first()

    if not user1 or not user2:
        return jsonify({"error": "User not found"}), 404

    return jsonify(merge_user_data(user1, user2))
