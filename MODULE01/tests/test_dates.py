"""Tests de la conversion des dates."""

import pytest

from MODULE01.src.processing.dates import convertir_date


@pytest.mark.parametrize("texte, attendu", [
    ("2024-03-01", ("2024-03-01", "ok")),
    ("01/03/2024", ("2024-03-01", "corrige")),     # JJ/MM/AAAA
    ("29/02/2024", ("2024-02-29", "corrige")),     # année bissextile : limite
])
def test_dates_valides(texte, attendu):
    assert convertir_date(texte) == attendu


@pytest.mark.parametrize("texte", ["32/13/2024", "hier", "29/02/2023", "2024-13-01"])
def test_dates_impossibles(texte):
    assert convertir_date(texte) == (None, "erreur")


def test_date_manquante():
    assert convertir_date(None) == (None, "manquant")