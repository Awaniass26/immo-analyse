# src/config.py
"""Chemins et constantes du module 2."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ROOT.parent
DATA_ROOT = PROJECT_ROOT / "MODULE01" / "data"
SRC_DIR = DATA_ROOT / "raw"
REF_DIR = DATA_ROOT / "referentiels"
OUT_DIR = ROOT / "sortie"
FIG_DIR = ROOT / "reports" / "figures"
MODELS_DIR = ROOT / "models"
DOCS_DIR = ROOT / "docs"
F_RAPPORT_EDA = ROOT / "reports" / "eda_summary.json"
F_DONNEES_PROPRES = OUT_DIR / "donnees_propres.csv"
F_QUARANTAINE = OUT_DIR / "quarantine.csv"
F_AVERTISSEMENTS = OUT_DIR / "avertissements.csv"
F_RAPPORT_QUALITE = OUT_DIR / "rapport_qualite.md"

for d in (OUT_DIR, FIG_DIR, MODELS_DIR, DOCS_DIR, ROOT / "reports"):
    d.mkdir(parents=True, exist_ok=True)

# Fichiers sources partagés en lecture seule avec le module 1
F_AGENCE = SRC_DIR / "agence_teranga.xlsx"
F_HISTORIQUE = SRC_DIR / "import_historique.csv"
F_NOTAIRE = SRC_DIR / "notaires.csv"
F_PARTICULIER = SRC_DIR / "particuliers.json"
F_PLATEFORME = SRC_DIR / "plateforme_immo_sn.csv"

# Référentiels
F_REF_GEO = REF_DIR / "referentiel_geographique.csv"
F_REF_CAT = REF_DIR / "referentiel_categories.csv"

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