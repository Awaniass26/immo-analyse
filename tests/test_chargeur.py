"""Tests du chargement : volumes, colonnes communes, provenance."""

import pytest

from src.loaders import chargeur

VOLUMES_ATTENDUS = {
    "plateforme": 875,
    "agence": 640,
    "particuliers": 731,
    "notaires": 410,
    "historique": 528,
}

FONCTIONS = {
    "plateforme": chargeur.charger_plateforme,
    "agence": chargeur.charger_agence,
    "particuliers": chargeur.charger_particuliers,
    "notaires": chargeur.charger_notaires,
    "historique": chargeur.charger_historique,
}


@pytest.mark.parametrize("nom", list(FONCTIONS))
def test_volume_de_chaque_source(nom):
    assert len(FONCTIONS[nom]()) == VOLUMES_ATTENDUS[nom]


@pytest.mark.parametrize("nom", list(FONCTIONS))
def test_colonnes_communes_et_provenance(nom):
    tableau = FONCTIONS[nom]()
    assert list(tableau.columns) == chargeur.COLONNES_COMMUNES
    assert (tableau["source"] == nom).all()


def test_accents_historique_bien_lus():
    tableau = chargeur.charger_historique()
    assert "Thiès" in set(tableau["region"].dropna())


def test_total_apres_empilement():
    total = len(chargeur.charger_toutes_les_sources())
    assert total == sum(VOLUMES_ATTENDUS.values())
