"""Étape 1 : fonctions simples sur des biens immobiliers.

Notions : variables, conditions, boucles, fonctions, exceptions,
listes, dictionnaires, tuples, ensembles.
"""

BIENS = [
    {"ville": "Dakar", "type": "Villa", "prix": 120_000_000, "surface": 250.0},
    {"ville": "Thiès", "type": "Maison", "prix": 45_000_000, "surface": 120.0},
    {"ville": "Dakar", "type": "Studio", "prix": 25_000_000, "surface": 30.0},
    {"ville": "Saint-Louis", "type": "Terrain", "prix": 8_000_000, "surface": 400.0},
    {"ville": "Thiès", "type": "Maison", "prix": 52_000_000, "surface": 140.0},
]


def filtrer_par_ville(biens, ville):
    """Liste des biens d'une ville."""
    return [bien for bien in biens if bien["ville"] == ville]


def villes_uniques(biens):
    """Ensemble (set) des villes, sans doublon."""
    return {bien["ville"] for bien in biens}


def compter_par_type(biens):
    """Dictionnaire {type: nombre de biens}."""
    comptes = {}
    for bien in biens:
        type_bien = bien["type"]
        comptes[type_bien] = comptes.get(type_bien, 0) + 1
    return comptes


def prix_moyen(biens):
    """Prix moyen, ou None si la liste est vide."""
    if len(biens) == 0:
        return None
    total = 0
    for bien in biens:
        total += bien["prix"]
    return total / len(biens)


def bien_le_plus_cher(biens):
    """Le bien au prix le plus élevé, ou None si la liste est vide."""
    if not biens:
        return None
    return max(biens, key=lambda bien: bien["prix"])


def convertir_en_entier(texte):
    """Convertit un texte en entier, ou None s'il est illisible (exception gérée)."""
    try:
        return int(texte)
    except (ValueError, TypeError):
        return None


def verifier_bien(bien):
    """Renvoie un tuple (est_valide, liste_des_problemes)."""
    problemes = []
    if bien.get("prix") is None or bien["prix"] <= 0:
        problemes.append("prix invalide")
    if bien.get("surface") is None or bien["surface"] <= 0:
        problemes.append("surface invalide")
    if not bien.get("ville"):
        problemes.append("ville absente")
    return len(problemes) == 0, problemes