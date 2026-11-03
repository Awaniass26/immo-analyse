"""Nettoyage, EDA et préparation ML autonomes du module 2."""
import json
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from . import config as C
from . import clean, io_sources, stats_eda, viz_eda
from .pipeline import construire_pipeline, preparer_features


def _evaluer_candidates(
    donnees: pd.DataFrame,
    cible: pd.Series,
) -> pd.DataFrame:
    """Compare quelques candidates par CV sans consulter validation ni test."""
    candidats = {
        "categorie": (["categorie"], []),
        "region": (["categorie", "region"], []),
        "surface_log": (["categorie"], ["surface_log"]),
        "annee": (["categorie"], ["annee"]),
        "source": (["categorie", "source"], []),
        "prix_m2": (["categorie"], ["prix_m2"]),
    }
    resultats = []
    cv = KFold(n_splits=5, shuffle=True, random_state=C.RANDOM_STATE)

    for nom, (colonnes_cat, colonnes_num) in candidats.items():
        transformateurs = []
        if colonnes_cat:
            transformateurs.append((
                "cat",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("onehot", OneHotEncoder(
                        handle_unknown="ignore",
                        sparse_output=False,
                    )),
                ]),
                colonnes_cat,
            ))
        if colonnes_num:
            transformateurs.append((
                "num",
                SimpleImputer(strategy="median"),
                colonnes_num,
            ))
        estimateur = Pipeline([
            ("preprocessor", ColumnTransformer(transformateurs)),
            ("model", RandomForestRegressor(
                n_estimators=40,
                min_samples_leaf=3,
                random_state=C.RANDOM_STATE,
                n_jobs=-1,
            )),
        ])
        scores = cross_val_score(
            estimateur,
            donnees[colonnes_cat + colonnes_num],
            cible,
            scoring="r2",
            cv=cv,
            n_jobs=1,
        )
        resultats.append({
            "candidate": nom,
            "r2_moyen_cv": round(float(scores.mean()), 8),
            "ecart_type_cv": round(float(scores.std()), 8),
        })

    tableau = pd.DataFrame(resultats)
    baseline = tableau.loc[
        tableau["candidate"] == "categorie", "r2_moyen_cv"
    ].iloc[0]
    tableau["gain_vs_categorie"] = (
        tableau["r2_moyen_cv"] - baseline
    ).round(8)
    tableau["decision"] = "à réévaluer selon le cas d'usage"
    tableau.loc[
        tableau["candidate"].isin({"categorie", "surface_log"}),
        "decision",
    ] = "conserver pour le premier pipeline"
    tableau.loc[tableau["candidate"] == "source", "decision"] = (
        "exclure du pipeline final : identifiant de flux"
    )
    tableau.loc[tableau["candidate"] == "prix_m2", "decision"] = (
        "exclure : calculé à partir de la cible"
    )
    return tableau


def _verifier_splits(
    ensembles: dict[str, tuple[pd.DataFrame, pd.Series]],
    donnees: pd.DataFrame,
) -> dict:
    """Construit les effectifs et vérifie les identifiants des splits."""
    resume = {}
    identifiants = {}
    for nom, (X_partie, _) in ensembles.items():
        lignes = donnees.loc[X_partie.index]
        resume[nom] = {
            "nombre": len(lignes),
            "categories": lignes["categorie"].value_counts().to_dict(),
            "categories_pct": (
                lignes["categorie"].value_counts(normalize=True) * 100
            ).to_dict(),
            "sources": lignes["source"].value_counts().to_dict(),
            "sources_pct": (
                lignes["source"].value_counts(normalize=True) * 100
            ).to_dict(),
        }
        identifiants[nom] = set(
            lignes.loc[lignes["id_local"].notna()]
            .apply(
                lambda ligne: f"{ligne['source']}:{ligne['id_local']}",
                axis=1,
            )
        )

    noms = list(identifiants)
    intersections = {
        f"{noms[i]}_{noms[j]}": len(
            identifiants[noms[i]] & identifiants[noms[j]]
        )
        for i in range(len(noms))
        for j in range(i + 1, len(noms))
    }
    if any(intersections.values()):
        raise ValueError(
            "Des identifiants apparaissent dans plusieurs splits : "
            f"{intersections}"
        )
    return {"ensembles": resume, "identifiants_partages": intersections}


def _ecrire_rapport_eda(
    donnees: pd.DataFrame,
    brut: pd.DataFrame,
    skew: pd.DataFrame,
    simpson: dict,
    normalite_log_prix: dict,
) -> None:
    """Écrit les conclusions chiffrées associées aux six figures."""
    medianes = donnees.groupby("categorie")["prix"].median()
    ratio = medianes.max() / medianes.min()
    correlations = donnees[["prix", "surface", "chambres", "sdb"]].corr()
    redondances = [
        f"{col_a}/{col_b} ({correlations.loc[col_a, col_b]:.2f})"
        for position, col_a in enumerate(correlations.columns)
        for col_b in correlations.columns[position + 1:]
        if abs(correlations.loc[col_a, col_b]) > 0.8
    ]
    moyenne_categories = float(
        np.nanmean(list(simpson["par_categorie"].values()))
    )
    sources = donnees.groupby("source").agg(
        nombre=("prix", "size"),
        mediane_prix=("prix", "median"),
        mediane_surface=("surface", "median"),
    )
    p_value = normalite_log_prix["p_value"]
    normalite = (
        f"p={p_value:.3g}"
        if p_value is not None
        else "test non calculable"
    )
    lignes = [
        "# Résultats EDA et figures de restitution",
        "",
        "1. **V1 — Distribution de la cible.** "
        f"Le skew passe de {skew.loc['skew', 'prix']:.3f} à "
        f"{skew.loc['skew', 'log_prix']:.3f} après logarithme. "
        f"Shapiro-Wilk sur n={normalite_log_prix['n']} donne "
        f"{normalite}; la normalité n'est donc pas retenue.",
        "",
        "![V1 — Distribution de la cible](figures/01_distribution_prix.png)",
        "",
        "2. **V2 — Prix par catégorie.** "
        f"Le ratio des médianes de catégorie extrêmes est {ratio:.2f}. "
        "Les boîtes utilisent une échelle logarithmique.",
        "",
        "![V2 — Prix par catégorie](figures/02_prix_par_categorie.png)",
        "",
        "3. **V3 — Prix et surface.** "
        f"Spearman global = {simpson['global_spearman']:.3f}; "
        f"moyenne des corrélations par catégorie = {moyenne_categories:.3f}. "
        "Ces statistiques indiquent une hétérogénéité entre groupes, pas une "
        "preuve suffisante d'un paradoxe de Simpson strict.",
        "",
        "![V3 — Prix et surface par catégorie]("
        "figures/03_prix_surface_categories.png)",
        "",
        "4. **V4 — Corrélations numériques.** "
        + (
            "Paires avec |r| > 0,8 : " + ", ".join(redondances) + "."
            if redondances else "Aucune paire ne dépasse |r| = 0,8."
        ),
        "",
        "![V4 — Matrice de corrélation](figures/04_matrice_correlation.png)",
        "",
        "5. **V5 — Nettoyage.** "
        f"{len(brut)} lignes reçues, {len(donnees)} conservées et "
        f"{len(brut) - len(donnees)} mises en quarantaine. "
        f"{int(donnees['avertissements'].fillna('').ne('').sum())} lignes "
        "conservées portent au moins un avertissement.",
        "",
        "![V5 — Bilan du nettoyage](figures/05_preuve_nettoyage.png)",
        "",
        "6. **V6 — Comparaison des sources.** Les médianes et effectifs "
        "présentés dans les figures sont :",
        "",
        "![V6 — Comparaison des sources]("
        "figures/06_comparaison_sources.png)",
        "",
        sources.to_markdown(),
        "",
        "Les graphiques soutiennent l'exploration du corpus synthétique et ne "
        "permettent pas d'inférer des prix de marché réels.",
    ]
    (C.ROOT / "reports" / "rapport_eda.md").write_text(
        "\n".join(lignes) + "\n",
        encoding="utf-8",
    )


def separer_ensembles(
    X: pd.DataFrame,
    y: pd.Series,
    dates: pd.Series,
    strategie: str,
    stratification: Optional[pd.Series] = None,
) -> dict[str, tuple[pd.DataFrame, pd.Series]]:
    """Crée des ensembles 70/15/15 aléatoires ou chronologiques."""
    if strategie == "temporelle":
        dates = pd.to_datetime(dates.loc[X.index], errors="raise")
        if dates.isna().any():
            raise ValueError(
                "Le split temporel exige une date valide pour chaque ligne."
            )
        jours = (
            dates.sort_values(kind="mergesort")
            .drop_duplicates()
            .to_numpy()
        )
        if len(jours) < 3:
            raise ValueError(
                "Un split temporel exige au moins trois dates distinctes."
            )

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
        X,
        y,
        test_size=0.30,
        random_state=C.RANDOM_STATE,
        stratify=stratification,
    )
    stratification_reste = (
        stratification.loc[X_reste.index]
        if stratification is not None else None
    )
    X_validation, X_test, y_validation, y_test = train_test_split(
        X_reste,
        y_reste,
        test_size=0.50,
        random_state=C.RANDOM_STATE,
        stratify=stratification_reste,
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

    brut = io_sources.lire_sources_brutes()
    print(f"Sources brutes chargées : {len(brut)} lignes")
    clean.nettoyer_et_exporter(brut)
    df = io_sources.lire_donnees_module02()
    if df.empty:
        raise ValueError(
            "Le fichier propre du module 2 ne contient aucune ligne."
        )
    if df[["prix", "surface", "date"]].isna().any().any():
        raise ValueError(
            "Le fichier du module 2 contient un prix, une surface ou "
            "une date manquante."
        )
    if (df["prix"] <= 0).any():
        raise ValueError(
            "Le fichier du module 2 contient un prix nul ou négatif."
        )

    print(f"Données propres du module 2 : {len(df)} lignes")
    skew = stats_eda.comparer_prix_log(df)
    simpson = stats_eda.tester_simpson(df)
    mann_kendall = stats_eda.tester_mann_kendall(df)
    normalite_log_prix = stats_eda.tester_normalite_log_prix(df)
    anova = stats_eda.anova_prix_categorie(df)
    khi2 = stats_eda.khi2_categorie_region(df)
    statistiques_source = stats_eda.stats_par_source(
        df, ["prix", "surface"]
    )
    types_source = stats_eda.types_par_source(df)
    statistiques_source.to_csv(
        C.ROOT / "reports" / "stats_descriptives_par_source.csv",
        index=False,
    )
    types_source.to_csv(
        C.ROOT / "reports" / "types_par_source.csv",
        index=False,
    )
    p_value = mann_kendall["p_value"]
    strategie = (
        "temporelle"
        if p_value is not None and p_value < 0.05
        else "aleatoire"
    )
    viz_eda.generer_toutes(df, C.FIG_DIR, brut=brut)
    _ecrire_rapport_eda(
        df,
        brut,
        skew,
        simpson,
        normalite_log_prix,
    )

    rapport = {
        "nombre_lignes": len(df),
        "distribution_prix": skew.to_dict(orient="index"),
        "simpson": {
            "global_spearman": simpson["global_spearman"],
            "par_categorie": simpson["par_categorie"],
        },
        "normalite_log_prix": normalite_log_prix,
        "anova_prix_categorie": anova,
        "khi2_categorie_region": khi2,
        "statistiques_par_source": statistiques_source.to_dict(
            orient="records"
        ),
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
    ensembles = separer_ensembles(
        X,
        y,
        df["date"],
        strategie,
        stratification=df["categorie"] if strategie == "aleatoire" else None,
    )
    resume_split = _verifier_splits(ensembles, df)
    with (C.ROOT / "reports" / "split_summary.json").open(
        "w", encoding="utf-8"
    ) as fichier:
        json.dump(resume_split, fichier, ensure_ascii=False, indent=2)

    X_train, _ = ensembles["train"]
    pipeline = construire_pipeline()
    pipeline.fit(X_train)
    chemin_pipeline = C.MODELS_DIR / "pipeline_preparation.joblib"
    joblib.dump(pipeline, chemin_pipeline)
    pipeline_recharge = joblib.load(chemin_pipeline)
    train_transforme = pipeline_recharge.transform(X_train)
    validation_transforme = pipeline_recharge.transform(
        ensembles["validation"][0]
    )
    controles_sources = {}
    premieres_lignes = df.groupby("source").head(1)
    for source, indices in premieres_lignes.groupby("source").groups.items():
        index = list(indices)[0]
        ligne = preparer_features(df.loc[[index]])
        controles_sources[source] = {
            "lignes_transformees": int(
                pipeline_recharge.transform(ligne).shape[0]
            ),
        }
    controles_sources["non_fuite_scaler"] = {
        "moyenne_surface_log_train": float(
            train_transforme[:, -1].mean()
        ),
        "moyenne_surface_log_validation": float(
            validation_transforme[:, -1].mean()
        ),
    }
    with (C.ROOT / "reports" / "pipeline_checks.json").open(
        "w", encoding="utf-8"
    ) as fichier:
        json.dump(controles_sources, fichier, ensure_ascii=False, indent=2)

    donnees_train = df.loc[X_train.index].copy()
    donnees_train["surface_log"] = X_train["surface_log"]
    donnees_train["annee"] = donnees_train["date"].dt.year
    donnees_train["prix_m2"] = (
        donnees_train["prix"] / donnees_train["surface"]
    )
    evaluation = _evaluer_candidates(
        donnees_train,
        pd.Series(np.log(donnees_train["prix"]), index=donnees_train.index),
    )
    evaluation.to_csv(C.ROOT / "reports" / "feature_cv.csv", index=False)
    prix_m2 = df["prix"] / df["surface"]
    erreur_fuite = float(np.max(np.abs(
        np.log(prix_m2) + np.log(df["surface"]) - np.log(df["prix"])
    )))
    with (C.ROOT / "reports" / "leakage_check.json").open(
        "w", encoding="utf-8"
    ) as fichier:
        json.dump({
            "prix_m2_est_exclu": True,
            "erreur_max_relation_log": erreur_fuite,
            "source_est_exclue_du_pipeline_final": True,
        }, fichier, ensure_ascii=False, indent=2)

    for nom, (X_partie, y_partie) in ensembles.items():
        _exporter_ensemble(nom, X_partie, y_partie, df, pipeline)
        print(f"  {nom:10s}: {len(X_partie)} lignes préparées")

    print(f"Split : {strategie} (graine {C.RANDOM_STATE})")
    print(
        "Pipeline sérialisé : "
        f"{C.MODELS_DIR / 'pipeline_preparation.joblib'}"
    )
    print(f"Figures : {C.FIG_DIR}")
    print(f"Rapport EDA : {C.F_RAPPORT_EDA}")
    print(
        "Le préprocesseur est ajusté uniquement sur l'ensemble "
        "d'entraînement."
    )


if __name__ == "__main__":
    main()
