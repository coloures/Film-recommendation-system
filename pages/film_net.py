import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import math

st.set_page_config(page_title="Сеть фильмов", page_icon="🕸️")
st.title("🕸️ Сеть похожих фильмов")

# Загрузка данных
def load_data():
    df = pd.read_pickle("model/movies_data.pkl")
    similarity = np.load("model/similarity_matrix.npy")
    with open("model/titles.pkl", "rb") as f:
        titles = pickle.load(f)
    return df, similarity, titles

df, similarity, titles = load_data()

min_sim = np.min(similarity[similarity > 0])
max_sim = np.max(similarity)

movie = st.selectbox("Фильм:", titles[:100])

threshold = st.slider(
    "Порог схожести",
    min_value=float(min_sim),
    max_value=float(max_sim),
    value=float(0.1),
    step=0.01,
    help=f"Диапазон схожести в датасете: от {min_sim:.2f} до {max_sim:.2f}"
)

st.caption(f"🔍 Минимум в датасете: {min_sim:.3f} | Максимум: {max_sim:.3f}")

if movie:
    idx = titles.index(movie)

    similar = [(i, s) for i, s in enumerate(similarity[idx]) 
               if s > threshold and i != idx]
    similar.sort(key=lambda x: x[1], reverse=True)
    similar = similar[:8] 
    
    if similar:
        fig, ax = plt.subplots(figsize=(9, 6))

        ax.scatter(0, 0, s=400, c='red', marker='*', alpha=0.9)
        ax.text(0, 0.15, movie[:18] + ("..." if len(movie) > 18 else ""), 
                ha='center', fontsize=10, weight='bold')

        n = len(similar)
        for i, (movie_idx, sim) in enumerate(similar):
            angle = 2 * math.pi * i / n
            x = math.cos(angle) * 1.8
            y = math.sin(angle) * 1.8

            size = 80 + sim * 200

            color = plt.cm.YlGn(sim)

            ax.scatter(x, y, s=size, c=[color], alpha=0.7, edgecolors='black', linewidth=0.5)

            title = df.iloc[movie_idx]['title']
            short_title = title[:14] + "..." if len(title) > 14 else title
            ax.text(x, y + 0.15, short_title, ha='center', fontsize=8)

            line_width = 1 + sim * 4
            ax.plot([0, x], [0, y], 'gray', alpha=sim*0.8, linewidth=line_width)

            ax.text(x*0.6, y*0.6, f"{sim:.2f}", fontsize=7, alpha=0.8)
        
        ax.set_xlim(-2.2, 2.2)
        ax.set_ylim(-2.2, 2.2)
        ax.set_aspect('equal')
        ax.axis('off')

        avg_sim = np.mean([s for _, s in similar])
        ax.set_title(
            f"Сеть похожих фильмов\n"
            f"Порог: {threshold:.2f} | Средняя схожесть: {avg_sim:.2f}", 
            fontsize=12, pad=20
        )
        
        st.pyplot(fig)

        st.subheader("📋 Похожие фильмы")
        
        table_data = []
        for movie_idx, sim in similar:
            m = df.iloc[movie_idx]
            table_data.append({
                'Фильм': m['title'],
                'Схожесть': f"{sim:.3f}",
                'Рейтинг': f"{m['rating']:.1f}",
                'Год': m['year'],
                'Жанр': str(m['genre']).split(',')[0] if pd.notna(m['genre']) else '—'
            })
        
        st.dataframe(
            pd.DataFrame(table_data),
            use_container_width=True,
            hide_index=True
        )
    
    else:
        st.warning(f"❌ Нет фильмов со схожестью выше {threshold:.2f}")
        st.info(f"Попробуйте уменьшить порог до {threshold*0.8:.2f} или ниже")