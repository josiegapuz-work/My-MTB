# -------------------------
# Type chart (full 18 types)
# -------------------------

def type_chart():
    type_dict = {
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
    return type_dict
