"""Règles métier de validation.

Chaque règle est un petit objet avec un nom, une gravité, un motif et une
fonction qui regarde UNE ligne et répond :
    True  -> conforme
    False -> non conforme
    None  -> non évaluable (ex. règle sur les loyers, mais c'est une vente)
"""

from datetime import date

import pandas as pd

from MODULE01.src import config
from MODULE01.src.processing.categories import charger_geographie, charger_types_de_bien

AUJOURDHUI = date.today().isoformat()
_, _, REGION_DE_VILLE = charger_geographie()
_, FOURCHETTES = charger_types_de_bien()


class RegleValidation:
    """Une règle métier : bloquante (quarantaine) ou avertissement (on garde)."""

    def __init__(self, nom, gravite, motif, fonction):
        self.nom = nom
        self.gravite = gravite        # "bloquante" ou "avertissement"
        self.motif = motif
        self.fonction = fonction

    def appliquer(self, donnees):
        resultats = [self.fonction(ligne) for _, ligne in donnees.iterrows()]
        return pd.Series(resultats, index=donnees.index, dtype="boolean")


# ---------- Fonctions de règles (une ligne -> True / False / None) --------
def _est_vente(ligne):
    return ligne["transaction_ref"] == "vente"


def _est_location(ligne):
    return ligne["transaction_ref"] == "location"


def id_present(ligne):
    return pd.notna(ligne["id_local"])


def transaction_interpretable(ligne):
    return pd.notna(ligne["transaction_ref"])


def prix_valide(ligne):
    return pd.notna(ligne["prix_nombre"]) and ligne["prix_nombre"] > 0


def surface_valide(ligne):
    return pd.notna(ligne["surface_nombre"]) and ligne["surface_nombre"] > 0


def date_valide(ligne):
    return pd.notna(ligne["date_iso"])


def date_pas_future_si_conclue(ligne):
    if pd.isna(ligne["date_iso"]):
        return None
    statut = str(ligne["statut"]).strip().lower() if pd.notna(ligne["statut"]) else ""
    conclue = (statut in config.STATUTS_VENTE_CONCLUE
               or ligne["source"] in config.SOURCES_VENTES)
    if not conclue:
        return None
    return ligne["date_iso"] <= AUJOURDHUI      # comparaison de textes ISO


def type_bien_dans_referentiel(ligne):
    return ligne["type_bien_etat"] in ("ok", "corrige")


def surface_non_atypique(ligne):
    if pd.isna(ligne["surface_nombre"]):
        return None
    return config.SURFACE_ATYPIQUE_MIN <= ligne["surface_nombre"] <= config.SURFACE_ATYPIQUE_MAX


def prix_vente_non_atypique(ligne):
    if not _est_vente(ligne) or pd.isna(ligne["prix_nombre"]):
        return None
    return config.PRIX_ATYPIQUE_MIN <= ligne["prix_nombre"] <= config.PRIX_ATYPIQUE_MAX


def loyer_non_atypique(ligne):
    if not _est_location(ligne) or ligne["periodicite_ref"] != "mensuel":
        return None                       # on ne compare qu'à un loyer mensuel
    if pd.isna(ligne["prix_nombre"]):
        return None
    return config.LOYER_MIN <= ligne["prix_nombre"] <= config.LOYER_MAX


def periodicite_connue(ligne):
    if not _est_location(ligne):
        return None
    return pd.notna(ligne["periodicite_ref"])


def prix_dans_fourchette_categorie(ligne):
    if not _est_vente(ligne) or pd.isna(ligne["prix_nombre"]):
        return None
    if ligne["type_bien_ref"] not in FOURCHETTES:
        return None
    prix_min, prix_max, _, _ = FOURCHETTES[ligne["type_bien_ref"]]
    return prix_min <= ligne["prix_nombre"] <= prix_max


def surface_dans_fourchette_categorie(ligne):
    if pd.isna(ligne["surface_nombre"]) or ligne["type_bien_ref"] not in FOURCHETTES:
        return None
    _, _, surface_min, surface_max = FOURCHETTES[ligne["type_bien_ref"]]
    return surface_min <= ligne["surface_nombre"] <= surface_max


def ville_connue(ligne):
    if ligne["ville_etat"] == "manquant":
        return None
    return ligne["ville_etat"] != "hors_referentiel"


def region_ville_coherentes(ligne):
    if pd.isna(ligne["ville_ref"]) or pd.isna(ligne["region_ref"]):
        return None
    if ligne["ville_etat"] == "hors_referentiel":
        return None
    return REGION_DE_VILLE.get(ligne["ville_ref"]) == ligne["region_ref"]


def chambres_non_atypiques(ligne):
    if pd.isna(ligne["chambres_nombre"]):
        return None
    if ligne["type_bien_ref"] in ("Appartement", "Studio"):
        return ligne["chambres_nombre"] <= config.CHAMBRES_MAX_APPARTEMENT
    return True


def sdb_non_atypiques(ligne):
    if pd.isna(ligne["sdb_nombre"]) or pd.isna(ligne["chambres_nombre"]):
        return None
    return ligne["sdb_nombre"] <= ligne["chambres_nombre"] + 2


# ---------- La liste complète des règles ---------------------------------
REGLES = [
    RegleValidation("id_present", "bloquante", "identifiant absent", id_present),
    RegleValidation("transaction_interpretable", "bloquante",
                    "vente ou location non interprétable", transaction_interpretable),
    RegleValidation("prix_valide", "bloquante",
                    "prix absent, illisible ou <= 0", prix_valide),
    RegleValidation("surface_valide", "bloquante",
                    "surface absente, illisible ou <= 0", surface_valide),
    RegleValidation("date_valide", "bloquante",
                    "date absente ou impossible", date_valide),
    RegleValidation("date_pas_future_si_conclue", "bloquante",
                    "date future pour une transaction conclue", date_pas_future_si_conclue),
    RegleValidation("type_bien_dans_referentiel", "bloquante",
                    "type de bien hors référentiel", type_bien_dans_referentiel),
    RegleValidation("surface_non_atypique", "avertissement",
                    "surface atypique", surface_non_atypique),
    RegleValidation("prix_vente_non_atypique", "avertissement",
                    "prix de vente atypique", prix_vente_non_atypique),
    RegleValidation("loyer_non_atypique", "avertissement",
                    "loyer mensuel atypique", loyer_non_atypique),
    RegleValidation("periodicite_connue", "avertissement",
                    "périodicité du loyer inconnue", periodicite_connue),
    RegleValidation("prix_dans_fourchette_categorie", "avertissement",
                    "prix hors fourchette indicative du type de bien",
                    prix_dans_fourchette_categorie),
    RegleValidation("surface_dans_fourchette_categorie", "avertissement",
                    "surface hors fourchette typique du type de bien",
                    surface_dans_fourchette_categorie),
    RegleValidation("ville_connue", "avertissement",
                    "ville absente du référentiel", ville_connue),
    RegleValidation("region_ville_coherentes", "avertissement",
                    "ville et région incompatibles", region_ville_coherentes),
    RegleValidation("chambres_non_atypiques", "avertissement",
                    "trop de chambres pour ce type de bien", chambres_non_atypiques),
    RegleValidation("sdb_non_atypiques", "avertissement",
                    "plus de salles de bain que de chambres + 2", sdb_non_atypiques),
]


def valider(donnees):
    """Applique toutes les règles.

    Renvoie (donnees avec motifs, tableau des résultats par règle).
    """
    donnees = donnees.copy()
    resultats = pd.DataFrame(
        {regle.nom: regle.appliquer(donnees) for regle in REGLES})

    motifs_bloquants = []
    motifs_avertissements = []
    for indice in donnees.index:
        bloquants, avertissements = [], []
        for regle in REGLES:
            valeur = resultats.at[indice, regle.nom]
            if pd.notna(valeur) and not valeur:        # False = non conforme
                (bloquants if regle.gravite == "bloquante" else avertissements).append(regle.motif)
        motifs_bloquants.append("; ".join(bloquants))
        motifs_avertissements.append("; ".join(avertissements))

    donnees["motif_quarantaine"] = motifs_bloquants
    donnees["avertissements"] = motifs_avertissements
    donnees["en_quarantaine"] = donnees["motif_quarantaine"] != ""
    return donnees, resultats