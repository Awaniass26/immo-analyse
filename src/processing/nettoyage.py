"""Nettoyage du tableau complet : ajoute des colonnes propres, garde le brut."""

import pandas as pd

from src.processing.categories import (
    charger_geographie, charger_types_de_bien, deduire_transaction,
    normaliser_nom, normaliser_periodicite,
)
from src.processing.dates import convertir_date
from src.processing.prix import convertir_prix
from src.processing.surface import convertir_surface


def _ajouter(donnees, colonne, resultats, nom_valeur, dtype=None):
    """Range une liste de (valeur, etat) dans deux colonnes."""
    donnees[nom_valeur] = pd.Series(
        [r[0] for r in resultats], index=donnees.index, dtype=dtype or "object")
    donnees[colonne + "_etat"] = [r[1] for r in resultats]


def ajouter_prix_nombre(donnees):
    donnees = donnees.copy()
    _ajouter(donnees, "prix", donnees["prix"].map(convertir_prix),
             "prix_nombre", "Int64")
    return donnees


def ajouter_surface_nombre(donnees):
    donnees = donnees.copy()
    _ajouter(donnees, "surface", donnees["surface"].map(convertir_surface),
             "surface_nombre", "Float64")
    return donnees


def nettoyer(donnees):
    """Applique toutes les normalisations. Les colonnes brutes sont conservées."""
    donnees = ajouter_prix_nombre(donnees)
    donnees = ajouter_surface_nombre(donnees)

    _ajouter(donnees, "date", donnees["date"].map(convertir_date), "date_iso")

    villes, regions, _ = charger_geographie()
    synonymes, _ = charger_types_de_bien()
    _ajouter(donnees, "ville", [normaliser_nom(v, villes) for v in donnees["ville"]], "ville_ref")
    _ajouter(donnees, "region", [normaliser_nom(r, regions) for r in donnees["region"]], "region_ref")
    _ajouter(donnees, "type_bien", [normaliser_nom(t, synonymes) for t in donnees["type_bien"]], "type_bien_ref")

    transactions = [
        deduire_transaction(t, s, st)
        for t, s, st in zip(donnees["type_transaction"], donnees["source"], donnees["statut"])
    ]
    _ajouter(donnees, "transaction", transactions, "transaction_ref")

    periodicites = [
        normaliser_periodicite(d, t)
        for d, t in zip(donnees["devise"], donnees["transaction_ref"])
    ]
    _ajouter(donnees, "periodicite", periodicites, "periodicite_ref")

    donnees["chambres_nombre"] = pd.to_numeric(donnees["chambres"], errors="coerce").round().astype("Int64")
    donnees["sdb_nombre"] = pd.to_numeric(donnees["salles_bain"], errors="coerce").round().astype("Int64")

    etats = [c for c in donnees.columns if c.endswith("_etat")]
    corriges = ("corrige", "deduit_source", "deduit_statut")
    donnees["corrige"] = donnees[etats].isin(corriges).any(axis=1)
    return donnees