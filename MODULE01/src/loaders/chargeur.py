"""Chargement des 5 sources brutes.

Chaque fonction lit UNE source, renomme ses colonnes avec des noms communs
et ajoute la provenance. On ne nettoie rien ici : les valeurs restent
telles qu'elles sont dans le fichier (en texte), pour ne rien perdre.
"""

import json

import pandas as pd

from MODULE01.src.config import DOSSIER_BRUT

# Le "moule" commun : toutes les sources auront ces colonnes, dans cet ordre
COLONNES_COMMUNES = [
    "source", "numero_ligne", "id_local", "date", "type_transaction",
    "type_bien", "region", "ville", "quartier", "prix", "devise",
    "surface", "pieces", "chambres", "salles_bain", "statut",
]


def _mettre_au_moule(tableau, nom_source):
    """Ajoute la provenance et force les mêmes colonnes pour toutes les sources."""
    tableau = tableau.copy()
    tableau["source"] = nom_source
    tableau["numero_ligne"] = range(1, len(tableau) + 1)

    # Colonne absente dans cette source -> on la crée vide
    for colonne in COLONNES_COMMUNES:
        if colonne not in tableau.columns:
            tableau[colonne] = None

    # Tout en texte : le nettoyage se fera plus tard, étape par étape
    return tableau[COLONNES_COMMUNES].astype("string")


def charger_plateforme():
    tableau = pd.read_csv(DOSSIER_BRUT / "plateforme_immo_sn.csv",
                          sep=";", dtype=str)
    tableau = tableau.rename(columns={
        "ref_plateforme": "id_local",
        "date_mise_en_ligne": "date",
        "categorie": "type_bien",
        "commune": "ville",
        "sdb": "salles_bain",
    })
    return _mettre_au_moule(tableau, "plateforme")


def charger_agence():
    tableau = pd.read_excel(DOSSIER_BRUT / "agence_teranga.xlsx",
                            sheet_name="Annonces", dtype=str)
    tableau = tableau.rename(columns={
        "Code": "id_local",
        "Date": "date",
        "Region": "region",
        "Ville": "ville",
        "Type": "type_bien",
        "Prix_FCFA": "prix",
        "Surface_m2": "surface",
        "Chambres": "chambres",
        "SDB": "salles_bain",
        "Statut": "statut",
    })
    return _mettre_au_moule(tableau, "agence")


def charger_particuliers():
    with open(DOSSIER_BRUT / "particuliers.json", encoding="utf-8") as fichier:
        annonces = json.load(fichier)

    lignes = []
    for objet in annonces:
        # .get(..., {}) : pas d'erreur si un bloc est absent
        annonce = objet.get("annonce", {})
        localisation = annonce.get("localisation", {})
        details = annonce.get("details", {})
        lignes.append({
            "id_local": annonce.get("id"),
            "date": annonce.get("date"),
            "region": localisation.get("region"),
            "ville": localisation.get("ville"),
            "type_transaction": details.get("transaction"),
            "type_bien": details.get("type"),
            "prix": details.get("prix"),
            "surface": details.get("surface"),
            "chambres": details.get("chambres"),
            "salles_bain": details.get("sdb"),
            "statut": annonce.get("statut"),
        })
    return _mettre_au_moule(pd.DataFrame(lignes), "particuliers")


def charger_notaires():
    tableau = pd.read_csv(DOSSIER_BRUT / "notaires.csv", sep=",", dtype=str)
    tableau = tableau.rename(columns={
        "id_acte": "id_local",
        "date_acte": "date",
        "type_bien": "type_bien",
        "montant_fcfa": "prix",
        "superficie": "surface",
        "nb_chambres": "chambres",
    })
    return _mettre_au_moule(tableau, "notaires")


def charger_historique():
    tableau = pd.read_csv(DOSSIER_BRUT / "import_historique.csv",
                          sep=";", encoding="latin-1", dtype=str)
    tableau = tableau.rename(columns={
        "ID": "id_local",
        "DateVente": "date",
        "Region": "region",
        "Ville": "ville",
        "TypeBien": "type_bien",
        "Prix": "prix",
        "Surface": "surface",
        "Chambres": "chambres",
        "SallesBain": "salles_bain",
    })
    return _mettre_au_moule(tableau, "historique")


def charger_toutes_les_sources():
    """Charge les 5 sources et les empile dans un seul tableau."""
    tableaux = [
        charger_plateforme(),
        charger_agence(),
        charger_particuliers(),
        charger_notaires(),
        charger_historique(),
    ]
    return pd.concat(tableaux, ignore_index=True)
