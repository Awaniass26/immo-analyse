"""Export des fichiers de sortie (données propres, quarantaine, doublons)."""

COLONNES_PROPRES = {
    "source": "source", "id_local": "id_local", "numero_ligne": "numero_ligne",
    "transaction_ref": "transaction", "type_bien_ref": "type_bien",
    "region_ref": "region", "ville_ref": "ville", "date_iso": "date",
    "prix_nombre": "prix_fcfa", "periodicite_ref": "periodicite",
    "surface_nombre": "surface_m2", "chambres_nombre": "chambres",
    "sdb_nombre": "salles_bain", "statut": "statut", "corrige": "corrige",
    "avertissements": "avertissements", "groupe_doublon": "groupe_doublon",
    "conflit_id": "conflit_id",
}

COLONNES_QUARANTAINE = [
    "source", "id_local", "numero_ligne", "motif_quarantaine",
    "date", "type_transaction", "type_bien", "region", "ville", "prix", "surface",
]


def exporter_propres(retenues, dossier):
    dossier.mkdir(parents=True, exist_ok=True)
    propres = retenues[list(COLONNES_PROPRES)].rename(columns=COLONNES_PROPRES)
    propres.to_csv(dossier / "donnees_propres.csv", index=False, encoding="utf-8")
    propres.to_json(dossier / "donnees_propres.json", orient="records",
                    force_ascii=False, indent=2)
    return propres


def exporter_quarantaine(quarantaine, ecartes, dossier):
    dossier.mkdir(parents=True, exist_ok=True)
    quarantaine[COLONNES_QUARANTAINE].to_csv(
        dossier / "quarantaine.csv", index=False, encoding="utf-8")
    ecartes = ecartes[["source", "id_local", "numero_ligne", "ville_ref", "date_iso",
                       "prix_nombre", "surface_nombre"]]
    ecartes.to_csv(dossier / "doublons_ecartes.csv", index=False, encoding="utf-8")