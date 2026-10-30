"""Tests de la conversion des surfaces."""

import pytest

from src.processing.surface import convertir_surface


@pytest.mark.parametrize("texte, attendu", [
    ("173.3", (173.3, "ok")),
    ("102,6", (102.6, "corrige")),
    ("1354,0", (1354.0, "corrige")),
    ("1,250", (None, "ambigu")),
    ("-30", (-30.0, "ok")),
])
def test_surfaces_convertibles(texte, attendu):
    assert convertir_surface(texte) == attendu


def test_surface_inconvertible():
    assert convertir_surface("quatre-vingt") == (None, "erreur")


def test_surface_manquante():
    assert convertir_surface(None) == (None, "manquant")