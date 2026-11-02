"""Détection des doublons exacts, des doublons probables et des conflits d'id."""

import pandas as pd

from MODULE01.src import config

COLONNES_METIER = [
    "transaction_ref", "type_bien_ref", "region_ref", "ville_ref", "date_iso",
    "prix_nombre", "surface_nombre", "chambres_nombre", "sdb_nombre",
]


def marquer_doublons_exacts(donnees):
    """Même contenu métier sur toutes les colonnes : on garde la 1re, on écarte les autres."""
    donnees = donnees.copy()
    donnees["doublon_exact"] = donnees.duplicated(subset=COLONNES_METIER, keep="first")
    return donnees


def marquer_conflits_id(donnees):
    """Même (source, id) mais contenu différent : l'identifiant n'est pas fiable."""
    donnees = donnees.copy()
    sans_exacts = donnees[~donnees["doublon_exact"]]
    meme_id = sans_exacts.duplicated(subset=["source", "id_local"], keep=False)
    donnees["conflit_id"] = False
    donnees.loc[meme_id[meme_id].index, "conflit_id"] = True
    return donnees


def _proche(a, b, tolerance):
    return abs(a - b) <= tolerance * max(abs(a), abs(b))


def _score_similarite(x, y):
    """Part des critères évaluables qui se ressemblent."""
    surface = _proche(x["surface_nombre"], y["surface_nombre"], config.TOLERANCE_SURFACE)
    prix = _proche(x["prix_nombre"], y["prix_nombre"], config.TOLERANCE_PRIX)
    ecart = abs((pd.Timestamp(x["date_iso"]) - pd.Timestamp(y["date_iso"])).days)
    date_proche = ecart <= config.TOLERANCE_DATE_JOURS
    criteres = [surface, prix, date_proche]
    # Les chambres ne comptent que si les DEUX lignes les connaissent
    if pd.notna(x["chambres_nombre"]) and pd.notna(y["chambres_nombre"]):
        criteres.append(x["chambres_nombre"] == y["chambres_nombre"])
    return surface, prix, sum(criteres) / len(criteres)


def marquer_doublons_probables(donnees):
    """Compare les lignes ayant même ville + type + transaction, sources différentes.

    On ne fusionne rien : on pose seulement un numéro de groupe.
    """
    donnees = donnees.copy()
    donnees["groupe_doublon"] = pd.Series(pd.NA, index=donnees.index, dtype="string")
    groupes = {}

    for _, bloc in donnees.groupby(["ville_ref", "type_bien_ref", "transaction_ref"]):
        indices = list(bloc.index)
        for position, i in enumerate(indices):
            for j in indices[position + 1:]:
                if donnees.at[i, "source"] == donnees.at[j, "source"]:
                    continue
                surface, prix, score = _score_similarite(donnees.loc[i], donnees.loc[j])
                if surface and prix and score >= config.SEUIL_DOUBLON_PROBABLE:
                    groupe = groupes.get(i, i)
                    groupes[i] = groupe
                    groupes[j] = groupe

    for indice, groupe in groupes.items():
        donnees.at[indice, "groupe_doublon"] = f"G{groupe}"
    donnees["doublon_probable"] = donnees["groupe_doublon"].notna()
    return donnees