"""Conversion des prix écrits en texte vers des nombres entiers (FCFA).

Ici on CONVERTIT seulement. On ne juge pas si le prix est plausible :
un prix négatif ou nul sera refusé plus tard, par les règles de validation.
"""

import re

import pandas as pd

UN_MILLION = 1_000_000


def convertir_prix(texte):
    """Convertit un prix texte en entier.

    Renvoie un tuple (valeur, etat) :
      - "ok"       : le texte était déjà un nombre propre
      - "corrige"  : converti après une correction fiable
      - "manquant" : pas de valeur du tout
      - "erreur"   : impossible à convertir (valeur = None)
    """
    if texte is None or pd.isna(texte):
        return None, "manquant"

    texte = str(texte).strip().lower()
    if texte == "":
        return None, "manquant"

    # Cas 1 : déjà un nombre ("83825000", "83825000.0", "-5000")
    if re.fullmatch(r"-?\d+(\.\d+)?", texte):
        return int(round(float(texte))), "ok"

    # Cas 2 : "57.62 millions" -> 57 620 000
    morceaux = re.fullmatch(r"(\d+(?:\.\d+)?)\s*millions?", texte)
    if morceaux:
        return int(round(float(morceaux.group(1)) * UN_MILLION)), "corrige"

    # Cas 3 : "83 825 000", "65575000 FCFA", "1,250,000"
    nettoye = texte.replace("fcfa", "")
    for caractere in [" ", "\u00a0", "\u202f"]:   # espaces normaux et insécables
        nettoye = nettoye.replace(caractere, "")
    if re.fullmatch(r"\d{1,3}(,\d{3})+", nettoye):  # virgule = milliers
        nettoye = nettoye.replace(",", "")
    if re.fullmatch(r"\d+", nettoye):
        return int(nettoye), "corrige"

    # Cas 4 : "à négocier", "quatre-vingt"... on ne devine pas
    return None, "erreur"
