import streamlit as st
import pandas as pd

st.set_page_config(page_title="Рекомендации фильмов", page_icon="🎬", layout="wide")

st.title("🎬 Система рекомендаций фильмов")
st.markdown("---")

try:
    df = pd.read_pickle("model/movies_data.pkl")
except:
    st.error("Не найдена папка model. Сначала запустите ноутбук 1_Обучение_модели.ipynb")
    st.stop()

st.write(f"Загружено фильмов: **{len(df)}**")
st.write("Модель обучена в Jupyter Notebook (жанры + актёры + описание)")

st.subheader("Топ-10 лучших фильмов")
top10 = df.sort_values("rating", ascending=False).head(10)
st.dataframe(
    top10[["title", "year", "rating", "genre"]],
    use_container_width=True,
    hide_index=True
)