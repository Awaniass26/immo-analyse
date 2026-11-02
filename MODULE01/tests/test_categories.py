"""Tests de la normalisation des catégories."""

from MODULE01.src.processing.categories import (
    charger_geographie, charger_types_de_bien, deduire_transaction,
    normaliser_nom, normaliser_periodicite, simplifier)


def test_simplifier_retire_accents_et_casse():
    assert simplifier("  THIÈS ") == "thies"


def test_ville_corrigee_et_inconnue():
    villes, _, _ = charger_geographie()
    assert normaliser_nom("THIÈS", villes) == ("Thiès", "corrige")
    assert normaliser_nom("Dakar", villes) == ("Dakar", "ok")
    assert normaliser_nom("Atlantide", villes) == ("Atlantide", "hors_referentiel")
    assert normaliser_nom(None, villes) == (None, "manquant")


def test_synonyme_type_bien():
    synonymes, _ = charger_types_de_bien()
    assert normaliser_nom("appart", synonymes) == ("Appartement", "corrige")
    assert normaliser_nom("LOCAL COMMERCIAL", synonymes) == ("Local commercial", "corrige")


def test_transaction_deduite():
    assert deduire_transaction("vente", "plateforme", None) == ("vente", "ok")
    assert deduire_transaction(None, "notaires", None) == ("vente", "deduit_source")
    assert deduire_transaction(None, "agence", "Loué") == ("location", "deduit_statut")
    assert deduire_transaction(None, "agence", "Disponible") == (None, "ambigu")


def test_periodicite():
    assert normaliser_periodicite("FCFA/mois", "location") == ("mensuel", "ok")
    assert normaliser_periodicite(None, "location") == (None, "inconnue")
    assert normaliser_periodicite("FCFA", "vente") == (None, "sans_objet")