# Préprocesseur réutilisable — Module 2

## Entrée et sortie

Le pipeline complet lit les cinq fichiers bruts définis dans
`MODULE02/src/config.py`, ainsi que les deux référentiels. Les fichiers sources
et référentiels sont partagés avec le module 1 et ne sont jamais modifiés.
Les données nettoyées et les jeux train/validation/test sont produits dans
`MODULE02/sortie/`.

## Étapes

1. Charger séparément Excel, CSV et JSON, puis aligner le schéma.
2. Normaliser les nombres, dates, catégories et noms géographiques.
3. Séparer les lignes bloquantes, conserver les avertissements et traiter les
   doublons avant le split.
4. Explorer et exporter les rapports et figures.
5. Séparer les ensembles avec la graine `42` ; le split aléatoire est stratifié
   par catégorie.
6. Calculer `surface_log` et construire la cible `prix_log`.
7. Ajuster l'imputation, le one-hot encoding et le scaler sur train seulement.
8. Transformer et exporter train, validation et test.

## Sérialiser, recharger et appliquer

Depuis la racine du dépôt :

```python
import joblib

pipeline = joblib.load(
    "MODULE02/models/pipeline_preparation.joblib"
)
matrice = pipeline.transform(features_alignees)
```

Le fichier `.joblib` stocke cet objet de prétraitement, pas un estimateur de
prix ni un modèle prédictif entraîné. `features_alignees` doit contenir
`type_transaction`, `categorie`, `region`
et `surface_log`. L'alignement d'une annonce brute à ce schéma est effectué
par les chargeurs et le nettoyage du module 2 avant l'application du
préprocesseur.

Les estimateurs utilisés pour comparer les candidates par validation croisée
sont temporaires : ils ne sont pas enregistrés dans le fichier `.joblib`.
L'entraînement final d'un modèle prédictif appartient à un module ultérieur.

## Vérifications automatiques

- Le pipeline sérialisé est rechargé et testé sur une ligne propre de chaque
  source ; les cinq contrôles sont consignés dans `reports/pipeline_checks.json`.
- Les identifiants sont vérifiés entre les trois ensembles dans
  `reports/split_summary.json`.
- Les paramètres du préprocesseur sont appris sur train uniquement.
- Les catégories inconnues sont ignorées par `OneHotEncoder` plutôt que de
  faire échouer la transformation.
