# src/config.py
"""Chemins et constantes globales du projet."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ROOT.parent
MODULE01_ROOT = PROJECT_ROOT / "MODULE01"

SRC_DIR = MODULE01_ROOT / "data" / "raw"
REF_DIR = MODULE01_ROOT / "data" / "referentiels"
OUT_DIR = ROOT / "sortie"
FIG_DIR = ROOT / "reports" / "figures"
MODELS_DIR = ROOT / "models"
DOCS_DIR = ROOT / "docs"
F_DONNEES_MODULE01 = MODULE01_ROOT / "data" / "processed" / "donnees_propres.csv"
F_RAPPORT_EDA = ROOT / "reports" / "eda_summary.json"

for d in (OUT_DIR, FIG_DIR, MODELS_DIR, DOCS_DIR, ROOT / "reports"):
    d.mkdir(parents=True, exist_ok=True)

# Fichiers sources (⚠️ jamais modifier)
F_AGENCE     = SRC_DIR / "agence_teranga.xlsx"
F_HISTORIQUE = SRC_DIR / "import_historique.csv"
F_NOTAIRE    = SRC_DIR / "notaires.csv"
F_PARTICULIER= SRC_DIR / "particuliers.json"
F_PLATEFORME = SRC_DIR / "plateforme_immo_sn.csv"

# Référentiels
F_REF_GEO   = REF_DIR / "referentiel_geographique.csv"
F_REF_CAT   = REF_DIR / "referentiel_categories.csv"

# Sorties
F_PROPRE      = OUT_DIR / "donnees_propres.csv"
F_QUARANTAINE = OUT_DIR / "quarantaine.csv"
F_AVERT       = OUT_DIR / "avertissements.csv"
F_RAPPORT     = OUT_DIR / "rapport_qualite.md"

# Reproductibilité
RANDOM_STATE = 42

# Mapping des sources vers un schéma commun cible
SCHEMA_CIBLE = [
    "id", "source", "date", "type_transaction", "categorie",
    "region", "commune", "prix", "surface", "chambres", "sdb", "statut"
]

# Fourchettes acceptées (référentiel catégoriel)
PRIX_MIN_FOURCHETTE = 100_000
PRIX_MAX_FOURCHETTE = 2_000_000_000
SURF_MIN_FOURCHETTE = 5
SURF_MAX_FOURCHETTE = 2_000