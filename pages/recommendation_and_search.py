import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from utils import card

st.title("🎬 Умные рекомендации и поиск фильмов")

if "df" not in st.session_state:
    st.session_state.df = pd.read_pickle("model/movies_data.pkl")

df = st.session_state.df

similarity = np.load("model/similarity_matrix.npy")
with open("model/titles.pkl", "rb") as f:
    titles = pickle.load(f)

with open("model/vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

tfidf_matrix_all = vectorizer.transform(df["features"])

st.header("Настройте рекомендации")

col1, col2 = st.columns(2)
with col1:
    selected_title = st.selectbox(
        "Понравившийся фильм (основа рекомендаций):",
        options=["Не выбран"] + sorted(titles)
    )
    keywords = st.text_input("Ключевые слова (например: prison escape, karate school, space travel)")
with col2:
    genre = st.text_input("Жанр (например: Drama, Action, Comedy)")
    min_rating = st.slider("Минимальный рейтинг", 0.0, 10.0, 6.0, 0.1)

if st.button("Подобрать фильмы", type="primary"):
    if selected_title != "Не выбран":
        idx = titles.index(selected_title)
        scores = list(enumerate(similarity[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:50]
        candidate_indices = [i[0] for i in scores]
        results = df.iloc[candidate_indices].copy()
        st.success(f"Основа: похожие на «{selected_title}» ({len(results)} кандидатов)")
    else:
        results = df.copy()
        st.info("Фильм не выбран — ищем по всем фильмам")

    if genre.strip():
        genre_lower = genre.strip().lower()
        results = results[results["genre"].str.contains(genre_lower, case=False, na=False)]

    results = results[results["rating"] >= min_rating]

    if keywords.strip():
        keywords_lower = keywords.strip().lower()
        query_vec = vectorizer.transform([keywords_lower])
        current_tfidf = vectorizer.transform(results["features"])
        sim_scores = cosine_similarity(query_vec, current_tfidf).flatten()

        results = results.copy()
        results["keyword_similarity"] = sim_scores
        if len(results) > 0:
            results = results[results["keyword_similarity"] > 0.05]
            results = results.sort_values("keyword_similarity", ascending=False)

    if selected_title != "Не выбран" and keywords.strip() == "" and genre.strip() == "":
        score_dict = {i: score for i, score in scores}
        def get_similarity(idx):
            return score_dict.get(idx, 0)
        results = results.copy()
        results['_similarity_score'] = results.index.map(get_similarity)
        results = results.sort_values('_similarity_score', ascending=False)
        results = results.drop('_similarity_score', axis=1)

    if len(results) == 0:
        st.info("По вашим критериям ничего не найдено 😔 Попробуйте ослабить фильтры.")
    else:
        st.write(f"**Найдено подходящих фильмов: {len(results)}**")

        for _, movie in results.head(20).iterrows():
            with st.container():
                caption = []
                if selected_title != "Не выбран":
                    movie_idx = df[df["title"] == movie["title"]].index[0]
                    film_score = similarity[titles.index(selected_title)][movie_idx]
                    caption.append(f"Похожесть с «{selected_title}»: {film_score:.3f}")
                if keywords.strip() and "keyword_similarity" in movie:
                    caption.append(f"По ключевым словам: {movie['keyword_similarity']:.3f}")
                if caption:
                    st.caption(" | ".join(caption))
                card(movie)
                