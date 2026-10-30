"""Tests de la conversion des prix : cas conformes, invalides et limites."""

import pytest

from src.processing.prix import convertir_prix


@pytest.mark.parametrize("texte, attendu", [
    ("83825000", (83825000, "ok")),
    ("83825000.0", (83825000, "ok")),
    ("83 825 000", (83825000, "corrige")),
    ("65575000 FCFA", (65575000, "corrige")),
    ("57.62 millions", (57620000, "corrige")),
    ("23.2 millions", (23200000, "corrige")),
    ("1,250,000", (1250000, "corrige")),
])
def test_prix_convertibles(texte, attendu):
    assert convertir_prix(texte) == attendu


@pytest.mark.parametrize("texte", ["à négocier", "quatre-vingt", "12abc"])
def test_prix_inconvertibles(texte):
    assert convertir_prix(texte) == (None, "erreur")


@pytest.mark.parametrize("texte", [None, "", "   "])
def test_prix_manquants(texte):
    assert convertir_prix(texte) == (None, "manquant")


def test_conversion_ne_juge_pas_la_validite():
    # un prix négatif est converti ; c'est la validation qui le refusera
    assert convertir_prix("-5000") == (-5000, "ok")
