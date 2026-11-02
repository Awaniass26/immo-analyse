"""Réglages du projet : chemins, listes autorisées et seuils.

Tous les seuils sont ici (et nulle part ailleurs dans le code),
pour pouvoir les modifier sans toucher aux fonctions de traitement.
"""

from pathlib import Path

# --- Chemins -------------------------------------------------------------
RACINE = Path(__file__).resolve().parent.parent
DOSSIER_BRUT = RACINE / "data" / "raw"
DOSSIER_REFERENTIELS = RACINE / "data" / "referentiels"
DOSSIER_PROPRE = RACINE / "data" / "processed"
DOSSIER_QUARANTAINE = RACINE / "data" / "quarantine"
DOSSIER_RAPPORTS = RACINE / "reports"

# --- Listes autorisées ---------------------------------------------------
TYPES_TRANSACTION = ["vente", "location"]

SOURCES_VENTES = ["notaires", "historique"]

TYPES_BIEN = [
    "Appartement", "Studio", "Chambre", "Villa",
    "Maison", "Terrain", "Local commercial",
]

PERIODICITES = ["mensuel", "trimestriel", "semestriel", "annuel"]

# --- Seuils (source : regles_metier.md) ----------------------------------
# Valeurs atypiques : on conserve la ligne et on signale (pas de suppression)
SURFACE_ATYPIQUE_MIN = 5
SURFACE_ATYPIQUE_MAX = 2_000
PRIX_ATYPIQUE_MIN = 100_000
PRIX_ATYPIQUE_MAX = 2_000_000_000

LOYER_MIN = 25_000
LOYER_MAX = 5_000_000

CHAMBRES_MAX_APPARTEMENT = 10


# --- Décisions de traitement (à justifier dans le README) ----------------
# Sources dont toutes les lignes sont des ventes (actes notariés, ventes passées)

# Statuts qui indiquent qu'une transaction est conclue
STATUTS_VENTE_CONCLUE = ["vendu", "vente conclue", "acte signe"]

# Doublons probables : tolérances de rapprochement
TOLERANCE_SURFACE = 0.02       # 2 % d'écart maximum
TOLERANCE_PRIX = 0.05          # 5 % d'écart maximum
TOLERANCE_DATE_JOURS = 30      # 30 jours d'écart maximum
SEUIL_DOUBLON_PROBABLE = 0.75  # part minimale de critères qui se ressemblent
