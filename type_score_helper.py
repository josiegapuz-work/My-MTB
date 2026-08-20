from pathlib import Path
from typing import List, Dict, Any
import streamlit as st

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