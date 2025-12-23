import streamlit as st
import pandas as pd
import plotly.express as px
import ast
from collections import Counter

st.header("📊 Аналитика")

try:
    df = pd.read_pickle("model/movies_data.pkl")
except:
    try:
        df = pd.read_csv("data/n_movies.csv")
    except:
        st.error("❌ Не могу загрузить данные!")
        st.stop()

st.success(f"✅ Фильмы загружены")

st.subheader("📈 Распределение рейтингов")
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df_clean = df.dropna(subset=["rating"])

if len(df_clean) > 0:
    fig = px.histogram(
        df_clean,
        x="rating",
        nbins=20,
        title="Распределение рейтингов IMDb",
        labels={"rating": "Рейтинг", "count": "Количество фильмов"},
        color_discrete_sequence=["#FF4B4B"]
    )
    fig.update_layout(bargap=0.1)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Нет данных о рейтингах")

st.subheader("🎬 Самые популярные жанры")
if "genre" in df.columns:
    genres_expanded = df["genre"].str.split(", ").explode()
    genre_counts = genres_expanded.value_counts().head(15)
    
    if len(genre_counts) > 0:
        fig = px.bar(
            x=genre_counts.values,
            y=genre_counts.index,
            orientation='h',
            title="Топ-15 жанров",
            labels={"x": "Количество фильмов", "y": "Жанр"},
            color=genre_counts.values,
            color_continuous_scale="viridis"
        )
        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        st.write("**Детализация:**")
        cols = st.columns(3)
        for i, (genre, count) in enumerate(genre_counts.items()):
            with cols[i % 3]:
                st.metric(genre, f"{count} фильмов")
else:
    st.warning("Нет данных о жанрах")

st.subheader("🎭 Топ-10 актёров")

if "stars" in df.columns:
    all_actors = []
    
    for stars in df["stars"].dropna().astype(str):
        clean = stars.replace('[', '').replace(']', '').replace("'", "")
        actors = [a.strip() for a in clean.split(',') if a.strip()]
        for actor in actors:
            if (len(actor) > 2 and 
                "star" not in actor.lower() and 
                "director" not in actor.lower() and
                "writer" not in actor.lower()):
                all_actors.append(actor)
    
    from collections import Counter
    top_10 = Counter(all_actors).most_common(10)
    
    if top_10:
        import plotly.express as px
        df_chart = pd.DataFrame(top_10, columns=["Актёр", "Фильмов"])
        fig = px.bar(df_chart, x="Актёр", y="Фильмов", title="Топ-10 актёров")
        st.plotly_chart(fig)
    else:
        st.write("Не нашлось актёров")
else:
    st.write("Нет данных об актёрах")

st.subheader("📊 Общая статистика")
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_rating = df["rating"].mean()
    st.metric("Средний рейтинг", f"{avg_rating:.2f}")

with col2:
    top_rating = df["rating"].max()
    top_movie = df[df["rating"] == top_rating]["title"].iloc[0] if len(df) > 0 else "-"
    st.metric("Максимальный рейтинг", f"{top_rating:.1f}")
    st.caption(f"{top_movie}")

with col3:
    def extract_year(year_str):
        if isinstance(year_str, str):
            import re
            match = re.search(r'\d{4}', year_str)
            if match:
                return int(match.group())
        return None
    
    years = df["year"].apply(extract_year)
    latest_year = years.max()
    st.metric("Последний год", int(latest_year) if not pd.isna(latest_year) else "-")

with col4:
    total_votes = df["votes"].str.replace(',', '').astype(float).sum()
    st.metric("Всего голосов", f"{total_votes:,.0f}")

st.subheader("🏆 Топ-10 фильмов по рейтингу")
top_movies = df.nlargest(10, "rating")[["title", "rating", "genre", "votes"]]
top_movies["votes"] = top_movies["votes"].str.replace(',', '').astype(int)

st.dataframe(
    top_movies.style
    .background_gradient(subset=["rating"], cmap="YlOrRd")
    .format({"rating": "{:.1f}", "votes": "{:,}"}),
    use_container_width=True
)