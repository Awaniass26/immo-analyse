# Visualisations et comparaison des prix — Module 1

Les prix bruts sont convertis uniquement pour permettre la comparaison
numérique ; les prix manquants ou illisibles sont exclus des histogrammes et
comptés dans `qualite_valeurs_brutes.csv`. Les graphiques comparent ensuite les
prix avant validation, après mise en quarantaine, puis après retrait des
doublons exacts. Les locations sont limitées aux loyers mensuels : les autres
périodicités ne sont pas comparables entre elles. Les doublons probables sont
signalés par le pipeline, mais ne sont pas fusionnés ni supprimés.

Les histogrammes utilisent une échelle logarithmique pour rendre visibles les
écarts de prix. Les prix au m² sont calculés uniquement sur les ventes ; les
barres d'erreur montrent l'intervalle entre le premier et le troisième quartile.
La règle de 1,5 fois l'écart interquartile sert uniquement à mesurer l'effet des
valeurs extrêmes sur la moyenne ; elle ne supprime aucune ligne. Les données
étant synthétiques, ces résultats ne décrivent pas le marché réel.

## Comparaison des distributions

| etape                 | transaction   | periodicite_location   |   nombre |   moyenne_fcfa |   mediane_fcfa |   q1_fcfa |   q3_fcfa |   minimum_fcfa |   maximum_fcfa |
|:----------------------|:--------------|:-----------------------|---------:|---------------:|---------------:|----------:|----------:|---------------:|---------------:|
| Avant nettoyage       | vente         | sans objet             |     2608 |      104566939 |       74462000 |  39046750 | 129765750 |        5156000 |      567559000 |
| Avant nettoyage       | location      | mensuelle              |      177 |         397288 |         315000 |    190000 |    545000 |          40000 |        1480000 |
| Après validation      | vente         | sans objet             |     2544 |      104455133 |       74555500 |  38814250 | 128819000 |        5156000 |      567559000 |
| Après validation      | location      | mensuelle              |      175 |         395143 |         315000 |    187500 |    542500 |          40000 |        1480000 |
| Après doublons exacts | vente         | sans objet             |     2534 |      104550271 |       74740000 |  38818250 | 129400250 |        5156000 |      567559000 |
| Après doublons exacts | location      | mensuelle              |      171 |         395292 |         315000 |    187500 |    542500 |          40000 |        1480000 |

## Valeurs manquantes, conversions et valeurs extrêmes

| source       | champ   |   total |   manquants |   non_convertibles |   convertibles |   valeurs_non_positives |
|:-------------|:--------|--------:|------------:|-------------------:|---------------:|------------------------:|
| agence       | prix    |     640 |           0 |                  0 |            640 |                       5 |
| agence       | surface |     640 |           0 |                  0 |            640 |                       4 |
| historique   | prix    |     528 |          10 |                  0 |            518 |                       0 |
| historique   | surface |     528 |           0 |                  0 |            528 |                       0 |
| notaires     | prix    |     410 |          14 |                  0 |            396 |                       0 |
| notaires     | surface |     410 |           0 |                  0 |            410 |                       0 |
| particuliers | prix    |     731 |          61 |                  2 |            668 |                       0 |
| particuliers | surface |     731 |          75 |                  4 |            652 |                       0 |
| plateforme   | prix    |     875 |           0 |                  6 |            869 |                       0 |
| plateforme   | surface |     875 |           5 |                  0 |            870 |                       0 |

| etape                 | transaction   |   nombre |   nombre_valeurs_extremes_iqr |   moyenne_fcfa |   mediane_fcfa |   moyenne_sans_extremes_fcfa |   mediane_sans_extremes_fcfa |
|:----------------------|:--------------|---------:|------------------------------:|---------------:|---------------:|-----------------------------:|-----------------------------:|
| Avant nettoyage       | vente         |     2608 |                           230 |      104566939 |       74462000 |                     79662621 |                     67494000 |
| Avant nettoyage       | location      |      177 |                             8 |         397288 |         315000 |                       355828 |                       310000 |
| Après validation      | vente         |     2544 |                           227 |      104455133 |       74555500 |                     79329354 |                     66722000 |
| Après validation      | location      |      175 |                             8 |         395143 |         315000 |                       353084 |                       305000 |
| Après doublons exacts | vente         |     2534 |                           227 |      104550271 |       74740000 |                     79324943 |                     66740000 |
| Après doublons exacts | location      |      171 |                             8 |         395292 |         315000 |                       352209 |                       305000 |

## Figures

- [Distribution des prix de vente et des loyers mensuels](./figures/distribution_prix_vente_location.png)
- [Effet du retrait des doublons exacts](./figures/impact_dedoublonnage_prix_vente.png)
- [Sensibilité de la moyenne aux valeurs extrêmes](./figures/sensibilite_valeurs_extremes.png)
- [Prix au m² par type de bien](./figures/prix_m2_par_type.png)
- [Prix au m² par ville](./figures/prix_m2_par_ville.png)

Les valeurs détaillées sont également disponibles dans les fichiers `comparaison_distributions_prix.csv`, `qualite_valeurs_brutes.csv` et `sensibilite_valeurs_extremes.csv`.
