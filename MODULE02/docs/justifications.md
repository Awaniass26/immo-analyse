# Décisions et consignes de préparation — ImmoAnalyse

Ce document explique les choix du module 2 et indique où vérifier les résultats.
Les mesures de référence viennent des données synthétiques actuellement
présentes dans `MODULE01/data/processed/donnees_propres.csv`. Elles changent si
les données ou les règles de nettoyage changent.

## 1. Contrat entre les modules

Le module 1 est l'unique étape qui lit les sources brutes et qui applique le
nettoyage et les règles qualité. Le module 2 charge son export propre, adapte
les noms de colonnes à son vocabulaire d'analyse, puis travaille sur ce même
jeu. Cela évite de produire deux versions contradictoires des données.

## 2. Distribution des prix et EDA

- Comparer l'asymétrie de `prix` et de `log(prix)` avec
  `stats_eda.comparer_prix_log`.
- Examiner les relations prix/surface globalement et par catégorie avant
  d'interpréter une corrélation agrégée (risque de paradoxe de Simpson).
- Examiner la tendance des prix médians annuels avec le test de Mann-Kendall.
- Les six graphiques sont écrits dans `MODULE02/reports/figures/`.
- Les valeurs calculées sont consignées dans `MODULE02/reports/eda_summary.json`.

Sur le jeu actuel, l'asymétrie passe de `1.893` pour le prix brut à `-1.522`
pour `log(prix)`. La valeur absolue diminue, mais la distribution transformée
reste asymétrique : le logarithme ne rend pas les prix normalement distribués.
Cette transformation reste la cible pédagogique initiale ; elle devra être
comparée à une cible non transformée lors de l'évaluation des modèles.

La corrélation de Spearman prix/surface vaut `0.318` globalement, alors que les
corrélations par catégorie sont proches de zéro ou négatives (de `-0.100` à
`0.018`). L'association globale ne décrit donc pas correctement chaque
catégorie. C'est un signal de confusion par catégorie, pas une preuve à elle
seule d'un paradoxe de Simpson strict.

Avec la version actuelle des données, Mann-Kendall donne `p = 0.4767` : aucune
tendance temporelle significative n'est détectée au seuil de 5 %. Le script
choisit donc le split aléatoire. Ce résultat décrit ce jeu synthétique, il ne
prouve pas l'absence de tendance dans un futur jeu réel.

## 2.1 Résultats qualité du module 1

Le rapport qualité de référence indique 3 184 lignes reçues, 246 en
quarantaine, 14 doublons exacts écartés et 2 924 lignes retenues, dont 411 avec
avertissement. Le taux de conformité complète est de 27,8 %. Il mesure les
lignes sans correction ni avertissement par rapport au total reçu : ce n'est
pas le taux de lignes conservées.

## 3. Split train / validation / test

- Répartition visée : 70 % / 15 % / 15 %.
- Si le test de tendance est significatif (`p < 0.05`), le split est
  chronologique afin que validation et test soient postérieurs à train.
- Sinon, le split est aléatoire avec `random_state = 42` pour être reproductible.
- Si le test ne peut pas être calculé faute d'années suffisantes, le script
  utilise le split aléatoire ; cette limite doit être mentionnée dans l'analyse.
- Les sorties sont `prepared_train.csv`, `prepared_validation.csv` et
  `prepared_test.csv` dans `MODULE02/sortie/`.
- Sur le jeu courant, cela donne respectivement 2 046, 439 et 439 lignes.

Le découpage est effectué avant l'ajustement des transformations. Aucune
information de validation ou de test ne sert à apprendre une médiane, une
modalité ou une échelle.

## 4. Choix des features et prévention des fuites

| Variable | Décision | Justification |
|---|---|---|
| `type_transaction`, `categorie`, `region` | Conservées | Informations disponibles au moment de l'estimation. |
| `surface_log` | Conservée | Transformation de `surface` pour réduire l'influence des grandes surfaces. |
| `prix` | Cible uniquement | La cible ne doit jamais être incluse dans les entrées. |
| `prix_log` | Cible exportée uniquement | Le logarithme du prix est la variable à prédire, pas une feature. |
| `prix_m2`, ratios calculés à partir du prix | Exclus | Ils contiennent directement la cible : fuite de type 1. |
| `statut` | Exclu | Peut être connu après la mise en vente ou la transaction : fuite temporelle. |
| `source`, `id_local` | Métadonnées uniquement | Identifient la provenance ou la ligne, et ne généralisent pas comme attributs du bien. |
| `commune`, `quartier`, `description`, `date_expiration` | Exclues du premier pipeline | Variables très cardinales, textuelles ou indisponibles au moment de la prédiction ; à réévaluer avec une validation dédiée. |

Le choix d'exclure une variable doit être réexaminé pour chaque cas d'usage :
la disponibilité réelle de la donnée au moment de la prédiction est le critère
central.

## 5. Prétraitement réutilisable

`pipeline.py` applique :

1. Imputation des catégories par la modalité la plus fréquente.
2. One-hot encoding avec tolérance aux catégories inconnues.
3. Imputation numérique par la médiane.
4. Standardisation de `surface_log`.

Le pipeline sklearn est ajusté uniquement sur train, enregistré sous
`MODULE02/models/pipeline_preparation.joblib`, puis appliqué séparément aux
trois ensembles. Le module 2 prépare les données ; il n'entraîne pas encore de
modèle prédictif. L'entraînement, le choix des métriques et l'évaluation
relèvent des modules suivants.

## 6. Reproduction et contrôle

À la racine du dépôt :

```powershell
python run_project.py
python -m pytest -q
```

Le premier script exécute les modules dans l'ordre et actualise les rapports,
les figures, les ensembles préparés et le pipeline sérialisé.
