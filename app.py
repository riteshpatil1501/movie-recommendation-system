from pathlib import Path

import pandas as pd
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "Artifacts"
DATA_FILE = ARTIFACTS_DIR / "main_data.csv"


# ---------------------------------------------------------
# Flask application
# ---------------------------------------------------------

app = Flask(__name__)


# ---------------------------------------------------------
# Global ML data
# ---------------------------------------------------------

movie_data = None
count_matrix = None
vectorizer = None


# ---------------------------------------------------------
# Load movie dataset and create ML representation
# ---------------------------------------------------------

def load_movie_data():
    global movie_data
    global count_matrix
    global vectorizer

    if movie_data is not None and count_matrix is not None:
        return

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Movie dataset not found at: {DATA_FILE}"
        )

    print("Loading movie dataset...")

    movie_data = pd.read_csv(DATA_FILE)

    required_columns = [
        "movie_title",
        "director_name",
        "actor_1_name",
        "actor_2_name",
        "actor_3_name",
        "genres",
        "comb"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in movie_data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in main_data.csv: {missing_columns}"
        )

    # Clean missing values
    for column in required_columns:
        movie_data[column] = movie_data[column].fillna("").astype(str)

    # Keep the original movie title for display
    movie_data["display_title"] = movie_data["movie_title"].str.strip()

    # Normalized title used for searching
    movie_data["normalized_title"] = (
        movie_data["movie_title"]
        .str.strip()
        .str.lower()
    )

    # Create the ML feature matrix
    vectorizer = CountVectorizer()

    count_matrix = vectorizer.fit_transform(
        movie_data["comb"]
    )

    print(
        f"Movie dataset loaded successfully: "
        f"{len(movie_data)} movies"
    )

    print("Movie recommendation model is ready!")


# ---------------------------------------------------------
# Get autocomplete suggestions
# ---------------------------------------------------------

def get_suggestions():
    load_movie_data()

    return movie_data["display_title"].tolist()


# ---------------------------------------------------------
# Get movie recommendations
# ---------------------------------------------------------

def get_recommendations(movie_title, number_of_recommendations=10):
    load_movie_data()

    movie_title = movie_title.strip().lower()

    matches = movie_data.index[
        movie_data["normalized_title"] == movie_title
    ].tolist()

    if not matches:
        return None

    movie_index = matches[0]

    # Calculate similarity only for the selected movie.
    # This is much more memory efficient than creating
    # the complete movie-to-movie similarity matrix.
    similarity_scores = cosine_similarity(
        count_matrix[movie_index],
        count_matrix
    ).flatten()

    # Highest similarity first
    similar_indices = similarity_scores.argsort()[::-1]

    recommendations = []

    for index in similar_indices:

        # Skip the movie the user searched for
        if index == movie_index:
            continue

        row = movie_data.iloc[index]

        recommendations.append({
            "title": row["display_title"],
            "director": row["director_name"],
            "actors": ", ".join(
                actor
                for actor in [
                    row["actor_1_name"],
                    row["actor_2_name"],
                    row["actor_3_name"]
                ]
                if actor.strip()
            ),
            "genres": row["genres"],
            "score": round(
                float(similarity_scores[index]) * 100,
                1
            )
        })

        if len(recommendations) >= number_of_recommendations:
            break

    return recommendations


# ---------------------------------------------------------
# Home page
# ---------------------------------------------------------

@app.route("/")
@app.route("/home")
def home():
    try:
        suggestions = get_suggestions()

        return render_template(
            "home.html",
            suggestions=suggestions
        )

    except Exception as error:
        return f"""
        <h2>Application Error</h2>
        <p>{error}</p>
        """


# ---------------------------------------------------------
# Similarity API
# ---------------------------------------------------------

@app.route("/similarity", methods=["POST"])
def similarity():

    movie = request.form.get("name", "").strip()

    if not movie:
        return "Please enter a movie name.", 400

    recommendations = get_recommendations(movie)

    if recommendations is None:
        return (
            "Sorry! The movie you requested is not in our database. "
            "Please check the spelling or try with some other movies"
        )

    return "---".join(
        movie["title"]
        for movie in recommendations
    )


# ---------------------------------------------------------
# Local recommendation results page
# ---------------------------------------------------------

@app.route("/local-recommend", methods=["POST"])
def local_recommend():

    movie = request.form.get("name", "").strip()

    if not movie:
        return render_template(
            "local_recommend.html",
            title="Movie",
            recommendations=[],
            error="Please enter a movie name."
        )

    recommendations = get_recommendations(movie)

    if recommendations is None:
        return render_template(
            "local_recommend.html",
            title=movie,
            recommendations=[],
            error=(
                "The movie was not found in our database. "
                "Please select a movie from the suggestions."
            )
        )

    return render_template(
        "local_recommend.html",
        title=movie,
        recommendations=recommendations,
        error=None
    )


# ---------------------------------------------------------
# Run application
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )