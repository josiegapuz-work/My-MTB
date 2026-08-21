# app.py
import json
from pathlib import Path
from typing import List, Dict, Any
import streamlit as st
import os
from PIL import Image

#=======================#
#===== Own Modules =====#
#=======================#

from type_score_helper import *
from gsheet_helper import *
from get_images import *
from card import *

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Mezastar Team Builder", layout="wide", initial_sidebar_state="expanded")
st.title("Pokemon Mezastar Team Builder")

# Load tags
tags = load_tags(DEFAULT_TAGS_FILE)
if not tags:
    st.stop()

# Build maps
name_map = {t.get("name"): t for t in tags}
all_names = sorted(name_map.keys())

# Sidebar: persistence controls
st.sidebar.header("Enter your Google Sheet ID to save your Tags!")
sheet_id_secret = st.secrets.get("owned_sheet_id", "")
sheet_id_input = st.sidebar.text_input("Google Sheet ID (optional)", value=sheet_id_secret)
use_sheet = bool(sheet_id_input and st.secrets.get("gcp_service_account"))

if sheet_id_input and not st.secrets.get("gcp_service_account"):
    st.sidebar.warning("Add your service account JSON to Streamlit secrets as gcp_service_account to enable Sheets persistence.")

# Determine default owned list (sheet -> local -> first N)
default_owned = all_names[:12]
if use_sheet:
    sheet_owned = load_owned_from_sheet(sheet_id_input)
    if sheet_owned:
        resolved = []
        for v in sheet_owned:
            if v in name_map:
                resolved.append(v)
            else:
                match = next((t.get("name") for t in tags if t.get("pokemon_id") == v), None)
                if match:
                    resolved.append(match)
        if resolved:
            default_owned = resolved
else:
    local_owned = load_owned_local()
    if local_owned:
        resolved = []
        for v in local_owned:
            if v in name_map:
                resolved.append(v)
            else:
                match = next((t.get("name") for t in tags if t.get("pokemon_id") == v), None)
                if match:
                    resolved.append(match)
        if resolved:
            default_owned = resolved

# Owned tags selection UI
st.sidebar.header("Your Owned Tags")
owned = st.sidebar.multiselect("Select tags you own", options=all_names, default=default_owned)

# Save buttons
if use_sheet:
    if st.sidebar.button("Save owned tags to Google Sheet"):
        save_owned_to_sheet(sheet_id_input, owned)
else:
    if st.sidebar.button("Save owned tags locally"):
        save_owned_local(owned)

# Enemy selection
st.sidebar.header("Enemies to Battle")

# enemy_mode = st.sidebar.radio("Choose enemies", ["Random 3", "Pick manually"])
# if enemy_mode == "Random 3":
#     import random
#     enemies = random.sample(tags, k=3) if len(tags) >= 3 else tags
# else:

# Pick up to 3 enemies
enemy_choices = st.sidebar.multiselect("Pick up to 3 enemies", options=all_names, max_selections=3, default=all_names[:3])
enemies = [name_map[n] for n in enemy_choices if n in name_map]

# ========= Main UI: show merged cards ========= #

st.subheader("Your Enemies")

if not owned:
    st.warning("You have not selected any owned tags. Select tags in the sidebar to get recommendations.")
    st.stop()

owned_tags = [name_map[n] for n in owned if n in name_map]

# create up to 3 tabs, using placeholders if fewer enemies selected
max_tabs = 3
names = []
for i in range(max_tabs):
    if i < len(enemies):
        names.append(enemies[i].get("name", "Unknown"))
    else:
        names.append(f"Select Enemy {i+1}")

enemy1, enemy2, enemy3 = st.tabs(names)

for n in range(len(enemies)):
    if n == 0:
        with enemy1:
            recs = recommend_against_enemy(owned_tags, enemies[0], top_n=4)
            enemy_with_team_card(enemies[0], recs)
    elif n == 1:
        with enemy2:
            recs = recommend_against_enemy(owned_tags, enemies[1], top_n=4)
            enemy_with_team_card(enemies[1], recs)
    elif n == 2:
        with enemy3:
            recs = recommend_against_enemy(owned_tags, enemies[2], top_n=4)
            enemy_with_team_card(enemies[2], recs)
    else:
        break
