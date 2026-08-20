from typing import List, Dict, Any
import streamlit as st
from PIL import Image

from get_images import *

# -------------------------
# Combined card renderer
# -------------------------
def enemy_with_team_card(enemy: Dict[str, Any], recommendations: List[Dict[str, Any]]):
    """
    Single merged card: everything about the enemy, then underneath the recommended team.
    Designed to be placed inside a column; three such cards can be shown side-by-side.
    """
    with st.container():
        st.markdown("---")
        # Enemy header
        st.markdown(f"## {enemy.get('name')}")
        # Enemy image
        img_path = get_tag_image_path(enemy.get("pokemon_id"))
        try:
            if img_path.exists():
                image = Image.open(img_path)
                st.image(image, use_container_width=True)
            else:
                st.write("(Enemy image not found)")
        except Exception as ex:
            st.write("(Enemy image failed to load)", ex)

        # Enemy types and stats
        st.write("**Types:**")
        show_types(enemy.get("types") or [])

        stats_cols = st.columns(3)
        stats_cols[0].metric("HP", enemy.get("hp"))
        stats_cols[1].metric("Attack", enemy.get("attack"))
        stats_cols[2].metric("Speed", enemy.get("speed"))

        st.markdown("----")
        st.markdown("**Recommended Pokemon**")

        if not recommendations:
            st.write("No recommendations available.")
            st.markdown("---")
            return

        # Render up to 6 recommendations in rows of 3 (responsive)
        for row_start in range(0, len(recommendations), 2):
            row = recommendations[row_start:row_start + 2]
            cols = st.columns(len(row))
            for col_idx, (c, r) in enumerate(zip(cols, row)):
                with c:
                    # compact team card inside the merged card
                    st.markdown("###")
                    st.markdown(f"**{r.get('name')}**")
                    # inner_cols = st.columns([1, 2])
                    # with inner_cols[0]:
                    img_path = get_tag_image_path(r.get("pokemon_id"))
                    try:
                        if img_path.exists():
                            image = Image.open(img_path)
                            st.image(image, use_container_width=True)
                        else:
                            st.write("(Image not found)")
                    except Exception as ex:
                        st.write("(Image failed to load)", ex)
                    # with inner_cols[1]:
                    # st.write("**Move Type:**")
                    # show_types([r.get("move_type")] if r.get("move_type") else [])
                    st.write("**Types:**")
                    show_types(r.get("types") or [])
                    # Stats: Attack, Speed, Score
                    stats = st.columns(2)
                    stats[0].metric("Attack", r.get("attack", 0))
                    stats[1].metric("Speed", r.get("speed", 0))
                    st.metric("Score", r.get("score", 0))
        st.markdown("---")
