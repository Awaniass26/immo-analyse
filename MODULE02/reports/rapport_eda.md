# Résultats EDA et figures de restitution

1. **V1 — Distribution de la cible.** Le skew passe de 1.893 à -1.518 après logarithme. Shapiro-Wilk sur n=2928 donne p=3.38e-50; la normalité n'est donc pas retenue.

![V1 — Distribution de la cible](figures/01_distribution_prix.png)

2. **V2 — Prix par catégorie.** Le ratio des médianes de catégorie extrêmes est 22.23. Les boîtes utilisent une échelle logarithmique.

![V2 — Prix par catégorie](figures/02_prix_par_categorie.png)

3. **V3 — Prix et surface.** Spearman global = 0.319; moyenne des corrélations par catégorie = -0.034. Ces statistiques indiquent une hétérogénéité entre groupes, pas une preuve suffisante d'un paradoxe de Simpson strict.

![V3 — Prix et surface par catégorie](figures/03_prix_surface_categories.png)

4. **V4 — Corrélations numériques.** Aucune paire ne dépasse |r| = 0,8.

![V4 — Matrice de corrélation](figures/04_matrice_correlation.png)

5. **V5 — Nettoyage.** 3184 lignes reçues, 2928 conservées et 256 mises en quarantaine. 490 lignes conservées portent au moins un avertissement.

![V5 — Bilan du nettoyage](figures/05_preuve_nettoyage.png)

6. **V6 — Comparaison des sources.** Les médianes et effectifs présentés dans les figures sont :

![V6 — Comparaison des sources](figures/06_comparaison_sources.png)

| source       |   nombre |   mediane_prix |   mediane_surface |
|:-------------|---------:|---------------:|------------------:|
| agence       |      572 |    7.2129e+07  |            155    |
| historique   |      518 |    6.764e+07   |            135.45 |
| notaires     |      390 |    8.08575e+07 |            155.05 |
| particuliers |      599 |    4.2447e+07  |            145.1  |
| plateforme   |      849 |    5.7903e+07  |            145.6  |

Les graphiques soutiennent l'exploration du corpus synthétique et ne permettent pas d'inférer des prix de marché réels.
