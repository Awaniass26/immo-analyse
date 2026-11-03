"""Figures de restitution du module 2."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


def _sauver(fig: plt.Figure, dossier: Path, nom: str) -> None:
    fig.tight_layout()
    fig.savefig(dossier / nom, dpi=140)
    plt.close(fig)


def generer_toutes(
    df: pd.DataFrame,
    dossier: Path,
    brut: pd.DataFrame | None = None,
) -> None:
    """Génère les six figures V1 à V6 à partir des données propres."""
    dossier.mkdir(parents=True, exist_ok=True)
    prix = df.loc[df["prix"] > 0, "prix"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    axes[0].hist(prix, bins=40)
    axes[0].set(
        title=f"Prix brut — skew {prix.skew():.2f}",
        xlabel="Prix (FCFA)",
        ylabel="Nombre d'annonces",
    )
    log_prix = np.log(prix)
    axes[1].hist(log_prix, bins=40)
    axes[1].set(
        title=f"log(prix) — skew {log_prix.skew():.2f}",
        xlabel="log(prix)",
        ylabel="Nombre d'annonces",
    )
    stats.probplot(log_prix, dist="norm", plot=axes[2])
    axes[2].set_title("QQ-plot de log(prix)")
    _sauver(fig, dossier, "01_distribution_prix.png")

    medianes = df.groupby("categorie")["prix"].median().sort_values()
    groupes = [
        df.loc[df["categorie"] == categorie, "prix"].dropna().to_numpy()
        for categorie in medianes.index
    ]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.boxplot(groupes, showfliers=False)
    ax.set_yscale("log")
    ax.set_xticks(range(1, len(medianes) + 1))
    ax.set_xticklabels(medianes.index, rotation=35, ha="right")
    ratio = medianes.max() / medianes.min() if medianes.min() > 0 else np.nan
    ax.set(
        title=f"Prix par catégorie — ratio des médianes max/min : {ratio:.2f}",
        ylabel="Prix (FCFA, échelle logarithmique)",
    )
    _sauver(fig, dossier, "02_prix_par_categorie.png")

    valides = df.dropna(subset=["prix", "surface", "categorie"])
    valides = valides[(valides["prix"] > 0) & (valides["surface"] > 0)]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].scatter(valides["surface"], valides["prix"], alpha=0.25, s=10)
    correlation_globale = valides["prix"].corr(
        valides["surface"], method="spearman"
    )
    axes[0].set(
        title=f"Tous biens — Spearman {correlation_globale:.2f}",
        xlabel="Surface (m²)",
        ylabel="Prix (FCFA)",
    )
    correlations = []
    for categorie, groupe in valides.groupby("categorie"):
        if len(groupe) < 5:
            continue
        correlation = groupe["prix"].corr(
            groupe["surface"], method="spearman"
        )
        correlations.append(correlation)
        axes[1].scatter(
            groupe["surface"],
            groupe["prix"],
            alpha=0.3,
            s=8,
            label=f"{categorie} ({correlation:.2f})",
        )
    axes[1].set(
        title="Prix et surface par catégorie",
        xlabel="Surface (m²)",
        ylabel="Prix (FCFA)",
    )
    axes[1].legend(fontsize=7)
    moyenne_groupe = np.nanmean(correlations) if correlations else np.nan
    fig.suptitle(
        f"Association globale {correlation_globale:.2f} ; "
        f"moyenne des catégories {moyenne_groupe:.2f}"
    )
    _sauver(fig, dossier, "03_prix_surface_categories.png")

    numeriques = [
        colonne for colonne in ("prix", "surface", "chambres", "sdb")
        if colonne in df and pd.api.types.is_numeric_dtype(df[colonne])
    ]
    correlations_numeriques = df[numeriques].corr()
    fig, ax = plt.subplots(figsize=(7, 6))
    image = ax.imshow(
        correlations_numeriques,
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
    )
    ax.set_xticks(range(len(numeriques)), labels=numeriques, rotation=35)
    ax.set_yticks(range(len(numeriques)), labels=numeriques)
    for ligne in range(len(numeriques)):
        for colonne in range(len(numeriques)):
            ax.text(
                colonne,
                ligne,
                f"{correlations_numeriques.iloc[ligne, colonne]:.2f}",
                ha="center",
                va="center",
            )
    fig.colorbar(image, ax=ax, label="Corrélation de Pearson")
    ax.set_title("Corrélations des variables numériques")
    _sauver(fig, dossier, "04_matrice_correlation.png")

    brut = brut if brut is not None else df
    quarantaine = len(brut) - len(df)
    avertissements = int(df["avertissements"].fillna("").ne("").sum()) \
        if "avertissements" in df else 0
    valeurs = [len(brut), len(df), quarantaine, avertissements]
    etiquettes = ["Reçues", "Conservées", "Quarantaine", "Avec avertissement"]
    fig, ax = plt.subplots(figsize=(8, 4))
    couleurs = ["#64748b", "#16a34a", "#dc2626", "#f59e0b"]
    ax.bar(etiquettes, valeurs, color=couleurs)
    ax.set(title="Bilan du nettoyage", ylabel="Nombre de lignes")
    ax.tick_params(axis="x", rotation=15)
    for position, valeur in enumerate(valeurs):
        ax.text(position, valeur, str(valeur), ha="center", va="bottom")
    _sauver(fig, dossier, "05_preuve_nettoyage.png")

    sources = sorted(df["source"].dropna().unique())
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    prix_groupes = [
        df.loc[df["source"] == source, "prix"].dropna().to_numpy()
        for source in sources
    ]
    surface_groupes = [
        df.loc[df["source"] == source, "surface"].dropna().to_numpy()
        for source in sources
    ]
    positions = range(1, len(sources) + 1)
    axes[0].boxplot(prix_groupes, showfliers=False)
    axes[0].set_yscale("log")
    axes[0].set(title="Prix par source", ylabel="Prix (FCFA, log)")
    axes[1].boxplot(surface_groupes, showfliers=False)
    axes[1].set(title="Surface par source", ylabel="Surface (m²)")
    labels_prix = [
        f"{source}\nn={len(groupe)}\nmed={np.median(groupe):,.0f}"
        if len(groupe) else f"{source}\nn=0"
        for source, groupe in zip(sources, prix_groupes)
    ]
    labels_surface = [
        f"{source}\nn={len(groupe)}\nmed={np.median(groupe):.1f}"
        if len(groupe) else f"{source}\nn=0"
        for source, groupe in zip(sources, surface_groupes)
    ]
    axes[0].set_xticks(positions, labels=labels_prix, rotation=35, ha="right")
    axes[1].set_xticks(
        positions,
        labels=labels_surface,
        rotation=35,
        ha="right",
    )
    _sauver(fig, dossier, "06_comparaison_sources.png")
