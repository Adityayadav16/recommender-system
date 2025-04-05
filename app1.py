import streamlit as st
import pickle
import pandas as pd
import requests


def fetch_poster(movie_id):
    try:
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{}?api_key=a9c7bad3b6ce35880c7651ae7f9b8f33&language=en-US'.format(
                movie_id)
        )
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        return None  # Return None if no poster available
    except (requests.RequestException, KeyError) as e:
        st.error(f"Error fetching poster: {e}")
        return None


def recommend(movie):
    try:
        movie_matches = movies[movies['title'] == movie]
        if movie_matches.empty:
            raise ValueError(f"Movie '{movie}' not found in database")

        movie_index = movie_matches.index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_movies_posters = []
        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_posters.append(fetch_poster(movie_id))
        return recommended_movies, recommended_movies_posters
    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
        return [], []


# Load data with error handling
try:
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError as e:
    st.error(f"Data file not found: {e}")
    st.stop()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    'Recommendation',
    movies['title'].values
)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    if names:  # Only display if we have recommendations
        col1, col2, col3, col4, col5 = st.columns(5)
        columns = [col1, col2, col3, col4, col5]

        for idx, (col, name, poster) in enumerate(zip(columns, names, posters)):
            with col:
                st.text(name)
                if poster:
                    st.image(poster)
                else:
                    st.text("Poster not available")