"""Point d'entrée : lance tout le pipeline, de bout en bout."""

from MODULE01.src import config
from MODULE01.src.analysis.profilage import ecrire_profilage
from MODULE01.src.analysis.rapport import (
    calculer_indicateurs,
    ecrire_rapports,
    tableau_des_regles,
)
from MODULE01.src.analysis.statistiques import ajouter_prix_m2, resume_par
from MODULE01.src.analysis.visualisations import ecrire_visualisations_prix
from MODULE01.src.export import exporter_propres, exporter_quarantaine
from MODULE01.src.loaders.chargeur import charger_toutes_les_sources
from MODULE01.src.processing.doublons import (
    marquer_conflits_id, marquer_doublons_exacts, marquer_doublons_probables)
from MODULE01.src.processing.nettoyage import nettoyer
from MODULE01.src.validation.regles import valider


def main():
    # 1. Charger (rien n'est modifié)
    brut = charger_toutes_les_sources()

    # 2. Nettoyer puis valider
    nettoyees = nettoyer(brut)
    validees, resultats = valider(nettoyees)

    # 3. Séparer la quarantaine du reste
    quarantaine = validees[validees["en_quarantaine"]]
    reste = validees[~validees["en_quarantaine"]]

    # 4. Doublons et conflits (sur ce qui n'est pas en quarantaine)
    reste = marquer_doublons_exacts(reste)
    reste = marquer_conflits_id(reste)
    ecartes = reste[reste["doublon_exact"]]
    retenues = marquer_doublons_probables(reste[~reste["doublon_exact"]])

    # 5. Comparaisons descriptives et visualisations
    ecrire_visualisations_prix(
        brut, nettoyees, reste, retenues, config.DOSSIER_RAPPORTS)

    # 6. Indicateurs et rapports
    indicateurs = calculer_indicateurs(
        brut, validees, resultats, quarantaine, ecartes, retenues)
    motifs = quarantaine["motif_quarantaine"].value_counts().rename("nombre")
    ecrire_rapports(indicateurs, tableau_des_regles(resultats), motifs,
                    config.DOSSIER_RAPPORTS)

    ecrire_profilage(validees, config.DOSSIER_RAPPORTS)

    # 7. Exports
    exporter_propres(retenues, config.DOSSIER_PROPRE)
    exporter_quarantaine(quarantaine, ecartes, config.DOSSIER_QUARANTAINE)

    # 8. Analyse des prix au m² (ventes)
    ventes = ajouter_prix_m2(retenues)
    resume_par(ventes, "type_bien_ref").to_csv(
        config.DOSSIER_RAPPORTS / "prix_m2_par_type.csv")
    resume_par(ventes, "ville_ref").to_csv(
        config.DOSSIER_RAPPORTS / "prix_m2_par_ville.csv")

    print(f"Reçus : {indicateurs['total_recus']}")
    print(f"Quarantaine : {indicateurs['enregistrements_en_quarantaine']}")
    print(
        "Doublons exacts écartés : "
        f"{indicateurs['enregistrements_ecartes_doublons']}")
    print(f"Retenus : {indicateurs['enregistrements_retenus']}")
    print(
        "Taux global de conformité : "
        f"{indicateurs['taux_global_conformite_pct']} %")
    print("Rapports écrits dans le dossier reports/")


if __name__ == "__main__":
    main()