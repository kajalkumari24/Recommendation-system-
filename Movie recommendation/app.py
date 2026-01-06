import pickle
import streamlit as st
import requests
import pandas as pd

# ------------------ POSTER FETCH ------------------
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except Exception:
        pass

    return "https://placehold.co/500x750/333/FFFFFF?text=No+Poster"


# ------------------ RECOMMEND FUNCTION ------------------
def recommend(movie):
    try:
        index = movies[movies["title"] == movie].index[0]
    except IndexError:
        st.error("Movie not found.")
        return [], [], [], []

    distances = sorted(
        list(enumerate(similarity[index])),
        key=lambda x: x[1],
        reverse=True
    )

    names, posters, years, ratings = [], [], [], []

    for i in distances[1:6]:
        row = movies.iloc[i[0]]

        # ---- NAME ----
        names.append(row.get("title", "Unknown"))

        # ---- POSTER ----
        posters.append(fetch_poster(row.get("movie_id")))

        # ---- RATING ----
        ratings.append(row.get("vote_average", 0.0))

        # ---- YEAR (SAFE HANDLING) ----
        year = None
        if "release_date" in movies.columns:
            year = pd.to_datetime(row["release_date"], errors="coerce").year
        elif "release_year" in movies.columns:
            year = row["release_year"]
        elif "year" in movies.columns:
            year = row["year"]

        years.append(year)

    return names, posters, years, ratings


# ------------------ STREAMLIT UI ------------------
st.set_page_config(layout="wide")
st.header("🎬 Movie Recommender System Using Machine Learning")

# ------------------ LOAD DATA ------------------
try:
    movies_dict = pickle.load(open("artifacts/movie_dict.pkl", "rb"))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open("artifacts/similarity.pkl", "rb"))
except Exception as e:
    st.error("Model files not found or corrupted.")
    st.stop()

# ------------------ MOVIE SELECT ------------------
movie_list = movies["title"].values
selected_movie = st.selectbox(
    "Type or select a movie",
    movie_list
)

# ------------------ SHOW RESULT ------------------
if st.button("Show Recommendation"):
    with st.spinner("Finding recommendations..."):
        names, posters, years, ratings = recommend(selected_movie)

    if names:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(names[i])
                st.image(posters[i])

                if pd.notna(years[i]):
                    st.caption(f"Year: {int(years[i])}")
                else:
                    st.caption("Year: N/A")

                st.caption(f"Rating: {ratings[i]:.1f} ⭐")
