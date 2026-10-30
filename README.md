# ImmoAnalyse

Pipeline Python qui importe 5 sources immobilières hétérogènes (CSV, Excel, JSON),
contrôle leur qualité, corrige ce qui est sûr, met le reste en quarantaine et
produit des données propres avec un rapport de qualité chiffré.

> Données **synthétiques** inspirées du contexte sénégalais. Elles ne représentent
> pas des transactions réelles et ne servent pas à estimer les prix du marché.

## Installation

```bash
python -m venv .venv
# Windows : .venv\Scripts\activate      Mac/Linux : source .venv/bin/activate
pip install -r requirements.txt
```

Placer les 5 fichiers sources dans `data/raw/` et les 3 référentiels dans
`data/referentiels/`. Les fichiers sources ne sont **jamais modifiés**.

## Exécution

```bash
python -m src.main      # lance tout le pipeline
python -m pytest        # lance les tests
jupyter notebook        # puis ouvrir notebooks/01_exploration.ipynb
```

## Structure

| Dossier / fichier | Rôle |
|---|---|
| `src/config.py` | chemins, listes autorisées, seuils (aucun seuil dans le code) |
| `src/loaders/` | lecture des 5 sources, noms de colonnes communs, provenance |
| `src/processing/` | conversion des prix, surfaces, dates, catégories, doublons |
| `src/validation/` | règles métier (classe `RegleValidation`) |
| `src/analysis/` | indicateurs de qualité, rapports, statistiques |
| `src/export.py` | fichiers de sortie |
| `data/processed/` | `donnees_propres.csv` et `.json` |
| `data/quarantine/` | `quarantaine.csv` (avec motif), `doublons_ecartes.csv` |
| `reports/` | `quality_report.json`, `quality_summary.csv`, `rapport_qualite.md` |
| `tests/` | 54 tests (cas conformes, invalides et limites) |

## Déroulement du pipeline

1. Chargement des 5 sources (tout en texte, aucune perte).
2. Nettoyage : colonnes propres + un état par champ (`ok`, `corrige`, `erreur`, `manquant`).
3. Validation : 17 règles (7 bloquantes, 10 avertissements).
4. Quarantaine des lignes qui violent une règle bloquante, avec motif.
5. Doublons exacts (écartés), doublons probables (signalés), conflits d'identifiants.
6. Indicateurs, rapports, exports et statistiques.

## Règles métier

- **Bloquantes (quarantaine)** : identifiant absent, vente/location non interprétable,
  prix absent ou ≤ 0, surface absente ou ≤ 0, date absente ou impossible,
  date future pour une transaction conclue, type de bien hors référentiel.
- **Avertissements (on garde et on signale)** : surface ou prix atypique, loyer atypique,
  périodicité inconnue, hors fourchette du type de bien, ville inconnue, ville et région
  incompatibles, trop de chambres, salles de bain > chambres + 2.
- Les seuils sont dans `src/config.py`.

## Décisions et justifications

(À réécrire avec tes mots, une fois les points 3 à 8 compris.)

1. **Notaires et historique = ventes.** Ces sources n'ont pas de colonne vente/location ;
   un acte notarié et une `DateVente` correspondent à une vente conclue.
2. **Statut `Disponible` (agence) en quarantaine.** Il ne dit pas s'il s'agit d'une vente
   ou d'une location, et le cahier interdit de deviner. `Loué` donne location ;
   `Vendu` et `En vente` donnent vente.
3. **Dates avec `/` lues JJ/MM/AAAA.** Les sources sont francophones ; la convention est
   documentée et ces dates sont marquées `corrige`.
4. **`1,250` est ambigu.** Une virgule suivie de trois chiffres peut être un séparateur de
   milliers ou une décimale : la surface est marquée `ambigu` et envoyée en quarantaine.
   Une virgule suivie d'un ou deux chiffres (`102,6`) est lue comme décimale.
5. **Valeurs illisibles non devinées.** `à négocier`, `quatre-vingt` et `None FCFA`
   donnent `erreur` et non un chiffre inventé.
6. **Loyers sans périodicité.** Seule la plateforme indique `FCFA/mois`. Pour les autres
   locations, la périodicité reste inconnue (avertissement) et la règle sur les loyers
   est « non évaluable ».
7. **Doublons exacts écartés, doublons probables seulement signalés.** Critères : même
   ville, même type, même transaction, sources différentes, surface à 2 % et prix à 5 %
   près, score de similarité ≥ 0,75. Rien n'est fusionné sans preuve.
8. **Données brutes préservées.** Les colonnes d'origine restent à côté des colonnes propres.
9. **Les prix de vente sont des prix demandés** (annonces), pas des prix de transaction.

## Résultats (dernier lancement)

| Indicateur | Valeur |
|---|---|
| Enregistrements reçus | 3184 |
| En quarantaine | 246 |
| Doublons exacts écartés | 14 |
| Retenus | 2924 |
| Entièrement conformes | 884 |
| Taux global de conformité | 27,8 % |

Le taux global = entièrement conformes / reçus ; une ligne corrigée n'est pas
« entièrement conforme ». Détail complet dans `reports/rapport_qualite.md`.

## Limites

- Données synthétiques, seuils pédagogiques et non officiels.
- Doublons probables : seuils à calibrer sur des cas réels.
- Périodicité des loyers inconnue pour la majorité des locations.
- Le prix au m² n'est calculé que sur les ventes.