"""EDA et préparation ML sur les données validées par le module 1."""
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from . import config as C
from . import io_sources, stats_eda, viz_eda
from .pipeline import construire_pipeline, preparer_features


def separer_ensembles(
    X: pd.DataFrame,
    y: pd.Series,
    dates: pd.Series,
    strategie: str,
) -> dict[str, tuple[pd.DataFrame, pd.Series]]:
    """Crée des ensembles 70/15/15 aléatoires ou chronologiques."""
    if strategie == "temporelle":
        dates = pd.to_datetime(dates.loc[X.index], errors="raise")
        if dates.isna().any():
            raise ValueError("Le split temporel exige une date valide pour chaque ligne.")
        jours = dates.sort_values(kind="mergesort").drop_duplicates().to_numpy()
        if len(jours) < 3:
            raise ValueError("Un split temporel exige au moins trois dates distinctes.")

        borne_train = max(1, min(len(jours) - 2, round(len(jours) * 0.70)))
        borne_validation = max(
            borne_train + 1,
            min(len(jours) - 1, round(len(jours) * 0.85)),
        )
        fin_train = jours[borne_train - 1]
        fin_validation = jours[borne_validation - 1]
        train_mask = dates <= fin_train
        validation_mask = (dates > fin_train) & (dates <= fin_validation)
        test_mask = dates > fin_validation
        indices = {
            "train": dates.index[train_mask],
            "validation": dates.index[validation_mask],
            "test": dates.index[test_mask],
        }
        return {
            nom: (X.loc[index], y.loc[index])
            for nom, index in indices.items()
        }

    if strategie != "aleatoire":
        raise ValueError(f"Stratégie de split inconnue : {strategie}")

    X_train, X_reste, y_train, y_reste = train_test_split(
        X, y, test_size=0.30, random_state=C.RANDOM_STATE,
    )
    X_validation, X_test, y_validation, y_test = train_test_split(
        X_reste, y_reste, test_size=0.50, random_state=C.RANDOM_STATE,
    )
    return {
        "train": (X_train, y_train),
        "validation": (X_validation, y_validation),
        "test": (X_test, y_test),
    }


def _exporter_ensemble(
    nom: str,
    X: pd.DataFrame,
    y: pd.Series,
    donnees: pd.DataFrame,
    pipeline,
) -> None:
    transforme = pipeline.transform(X)
    colonnes = pipeline.named_steps["preprocessor"].get_feature_names_out()
    sortie = pd.DataFrame(transforme, columns=colonnes, index=X.index)
    sortie.insert(0, "prix_log", y)
    for colonne in ("id_local", "source"):
        if colonne in donnees:
            sortie.insert(0, colonne, donnees.loc[X.index, colonne])
    sortie.to_csv(C.OUT_DIR / f"prepared_{nom}.csv", index=False)


def main() -> None:
    print("=" * 60)
    print("IMMOANALYSE — MODULE 2 : EDA ET PRÉPARATION")
    print("=" * 60)

    df = io_sources.lire_donnees_module01()
    if df.empty:
        raise ValueError("Le fichier propre du module 1 ne contient aucune ligne.")
    if df[["prix", "surface", "date"]].isna().any().any():
        raise ValueError(
            "Le fichier du module 1 contient un prix, une surface ou une date manquante."
        )
    if (df["prix"] <= 0).any():
        raise ValueError("Le fichier du module 1 contient un prix nul ou négatif.")

    print(f"Données validées par le module 1 : {len(df)} lignes")
    skew = stats_eda.comparer_prix_log(df)
    simpson = stats_eda.tester_simpson(df)
    mann_kendall = stats_eda.tester_mann_kendall(df)
    p_value = mann_kendall["p_value"]
    strategie = (
        "temporelle"
        if p_value is not None and p_value < 0.05
        else "aleatoire"
    )
    viz_eda.generer_toutes(df, C.FIG_DIR)

    rapport = {
        "nombre_lignes": len(df),
        "distribution_prix": skew.to_dict(orient="index"),
        "simpson": {
            "global_spearman": simpson["global_spearman"],
            "par_categorie": simpson["par_categorie"],
        },
        "mann_kendall": mann_kendall,
        "strategie_split": strategie,
        "graine_aleatoire": C.RANDOM_STATE,
    }
    with C.F_RAPPORT_EDA.open("w", encoding="utf-8") as fichier:
        json.dump(
            rapport,
            fichier,
            ensure_ascii=False,
            indent=2,
            default=lambda valeur: valeur.item(),
        )

    X = preparer_features(df)
    y = pd.Series(np.log(df["prix"]), index=df.index, name="prix_log")
    ensembles = separer_ensembles(X, y, df["date"], strategie)
    X_train, _ = ensembles["train"]
    pipeline = construire_pipeline()
    pipeline.fit(X_train)
    joblib.dump(pipeline, C.MODELS_DIR / "pipeline_preparation.joblib")

    for nom, (X_partie, y_partie) in ensembles.items():
        _exporter_ensemble(nom, X_partie, y_partie, df, pipeline)
        print(f"  {nom:10s}: {len(X_partie)} lignes préparées")

    print(f"Split : {strategie} (graine {C.RANDOM_STATE})")
    print(f"Pipeline sérialisé : {C.MODELS_DIR / 'pipeline_preparation.joblib'}")
    print(f"Figures : {C.FIG_DIR}")
    print(f"Rapport EDA : {C.F_RAPPORT_EDA}")
    print("Le préprocesseur est ajusté uniquement sur l'ensemble d'entraînement.")


if __name__ == "__main__":
    main()
