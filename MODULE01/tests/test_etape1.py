"""Tests des fonctions de l'étape 1."""

from MODULE01.src.etape1_bases import (
    BIENS, bien_le_plus_cher, compter_par_type, convertir_en_entier,
    filtrer_par_ville, prix_moyen, verifier_bien, villes_uniques)


def test_filtrer_et_villes():
    assert len(filtrer_par_ville(BIENS, "Dakar")) == 2
    assert filtrer_par_ville(BIENS, "Atlantide") == []
    assert villes_uniques(BIENS) == {"Dakar", "Thiès", "Saint-Louis"}


def test_compter_par_type():
    assert compter_par_type(BIENS)["Maison"] == 2


def test_prix_moyen_et_liste_vide():
    assert prix_moyen(filtrer_par_ville(BIENS, "Thiès")) == 48_500_000
    assert prix_moyen([]) is None


def test_bien_le_plus_cher():
    assert bien_le_plus_cher(BIENS)["type"] == "Villa"
    assert bien_le_plus_cher([]) is None


def test_convertir_en_entier():
    assert convertir_en_entier("250") == 250
    assert convertir_en_entier("quatre-vingt") is None
    assert convertir_en_entier(None) is None


def test_verifier_bien():
    assert verifier_bien(BIENS[0]) == (True, [])
    valide, problemes = verifier_bien({"ville": "", "prix": 0, "surface": 10})
    assert not valide and len(problemes) == 2