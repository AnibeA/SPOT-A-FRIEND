from flask import Blueprint, jsonify, request
import json
from backend.models import User  # Import User model
import os
import math


def cosine_similarity(vec1, vec2):
    """
    Calculate cosine similarity between two binary vectors.
    Cosine similarity = (A • B) / (||A|| * ||B||)
    Where:
        - A • B is the dot product of vectors A and B
        - ||A|| is the magnitude (length) of vector A
        - ||B|| is the magnitude (length) of vector B
    """

    # Step 1: Calculate dot product (A • B)
    # This is the sum of element-wise multiplication
    dot_product = sum(a * b for a, b in zip(vec1, vec2))

    # Step 2: Calculate the magnitude of each vector
    # sqrt(a₁² + a₂² + ... + an²)
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))

    # Step 3: Avoid division by zero if either vector is empty or has no 1s
    if norm_a == 0 or norm_b == 0:
        return 0.0

    # Step 4: Return cosine similarity
    # Higher value (closer to 1) → more similar
    return dot_product / (norm_a * norm_b)



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
    """Merge user data, map sub-genres to main genres, and recommend artists based on shared genres."""

    # ✅ Safe JSON decoding
    genres_1 = set(safe_json_loads(user1.top_genres))
    genres_2 = set(safe_json_loads(user2.top_genres))

    print("User1 Parsed Genres:", genres_1)
    print("User2 Parsed Genres:", genres_2)

    # ✅ Extract and merge sub-genres (before mapping)
    merged_sub_genres = list(genres_1 | genres_2)  # Unmapped sub-genres remain unchanged
    print("Merged Sub-Genres Before Mapping:", merged_sub_genres)

    # ✅ Efficient mapping of sub-genres to main genres
    mapped_genres_cache = {}  # Dictionary to store already-mapped sub-genres
    mapped_genres = set()

    for genre in merged_sub_genres:
        if genre not in mapped_genres_cache:  # Only map if not already mapped
            mapped_genres_cache[genre] = map_to_main_genre(genre)
        mapped_genres.add(mapped_genres_cache[genre])

    print("Mapped Genres:", mapped_genres)

    # ✅ Ensure mapped genres exist before using them
    user1_mapped_genres = set(map_to_main_genre(genre) for genre in genres_1)
    user2_mapped_genres = set(map_to_main_genre(genre) for genre in genres_2)

    # ✅ Find shared genres (only recommend within these)
    shared_genres = user1_mapped_genres & user2_mapped_genres
    print("Shared Genres:", shared_genres)

    # ✅ Extract and merge artists
    artists_1 = set(safe_json_loads(user1.top_artists))
    artists_2 = set(safe_json_loads(user2.top_artists))
    merged_artists = list(artists_1 | artists_2)

    # ✅ Group artists under genres (ensuring only shared genres are used)
    user1_genre_to_artists = {genre: set() for genre in mapped_genres}
    user2_genre_to_artists = {genre: set() for genre in mapped_genres}

    for artist in artists_1:
        for genre in genres_1:
            mapped_genre = mapped_genres_cache.get(genre, genre)
            if mapped_genre in user1_genre_to_artists:
                user1_genre_to_artists[mapped_genre].add(artist)

    for artist in artists_2:
        for genre in genres_2:
            mapped_genre = mapped_genres_cache.get(genre, genre)
            if mapped_genre in user2_genre_to_artists:
                user2_genre_to_artists[mapped_genre].add(artist)

    # ✅ Recommend artists ONLY from shared genres
    user1_recommended = set()
    user2_recommended = set()

    for genre in shared_genres:
        user1_genre_artists = user1_genre_to_artists.get(genre, set())
        user2_genre_artists = user2_genre_to_artists.get(genre, set())

        # Artists in user2's genre but not in user1's genre
        user1_recommended.update(user2_genre_artists - user1_genre_artists)

        # Artists in user1's genre but not in user2's genre
        user2_recommended.update(user1_genre_artists - user2_genre_artists)

    print("User1 Recommended Artists:", user1_recommended)
    print("User2 Recommended Artists:", user2_recommended)

    #  Create a unique set of all possible genres for binary vectorization
    all_possible_genres = list(mapped_genres)

    #  Create binary vectors for cosine similarity (1 if a mapped genre is present)
    user1_vector = [1 if genre in user1_mapped_genres else 0 for genre in all_possible_genres]
    user2_vector = [1 if genre in user2_mapped_genres else 0 for genre in all_possible_genres]

    # Pass both binary vectors to the cosine similarity function
    # The similarity score will range from 0 (no overlap) to 1 (identical preferences)
    similarity_score = cosine_similarity(user1_vector, user2_vector)
    
    print("Cosine Similarity Score:", similarity_score)


    print("User1 Binary Vector:", user1_vector)
    print("User2 Binary Vector:", user2_vector)

    return {
        "merged_artists": merged_artists,
        "merged_genres": list(mapped_genres),  # Ensure only main genres appear
        "merged_sub_genres": merged_sub_genres,  # Keep unmapped sub-genres
        "user1_recommended_artists": list(user1_recommended),
        "user2_recommended_artists": list(user2_recommended),
        "user1_vector": user1_vector,
        "user2_vector": user2_vector,
        "all_genres_list": all_possible_genres,  # Needed for cosine similarity
        "cosine_similarity": similarity_score

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
    recommendation_result = recommend_artists(user1, user2)

    # Merge both results into a single response
    comparison_result.update(recommendation_result)

    return jsonify(comparison_result)

