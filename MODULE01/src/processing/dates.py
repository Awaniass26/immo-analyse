"""Conversion des dates texte vers le format ISO (AAAA-MM-JJ)."""

import re
from datetime import date

import pandas as pd


def convertir_date(texte):
    """Renvoie (date_iso, etat) avec etat : ok, corrige, manquant, erreur.

    Convention documentée : une date avec des "/" est lue JJ/MM/AAAA
    (les sources sont francophones).
    """
    if texte is None or pd.isna(texte) or str(texte).strip() == "":
        return None, "manquant"

    texte = str(texte).strip()

    iso = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", texte)
    francais = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", texte)

    if iso:
        annee, mois, jour = (int(x) for x in iso.groups())
        etat = "ok"
    elif francais:
        jour, mois, annee = (int(x) for x in francais.groups())
        etat = "corrige"
    else:
        return None, "erreur"        # "hier", "quatre-vingt"...

    try:
        return date(annee, mois, jour).isoformat(), etat
    except ValueError:               # "32/13/2024" : date impossible
        return None, "erreur"