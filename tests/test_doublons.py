"""Tests des doublons exacts et probables."""

import pandas as pd

from src.processing.doublons import marquer_doublons_exacts, marquer_doublons_probables


def faire_tableau(lignes):
    base = {"transaction_ref": "vente", "type_bien_ref": "Maison",
            "region_ref": "Dakar", "ville_ref": "Dakar", "date_iso": "2024-01-01",
            "prix_nombre": 50_000_000, "surface_nombre": 100.0,
            "chambres_nombre": 3, "sdb_nombre": 2, "source": "agence"}
    return pd.DataFrame([{**base, **ligne} for ligne in lignes])


def test_doublon_exact():
    tableau = faire_tableau([{}, {}, {"prix_nombre": 51_000_000}])
    resultat = marquer_doublons_exacts(tableau)
    assert resultat["doublon_exact"].tolist() == [False, True, False]


def test_doublon_probable_entre_deux_sources():
    tableau = faire_tableau([
        {"source": "agence"},
        {"source": "plateforme", "prix_nombre": 50_500_000, "surface_nombre": 101.0},
    ])
    assert marquer_doublons_probables(tableau)["doublon_probable"].all()


def test_pas_de_doublon_si_prix_tres_different():
    tableau = faire_tableau([
        {"source": "agence"},
        {"source": "plateforme", "prix_nombre": 90_000_000},
    ])
    assert not marquer_doublons_probables(tableau)["doublon_probable"].any()