"""Comparaisons descriptives et graphiques des prix du module 1."""

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from MODULE01.src.analysis.statistiques import ajouter_prix_m2, resume_par
from MODULE01.src.processing.prix import convertir_prix
from MODULE01.src.processing.surface import convertir_surface

ETAPES = (
    "Avant nettoyage",
    "Après validation",
    "Après doublons exacts",
)
COULEURS = ("#4C78A8", "#F58518", "#54A24B")


def _prix_valides(donnees, transaction):
    """Prix positifs d'une transaction, en limitant les loyers au mensuel."""
    selection = donnees["transaction_ref"] == transaction
    if transaction == "location":
        selection &= donnees["periodicite_ref"] == "mensuel"

    prix = pd.to_numeric(
        donnees.loc[selection, "prix_nombre"], errors="coerce")
    return prix[prix > 0].dropna()


def _resumer_distributions(etapes):
    """Calcule les statistiques des ventes et loyers mensuels à chaque étape."""
    lignes = []
    for nom_etape, donnees in etapes:
        for transaction in ("vente", "location"):
            prix = _prix_valides(donnees, transaction)
            ligne = {
                "etape": nom_etape,
                "transaction": transaction,
                "periodicite_location": (
                    "mensuelle" if transaction == "location" else "sans objet"),
                "nombre": len(prix),
                "moyenne_fcfa": None,
                "mediane_fcfa": None,
                "q1_fcfa": None,
                "q3_fcfa": None,
                "minimum_fcfa": None,
                "maximum_fcfa": None,
            }
            if not prix.empty:
                ligne.update({
                    "moyenne_fcfa": round(float(prix.mean()), 2),
                    "mediane_fcfa": round(float(prix.median()), 2),
                    "q1_fcfa": round(float(prix.quantile(0.25)), 2),
                    "q3_fcfa": round(float(prix.quantile(0.75)), 2),
                    "minimum_fcfa": float(prix.min()),
                    "maximum_fcfa": float(prix.max()),
                })
            lignes.append(ligne)
    return pd.DataFrame(lignes)


def _creer_donnees_brutes_comparables(brut, categories):
    """Convertit les montants bruts uniquement pour rendre les prix comparables."""
    valeurs = [convertir_prix(prix)[0] for prix in brut["prix"]]
    donnees = categories[["transaction_ref", "periodicite_ref"]].copy()
    donnees["prix_nombre"] = pd.Series(valeurs, index=donnees.index, dtype="Float64")
    return donnees


def _resumer_qualite_brute(brut):
    """Compte, par source, les champs convertibles et les valeurs manquantes."""
    lignes = []
    convertisseurs = {
        "prix": convertir_prix,
        "surface": convertir_surface,
    }
    for source, groupe in brut.groupby("source"):
        for champ, convertir in convertisseurs.items():
            resultats = [convertir(valeur) for valeur in groupe[champ]]
            valeurs = [resultat[0] for resultat in resultats]
            etats = [resultat[1] for resultat in resultats]
            lignes.append({
                "source": source,
                "champ": champ,
                "total": len(groupe),
                "manquants": etats.count("manquant"),
                "non_convertibles": sum(
                    etat in ("erreur", "ambigu") for etat in etats),
                "convertibles": sum(valeur is not None for valeur in valeurs),
                "valeurs_non_positives": sum(
                    valeur is not None and valeur <= 0 for valeur in valeurs),
            })
    return pd.DataFrame(lignes)


def _resumer_valeurs_extremes(etapes):
    """Mesure l'influence des valeurs extrêmes sans les retirer des données."""
    lignes = []
    for nom_etape, donnees in etapes:
        for transaction in ("vente", "location"):
            prix = _prix_valides(donnees, transaction)
            sans_extremes = prix
            nombre_extremes = 0
            if len(prix) >= 4:
                q1, q3 = prix.quantile([0.25, 0.75])
                ecart_interquartile = q3 - q1
                borne_basse = q1 - 1.5 * ecart_interquartile
                borne_haute = q3 + 1.5 * ecart_interquartile
                masque = prix.between(borne_basse, borne_haute)
                sans_extremes = prix[masque]
                nombre_extremes = int((~masque).sum())

            lignes.append({
                "etape": nom_etape,
                "transaction": transaction,
                "nombre": len(prix),
                "nombre_valeurs_extremes_iqr": nombre_extremes,
                "moyenne_fcfa": (
                    round(float(prix.mean()), 2) if not prix.empty else None),
                "mediane_fcfa": (
                    round(float(prix.median()), 2) if not prix.empty else None),
                "moyenne_sans_extremes_fcfa": (
                    round(float(sans_extremes.mean()), 2)
                    if not sans_extremes.empty else None),
                "mediane_sans_extremes_fcfa": (
                    round(float(sans_extremes.median()), 2)
                    if not sans_extremes.empty else None),
            })
    return pd.DataFrame(lignes)


def _tracer_distributions(etapes, figures):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for axe, transaction, titre in zip(
        axes,
        ("vente", "location"),
        ("Ventes", "Locations mensuelles"),
    ):
        series = [
            _prix_valides(donnees, transaction)
            for _, donnees in etapes
        ]
        valeurs = [serie.to_numpy(dtype=float) for serie in series if not serie.empty]
        if not valeurs:
            axe.text(
                0.5, 0.5, "Aucune donnée exploitable",
                ha="center", va="center", transform=axe.transAxes)
            axe.set_axis_off()
            continue

        minimum = min(float(valeurs_) for serie in valeurs for valeurs_ in serie)
        maximum = max(float(valeurs_) for serie in valeurs for valeurs_ in serie)
        if minimum == maximum:
            minimum /= 1.1
            maximum *= 1.1
        bins = np.logspace(np.log10(minimum), np.log10(maximum), 26)

        for (nom_etape, _), prix, couleur in zip(etapes, series, COULEURS):
            if prix.empty:
                continue
            axe.hist(
                prix.to_numpy(dtype=float),
                bins=bins,
                density=True,
                alpha=0.45,
                color=couleur,
                label=f"{nom_etape} (n={len(prix)})",
            )
        axe.set_xscale("log")
        axe.set_title(titre)
        axe.set_xlabel("Prix en FCFA (échelle logarithmique)")
        axe.set_ylabel("Densité")
        axe.grid(axis="y", alpha=0.25)
        axe.legend(fontsize=8)

    fig.suptitle("Distribution des prix bruts convertibles et après le pipeline")
    fig.tight_layout()
    fig.savefig(figures / "distribution_prix_vente_location.png", dpi=150)
    plt.close(fig)


def _tracer_impact_dedoublonnage(avant_doublons, apres_doublons, figures):
    series = [
        _prix_valides(avant_doublons, "vente"),
        _prix_valides(apres_doublons, "vente"),
    ]
    fig, axe = plt.subplots(figsize=(8, 5))
    valeurs = [serie.to_numpy(dtype=float) for serie in series if not serie.empty]
    if valeurs:
        minimum = min(float(v) for serie in valeurs for v in serie)
        maximum = max(float(v) for serie in valeurs for v in serie)
        if minimum == maximum:
            minimum /= 1.1
            maximum *= 1.1
        bins = np.logspace(np.log10(minimum), np.log10(maximum), 26)
        for prix, label, couleur in zip(
            series,
            ("Avant retrait", "Après retrait"),
            COULEURS[:2],
        ):
            if not prix.empty:
                axe.hist(
                    prix.to_numpy(dtype=float),
                    bins=bins,
                    density=True,
                    alpha=0.5,
                    color=couleur,
                    label=f"{label} des doublons exacts (n={len(prix)})",
                )
        axe.set_xscale("log")
        axe.set_xlabel("Prix de vente en FCFA (échelle logarithmique)")
        axe.set_ylabel("Densité")
        axe.legend()
    else:
        axe.text(
            0.5, 0.5, "Aucune vente exploitable",
            ha="center", va="center", transform=axe.transAxes)
    axe.set_title("Effet du retrait des doublons exacts sur les ventes")
    axe.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(figures / "impact_dedoublonnage_prix_vente.png", dpi=150)
    plt.close(fig)


def _tracer_effet_extremes(resume_extremes, figures):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for axe, transaction, titre in zip(
        axes,
        ("vente", "location"),
        ("Ventes", "Locations mensuelles"),
    ):
        tableau = resume_extremes[
            resume_extremes["transaction"] == transaction]
        if tableau.empty or tableau["nombre"].max() == 0:
            axe.text(
                0.5, 0.5, "Aucune donnée exploitable",
                ha="center", va="center", transform=axe.transAxes)
            axe.set_axis_off()
            continue

        positions = np.arange(len(tableau))
        axe.plot(
            positions,
            tableau["moyenne_fcfa"],
            marker="o",
            label="Moyenne avec valeurs extrêmes",
        )
        axe.plot(
            positions,
            tableau["moyenne_sans_extremes_fcfa"],
            marker="o",
            label="Moyenne sans valeurs extrêmes",
        )
        axe.plot(
            positions,
            tableau["mediane_fcfa"],
            marker="s",
            label="Médiane",
        )
        axe.set_yscale("log")
        axe.set_xticks(positions, tableau["etape"], rotation=20, ha="right")
        axe.set_title(titre)
        axe.set_ylabel("Prix en FCFA (échelle logarithmique)")
        axe.grid(axis="y", alpha=0.25)
        axe.legend(fontsize=8)

    fig.suptitle("Sensibilité de la moyenne aux valeurs extrêmes (règle IQR)")
    fig.tight_layout()
    fig.savefig(figures / "sensibilite_valeurs_extremes.png", dpi=150)
    plt.close(fig)


def _tracer_resume_prix_m2(ventes, colonne, titre, chemin, figures, limite=None):
    resume = resume_par(ventes, colonne)
    if limite is not None:
        resume = resume.head(limite)
    resume = resume.sort_values("mediane", ascending=True)

    hauteur = max(4, 0.45 * len(resume) + 1)
    fig, axe = plt.subplots(figsize=(10, hauteur))
    if resume.empty:
        axe.text(
            0.5, 0.5, "Aucune vente exploitable",
            ha="center", va="center", transform=axe.transAxes)
        axe.set_axis_off()
    else:
        mediane = resume["mediane"].to_numpy(dtype=float)
        bas = mediane - resume["q1"].to_numpy(dtype=float)
        haut = resume["q3"].to_numpy(dtype=float) - mediane
        axe.barh(resume.index.astype(str), mediane, color="#4C78A8")
        axe.errorbar(
            mediane,
            range(len(resume)),
            xerr=[bas, haut],
            fmt="none",
            ecolor="#222222",
            capsize=3,
        )
        axe.set_xlabel("Prix médian au m² (FCFA)")
        axe.set_ylabel("")
        axe.grid(axis="x", alpha=0.25)
    axe.set_title(titre)
    fig.tight_layout()
    fig.savefig(figures / chemin, dpi=150)
    plt.close(fig)


def ecrire_visualisations_prix(
    brut, apres_nettoyage, avant_doublons, retenues, dossier
):
    """Écrit les graphiques et les statistiques comparatives du module 1."""
    dossier = Path(dossier)
    figures = dossier / "figures"
    figures.mkdir(parents=True, exist_ok=True)

    avant_nettoyage = _creer_donnees_brutes_comparables(brut, apres_nettoyage)
    etapes = [
        (ETAPES[0], avant_nettoyage),
        (ETAPES[1], avant_doublons),
        (ETAPES[2], retenues),
    ]
    resume = _resumer_distributions(etapes)
    resume.to_csv(dossier / "comparaison_distributions_prix.csv", index=False)
    qualite_brute = _resumer_qualite_brute(brut)
    qualite_brute.to_csv(
        dossier / "qualite_valeurs_brutes.csv", index=False)
    resume_extremes = _resumer_valeurs_extremes(etapes)
    resume_extremes.to_csv(
        dossier / "sensibilite_valeurs_extremes.csv", index=False)
    _tracer_distributions(etapes, figures)
    _tracer_impact_dedoublonnage(avant_doublons, retenues, figures)
    _tracer_effet_extremes(resume_extremes, figures)

    ventes = ajouter_prix_m2(retenues)
    _tracer_resume_prix_m2(
        ventes,
        "type_bien_ref",
        "Prix médian au m² par type de bien (ventes)",
        "prix_m2_par_type.png",
        figures,
    )
    _tracer_resume_prix_m2(
        ventes,
        "ville_ref",
        "Prix médian au m² par ville (12 plus élevées, ventes)",
        "prix_m2_par_ville.png",
        figures,
        limite=12,
    )

    texte = """# Visualisations et comparaison des prix — Module 1

Les prix bruts sont convertis uniquement pour permettre la comparaison
numérique ; les prix manquants ou illisibles sont exclus des histogrammes et
comptés dans `qualite_valeurs_brutes.csv`. Les graphiques comparent ensuite les
prix avant validation, après mise en quarantaine, puis après retrait des
doublons exacts. Les locations sont limitées aux loyers mensuels : les autres
périodicités ne sont pas comparables entre elles. Les doublons probables sont
signalés par le pipeline, mais ne sont pas fusionnés ni supprimés.

Les histogrammes utilisent une échelle logarithmique pour rendre visibles les
écarts de prix. Les prix au m² sont calculés uniquement sur les ventes ; les
barres d'erreur montrent l'intervalle entre le premier et le troisième quartile.
La règle de 1,5 fois l'écart interquartile sert uniquement à mesurer l'effet des
valeurs extrêmes sur la moyenne ; elle ne supprime aucune ligne. Les données
étant synthétiques, ces résultats ne décrivent pas le marché réel.

## Comparaison des distributions

"""
    texte += resume.to_markdown(index=False, floatfmt=".0f")
    texte += "\n\n## Valeurs manquantes, conversions et valeurs extrêmes\n\n"
    texte += qualite_brute.to_markdown(index=False)
    texte += "\n\n"
    texte += resume_extremes.to_markdown(index=False, floatfmt=".0f")
    texte += "\n\n## Figures\n\n"
    texte += "\n".join([
        "- [Distribution des prix de vente et des loyers mensuels]"
        "(./figures/distribution_prix_vente_location.png)",
        "- [Effet du retrait des doublons exacts]"
        "(./figures/impact_dedoublonnage_prix_vente.png)",
        "- [Sensibilité de la moyenne aux valeurs extrêmes]"
        "(./figures/sensibilite_valeurs_extremes.png)",
        "- [Prix au m² par type de bien](./figures/prix_m2_par_type.png)",
        "- [Prix au m² par ville](./figures/prix_m2_par_ville.png)",
    ])
    texte += (
        "\n\nLes valeurs détaillées sont également disponibles dans les fichiers"
        " `comparaison_distributions_prix.csv`, `qualite_valeurs_brutes.csv` et"
        " `sensibilite_valeurs_extremes.csv`.\n"
    )
    (dossier / "analyse_prix.md").write_text(texte, encoding="utf-8")
