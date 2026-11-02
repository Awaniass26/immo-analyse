# src/clean.py
"""Helpers d'exploration du nettoyage ; le pipeline officiel nettoie au module 1."""
import re
import unicodedata
import numpy as np
import pandas as pd
from . import config as C


# ---------- Mojibake + casse ----------
MOJIBAKE_FIX = {
    "Thiï¿½s": "Thiès", "Linguï¿½re": "Linguère", "Kï¿½dougou": "Kédougou",
    "Sï¿½dhiou": "Sédhiou", "Vï¿½lingara": "Vélingara", "Mï¿½dina": "Médina",
    "Kï¿½bï¿½mer": "Kébémer", "Guinguinï¿½o": "Guinguinéo",
    "Mbackï¿½": "Mbacké", "Salï¿½mata": "Salémata",
}

def corriger_mojibake(s: str) -> str:
    if not isinstance(s, str):
        return s
    for bad, good in MOJIBAKE_FIX.items():
        s = s.replace(bad, good)
    return s


def normaliser_casse(s):
    """Retire accents pour comparaison + title case propre."""
    if not isinstance(s, str):
        return s
    return s.strip().title()


# ---------- Prix ----------
def parser_prix(v):
    """Convertit '26 620 000', '147.52 millions', '65575000 FCFA', 38448000 → float."""
    if pd.isna(v):
        return np.nan
    if isinstance(v, (int, float, np.integer, np.floating)):
        return float(v)
    s = str(v).strip().lower()
    if s in ("", "none fcfa", "n/a", "na", "à négocier", "a negocier"):
        return np.nan
    s = s.replace("fcfa", "").replace("f cfa", "").strip()
    # "millions"
    if "million" in s:
        m = re.search(r"([\d\.,\s]+)", s)
        if m:
            try:
                val = float(m.group(1).replace(" ", "").replace(",", "."))
                return val * 1_000_000
            except ValueError:
                return np.nan
    # Retirer espaces et virgules de milliers
    s = s.replace(" ", "").replace("\u202f", "").replace(",", "")
    try:
        return float(s)
    except ValueError:
        return np.nan


# ---------- Surface ----------
MOTS_NOMBRES = {"quatre-vingt": 80, "quatre vingt": 80, "vingt": 20, "trente": 30,
                "quarante": 40, "cinquante": 50, "soixante": 60, "cent": 100}

def parser_surface(v):
    if pd.isna(v):
        return np.nan
    if isinstance(v, (int, float, np.integer, np.floating)):
        return float(v)
    s = str(v).strip().lower()
    if s in ("", "n/a", "none", "null"):
        return np.nan
    if s in MOTS_NOMBRES:
        return float(MOTS_NOMBRES[s])
    s = s.replace(",", ".").replace(" ", "")
    try:
        return float(s)
    except ValueError:
        return np.nan


# ---------- Date ----------
def parser_date(v):
    """Retourne Timestamp ou NaT. Gère ISO et JJ/MM/AAAA + dates impossibles."""
    if pd.isna(v):
        return pd.NaT
    s = str(v).strip()
    # Détecte 32/13/2024 → impossible
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            dt = pd.to_datetime(s, format=fmt, errors="raise")
            return dt
        except (ValueError, TypeError):
            continue
    return pd.NaT


# ---------- Catégories ----------
SYNONYMES_CAT = {
    "appart": "Appartement", "appartement": "Appartement", "appt": "Appartement",
    "studio": "Studio",
    "chambre": "Chambre", "chambre simple": "Chambre",
    "villa": "Villa",
    "maison": "Maison",
    "terrain": "Terrain", "terrains": "Terrain",
    "local": "Local commercial", "local commercial": "Local commercial",
    "bureau": "Local commercial", "magasin": "Local commercial",
}

def normaliser_categorie(v):
    if not isinstance(v, str):
        return v
    s = v.strip().lower()
    return SYNONYMES_CAT.get(s, v.strip().title())


STATUTS_OK = {"vendu", "en vente", "disponible", "loué", "sous offre", "retiré", "à confirmer"}
STATUT_ALIAS = {
    "vente conclue": "Vendu", "acte signé": "Vendu", "vendu": "Vendu",
    "en vente": "En vente", "disponible": "Disponible", "loué": "Loué",
    "sous offre": "Sous offre", "retiré": "Retiré", "à confirmer": "À confirmer",
}

def normaliser_statut(v):
    if not isinstance(v, str):
        return v
    return STATUT_ALIAS.get(v.strip().lower(), v.strip().title())


# ---------- Vérif cohérence géo ----------
def verifier_region_ville(region, ville, ref_geo: pd.DataFrame) -> bool:
    if pd.isna(region) or pd.isna(ville):
        return False
    mask = (ref_geo["region"].str.lower() == str(region).lower()) & \
           (ref_geo["ville"].str.lower() == str(ville).lower())
    return mask.any()


# ---------- Application pipeline de nettoyage ----------
def normaliser_df(df: pd.DataFrame, ref_geo: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["region"]  = df["region"].apply(corriger_mojibake).apply(normaliser_casse)
    df["commune"] = df["commune"].apply(corriger_mojibake).apply(normaliser_casse)
    df["categorie"]       = df["categorie"].apply(normaliser_categorie)
    df["statut"]          = df["statut"].apply(normaliser_statut)
    df["prix"]            = df["prix"].apply(parser_prix)
    df["surface"]         = df["surface"].apply(parser_surface)
    df["date"]            = df["date"].apply(parser_date)
    df["chambres"]        = pd.to_numeric(df["chambres"], errors="coerce")
    df["sdb"]             = pd.to_numeric(df["sdb"], errors="coerce")
    df["type_transaction"] = df["type_transaction"].astype(str).str.lower().str.strip()
    # Cohérence géo
    df["geo_ok"] = [
        verifier_region_ville(r, v, ref_geo) for r, v in zip(df["region"], df["commune"])
    ]
    return df


# ---------- Quarantaine ----------
def appliquer_quarantaine(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Sépare (propre, quarantaine) selon les 5 règles bloquantes."""
    raisons = []
    for _, row in df.iterrows():
        r = []
        if pd.isna(row["id"]) or str(row["id"]).strip() == "":
            r.append("id_absent")
        if pd.isna(row["prix"]) or row["prix"] <= 0:
            r.append("prix_invalide")
        if pd.isna(row["surface"]) or row["surface"] <= 0:
            r.append("surface_invalide")
        if pd.isna(row["date"]):
            r.append("date_invalide")
        # Date future + vendu
        if not pd.isna(row["date"]) and row["date"] > pd.Timestamp.today():
            if str(row["statut"]).lower() == "vendu":
                r.append("date_future_vendu")
        raisons.append(";".join(r))

    df = df.copy()
    df["_raison"] = raisons
    df_quar = df[df["_raison"] != ""].copy()
    df_propre = df[df["_raison"] == ""].drop(columns=["_raison"]).copy()
    return df_propre, df_quar


# ---------- Avertissements ----------
def marquer_avertissements(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retourne toutes les lignes et, séparément, celles qui portent un avertissement."""
    av = []
    for _, row in df.iterrows():
        r = []
        if row["surface"] < C.SURF_MIN_FOURCHETTE:
            r.append("surface_tres_petite")
        if row["surface"] > C.SURF_MAX_FOURCHETTE:
            r.append("surface_tres_grande")
        if row["prix"] < C.PRIX_MIN_FOURCHETTE:
            r.append("prix_tres_bas")
        if row["prix"] > C.PRIX_MAX_FOURCHETTE:
            r.append("prix_tres_haut")
        if not row["geo_ok"]:
            r.append("region_ville_incoherentes")
        av.append(";".join(r))

    df = df.copy()
    df["_avert"] = av
    df["avertissements"] = df["_avert"]
    df_av = df[df["_avert"] != ""].copy()
    df_toutes = df.drop(columns=["_avert", "geo_ok"]).copy()
    return df_toutes, df_av


# ---------- Doublons ----------
def supprimer_doublons_exacts(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in df.columns if c not in ("source",)]  # ignorer source
    before = len(df)
    df2 = df.drop_duplicates(subset=[c for c in cols if c != "id"], keep="first")
    print(f"[doublons] {before - len(df2)} doublons exacts supprimés")
    return df2


def dedupliquer_ids(df: pd.DataFrame) -> pd.DataFrame:
    """Au sein d'une source, si plusieurs lignes même id → on garde 1 (le premier)."""
    before = len(df)
    df2 = df.drop_duplicates(subset=["source", "id"], keep="first")
    print(f"[doublons ID] {before - len(df2)} doublons d'ID supprimés")
    return df2