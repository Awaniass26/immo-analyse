import joblib
import numpy as np
import pandas as pd
import pytest

from MODULE02.src import clean, io_sources
from MODULE02.src.pipeline import construire_pipeline, preparer_features
from MODULE02.src.run_pipeline import separer_ensembles


def test_loader_adapts_module1_schema(tmp_path, monkeypatch):
    source = tmp_path / "donnees_propres.csv"
    pd.DataFrame({
        "transaction": ["vente"],
        "type_bien": ["Maison"],
        "region": ["Dakar"],
        "date": ["2024-01-02"],
        "prix_fcfa": [125_000_000],
        "surface_m2": [125.0],
        "ville": ["Dakar"],
    }).to_csv(source, index=False)
    monkeypatch.setattr(io_sources.C, "F_DONNEES_MODULE01", source)

    df = io_sources.lire_donnees_module01()

    assert df.loc[0, "type_transaction"] == "vente"
    assert df.loc[0, "categorie"] == "Maison"
    assert df.loc[0, "prix"] == 125_000_000
    assert df.loc[0, "surface"] == 125.0
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_features_exclude_price_and_transform_surface():
    df = pd.DataFrame({
        "type_transaction": ["vente"],
        "categorie": ["Maison"],
        "region": ["Dakar"],
        "surface": [99.0],
        "prix": [125_000_000],
    })

    features = preparer_features(df)

    assert "prix" not in features
    assert features.loc[0, "surface_log"] == pytest.approx(np.log1p(99))


def test_random_split_is_70_15_15():
    index = pd.RangeIndex(100)
    X = pd.DataFrame({"surface_log": range(100)}, index=index)
    y = pd.Series(range(100), index=index)
    dates = pd.Series(pd.date_range("2020-01-01", periods=100), index=index)

    ensembles = separer_ensembles(X, y, dates, "aleatoire")

    assert {nom: len(partie[0]) for nom, partie in ensembles.items()} == {
        "train": 70, "validation": 15, "test": 15,
    }


def test_temporal_split_keeps_dates_in_order():
    index = pd.RangeIndex(100)
    dates = pd.Series(pd.date_range("2020-01-01", periods=100), index=index)
    X = pd.DataFrame({"surface_log": range(100)}, index=index)
    y = pd.Series(range(100), index=index)

    ensembles = separer_ensembles(X, y, dates, "temporelle")

    last_train = dates.loc[ensembles["train"][0].index].max()
    first_validation = dates.loc[ensembles["validation"][0].index].min()
    last_validation = dates.loc[ensembles["validation"][0].index].max()
    first_test = dates.loc[ensembles["test"][0].index].min()
    assert last_train < first_validation
    assert last_validation < first_test


def test_warning_does_not_remove_rows():
    df = pd.DataFrame({
        "surface": [3.0, 100.0],
        "prix": [100_000_000, 100_000_000],
        "geo_ok": [True, True],
    })

    toutes, averties = clean.marquer_avertissements(df)

    assert len(toutes) == 2
    assert len(averties) == 1
    assert toutes.loc[0, "avertissements"] == "surface_tres_petite"


def test_preparation_pipeline_can_be_serialized(tmp_path):
    features = pd.DataFrame({
        "type_transaction": ["vente", "location", "vente", "location"],
        "categorie": ["Maison", "Appartement", "Maison", "Appartement"],
        "region": ["Dakar", "Thiès", "Dakar", "Thiès"],
        "surface_log": [3.0, 4.0, 5.0, 6.0],
    })
    pipeline = construire_pipeline().fit(features)
    attendu = pipeline.transform(features)
    chemin = tmp_path / "pipeline.joblib"

    joblib.dump(pipeline, chemin)
    recharge = joblib.load(chemin)

    np.testing.assert_allclose(recharge.transform(features), attendu)
