# src/pipeline.py
"""Comp 5 + 9 : pipeline sklearn sérialisable."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer

from . import config as C


# ⚠️ `statut`, `source`, `commune` EXCLUS (fuites types 2 et 4)
FEATURES_CAT = ["type_transaction", "categorie", "region"]
FEATURES_NUM = ["surface_log"]


def preparer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute surface_log, garde uniquement les features retenues."""
    df = df.copy()
    if (df["surface"].dropna() < 0).any():
        raise ValueError("La surface doit être positive ou manquante.")
    df["surface_log"] = np.log1p(df["surface"])
    cols = FEATURES_CAT + FEATURES_NUM
    return df[cols].copy()


def construire_pipeline() -> Pipeline:
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    num_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    pre = ColumnTransformer([
        ("cat", cat_pipe, FEATURES_CAT),
        ("num", num_pipe, FEATURES_NUM),
    ])
    return Pipeline([("preprocessor", pre)])