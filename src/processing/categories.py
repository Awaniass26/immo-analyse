"""Normalisation : ville, région, type de bien, transaction, périodicité."""

import re
import unicodedata

import pandas as pd

from src.config import DOSSIER_REFERENTIELS, SOURCES_VENTES, TYPES_TRANSACTION


def simplifier(texte):
    """Minuscules, sans accents, sans espaces en trop : 'THIÈS ' -> 'thies'."""
    texte = unicodedata.normalize("NFD", str(texte).strip().lower())
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texte)


# ---------- Référentiels -------------------------------------------------
def charger_geographie():
    """Renvoie (villes, regions, region_de_ville)."""
    tableau = pd.read_csv(DOSSIER_REFERENTIELS / "referentiel_geographique.csv")
    villes = {simplifier(v): v for v in tableau["ville"]}
    regions = {simplifier(r): r for r in tableau["region"].unique()}
    region_de_ville = dict(zip(tableau["ville"], tableau["region"]))
    return villes, regions, region_de_ville


def charger_types_de_bien():
    """Renvoie (synonymes, fourchettes)."""
    tableau = pd.read_csv(DOSSIER_REFERENTIELS / "referentiel_categories.csv")
    synonymes = {}
    fourchettes = {}
    for _, ligne in tableau.iterrows():
        categorie = ligne["categorie"]
        synonymes[simplifier(categorie)] = categorie
        for mot in ligne["synonymes"].split("|"):
            synonymes[simplifier(mot)] = categorie
        fourchettes[categorie] = (
            ligne["prix_min_indicatif"], ligne["prix_max_indicatif"],
            ligne["surface_min_typique"], ligne["surface_max_typique"],
        )
    return synonymes, fourchettes


# ---------- Normalisation ------------------------------------------------
def normaliser_nom(texte, dictionnaire):
    """Cherche le nom officiel. Renvoie (nom, etat) : ok, corrige,
    hors_referentiel ou manquant. On ne corrige JAMAIS sans preuve."""
    if texte is None or pd.isna(texte) or str(texte).strip() == "":
        return None, "manquant"

    cle = simplifier(texte)
    if cle in dictionnaire:
        officiel = dictionnaire[cle]
        return officiel, ("ok" if officiel == str(texte).strip() else "corrige")
    return str(texte).strip(), "hors_referentiel"


def deduire_transaction(type_brut, source, statut):
    """Renvoie (vente|location|None, etat)."""
    if pd.notna(type_brut):
        cle = simplifier(type_brut)
        if cle in TYPES_TRANSACTION:
            return cle, "ok"
        return None, "non_interpretable"

    if source in SOURCES_VENTES:
        return "vente", "deduit_source"

    cle = simplifier(statut) if pd.notna(statut) else ""
    if cle == "loue":
        return "location", "deduit_statut"
    if cle in ("vendu", "en vente"):
        return "vente", "deduit_statut"
    return None, "ambigu"      # "Disponible" : vente ou location ? on ne devine pas


def normaliser_periodicite(devise, transaction):
    """Renvoie (periodicite|None, etat). Seules les locations en ont une."""
    if transaction != "location":
        return None, "sans_objet"
    if pd.isna(devise):
        return None, "inconnue"
    if re.search(r"/\s*mois|par mois|mensuel|mens\.?", simplifier(devise)):
        return "mensuel", "ok"
    return None, "inconnue"