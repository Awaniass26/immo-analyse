"""Tests des règles de validation sur des lignes fabriquées à la main."""

import pandas as pd

from MODULE01.src.validation import regles


def faire_ligne(**champs):
    """Une ligne conforme par défaut ; on change seulement ce qu'on teste."""
    ligne = {
        "source": "plateforme", "id_local": "X1", "statut": "En vente",
        "transaction_ref": "vente", "prix_nombre": 50_000_000,
        "surface_nombre": 100.0, "date_iso": "2024-01-01",
        "type_bien_etat": "ok", "type_bien_ref": "Maison",
        "periodicite_ref": None, "chambres_nombre": 3, "sdb_nombre": 2,
    }
    ligne.update(champs)
    return pd.Series(ligne)


def test_prix_valide_cas_conforme_invalide_limite():
    assert regles.prix_valide(faire_ligne()) is True
    assert not regles.prix_valide(faire_ligne(prix_nombre=pd.NA))
    assert not regles.prix_valide(faire_ligne(prix_nombre=0))      # limite
    assert not regles.prix_valide(faire_ligne(prix_nombre=-5))


def test_surface_atypique_limites():
    assert regles.surface_non_atypique(faire_ligne(surface_nombre=5.0))     # limite basse OK
    assert not regles.surface_non_atypique(faire_ligne(surface_nombre=4.9))
    assert not regles.surface_non_atypique(faire_ligne(surface_nombre=2001))


def test_date_future_refusee_si_vente_conclue():
    assert not regles.date_pas_future_si_conclue(
        faire_ligne(statut="Vendu", date_iso="2999-01-01"))
    # annonce encore en vente : la règle ne s'applique pas
    assert regles.date_pas_future_si_conclue(
        faire_ligne(statut="En vente", date_iso="2999-01-01")) is None


def test_loyer_evalue_seulement_si_mensuel():
    location = faire_ligne(transaction_ref="location", prix_nombre=20_000,
                           periodicite_ref="mensuel")
    assert not regles.loyer_non_atypique(location)           # < 25 000
    sans_periode = faire_ligne(transaction_ref="location", periodicite_ref=None)
    assert regles.loyer_non_atypique(sans_periode) is None   # non évaluable


def test_chambres_et_salles_de_bain():
    assert not regles.chambres_non_atypiques(
        faire_ligne(type_bien_ref="Studio", chambres_nombre=11))
    assert not regles.sdb_non_atypiques(faire_ligne(chambres_nombre=1, sdb_nombre=4))