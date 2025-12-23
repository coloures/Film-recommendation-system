import streamlit as st

def card(movie):
    st.markdown("---")
    st.subheader(movie["title"])
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.write(f"**Год:** {movie.get('year', '-')}")
        st.write(f"**Рейтинг:** ⭐ {movie.get('rating', 0):.1f}")
    
    with col2:
        st.write(f"**Жанры:** {movie.get('genre', '-')}")
    
    if movie.get("description"):
        st.caption(movie["description"][:200] + "...")

    if movie.get("stars"):
        actors = str(movie["stars"]).replace('[', '').replace(']', '').replace("'", "")
        while ", ," in actors:
            actors = actors.replace(", ,", ", ")
        actors = actors.strip(', ')
    
        if actors and len(actors) > 5:
            st.caption(f"**Актёры:** {actors[:100]}...")