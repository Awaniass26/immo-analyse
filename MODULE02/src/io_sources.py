"""Chargement indépendant des cinq sources brutes du module 2."""

import json

import pandas as pd

from . import config as C

COLONNES = [
    "id_local",
    "numero_ligne",
    "source",
    "date",
    "type_transaction",
    "categorie",
    "region",
    "commune",
    "quartier",
    "prix",
    "devise",
    "surface",
    "chambres",
    "sdb",
    "statut",
    "date_expiration",
    "description",
]


def _harmoniser(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """Aligne les colonnes sans modifier les valeurs des fichiers d'origine."""
    df = df.copy()
    df.columns = [str(colonne).strip() for colonne in df.columns]
    df["numero_ligne"] = range(1, len(df) + 1)
    df["source"] = source

    for colonne in COLONNES:
        if colonne not in df:
            df[colonne] = pd.NA

    return df[COLONNES].astype("string")


def lire_agence() -> pd.DataFrame:
    """Lit uniquement la feuille Annonces du fichier Excel."""
    df = pd.read_excel(C.F_AGENCE, sheet_name="Annonces", dtype=str)
    df = df.rename(columns={
        "Code": "id_local",
        "Date": "date",
        "Region": "region",
        "Ville": "commune",
        "Type": "categorie",
        "Prix_FCFA": "prix",
        "Surface_m2": "surface",
        "Chambres": "chambres",
        "SDB": "sdb",
        "Statut": "statut",
    })
    return _harmoniser(df, "agence")


def lire_historique() -> pd.DataFrame:
    """Lit le CSV historique en UTF-8 et marque ses lignes comme ventes."""
    df = pd.read_csv(C.F_HISTORIQUE, sep=";", encoding="latin-1", dtype=str)
    df = df.rename(columns={
        "ID": "id_local",
        "DateVente": "date",
        "Region": "region",
        "Ville": "commune",
        "TypeBien": "categorie",
        "Prix": "prix",
        "Surface": "surface",
        "SallesBain": "sdb",
    })
    df["type_transaction"] = "vente"
    df["statut"] = "Vendu"
    return _harmoniser(df, "historique")


def lire_notaires() -> pd.DataFrame:
    """Lit les actes notariés, qui représentent des ventes."""
    df = pd.read_csv(C.F_NOTAIRE, encoding="utf-8-sig", dtype=str)
    df = df.rename(columns={
        "id_acte": "id_local",
        "date_acte": "date",
        "ville": "commune",
        "type_bien": "categorie",
        "montant_fcfa": "prix",
        "superficie": "surface",
        "nb_chambres": "chambres",
    })
    df["type_transaction"] = "vente"
    return _harmoniser(df, "notaires")


def lire_particuliers() -> pd.DataFrame:
    """Aplatit les annonces JSON de particuliers."""
    with C.F_PARTICULIER.open(encoding="utf-8") as fichier:
        annonces = json.load(fichier)

    lignes = []
    for objet in annonces:
        annonce = objet.get("annonce", {})
        localisation = annonce.get("localisation", {})
        details = annonce.get("details", {})
        lignes.append({
            "id_local": annonce.get("id"),
            "date": annonce.get("date"),
            "region": localisation.get("region"),
            "commune": localisation.get("ville"),
            "categorie": details.get("type"),
            "type_transaction": details.get("transaction"),
            "prix": details.get("prix"),
            "surface": details.get("surface"),
            "chambres": details.get("chambres"),
            "sdb": details.get("sdb"),
            "statut": annonce.get("statut"),
        })

    return _harmoniser(pd.DataFrame(lignes), "particuliers")


def lire_plateforme() -> pd.DataFrame:
    """Lit le CSV plateforme et retire son éventuel en-tête répété."""
    df = pd.read_csv(C.F_PLATEFORME, sep=";", encoding="utf-8-sig", dtype=str)
    df = df.rename(columns={
        "ref_plateforme": "id_local",
        "date_mise_en_ligne": "date",
        "commune": "commune",
        "pieces": "chambres",
    })
    df = df[df["id_local"] != "ref_plateforme"].copy()
    return _harmoniser(df, "plateforme")


def lire_sources_brutes() -> pd.DataFrame:
    """Charge puis aligne les cinq sources sans dépendre du module 1."""
    sources = [
        lire_agence(),
        lire_historique(),
        lire_notaires(),
        lire_particuliers(),
        lire_plateforme(),
    ]
    return pd.concat(sources, ignore_index=True)


def lire_donnees_module02() -> pd.DataFrame:
    """Relit les lignes conformes et averties, jamais la quarantaine."""
    df = pd.read_csv(C.F_DONNEES_PROPRES)
    avertissements = pd.read_csv(C.F_AVERTISSEMENTS)
    df = pd.concat([df, avertissements], ignore_index=True)
    colonnes_requises = {
        "transaction",
        "type_bien",
        "region",
        "date",
        "prix_fcfa",
        "surface_m2",
    }
    manquantes = colonnes_requises.difference(df.columns)
    if manquantes:
        raise ValueError(
            "Le fichier propre du module 2 ne respecte pas le schéma attendu. "
            f"Colonnes manquantes : {', '.join(sorted(manquantes))}"
        )

    df = df.rename(columns={
        "transaction": "type_transaction",
        "type_bien": "categorie",
        "prix_fcfa": "prix",
        "surface_m2": "surface",
    })
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df["prix"] = pd.to_numeric(df["prix"], errors="raise")
    df["surface"] = pd.to_numeric(df["surface"], errors="raise")
    return df
