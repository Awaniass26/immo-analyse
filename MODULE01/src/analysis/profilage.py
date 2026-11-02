"""Profilage par source : un mini-rapport de qualité pour chacune des 5 sources."""

import pandas as pd

COLONNES_BRUTES = ["id_local", "date", "type_transaction", "type_bien", "region",
                   "ville", "quartier", "prix", "devise", "surface", "pieces",
                   "chambres", "salles_bain", "statut"]
COLONNES_DOUBLONS = ["date", "type_transaction", "type_bien", "region", "ville",
                     "prix", "surface", "chambres", "salles_bain"]


def profiler_source(tableau):
    """Renvoie un dictionnaire de mesures pour UNE source (colonnes brutes + états)."""
    # Colonnes réellement présentes dans cette source (au moins une valeur)
    presentes = [c for c in COLONNES_BRUTES if tableau[c].notna().any()]
    absentes = [c for c in COLONNES_BRUTES if c not in presentes]

    manquants = pd.DataFrame({
        "manquants": tableau[presentes].isna().sum(),
        "taux_pct": (tableau[presentes].isna().mean() * 100).round(1),
    })

    colonnes_doublons = [c for c in COLONNES_DOUBLONS if c in presentes]
    doublons_exacts = int(tableau.duplicated(subset=colonnes_doublons).sum())

    erreurs = {
        "prix": int((tableau["prix_etat"] == "erreur").sum()),
        "surface": int(tableau["surface_etat"].isin(["erreur", "ambigu"]).sum()),
        "date": int((tableau["date_etat"] == "erreur").sum()),
    }

    mesures = tableau[["prix_nombre", "surface_nombre"]].astype(float)
    distribution = mesures.describe().loc[["count", "mean", "min", "50%", "max"]].round(1)
    distribution.index = ["nombre", "moyenne", "minimum", "mediane", "maximum"]

    return {
        "lignes": len(tableau),
        "colonnes_presentes": presentes,
        "colonnes_absentes": absentes,
        "manquants": manquants,
        "doublons_exacts_bruts": doublons_exacts,
        "erreurs_conversion": erreurs,
        "distribution": distribution,
        "types_de_bien": tableau["type_bien_ref"].value_counts().head(7),
        "villes_principales": tableau["ville_ref"].value_counts().head(5),
    }


def ecrire_profilage(validees, dossier):
    """Écrit reports/profilage_par_source.md (une section par source)."""
    dossier.mkdir(parents=True, exist_ok=True)
    texte = "# Profilage par source\n\n"
    texte += ("Pour chaque source : volume, colonnes présentes, valeurs manquantes, "
              "doublons exacts, erreurs de conversion et distributions.\n")

    for nom, tableau in validees.groupby("source"):
        profil = profiler_source(tableau)
        texte += f"\n## Source : {nom}\n\n"
        texte += f"- Lignes : **{profil['lignes']}**\n"
        texte += f"- Colonnes absentes de cette source : {', '.join(profil['colonnes_absentes']) or 'aucune'}\n"
        texte += f"- Doublons exacts (colonnes brutes) : {profil['doublons_exacts_bruts']}\n"
        texte += f"- Erreurs de conversion : {profil['erreurs_conversion']}\n"
        texte += "\n**Valeurs manquantes (colonnes présentes)**\n\n"
        texte += profil["manquants"].to_markdown() + "\n"
        texte += "\n**Distribution du prix et de la surface (après conversion)**\n\n"
        texte += profil["distribution"].to_markdown() + "\n"
        texte += "\n**Types de bien**\n\n" + profil["types_de_bien"].to_markdown() + "\n"
        texte += "\n**Villes principales**\n\n" + profil["villes_principales"].to_markdown() + "\n"

    (dossier / "profilage_par_source.md").write_text(texte, encoding="utf-8")