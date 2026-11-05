"""Tests des comparaisons et des figures de prix du module 1."""

import pandas as pd

from MODULE01.src.analysis.visualisations import (
    _resumer_distributions,
    ecrire_visualisations_prix,
)


def faire_donnees(prix_vente, prix_location):
    lignes = [
        {
            "transaction_ref": "vente",
            "periodicite_ref": None,
            "prix_nombre": prix_vente,
            "surface_nombre": 100.0,
            "type_bien_ref": "Maison",
            "ville_ref": "Dakar",
        },
        {
            "transaction_ref": "location",
            "periodicite_ref": "mensuel",
            "prix_nombre": prix_location,
            "surface_nombre": 100.0,
            "type_bien_ref": "Maison",
            "ville_ref": "Dakar",
        },
        {
            "transaction_ref": "location",
            "periodicite_ref": None,
            "prix_nombre": prix_location * 2,
            "surface_nombre": 100.0,
            "type_bien_ref": "Maison",
            "ville_ref": "Dakar",
        },
    ]
    return pd.DataFrame(lignes)


def test_resume_separe_ventes_et_loyers_mensuels():
    donnees = faire_donnees(50_000_000, 250_000)
    resume = _resumer_distributions([("Avant validation", donnees)])

    ventes = resume.loc[resume["transaction"] == "vente"].iloc[0]
    loyers = resume.loc[resume["transaction"] == "location"].iloc[0]

    assert ventes["nombre"] == 1
    assert ventes["mediane_fcfa"] == 50_000_000
    assert loyers["nombre"] == 1
    assert loyers["mediane_fcfa"] == 250_000


def test_ecrire_visualisations_cree_rapports_et_figures(tmp_path):
    avant_validation = faire_donnees(50_000_000, 250_000)
    avant_doublons = faire_donnees(50_000_000, 250_000)
    retenues = faire_donnees(50_000_000, 250_000)
    brut = pd.DataFrame({
        "source": ["test"] * 3,
        "prix": ["50000000", "250000", "500000"],
        "surface": ["100", "100", "100"],
    })

    ecrire_visualisations_prix(
        brut,
        avant_validation,
        avant_doublons,
        retenues,
        tmp_path,
    )

    assert (tmp_path / "analyse_prix.md").is_file()
    assert (tmp_path / "comparaison_distributions_prix.csv").is_file()
    assert (tmp_path / "qualite_valeurs_brutes.csv").is_file()
    assert (tmp_path / "sensibilite_valeurs_extremes.csv").is_file()
    figures = tmp_path / "figures"
    assert len(list(figures.glob("*.png"))) == 5
