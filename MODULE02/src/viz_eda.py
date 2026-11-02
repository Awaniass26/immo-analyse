"""Visualisations exploratoires produites à partir du jeu propre."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def generer_toutes(df: pd.DataFrame, dossier: Path) -> None:
    """Enregistre six graphiques EDA reproductibles."""
    dossier.mkdir(parents=True, exist_ok=True)
    prix = df.loc[df["prix"] > 0, "prix"]
    surface = df.loc[(df["prix"] > 0) & (df["surface"] > 0)]

    fig, ax = plt.subplots()
    ax.hist(prix, bins=40)
    ax.set(title="Distribution des prix", xlabel="Prix (FCFA)", ylabel="Nombre")
    fig.tight_layout()
    fig.savefig(dossier / "01_distribution_prix.png")
    plt.close(fig)

    fig, ax = plt.subplots()
    ax.hist(np.log(prix), bins=40)
    ax.set(title="Distribution de log(prix)", xlabel="log(prix)", ylabel="Nombre")
    fig.tight_layout()
    fig.savefig(dossier / "02_distribution_log_prix.png")
    plt.close(fig)

    fig, ax = plt.subplots()
    ax.scatter(surface["surface"], surface["prix"], alpha=0.35, s=12)
    ax.set(title="Prix en fonction de la surface",
           xlabel="Surface (m²)", ylabel="Prix (FCFA)")
    fig.tight_layout()
    fig.savefig(dossier / "03_prix_surface.png")
    plt.close(fig)

    groupes = [
        groupe["prix"].to_numpy()
        for _, groupe in df.groupby("categorie")
        if len(groupe) > 0
    ]
    etiquettes = [
        nom for nom, groupe in df.groupby("categorie")
        if len(groupe) > 0
    ]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.boxplot(groupes, showfliers=False)
    ax.set_xticks(range(1, len(etiquettes) + 1))
    ax.set_xticklabels(etiquettes, rotation=35)
    ax.set(title="Prix par catégorie", ylabel="Prix (FCFA)")
    fig.tight_layout()
    fig.savefig(dossier / "04_prix_par_categorie.png")
    plt.close(fig)

    region = df.groupby("region")["prix"].median().sort_values()
    fig, ax = plt.subplots(figsize=(8, 7))
    region.plot.barh(ax=ax)
    ax.set(title="Prix médian par région", xlabel="Prix médian (FCFA)")
    fig.tight_layout()
    fig.savefig(dossier / "05_prix_par_region.png")
    plt.close(fig)

    annuel = df.groupby(df["date"].dt.year)["prix"].median().dropna()
    fig, ax = plt.subplots()
    ax.plot(annuel.index, annuel.values, marker="o")
    ax.set(title="Prix médian par année", xlabel="Année", ylabel="Prix médian (FCFA)")
    fig.tight_layout()
    fig.savefig(dossier / "06_evolution_annuelle.png")
    plt.close(fig)