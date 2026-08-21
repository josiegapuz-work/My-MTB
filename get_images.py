from pathlib import Path
from typing import List
import streamlit as st

# -------------------------
# Aesthetics helpers
# -------------------------
def show_types(types: List[str]):
    """Display type icons with names side by side. Responsive on mobile."""
    if not types:
        return
    cols = st.columns(len(types), vertical_alignment="center")
    for c, t in zip(cols, types):
        img_path = Path(__file__).parent / "types_img" / f"{t}.png"
        with c:
            try:
                if img_path.exists():
                    st.image(str(img_path), width=200)
                else:
                    st.caption(t)
            except Exception:
                st.caption(t)

def get_tag_image_path(pokemon_id: str) -> Path:
    return Path(__file__).parent / "images" / f"pm_en_{pokemon_id}_f.jpg"
