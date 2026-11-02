# ImmoAnalyse

Projet fil rouge de data science sur des annonces immobilières synthétiques
inspirées du contexte sénégalais. Le but est de suivre une chaîne complète et
reproductible : des fichiers bruts jusqu'à un jeu de données préparé pour un
futur modèle de Machine Learning.

> Les données sont synthétiques : elles ne représentent pas des transactions
> réelles et ne permettent pas d'estimer les prix du marché.

## Parcours du projet

Le projet est **un seul dépôt composé de modules successifs**, pas deux projets
indépendants.

1. **Module 1 — Bases Python et qualité des données** : charge les cinq formats
   de sources, harmonise les colonnes, nettoie et valide les valeurs, met les
   lignes bloquantes en quarantaine, repère les doublons, puis exporte le jeu
   propre et les rapports qualité.
2. **Module 2 — Analyse et préparation** : lit le jeu propre du module 1 (sans
   relire ni recopier les sources), explore les distributions et relations,
   produit des graphiques, sépare train/validation/test, puis ajuste un pipeline
   sklearn de préparation uniquement sur train.
3. **Modules suivants** : réutiliseront les ensembles préparés et le pipeline
   sérialisé pour entraîner, évaluer, améliorer et déployer des modèles.

Le point de passage entre les deux premiers modules est
`MODULE01/data/processed/donnees_propres.csv`. Les sources et référentiels
canoniques sont stockés une seule fois dans `MODULE01/data/`.

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
  src/                   lecture du résultat module 1, EDA, features, pipeline
  sortie/                ensembles préparés train/validation/test
  tests/                 tests unitaires du module 2
run_project.py            lance le module 1 puis le module 2
```

Les scripts et notebooks du module 2 pointent vers les sources et référentiels
du module 1. Ne crée pas une deuxième copie des mêmes fichiers dans `MODULE02`.

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

Le module 2 nécessite d'abord la sortie du module 1. Pour relancer seulement
l'analyse, vérifie que `MODULE01/data/processed/donnees_propres.csv` existe et
correspond aux données courantes.

Ouvrir les notebooks depuis la racine du dépôt :

```powershell
jupyter notebook
```

Puis ouvrir `MODULE01/notebooks/01_exploration.ipynb` ou
`MODULE02/notebooks/02_preparation_analyse.ipynb`.

## Sorties principales

- Module 1 : `MODULE01/data/processed/`, `MODULE01/data/quarantine/` et
  `MODULE01/reports/`.
- Module 2 : `MODULE02/reports/figures/`, `MODULE02/reports/eda_summary.json`,
  `MODULE02/sortie/prepared_train.csv`,
  `MODULE02/sortie/prepared_validation.csv`,
  `MODULE02/sortie/prepared_test.csv` et
  `MODULE02/models/pipeline_preparation.joblib`.

Les CSV préparés incluent `prix_log` comme cible, mais cette cible n'est pas une
feature d'entrée. `source` et `id_local` sont conservés comme métadonnées de
traçabilité, pas comme variables d'entraînement.

## Décisions de préparation

- Les lignes invalides selon les règles bloquantes sont isolées au module 1 ;
  les avertissements sont conservés et signalés.
- Les données propres sont le seul contrat d'entrée du module 2 : le module 2
  ne refait pas un second nettoyage divergent.
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
