"""Statistiques descriptives sur les données retenues (étape 5)."""

import numpy as np


def ajouter_prix_m2(retenues):
    """Prix au m² pour les VENTES uniquement (un loyer n'est pas un prix de vente)."""
    ventes = retenues[retenues["transaction_ref"] == "vente"].copy()
    ventes["prix_m2"] = ventes["prix_nombre"].astype(float) / ventes["surface_nombre"].astype(float)
    return ventes


def resume_par(ventes, colonne):
    """Nombre, moyenne, médiane et quartiles du prix au m², groupés par colonne."""
    def q1(serie):
        return np.percentile(serie, 25)

    def q3(serie):
        return np.percentile(serie, 75)

    resume = ventes.groupby(colonne)["prix_m2"].agg(
        nombre="count", moyenne="mean", mediane="median", q1=q1, q3=q3)
    return resume.round(0).sort_values("mediane", ascending=False)