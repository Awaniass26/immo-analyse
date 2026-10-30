"""Indicateurs de qualité et écriture des rapports."""

import json

import pandas as pd

from src.validation.regles import REGLES


def tableau_des_regles(resultats):
    """Pour chaque règle : conformes, non conformes, non évaluables, taux."""
    lignes = []
    for regle in REGLES:
        serie = resultats[regle.nom]
        conformes = int((serie == True).sum())        # noqa: E712
        non_conformes = int((serie == False).sum())   # noqa: E712
        non_evaluables = int(serie.isna().sum())
        evaluables = conformes + non_conformes
        taux = round(conformes / evaluables * 100, 1) if evaluables else None
        lignes.append({
            "regle": regle.nom,
            "gravite": regle.gravite,
            "conformes": conformes,
            "non_conformes": non_conformes,
            "non_evaluables": non_evaluables,
            "denominateur_evaluables": evaluables,
            "taux_conformite_pct": taux,
        })
    return pd.DataFrame(lignes)


def calculer_indicateurs(brut, validees, resultats, quarantaine, ecartes, retenues):
    """Rassemble tous les indicateurs obligatoires du cahier des charges."""
    total = len(brut)
    hors_quarantaine = total - len(quarantaine)

    a_avertissement = (retenues["avertissements"] != "") | retenues["doublon_probable"] | retenues["conflit_id"]
    entierement_conformes = ~a_avertissement & ~retenues["corrige"]

    erreurs_conversion = {
        "prix": int((validees["prix_etat"] == "erreur").sum()),
        "surface": int(validees["surface_etat"].isin(["erreur", "ambigu"]).sum()),
        "date": int((validees["date_etat"] == "erreur").sum()),
    }

    return {
        "total_recus": total,
        "recus_par_source": brut["source"].value_counts().to_dict(),
        "valeurs_manquantes_par_colonne": {
            colonne: int(brut[colonne].isna().sum())
            for colonne in brut.columns if brut[colonne].isna().sum() > 0},
        "doublons_exacts": {
            "nombre": len(ecartes),
            "taux_pct": round(len(ecartes) / hors_quarantaine * 100, 2),
            "denominateur": "enregistrements hors quarantaine",
        },
        "doublons_probables": int(retenues["doublon_probable"].sum()),
        "conflits_identifiants": int(retenues["conflit_id"].sum()),
        "erreurs_de_conversion": erreurs_conversion,
        "enregistrements_corriges": int(validees["corrige"].sum()),
        "enregistrements_en_quarantaine": len(quarantaine),
        "enregistrements_ecartes_doublons": len(ecartes),
        "enregistrements_retenus": len(retenues),
        "retenus_avec_avertissement": int(a_avertissement.sum()),
        "entierement_conformes": int(entierement_conformes.sum()),
        "taux_global_conformite_pct": round(entierement_conformes.sum() / total * 100, 1),
        "definition_taux_global": (
            "entierement conformes (retenus, sans correction ni avertissement) "
            "/ total des enregistrements recus ; chaque enregistrement compte une fois"),
    }


def ecrire_rapports(indicateurs, tableau_regles, motifs_quarantaine, dossier):
    dossier.mkdir(parents=True, exist_ok=True)

    with open(dossier / "quality_report.json", "w", encoding="utf-8") as f:
        json.dump(indicateurs, f, ensure_ascii=False, indent=2)

    tableau_regles.to_csv(dossier / "quality_summary.csv", index=False)

    i = indicateurs
    texte = f"""# Rapport de qualité — ImmoAnalyse

## Vue d'ensemble
- Enregistrements reçus : **{i['total_recus']}**
- Mis en quarantaine : **{i['enregistrements_en_quarantaine']}**
- Écartés (doublons exacts) : **{i['enregistrements_ecartes_doublons']}**
- Retenus : **{i['enregistrements_retenus']}** dont {i['retenus_avec_avertissement']} avec avertissement
- Entièrement conformes : **{i['entierement_conformes']}**
- Taux global de conformité : **{i['taux_global_conformite_pct']} %**
  ({i['definition_taux_global']})
- Enregistrements corrigés : {i['enregistrements_corriges']}

## Doublons et conflits
- Doublons exacts : {i['doublons_exacts']['nombre']} ({i['doublons_exacts']['taux_pct']} % des {i['doublons_exacts']['denominateur']})
- Doublons probables (signalés, non fusionnés) : {i['doublons_probables']}
- Conflits d'identifiants : {i['conflits_identifiants']}

## Erreurs de conversion
{chr(10).join(f"- {champ} : {n}" for champ, n in i['erreurs_de_conversion'].items())}

## Motifs de quarantaine
{motifs_quarantaine.to_markdown()}

## Conformité par règle
Taux = conformes / évaluables x 100. Les valeurs non évaluables sont comptées à part.

{tableau_regles.to_markdown(index=False)}
"""
    (dossier / "rapport_qualite.md").write_text(texte, encoding="utf-8")