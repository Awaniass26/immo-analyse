# src/stats_eda.py
"""Comp 1 + 2 : stats descriptives et EDA."""
import numpy as np
import pandas as pd
from scipy import stats


def tableau_types(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "colonne": df.columns,
        "dtype": df.dtypes.astype(str).values,
        "non_nuls": df.notna().sum().values,
        "manquants": df.isna().sum().values,
        "pct_manquants": (df.isna().mean() * 100).round(2).values,
    })


def stats_numeriques(df: pd.DataFrame, col: str) -> dict:
    s = df[col].dropna()
    return {
        "count": len(s),
        "mean": s.mean(),
        "median": s.median(),
        "std": s.std(),
        "q1": s.quantile(0.25),
        "q3": s.quantile(0.75),
        "skew": s.skew(),
        "kurtosis": s.kurtosis(),
    }


def stats_par_source(df: pd.DataFrame, colonnes: list[str]) -> pd.DataFrame:
    """Calcule les statistiques descriptives numériques par source."""
    lignes = []
    for source, groupe in df.groupby("source", dropna=False):
        for colonne in colonnes:
            if colonne not in groupe:
                continue
            mesures = stats_numeriques(groupe, colonne)
            lignes.append({"source": source, "champ": colonne, **mesures})
    return pd.DataFrame(lignes)


def types_par_source(df: pd.DataFrame) -> pd.DataFrame:
    """Décrit les types présents et les valeurs manquantes par source."""
    lignes = []
    for source, groupe in df.groupby("source", dropna=False):
        for colonne in groupe.columns:
            lignes.append({
                "source": source,
                "champ": colonne,
                "type_python": str(groupe[colonne].dtype),
                "non_nuls": int(groupe[colonne].notna().sum()),
                "manquants": int(groupe[colonne].isna().sum()),
            })
    return pd.DataFrame(lignes)


def comparer_prix_log(df: pd.DataFrame) -> pd.DataFrame:
    """Skew prix brut vs log(prix) — preuve comp 1."""
    s = df["prix"].dropna()
    s = s[s > 0]
    return pd.DataFrame({
        "prix":     [s.skew(), s.kurtosis()],
        "log_prix": [np.log(s).skew(), np.log(s).kurtosis()],
    }, index=["skew", "kurtosis"])


def tester_simpson(df: pd.DataFrame) -> dict:
    """Corrélation prix~surface globale vs par catégorie."""
    d = df.dropna(subset=["prix", "surface"])
    d = d[(d["prix"] > 0) & (d["surface"] > 0)]
    global_r = d["prix"].corr(d["surface"], method="spearman")
    par_cat = d.groupby("categorie").apply(
        lambda groupe: (
            groupe["prix"].corr(groupe["surface"], method="spearman")
            if len(groupe) >= 5 else np.nan
        )
    )
    return {"global_spearman": global_r, "par_categorie": par_cat.to_dict()}


def tester_mann_kendall(df: pd.DataFrame) -> dict:
    """Tendance temporelle sur prix médian par année."""
    d = df.dropna(subset=["date", "prix"]).copy()
    d["annee"] = d["date"].dt.year
    serie = d.groupby("annee")["prix"].median().sort_index()
    if len(serie) < 3:
        return {"p_value": None, "conclusion": "trop peu d'années"}
    # Mann-Kendall simplifié via scipy.kendalltau
    tau, p = stats.kendalltau(serie.index.values, serie.values)
    return {
        "tau": tau,
        "p_value": p,
        "tendance": p < 0.05,
        "serie": serie.to_dict(),
    }


def tester_normalite_log_prix(df: pd.DataFrame) -> dict:
    """Applique Shapiro à un échantillon reproductible de log(prix)."""
    valeurs = np.log(df.loc[df["prix"] > 0, "prix"].dropna()).to_numpy()
    if len(valeurs) < 3:
        return {"statistique": None, "p_value": None, "n": len(valeurs)}
    if len(valeurs) > 5_000:
        valeurs = np.random.default_rng(42).choice(
            valeurs, size=5_000, replace=False
        )
    statistique, p_value = stats.shapiro(valeurs)
    return {
        "statistique": float(statistique),
        "p_value": float(p_value),
        "n": len(valeurs),
    }


def anova_prix_categorie(df: pd.DataFrame) -> dict:
    groupes = [
        groupe["prix"].dropna().values
        for _, groupe in df.groupby("categorie")
        if len(groupe) > 2
    ]
    if len(groupes) < 2:
        return {"F": None, "p": None}
    F, p = stats.f_oneway(*groupes)
    return {"F": F, "p": p}


def khi2_categorie_region(df: pd.DataFrame) -> dict:
    table = pd.crosstab(df["categorie"], df["region"])
    if table.size == 0:
        return {"chi2": None, "p": None}
    chi2, p, dof, _ = stats.chi2_contingency(table)
    return {"chi2": chi2, "p": p, "dof": dof}