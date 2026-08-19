# app.py
import json
from pathlib import Path
from typing import List, Dict, Any
import streamlit as st

# Optional Google Sheets libs
try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception:
    gspread = None
    Credentials = None

# -------------------------
# Type chart (full 18 types)
# -------------------------
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
# Helpers: type and scoring
# -------------------------
def normalize_type(t):
    return t.strip().title() if isinstance(t, str) and t.strip() != "" else None

def get_move_type(tag: Dict[str, Any]) -> str:
    mt = tag.get("move_1_type") or (tag.get("types")[0] if tag.get("types") else None)
    return normalize_type(mt) or ""

def type_multiplier(attacker_type: str, defender_types: List[str]) -> float:
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
    defender_types = defender.get("types", []) or []
    move_type = get_move_type(attacker)
    t_mult = type_multiplier(move_type, defender_types)
    attack_val = int(attacker.get("attack") or 0)
    speed_val = int(attacker.get("speed") or 0)
    final = int(t_mult * 100000) + attack_val * 100 + speed_val
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
# Google Sheets helpers
# -------------------------
def get_gsheet_client_from_secrets():
    """
    Expects st.secrets["gcp_service_account"] to contain the service account JSON object.
    """
    if gspread is None or Credentials is None:
        raise RuntimeError("gspread/google-auth not installed. Add to requirements.txt")
    sa_info = st.secrets.get("gcp_service_account")
    if not sa_info:
        raise RuntimeError("Missing Streamlit secret: gcp_service_account")
    creds = Credentials.from_service_account_info(sa_info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    return client

def load_owned_from_sheet(sheet_id: str) -> List[str]:
    try:
        client = get_gsheet_client_from_secrets()
        sh = client.open_by_key(sheet_id)
        ws = sh.sheet1
        values = ws.col_values(1)
        return [v.strip() for v in values if v.strip()]
    except Exception as e:
        st.error(f"Failed to load owned tags from Google Sheet: {e}")
        return []

def save_owned_to_sheet(sheet_id: str, owned_list: List[str]):
    try:
        client = get_gsheet_client_from_secrets()
        sh = client.open_by_key(sheet_id)
        ws = sh.sheet1
        ws.clear()
        if owned_list:
            # write as column
            ws.update('A1', [[v] for v in owned_list])
        st.success("Saved owned tags to Google Sheet")
    except Exception as e:
        st.error(f"Failed to save owned tags to Google Sheet: {e}")

# -------------------------
# Load tags JSON (local file)
# -------------------------
DEFAULT_TAGS_FILE = "[02]stardust_v3_tags.json"
def load_tags(path: str) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        st.error(f"Tags file not found: {path}")
        return []
    with p.open(encoding="utf-8") as f:
        return json.load(f)

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Mezastar Team Builder", layout="wide")
st.title("Pokemon Mezastar Team Builder")

# Load tags
tags = load_tags(DEFAULT_TAGS_FILE)
if not tags:
    st.stop()

# Build maps
name_map = {t.get("name"): t for t in tags}
all_names = sorted(name_map.keys())

# Sidebar: Google Sheets persistence controls
st.sidebar.header("Persistence (Google Sheets)")
sheet_id = st.sidebar.text_input("Owned tags Google Sheet ID", value=st.secrets.get("owned_sheet_id", ""))
use_sheet = bool(sheet_id and st.secrets.get("gcp_service_account"))

if sheet_id and not st.secrets.get("gcp_service_account"):
    st.sidebar.warning("Add your service account JSON to Streamlit secrets as gcp_service_account to enable Sheets persistence.")

# Load owned defaults from sheet if available, otherwise from local default
default_owned = all_names[:12]
if use_sheet:
    try:
        sheet_owned = load_owned_from_sheet(sheet_id)
        if sheet_owned:
            # map ids to names if user stored ids; prefer names
            resolved = []
            for v in sheet_owned:
                if v in name_map:
                    resolved.append(v)
                else:
                    # try to match by pokemon_id
                    match = next((t.get("name") for t in tags if t.get("pokemon_id") == v), None)
                    if match:
                        resolved.append(match)
            if resolved:
                default_owned = resolved
    except Exception:
        pass

# Owned tags selection UI
st.sidebar.header("Your Owned Tags")
owned = st.sidebar.multiselect("Select tags you own", options=all_names, default=default_owned)

# Save to sheet button
if use_sheet:
    if st.sidebar.button("Save owned tags to Google Sheet"):
        # Save names; you may prefer to save pokemon_id instead
        save_owned_to_sheet(sheet_id, owned)

# Enemy selection
st.sidebar.header("Enemies to Battle")
enemy_mode = st.sidebar.radio("Choose enemies", ["Random 3", "Pick manually"])
if enemy_mode == "Random 3":
    import random
    enemies = random.sample(tags, k=3) if len(tags) >= 3 else tags
else:
    enemy_choices = st.sidebar.multiselect("Pick up to 3 enemies", options=all_names, max_selections=3, default=all_names[:3])
    enemies = [name_map[n] for n in enemy_choices if n in name_map]

# Main UI: show enemies
st.subheader("Selected Enemies")
cols = st.columns(len(enemies) if enemies else 1)
for c, e in zip(cols, enemies):
    with c:
        st.markdown(f"**{e.get('name')}**")
        st.write(f"Types: {', '.join(e.get('types') or [])}")
        st.write(f"HP: {e.get('hp')}, Attack: {e.get('attack')}, Speed: {e.get('speed')}")

if not owned:
    st.warning("You have not selected any owned tags. Select tags in the sidebar to get recommendations.")
    st.stop()

owned_tags = [name_map[n] for n in owned if n in name_map]

# Compute and display recommendations
st.subheader("Recommendations from Your Owned Tags")
for enemy in enemies:
    st.markdown(f"### Against {enemy.get('name')}")
    recs = recommend_against_enemy(owned_tags, enemy, top_n=6)
    if not recs:
        st.write("No recommendations available.")
        continue
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
st.info("Type effectiveness dominates the ranking, then attack, then speed.")

# Footer: instructions for Streamlit Cloud
st.markdown("#### Deploying to Streamlit Community Cloud")
st.markdown(
    """
1. Push this repo to GitHub (include app.py, [02]stardust_v3_tags.json, requirements.txt).  
2. On Streamlit Cloud, create a new app from the repo.  
3. In the app settings, add two secrets:  
   - gcp_service_account (paste the service account JSON object)  
   - owned_sheet_id (the Google Sheet ID)  
4. In the app UI sidebar, paste the Sheet ID (or set it in secrets as owned_sheet_id).  
5. Run the app. The app will read/write your owned tags to the sheet.
"""
)
