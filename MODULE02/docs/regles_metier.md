# Règles métier — Module 2 ImmoAnalyse

Ces règles sont appliquées par le pipeline du module 2 aux cinq sources brutes
partagées en lecture seule avec le module 1. Les livrables du module 2 sont
écrits dans `MODULE02/sortie/`.

## Règles bloquantes

Une ligne est mise en quarantaine si son identifiant est absent, si son prix ou
sa surface est manquant/illisible/non positif, si sa date est impossible, si
la transaction ou le type de bien ne peut pas être interprété, ou si une date
future est associée à une transaction conclue.

## Corrections autorisées

Les corrections doivent être déterministes et traçables : normalisation de la
casse et des espaces, conversion documentée des séparateurs numériques,
normalisation des synonymes présents dans les référentiels et interprétation
des dates selon le format explicite de la source. Une valeur ambiguë n'est pas
devinée.

## Avertissements

Les valeurs atypiques, les incohérences géographiques, les périodicités
inconnues et les doublons probables sont signalés mais ne sont pas supprimés
automatiquement. Un doublon probable n'est pas fusionné sans preuve.

## Indicateurs à communiquer

- Valeurs manquantes et erreurs de conversion par champ.
- Doublons exacts écartés et doublons probables signalés.
- Lignes corrigées, mises en quarantaine et conservées avec avertissement.
- Taux de conformité et dénominateur utilisé pour le calcul.
