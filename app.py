# app.py
import json
import random
from pathlib import Path
from typing import List, Dict, Any

import streamlit as st

# -------------------------
# Type chart (full 18 types)
# -------------------------
# You can also keep this in a separate type_chart.json file if you prefer.
type_chart = {
    "Normal": {"super_effective": [], "not_very_effective": ["Rock", "Steel"], "immune": ["Ghost"]},
    "Fighting": {"super_effective": ["Normal", "Rock", "Steel", "Ice", "Dark"], "not_very_effective": ["Flying", "Poison", "Bug", "Psychic", "Fairy"], "immune": ["Ghost"]},
    "Poison": {"super_effective": ["Grass", "Fairy"], "not_very_effective": ["Poison", "Ground", "Rock", "Ghost"], "immune": ["Steel"]},
    "Ground": {"super_effective": ["Fire", "Electric", "Poison", "Rock", "Steel"], "not_very_effective": ["Grass", "Bug"], "immune": ["Flying"]},
    "Flying": {"super_effective": ["Grass", "Fighting", "Bug"], "not_very_effective": ["Electric", "Rock", "Steel"], "immune": []},
    "Bug": {"super_effective": ["Grass", "Psychic", "Dark"], "not_very_effective": ["Fire", "Fighting", "Flying", "Ghost", "Steel", "Fairy"], "immune": []},
    "Rock": {"super_effective": ["Fire", "Ice", "Flying", "Bug"], "not_very_effective": ["Fighting", "Ground", "Steel"], "immune": []},
    "Ghost": {"super_effective": ["Psychic", "Ghost"], "not_very_effective": ["Dark"], "immune": ["Normal"]},
    "Steel": {"super_effective": ["Ice", "Rock", "Fairy"], "not_very_effective": ["Fire", "Water", "Electric", "Steel"], "immune": []},
    "Fire": {"super_effective": ["Grass", "Bug", "Ice", "Steel"], "not_very_effective": ["Fire", "Water", "Rock", "Dragon"], "immune": []},
    "Water": {"super_effective": ["Fire", "Ground", "Rock"], "not_very_effective": ["Water", "Grass", "Dragon"], "immune": []},
    "Electric": {"super_effective": ["Water", "Flying"], "not_very_effective": ["Electric", "Grass", "Dragon"], "immune": ["Ground"]},
    "Grass": {"super_effective": ["Water", "Ground", "Rock"], "not_very_effective": ["Fire", "Grass", "Poison", "Flying", "Bug", "Dragon", "Steel"], "immune": []},
    "Ice": {"super_effective": ["Grass", "Ground", "Flying", "Dragon"], "not_very_effective": ["Fire", "Water", "Ice", "Steel"], "immune": []},
    "Psychic": {"super_effective": ["Fighting", "Poison"], "not_very_effective": ["Psychic", "Steel"], "immune": ["Dark"]},
    "Dragon": {"super_effective": ["Dragon"], "not_very_effective": ["Steel"], "immune": ["Fairy"]},
    "Dark": {"super_effective": ["Psychic", "Ghost"], "not_very_effective": ["Fighting", "Dark", "Fairy"], "immune": []},
    "Fairy": {"super_effective": ["Fighting", "Dragon", "Dark"], "not_very_effective": ["Fire", "Poison", "Steel"], "immune": []}
}

# -------------------------
# Helper functions
# -------------------------
def load_tags(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        st.error(f"Tags file not found: {path}")
        return []
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def normalize_type(t):
    return t.strip().title() if isinstance(t, str) and t.strip() != "" else None

def get_move_type(tag: Dict[str, Any]) -> str:
    # Prefer move_1_type if present, otherwise use first type of the Pokémon
    mt = tag.get("move_1_type") or (tag.get("types")[0] if tag.get("types") else None)
    return normalize_type(mt) or ""

def type_multiplier(attacker_type: str, defender_types: List[str]) -> float:
    # attacker_type: single type string
    # defender_types: list of defender types
    if not attacker_type:
        return 1.0
    attacker_type = normalize_type(attacker_type)
    mult = 1.0
    chart = type_chart.get(attacker_type, {})
    for d in defender_types:
        dnorm = normalize_type(d)
        if not dnorm:
            continue
        if dnorm in chart.get("super_effective", []):
            mult *= 2.0
        elif dnorm in chart.get("not_very_effective", []):
            mult *= 0.5
        elif dnorm in chart.get("immune", []):
            mult *= 0.0
        else:
            mult *= 1.0
    return mult

def compute_score(attacker: Dict[str, Any], defender: Dict[str, Any]) -> float:
    """
    Composite score that enforces priority:
      1) Type effectiveness (dominant)
      2) Attack stat
      3) Speed stat
    Implementation detail:
      - type_score is multiplier (0, 0.5, 1, 2, 4 for dual super etc.)
      - final numeric score = int(type_score * 100000) + attack * 100 + speed
      This ensures type dominates ordering.
    """
    defender_types = defender.get("types", []) or []
    move_type = get_move_type(attacker)
    t_mult = type_multiplier(move_type, defender_types)
    # Normalize attack and speed to numeric safe values
    attack_val = attacker.get("attack") or 0
    speed_val = attacker.get("speed") or 0
    # Compose final score
    final = int(t_mult * 100000) + int(attack_val) * 100 + int(speed_val)
    return final

def recommend_against_enemy(owned_tags: List[Dict[str, Any]], enemy: Dict[str, Any], top_n: int = 6) -> List[Dict[str, Any]]:
    scored = []
    for tag in owned_tags:
        score = compute_score(tag, enemy)
        scored.append((score, tag))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for s, tag in scored[:top_n]:
        results.append({
            "pokemon_id": tag.get("pokemon_id"),
            "name": tag.get("name"),
            "types": tag.get("types"),
            "move_type": get_move_type(tag),
            "attack": tag.get("attack") or 0,
            "speed": tag.get("speed") or 0,
            "score": s
        })
    return results

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Mezastar Team Builder", layout="wide")
st.title("Pokemon Mezastar Team Builder")

# Load tags
default_path = "[02]stardust_v3_tags.json"
tags = load_tags(default_path)
if not tags:
    st.stop()

# Sidebar controls
st.sidebar.header("Data and Controls")
st.sidebar.markdown("Upload your tags JSON to override the default file.")
uploaded = st.sidebar.file_uploader("Upload [02]stardust_v3_tags.json", type=["json"])
if uploaded:
    try:
        tags = json.load(uploaded)
        st.sidebar.success("Uploaded tags loaded")
    except Exception as e:
        st.sidebar.error("Failed to load uploaded JSON")

# Build lookup maps
id_map = {t.get("pokemon_id"): t for t in tags}
name_map = {t.get("name"): t for t in tags}

# Owned tags selection
st.sidebar.header("Your Owned Tags")
all_names = [t.get("name") for t in tags]
owned = st.sidebar.multiselect("Select tags you own (or upload file)", options=all_names, default=all_names[:12])

# Option to upload a simple list of owned IDs (optional)
owned_file = st.sidebar.file_uploader("Upload owned IDs (one per line) optional", type=["txt", "csv"])
if owned_file:
    try:
        content = owned_file.read().decode("utf-8").splitlines()
        # match by id or name
        owned = []
        for line in content:
            s = line.strip()
            if s in id_map:
                owned.append(id_map[s].get("name"))
            elif s in name_map:
                owned.append(s)
        st.sidebar.success("Owned list loaded")
    except Exception:
        st.sidebar.error("Could not parse owned file")

owned_tags = [name_map[n] for n in owned if n in name_map]

# Enemy selection
st.sidebar.header("Enemies to Battle")
enemy_mode = st.sidebar.radio("Choose enemies", ["Random 3", "Pick manually"])
if enemy_mode == "Random 3":
    enemies = random.sample(tags, k=3) if len(tags) >= 3 else tags
else:
    enemy_choices = st.sidebar.multiselect("Pick up to 3 enemies", options=all_names, max_selections=3)
    enemies = [name_map[n] for n in enemy_choices if n in name_map]

# Main UI
st.subheader("Selected Enemies")
cols = st.columns(len(enemies) if enemies else 1)
for c, e in zip(cols, enemies):
    with c:
        st.markdown(f"**{e.get('name')}**")
        st.write(f"Types: {', '.join(e.get('types') or [])}")
        st.write(f"HP: {e.get('hp')}, Attack: {e.get('attack')}, Speed: {e.get('speed')}")

if not owned_tags:
    st.warning("You have not selected any owned tags. Select tags in the sidebar to get recommendations.")
    st.stop()

# Compute recommendations
st.subheader("Recommendations from Your Owned Tags")
for enemy in enemies:
    st.markdown(f"### Against {enemy.get('name')}")
    recs = recommend_against_enemy(owned_tags, enemy, top_n=6)
    if not recs:
        st.write("No recommendations available.")
        continue
    # Display table
    rows = []
    for r in recs:
        rows.append({
            "Name": r["name"],
            "Move Type": r["move_type"],
            "Types": ", ".join(r["types"] or []),
            "Attack": r["attack"],
            "Speed": r["speed"],
            "Score": r["score"]
        })
    st.table(rows)

st.markdown("---")
st.info("How scoring works: Type effectiveness dominates (super effective > normal > not very > immune). Within the same type effectiveness, higher attack then higher speed are preferred.")

# Footer with run instructions
st.markdown("#### Run instructions")
st.markdown(
    """
1. Install Streamlit: `pip install streamlit`  
2. Place `app.py` and `[02]stardust_v3_tags.json` in the same folder.  
3. Run: `streamlit run app.py`  
4. On your iPhone, open `http://<your-computer-ip>:8501` (use your computer's local IP).  
   - Make sure your computer and iPhone are on the same Wi‑Fi network.  
   - If you need to allow firewall access, permit Python/Streamlit to accept connections.
"""
)
