# ImmoAnalyse

Projet fil rouge de data science sur des annonces immobilières synthétiques
inspirées du contexte sénégalais. Le but est de suivre une chaîne complète et
reproductible : des fichiers bruts jusqu'à un jeu de données préparé pour un
futur modèle de Machine Learning.

> Les données sont synthétiques : elles ne représentent pas des transactions
> réelles et ne permettent pas d'estimer les prix du marché.

## Parcours du projet

Le dépôt contient des modules distincts qui partagent les mêmes fichiers bruts
et référentiels en lecture seule.

1. **Module 1 — Bases Python et qualité des données** : charge les cinq formats
   de sources, harmonise les colonnes, nettoie et valide les valeurs, met les
   lignes bloquantes en quarantaine, repère les doublons, puis exporte le jeu
   propre et les rapports qualité.
2. **Module 2 — Analyse et préparation** : relit directement les cinq sources
   brutes, applique ses propres règles et produit ses propres données propres,
   quarantaines et rapports. Il n'importe pas le code du module 1 et ne dépend
   pas de ses sorties.
3. **Modules suivants** : réutiliseront les ensembles préparés et le pipeline
   sérialisé pour entraîner, évaluer, améliorer et déployer des modèles.

Les sources et référentiels canoniques sont stockés une seule fois dans
`MODULE01/data/`. Le module 2 les lit sans les modifier ; ses résultats restent
dans `MODULE02/`.

## Structure

```text
MODULE01/
  data/                 sources, référentiels, données propres et quarantaine
  notebooks/            exploration du module 1
  reports/               rapports de qualité
  src/                   chargement, nettoyage, validation, analyse, exports
  tests/                 tests unitaires du module 1
MODULE02/
  docs/                  décisions et règles métier
  models/                pipeline de préparation sérialisé
  notebooks/             exploration et préparation du module 2
  reports/               figures et résumé EDA
  src/                   chargement brut, nettoyage autonome, EDA et pipeline
  sortie/                données propres, quarantaine, rapports et ensembles
  tests/                 tests unitaires du module 2
run_project.py            lance le module 1 puis le module 2
```

Les scripts et notebooks du module 2 lisent les sources et référentiels
canoniques de `MODULE01/data/`. Ne lance pas le module 1 comme prérequis du
module 2 et ne modifie pas ces fichiers d'entrée.

## Installation (Windows PowerShell)

Depuis la racine du dépôt :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Exécution

Lancer toute la chaîne dans le bon ordre :

```powershell
python run_project.py
```

Lancer une étape séparément :

```powershell
python -m MODULE01.src.main
python -m MODULE02.src.run_pipeline
```

Le module 2 peut être lancé seul. Il a besoin des fichiers sources bruts et
référentiels présents dans `MODULE01/data/`, mais pas de la sortie du module 1.

Ouvrir les notebooks depuis la racine du dépôt :

```powershell
jupyter notebook
```

Puis ouvrir `MODULE01/notebooks/01_exploration.ipynb` ou
`MODULE02/notebooks/02_preparation_analyse.ipynb`.

## Sorties principales

- Module 1 : `MODULE01/data/processed/`, `MODULE01/data/quarantine/` et
  `MODULE01/reports/`.
- Module 2 : `MODULE02/sortie/donnees_propres.csv`,
  `MODULE02/sortie/quarantine.csv`,
  `MODULE02/sortie/avertissements.csv`,
  `MODULE02/sortie/rapport_qualite.md`,
  `MODULE02/reports/figures/`, `MODULE02/reports/eda_summary.json`,
  `MODULE02/reports/rapport_eda.md` et `MODULE02/reports/feature_cv.csv`,
  `MODULE02/sortie/prepared_train.csv`,
  `MODULE02/sortie/prepared_validation.csv`,
  `MODULE02/sortie/prepared_test.csv` et
  `MODULE02/models/pipeline_preparation.joblib`.

Les CSV préparés incluent `prix_log` comme cible, mais cette cible n'est pas une
feature d'entrée. `source` et `id_local` sont conservés comme métadonnées de
traçabilité, pas comme variables d'entraînement.

Le fichier `pipeline_preparation.joblib` contient uniquement le préprocesseur
scikit-learn ajusté sur train (imputation, encodage et standardisation). Il ne
contient pas de modèle prédictif entraîné ; cette étape appartient à un module
ultérieur.

## Décisions de préparation

- Le module 1 et le module 2 nettoient indépendamment les mêmes sources ; leurs
  sorties et leurs rapports ne se remplacent pas.
- Dans le module 2, les lignes bloquantes sont exportées en quarantaine et les
  anomalies non bloquantes sont conservées avec un avertissement.
- La cible explorée est `log(prix)` afin de réduire l'asymétrie potentielle des
  prix. Les métriques mesurées sont enregistrées dans le rapport EDA.
- Le test de tendance de Mann-Kendall choisit le split : split chronologique si
  `p < 0,05`, sinon split aléatoire reproductible (graine 42). Le ratio visé est
  70/15/15.
- L'imputation, le one-hot encoding et la standardisation sont ajustés sur
  train seulement. Validation et test ne servent pas à apprendre les
  paramètres du préprocesseur.
- `prix_m2`, les statuts postérieurs à l'observation et les identifiants de
  source ne sont pas utilisés comme features ; ils risquent de créer une fuite
  ou un signal artificiel.

Les justifications détaillées et les résultats de référence sont dans
`MODULE02/docs/justifications.md`.

## Vérification

```powershell
python -m pytest -q
```
