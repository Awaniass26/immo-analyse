"""Conversion des surfaces écrites en texte vers des nombres (m²)."""

import re

import pandas as pd


def convertir_surface(texte):
    """Renvoie (valeur, etat) avec etat : ok, corrige, ambigu, manquant, erreur."""
    if texte is None or pd.isna(texte):
        return None, "manquant"

    texte = str(texte).strip().lower()
    if texte == "":
        return None, "manquant"

    # Cas 1 : déjà un nombre ("173.3", "-30")
    if re.fullmatch(r"-?\d+(\.\d+)?", texte):
        return float(texte), "ok"

    # Cas 2 : virgule suivie d'un ou deux chiffres -> décimale ("102,6")
    if re.fullmatch(r"-?\d+,\d{1,2}", texte):
        return float(texte.replace(",", ".")), "corrige"

    # Cas 3 : virgule suivie de trois chiffres -> ambigu ("1,250")
    if re.fullmatch(r"-?\d+,\d{3}", texte):
        return None, "ambigu"

    # Cas 4 : tout le reste ("quatre-vingt") -> on ne devine pas
    return None, "erreur"