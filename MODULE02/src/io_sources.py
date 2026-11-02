# src/io_sources.py
"""Chargement du résultat module 1 et helpers de lecture pour les exercices."""
import json
import pandas as pd
from . import config as C


def lire_donnees_module01() -> pd.DataFrame:
    """Charge le jeu validé par le module 1 et l'adapte au schéma d'analyse."""
    df = pd.read_csv(C.F_DONNEES_MODULE01)
    colonnes_requises = {
        "transaction", "type_bien", "region", "date", "prix_fcfa", "surface_m2",
    }
    manquantes = colonnes_requises.difference(df.columns)
    if manquantes:
        raise ValueError(
            "Le fichier du module 1 ne respecte pas le schéma attendu. "
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


def lire_agence() -> pd.DataFrame:
    """Excel, feuille Annonces uniquement (⚠️ PAS la feuille Params)."""
    df = pd.read_excel(C.F_AGENCE, sheet_name="Annonces")
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        "Code": "id", "Date": "date", "Region": "region", "Ville": "commune",
        "Type": "categorie", "Prix_FCFA": "prix", "Surface_m2": "surface",
        "Chambres": "chambres", "SDB": "sdb", "Statut": "statut",
    })
    df["source"] = "agence"
    df["type_transaction"] = None  # absent de la source
    return df


def lire_historique() -> pd.DataFrame:
    """Lit l'historique en latin-1 ; le texte reste brut pour le nettoyage."""
    df = pd.read_csv(C.F_HISTORIQUE, sep=";", encoding="latin-1", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        "ID": "id", "DateVente": "date", "Region": "region", "Ville": "commune",
        "TypeBien": "categorie", "Prix": "prix", "Surface": "surface",
        "Chambres": "chambres", "SallesBain": "sdb",
    })
    df["source"] = "historique"
    df["type_transaction"] = "vente"   # source = ventes historiques
    df["statut"] = "Vendu"
    return df


def lire_notaires() -> pd.DataFrame:
    """CSV ',' — statuts variables."""
    df = pd.read_csv(C.F_NOTAIRE, sep=",", encoding="utf-8")
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        "id_acte": "id", "date_acte": "date", "region": "region", "ville": "commune",
        "type_bien": "categorie", "montant_fcfa": "prix", "superficie": "surface",
        "nb_chambres": "chambres", "statut": "statut",
    })
    df["source"] = "notaires"
    df["type_transaction"] = "vente"
    df["sdb"] = None
    return df


def lire_particuliers() -> pd.DataFrame:
    """JSON imbriqué à aplatir."""
    with open(C.F_PARTICULIER, encoding="utf-8") as f:
        data = json.load(f)
    rows = []
    for item in data:
        a = item["annonce"]
        rows.append({
            "id": a.get("id"),
            "date": a.get("date"),
            "region": a.get("localisation", {}).get("region"),
            "commune": a.get("localisation", {}).get("ville"),
            "categorie": a.get("details", {}).get("type"),
            "type_transaction": a.get("details", {}).get("transaction"),
            "prix": a.get("details", {}).get("prix"),
            "surface": a.get("details", {}).get("surface"),
            "chambres": a.get("details", {}).get("chambres"),
            "sdb": a.get("details", {}).get("sdb"),
            "statut": a.get("statut"),
            "source": "particuliers",
        })
    return pd.DataFrame(rows)


def lire_plateforme() -> pd.DataFrame:
    """CSV ';' avec header dupliqué en cours de fichier."""
    df = pd.read_csv(C.F_PLATEFORME, sep=";", encoding="utf-8", dtype=str)
    # ⚠️ Filtre du header dupliqué
    df = df[df["ref_plateforme"] != "ref_plateforme"].copy()
    df = df.rename(columns={
        "ref_plateforme": "id", "date_mise_en_ligne": "date",
        "type_transaction": "type_transaction", "categorie": "categorie",
        "region": "region", "commune": "commune", "prix": "prix",
        "surface": "surface", "pieces": "chambres", "sdb": "sdb",
        "statut": "statut",
    })
    df["source"] = "plateforme"
    # Colonnes mono-source exclues AVANT concaténation (fuite type 4)
    df = df.drop(columns=[c for c in ["quartier", "devise", "description", "date_expiration"] if c in df.columns])
    return df


def lire_toutes() -> dict[str, pd.DataFrame]:
    """Retourne le résultat commun du module 1, sans relire les sources."""
    return {
        "module01": lire_donnees_module01(),
    }


def aligner(df: pd.DataFrame) -> pd.DataFrame:
    """Garde uniquement les colonnes du schéma cible (ajoute les manquantes en NaN)."""
    for col in C.SCHEMA_CIBLE:
        if col not in df.columns:
            df[col] = None
    return df[C.SCHEMA_CIBLE].copy()