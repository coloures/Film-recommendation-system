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
        st.caption(movie["description"])

    if movie.get("stars"):
        actors = movie["stars"]
        if isinstance(actors, str):
            actors = actors.replace('[', '').replace(']', '').replace("'", "")
            actors_list = [actor.strip() for actor in actors.split(',') if actor.strip()]
        elif isinstance(actors, list):
            actors_list = [str(actor).strip() for actor in actors if str(actor).strip()]
        else:
            actors_list = []

        filtered_actors = []
        for actor in actors_list:
            actor = actor.strip()
            if (actor and 
                len(actor) > 2 and 
                not actor.endswith(':') and
                actor != '|' and 
                not actor.startswith(':')): 
                filtered_actors.append(actor)
        if filtered_actors:
            display_actors = filtered_actors[:7]
            st.caption(f"**Актёры:** {', '.join(display_actors)}")