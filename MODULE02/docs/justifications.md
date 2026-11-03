# Décisions et résultats — Module 2

Les chiffres ci-dessous sont produits par `python -m MODULE02.src.run_pipeline`
à partir des cinq sources brutes et des référentiels en lecture seule. Les
sorties propres du module 1 ne sont pas utilisées.

## 1. Séparation des modules

Le module 2 possède ses propres chargeurs, règles de nettoyage, rapports,
figures, split et pipeline. Il lit les fichiers canoniques dans
`MODULE01/data/raw/` et `MODULE01/data/referentiels/` sans les modifier. Il ne
importe aucune fonction du module 1 et peut être exécuté seul.

## 2. Nettoyage et qualité

Le détail actualisé est dans `MODULE02/sortie/rapport_qualite.md`.

- Les valeurs qui ne peuvent pas être converties de manière fiable sont mises
  en quarantaine ; une valeur incertaine n'est pas devinée.
- Les dates `JJ/MM/AAAA`, les nombres avec séparateurs explicites, les suffixes
  `FCFA`/`millions`, les synonymes de catégories et les noms géographiques
  reconnus sont normalisés.
- Les prix ou surfaces non positifs, les dates impossibles, les identifiants
  absents, les transactions ambiguës et les dates futures de transactions
  conclues sont bloquants.
- Les valeurs extrêmes et les incohérences géographiques sont conservées avec
  avertissement.
- Les doublons exacts et les identifiants répétés dans une même source sont
  écartés avant le split. Les doublons probables entre sources ne sont jamais
  fusionnés automatiquement.

## 3. Exploration

Le rapport `MODULE02/reports/eda_summary.json` contient les asymétries, les
corrélations, les tests et la tendance temporelle. Les statistiques par source
sont dans `stats_descriptives_par_source.csv` et les types/manquants dans
`types_par_source.csv`.

Les figures V1 à V6 sont dans `MODULE02/reports/figures/`. Elles couvrent la
distribution du prix, le prix par catégorie, l'association prix/surface,
les corrélations numériques, le bilan du nettoyage et la comparaison des
sources. Les associations globales et par catégorie sont interprétées comme
des corrélations, pas comme des relations causales.

Le test de Mann-Kendall porte sur le prix médian par année. Le split
chronologique est choisi si `p < 0,05`; sinon, le split aléatoire stratifié par
catégorie utilise la graine 42. Une tendance non significative n'est pas une
preuve d'absence de tendance dans d'autres données.

## 4. Features et prévention des fuites

Le pipeline final utilise `type_transaction`, `categorie`, `region` et
`surface_log`. Le prix n'est jamais une entrée du pipeline : la cible est
`log(prix)`. `statut`, `source`, `id_local`, `commune` et les colonnes propres à
une seule source ne sont pas utilisées comme features.

`reports/feature_cv.csv` compare en validation croisée sur le train la
catégorie de base à `region`, `surface_log`, `annee`, `source` et `prix_m2`.
Le résultat est calculé sur ce jeu synthétique et ne constitue pas un score de
production. `source` est testée à titre pédagogique, puis exclue parce qu'elle
représente le flux de collecte. `prix_m2` est calculé à partir de la cible et
est exclu même si son score est élevé. `reports/leakage_check.json` confirme
numériquement l'identité
`log(prix_m2) + log(surface) = log(prix)`.

## 5. Split et réutilisation

Le résumé par source et catégorie est dans `reports/split_summary.json`.
L'intersection des identifiants entre les ensembles est vérifiée avant
l'export ; le test est réservé à l'évaluation finale et n'est pas utilisé pour
la comparaison des features. La graine du split est `42`.

Les transformations apprises (imputation, one-hot encoding et standardisation)
sont ajustées uniquement sur le train. Le préprocesseur est sérialisé dans
`MODULE02/models/pipeline_preparation.joblib`, rechargé puis essayé sur une
ligne de chacune des cinq sources. Ce fichier ne contient pas de modèle
prédictif entraîné ; les modèles de validation croisée sont temporaires. Les
résultats sont dans
`reports/pipeline_checks.json`; sa structure détaillée est décrite dans
[`pipeline.md`](./pipeline.md).
