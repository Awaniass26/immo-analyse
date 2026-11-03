"""Nettoyage autonome des cinq sources et production des livrables qualité."""

import re
import unicodedata
from datetime import date

import numpy as np
import pandas as pd

from . import config as C

COLONNES_METIER = [
    "type_transaction",
    "categorie",
    "region",
    "commune",
    "date",
    "prix",
    "surface",
    "chambres",
    "sdb",
]

MOJIBAKE = {
    "Ã¡": "á",
    "Ã ": "à",
    "Ã¢": "â",
    "Ã§": "ç",
    "Ã©": "é",
    "Ã¨": "è",
    "Ãª": "ê",
    "Ã«": "ë",
    "Ã®": "î",
    "Ã¯": "ï",
    "Ã´": "ô",
    "Ã¹": "ù",
    "Ã»": "û",
    "Ã¼": "ü",
    "Ã‰": "É",
    "Ã€": "À",
    "Ã‚": "Â",
    "Ã‡": "Ç",
    "ÃŠ": "Ê",
    "ÃŽ": "Î",
    "Ã”": "Ô",
    "Ã›": "Û",
    "ï¿½": "é",
}

MOTS_SURFACE = {
    "vingt": 20,
    "trente": 30,
    "quarante": 40,
    "cinquante": 50,
    "soixante": 60,
    "quatre-vingt": 80,
    "quatre vingt": 80,
    "cent": 100,
}

ALIAS_CATEGORIE = {
    "appart": "Appartement",
    "appartement": "Appartement",
    "appt": "Appartement",
    "studio": "Studio",
    "chambre": "Chambre",
    "chambre simple": "Chambre",
    "villa": "Villa",
    "maison": "Maison",
    "terrain": "Terrain",
    "terrains": "Terrain",
    "local": "Local commercial",
    "local commercial": "Local commercial",
    "bureau": "Local commercial",
    "magasin": "Local commercial",
}

ALIAS_STATUT = {
    "acte signe": "Vendu",
    "vente conclue": "Vendu",
    "vendu": "Vendu",
    "en vente": "En vente",
    "disponible": "Disponible",
    "loue": "Loué",
    "sous offre": "Sous offre",
    "retire": "Retiré",
    "a confirmer": "À confirmer",
}


def _simplifier(valeur: object) -> str:
    texte = unicodedata.normalize("NFKD", str(valeur).strip().lower())
    texte = "".join(
        caractere for caractere in texte
        if not unicodedata.combining(caractere)
    )
    return re.sub(r"\s+", " ", texte)


def corriger_mojibake(valeur: object) -> object:
    """Répare les séquences connues sans modifier les fichiers bruts."""
    if not isinstance(valeur, str):
        return valeur

    for incorrect, correct in MOJIBAKE.items():
        valeur = valeur.replace(incorrect, correct)
    return valeur.strip()


def parser_prix(valeur: object) -> float:
    """Convertit les nombres FCFA et les suffixes explicites « millions »."""
    if pd.isna(valeur):
        return np.nan

    texte = str(valeur).strip().lower()
    if texte in {
        "",
        "n/a",
        "na",
        "none",
        "none fcfa",
        "à négocier",
        "a negocier",
    }:
        return np.nan

    texte = texte.replace("fcfa", "").replace("f cfa", "").strip()
    texte = texte.replace("\u00a0", "").replace("\u202f", "").replace(" ", "")
    millions = re.fullmatch(r"(-?\d+(?:[.,]\d+)?)\s*millions?", texte)
    if millions:
        return float(millions.group(1).replace(",", ".")) * 1_000_000

    if re.fullmatch(r"-?\d{1,3}(?:,\d{3})+(?:\.0+)?", texte):
        texte = texte.replace(",", "")
    elif re.fullmatch(r"-?\d+(?:\.\d+)?", texte):
        pass
    elif re.fullmatch(r"-?\d+,\d{1,2}", texte):
        texte = texte.replace(",", ".")
    else:
        return np.nan

    return float(texte)


def parser_surface(valeur: object) -> float:
    """Convertit une surface numérique ou une virgule décimale explicite."""
    if pd.isna(valeur):
        return np.nan

    texte = str(valeur).strip().lower()
    if texte in {"", "n/a", "na", "none", "null"}:
        return np.nan
    if texte in MOTS_SURFACE:
        return float(MOTS_SURFACE[texte])
    texte = texte.replace("\u00a0", "").replace(" ", "")
    if re.fullmatch(r"-?\d+,\d{1,2}", texte):
        texte = texte.replace(",", ".")
    if re.fullmatch(r"-?\d+(?:\.\d+)?", texte):
        return float(texte)
    return np.nan


def parser_date(valeur: object) -> pd.Timestamp:
    """Lit les dates ISO et JJ/MM/AAAA, et rejette les dates impossibles."""
    if pd.isna(valeur) or not str(valeur).strip():
        return pd.NaT

    texte = str(valeur).strip()
    for format_date in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return pd.to_datetime(texte, format=format_date, errors="raise")
        except ValueError:
            continue
    return pd.NaT


def normaliser_categorie(valeur: object, categories: dict[str, str]) -> object:
    if pd.isna(valeur):
        return pd.NA
    cle = _simplifier(corriger_mojibake(valeur))
    return categories.get(cle, str(corriger_mojibake(valeur)).strip().title())


def normaliser_nom(
    valeur: object,
    valeurs_reference: dict[str, str],
) -> object:
    if pd.isna(valeur) or not str(valeur).strip():
        return pd.NA
    nettoye = corriger_mojibake(str(valeur))
    return valeurs_reference.get(
        _simplifier(nettoye),
        str(nettoye).strip().title(),
    )


def _charger_referentiels() -> tuple[dict[str, str], dict[str, str], dict]:
    geo = pd.read_csv(C.F_REF_GEO, encoding="utf-8-sig")
    categories_df = pd.read_csv(C.F_REF_CAT, encoding="utf-8-sig")
    villes = {_simplifier(ville): ville for ville in geo["ville"].dropna()}
    regions = {
        _simplifier(region): region
        for region in geo["region"].dropna()
    }
    categories = {}
    for _, ligne in categories_df.iterrows():
        officiel = ligne["categorie"]
        categories[_simplifier(officiel)] = officiel
        for alias in str(ligne["synonymes"]).split("|"):
            categories[_simplifier(alias)] = officiel
    region_par_ville = dict(zip(geo["ville"], geo["region"]))
    fourchettes = categories_df.set_index("categorie").to_dict(orient="index")
    return villes, regions, {
        "categories": categories,
        "region_par_ville": region_par_ville,
        "fourchettes": fourchettes,
    }


def _normaliser_transaction(ligne: pd.Series) -> object:
    valeur = ligne["type_transaction"]
    if pd.notna(valeur):
        cle = _simplifier(corriger_mojibake(valeur))
        if cle in {"vente", "location"}:
            return cle

    source = ligne["source"]
    statut = _simplifier(ligne["statut"]) if pd.notna(ligne["statut"]) else ""
    if source in {"historique", "notaires"} or statut in {
        "vendu",
        "vente conclue",
        "acte signe",
        "en vente",
    }:
        return "vente"
    if statut == "loue":
        return "location"
    return pd.NA


def normaliser_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise les champs communs et conserve les colonnes d'origine."""
    villes, regions, referentiels = _charger_referentiels()
    resultat = df.copy()
    originaux = {
        colonne: resultat[colonne].copy()
        for colonne in ("region", "commune", "categorie", "statut")
    }
    for colonne in ("region", "commune", "categorie", "statut"):
        resultat[colonne] = resultat[colonne].map(corriger_mojibake)

    resultat["region"] = resultat["region"].map(
        lambda valeur: normaliser_nom(valeur, regions)
    )
    resultat["commune"] = resultat["commune"].map(
        lambda valeur: normaliser_nom(valeur, villes)
    )
    resultat["categorie"] = resultat["categorie"].map(
        lambda valeur: normaliser_categorie(
            valeur, referentiels["categories"]
        )
    )
    resultat["statut"] = resultat["statut"].map(
        lambda valeur: (
            ALIAS_STATUT.get(_simplifier(valeur), str(valeur).strip().title())
            if pd.notna(valeur) else pd.NA
        )
    )
    resultat["type_transaction"] = resultat.apply(
        _normaliser_transaction, axis=1
    )
    resultat["prix_initial"] = resultat["prix"]
    resultat["surface_initiale"] = resultat["surface"]
    resultat["date_initiale"] = resultat["date"]
    resultat["prix"] = resultat["prix"].map(parser_prix)
    resultat["surface"] = resultat["surface"].map(parser_surface)
    resultat["date"] = resultat["date"].map(parser_date)
    resultat["chambres"] = pd.to_numeric(resultat["chambres"], errors="coerce")
    resultat["sdb"] = pd.to_numeric(resultat["sdb"], errors="coerce")
    resultat["geo_ok"] = [
        pd.notna(ville)
        and pd.notna(region)
        and referentiels["region_par_ville"].get(ville) == region
        for region, ville in zip(resultat["region"], resultat["commune"])
    ]
    resultat["categorie_connue"] = resultat["categorie"].isin(
        set(referentiels["fourchettes"])
    )
    prix_numerique = resultat["prix_initial"].astype("string").str.fullmatch(
        r"-?\d+(?:\.0+)?"
    )
    surface_numerique = (
        resultat["surface_initiale"]
        .astype("string")
        .str.fullmatch(r"-?\d+(?:\.\d+)?")
    )
    date_iso = resultat["date_initiale"].astype("string").str.fullmatch(
        r"\d{4}-\d{2}-\d{2}"
    )
    resultat["corrige"] = (
        (resultat["prix_initial"].notna() & ~prix_numerique.fillna(False))
        | (
            resultat["surface_initiale"].notna()
            & ~surface_numerique.fillna(False)
        )
        | (resultat["date_initiale"].notna() & ~date_iso.fillna(False))
    )
    for colonne, original in originaux.items():
        resultat["corrige"] |= (
            original.fillna("").astype(str)
            != resultat[colonne].fillna("").astype(str)
        )
    return resultat


def _motifs_quarantaine(ligne: pd.Series) -> list[str]:
    motifs = []
    if pd.isna(ligne["id_local"]) or not str(ligne["id_local"]).strip():
        motifs.append("identifiant absent")
    if pd.isna(ligne["type_transaction"]):
        motifs.append("transaction non interprétable")
    if pd.isna(ligne["prix"]) or ligne["prix"] <= 0:
        motifs.append("prix absent, illisible ou non positif")
    if pd.isna(ligne["surface"]) or ligne["surface"] <= 0:
        motifs.append("surface absente, illisible ou non positive")
    if pd.isna(ligne["date"]):
        motifs.append("date absente ou impossible")

    statut = _simplifier(ligne["statut"]) if pd.notna(ligne["statut"]) else ""
    vente_conclue = statut in {"vendu", "vente conclue", "acte signe"}
    if (
        pd.notna(ligne["date"])
        and ligne["date"].date() > date.today()
        and (vente_conclue or ligne["source"] in {"historique", "notaires"})
    ):
        motifs.append("date future pour une transaction conclue")
    return motifs


def _avertissements(ligne: pd.Series, fourchettes: dict) -> list[str]:
    avertissements = []
    if pd.notna(ligne["surface"]):
        if ligne["surface"] < 5 or ligne["surface"] > 2_000:
            avertissements.append("surface hors fourchette générale")
    if pd.notna(ligne["prix"]):
        if ligne["prix"] < 100_000 or ligne["prix"] > 2_000_000_000:
            avertissements.append("prix hors fourchette générale")
    if not ligne["categorie_connue"]:
        avertissements.append("catégorie absente du référentiel")
    elif pd.notna(ligne["prix"]) and pd.notna(ligne["surface"]):
        limites = fourchettes[ligne["categorie"]]
        if not (
            limites["prix_min_indicatif"]
            <= ligne["prix"]
            <= limites["prix_max_indicatif"]
        ):
            avertissements.append(
                "prix hors fourchette indicative de la catégorie"
            )
        if not (
            limites["surface_min_typique"]
            <= ligne["surface"]
            <= limites["surface_max_typique"]
        ):
            avertissements.append(
                "surface hors fourchette typique de la catégorie"
            )
    if pd.isna(ligne["commune"]) or pd.isna(ligne["region"]):
        avertissements.append("région ou ville manquante")
    elif not ligne["geo_ok"]:
        avertissements.append("ville et région incompatibles")
    if pd.notna(ligne["date"]) and ligne["date"].date() > date.today():
        avertissements.append("date future à vérifier")
    return avertissements


def _compter_doublons_probables(df: pd.DataFrame) -> int:
    colonnes = ["commune", "categorie"]
    candidats = df.dropna(subset=colonnes + ["surface", "prix", "date"])
    total = 0
    for _, groupe in candidats.groupby(colonnes, dropna=False):
        lignes = groupe.to_dict("records")
        for position, ligne in enumerate(lignes):
            for autre in lignes[position + 1:]:
                if ligne["source"] == autre["source"]:
                    continue
                surface_proche = abs(ligne["surface"] - autre["surface"]) <= (
                    0.02 * max(abs(ligne["surface"]), abs(autre["surface"]))
                )
                prix_proche = abs(ligne["prix"] - autre["prix"]) <= (
                    0.05 * max(abs(ligne["prix"]), abs(autre["prix"]))
                )
                jours = abs((ligne["date"] - autre["date"]).days)
                if surface_proche and prix_proche and jours <= 30:
                    total += 1
    return total


def marquer_avertissements(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Marque les anomalies non bloquantes sans supprimer de lignes."""
    toutes = df.copy()
    avertissements = []
    for _, ligne in toutes.iterrows():
        motifs = []
        if pd.notna(ligne.get("surface")):
            if ligne["surface"] < 5:
                motifs.append("surface_tres_petite")
            elif ligne["surface"] > 2_000:
                motifs.append("surface_tres_grande")
        if pd.notna(ligne.get("prix")):
            if ligne["prix"] < 100_000:
                motifs.append("prix_tres_bas")
            elif ligne["prix"] > 2_000_000_000:
                motifs.append("prix_tres_haut")
        if "geo_ok" in ligne and not bool(ligne["geo_ok"]):
            motifs.append("region_ville_incoherentes")
        avertissements.append(";".join(motifs))
    toutes["avertissements"] = avertissements
    averties = toutes[toutes["avertissements"] != ""].copy()
    return toutes, averties


def _ecrire_rapport_qualite(
    brut: pd.DataFrame,
    normalise: pd.DataFrame,
    propres: pd.DataFrame,
    quarantaine: pd.DataFrame,
    averties: pd.DataFrame,
    doublons_exacts: int,
    doublons_id: int,
    doublons_probables: int,
) -> None:
    manquants = (
        brut.groupby("source")[["prix", "surface", "date"]]
        .apply(lambda groupe: groupe.isna().sum())
    )
    erreurs_conversion = {
        "prix": int(
            normalise["prix"].isna().sum() - brut["prix"].isna().sum()
        ),
        "surface": int(
            normalise["surface"].isna().sum() - brut["surface"].isna().sum()
        ),
        "date": int(
            normalise["date"].isna().sum() - brut["date"].isna().sum()
        ),
    }
    erreurs_par_source = []
    for source, indices in brut.groupby("source").groups.items():
        lignes_brutes = brut.loc[indices]
        lignes_normalisees = normalise.loc[indices]
        erreurs_par_source.append({
            "source": source,
            "prix_illisible": int(
                (
                    lignes_brutes["prix"].notna()
                    & lignes_normalisees["prix"].isna()
                ).sum()
            ),
            "surface_illisible": int(
                (
                    lignes_brutes["surface"].notna()
                    & lignes_normalisees["surface"].isna()
                ).sum()
            ),
            "date_illisible": int(
                (
                    lignes_brutes["date"].notna()
                    & lignes_normalisees["date"].isna()
                ).sum()
            ),
        })
    conformes = int(
        (normalise["motif_quarantaine"] == "")
        .mul(~normalise["corrige"])
        .mul(normalise["avertissements"].eq(""))
        .sum()
    ) if "avertissements" in normalise else len(propres) - len(averties)
    taux_conformite = conformes / len(brut) * 100 if len(brut) else 0.0
    lignes = [
        "# Rapport de qualité — Module 2",
        "",
        f"- Lignes brutes reçues : {len(brut)}",
        f"- Lignes conservées : {len(propres)}",
        f"- Lignes en quarantaine : {len(quarantaine)}",
        f"- Lignes conservées avec avertissement : {len(averties)}",
        f"- Lignes corrigées : {int(normalise['corrige'].sum())}",
        f"- Doublons exacts écartés : {doublons_exacts}",
        f"- Identifiants dupliqués écartés : {doublons_id}",
        f"- Doublons probables signalés (paires) : {doublons_probables}",
        f"- Taux de conformité complète : {taux_conformite:.1f} %",
        "",
        "Le taux de conformité complète est calculé sur le nombre de lignes "
        "brutes reçues : lignes conservées sans correction ni avertissement / "
        "lignes reçues.",
        "",
        "## Valeurs manquantes initiales par source",
        "",
        manquants.to_markdown(),
        "",
        "## Erreurs de conversion",
        "",
        "| Champ | Valeurs non convertibles |",
        "|---|---:|",
    ]
    lignes.extend(
        f"| {champ} | {nombre} |"
        for champ, nombre in erreurs_conversion.items()
    )
    lignes.extend([
        "",
        "## Erreurs de conversion par source",
        "",
        "| Source | Prix illisible | Surface illisible | Date illisible |",
        "|---|---:|---:|---:|",
    ])
    lignes.extend(
        f"| {ligne['source']} | {ligne['prix_illisible']} | "
        f"{ligne['surface_illisible']} | {ligne['date_illisible']} |"
        for ligne in erreurs_par_source
    )
    C.F_RAPPORT_QUALITE.write_text("\n".join(lignes) + "\n", encoding="utf-8")


def nettoyer_et_exporter(brut: pd.DataFrame) -> pd.DataFrame:
    """Produit les trois livrables qualité indépendamment du module 1."""
    C.OUT_DIR.mkdir(parents=True, exist_ok=True)
    if "numero_ligne" not in brut:
        brut = brut.copy()
        brut["numero_ligne"] = range(1, len(brut) + 1)
    _, _, referentiels = _charger_referentiels()
    normalise = normaliser_df(brut)

    doublon_id = normalise.duplicated(
        subset=["source", "id_local"], keep="first"
    ) & normalise["id_local"].notna()
    colonnes_exactes = [
        colonne for colonne in brut.columns
        if colonne not in {"source", "id_local"}
    ]
    doublon_exact = brut.duplicated(subset=colonnes_exactes, keep="first")

    normalise["motif_quarantaine"] = normalise.apply(
        lambda ligne: "; ".join(_motifs_quarantaine(ligne)), axis=1
    )
    normalise.loc[doublon_id, "motif_quarantaine"] = (
        normalise.loc[doublon_id, "motif_quarantaine"]
        .map(
            lambda motif: (
                f"{motif}; identifiant dupliqué dans la source"
            ).strip("; ")
        )
    )
    normalise.loc[doublon_exact, "motif_quarantaine"] = (
        normalise.loc[doublon_exact, "motif_quarantaine"]
        .map(lambda motif: f"{motif}; doublon exact écarté".strip("; "))
    )

    quarantine = normalise[normalise["motif_quarantaine"] != ""].copy()
    retenues = normalise[normalise["motif_quarantaine"] == ""].copy()
    retenues["avertissements"] = retenues.apply(
        lambda ligne: "; ".join(
            _avertissements(ligne, referentiels["fourchettes"])
        ),
        axis=1,
    )
    averties = retenues[retenues["avertissements"] != ""].copy()
    normalise["avertissements"] = ""
    normalise.loc[retenues.index, "avertissements"] = (
        retenues["avertissements"]
    )
    doublons_probables = _compter_doublons_probables(retenues)

    colonnes_sortie = [
        "id_local",
        "numero_ligne",
        "source",
        "date",
        "type_transaction",
        "categorie",
        "region",
        "commune",
        "prix",
        "surface",
        "chambres",
        "sdb",
        "statut",
        "avertissements",
    ]
    colonnes_export = {
        "type_transaction": "transaction",
        "categorie": "type_bien",
        "prix": "prix_fcfa",
        "surface": "surface_m2",
        "commune": "ville",
    }
    toutes_valides = retenues[colonnes_sortie].rename(
        columns=colonnes_export
    )
    propres = toutes_valides[
        toutes_valides["avertissements"].fillna("") == ""
    ].copy()
    avertissements_export = toutes_valides[
        toutes_valides["avertissements"].fillna("") != ""
    ].copy()
    avertissements_export.to_csv(
        C.F_AVERTISSEMENTS,
        index=False,
        encoding="utf-8",
    )
    quarantine.to_csv(C.F_QUARANTAINE, index=False, encoding="utf-8")
    propres.to_csv(C.F_DONNEES_PROPRES, index=False, encoding="utf-8")
    _ecrire_rapport_qualite(
        brut,
        normalise,
        retenues,
        quarantine,
        averties,
        int(doublon_exact.sum()),
        int(doublon_id.sum()),
        doublons_probables,
    )
    return pd.concat([propres, avertissements_export]).sort_index()
