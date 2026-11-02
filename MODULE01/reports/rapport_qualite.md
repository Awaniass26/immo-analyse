# Rapport de qualité — ImmoAnalyse

## Vue d'ensemble
- Enregistrements reçus : **3184**
- Mis en quarantaine : **246**
- Écartés (doublons exacts) : **14**
- Retenus : **2924** dont 411 avec avertissement
- Entièrement conformes : **884**
- Taux global de conformité : **27.8 %**
  (entierement conformes (retenus, sans correction ni avertissement) / total des enregistrements recus ; chaque enregistrement compte une fois)
- Enregistrements corrigés : 2089

## Doublons et conflits
- Doublons exacts : 14 (0.48 % des enregistrements hors quarantaine)
- Doublons probables (signalés, non fusionnés) : 4
- Conflits d'identifiants : 0

## Erreurs de conversion
- prix : 8
- surface : 4
- date : 6

## Motifs de quarantaine
| motif_quarantaine                                                   |   nombre |
|:--------------------------------------------------------------------|---------:|
| prix absent, illisible ou <= 0                                      |       90 |
| surface absente, illisible ou <= 0                                  |       82 |
| vente ou location non interprétable                                 |       59 |
| prix absent, illisible ou <= 0; surface absente, illisible ou <= 0  |        6 |
| date absente ou impossible                                          |        6 |
| vente ou location non interprétable; prix absent, illisible ou <= 0 |        2 |
| date future pour une transaction conclue                            |        1 |

## Conformité par règle
Taux = conformes / évaluables x 100. Les valeurs non évaluables sont comptées à part.

| regle                             | gravite       |   conformes |   non_conformes |   non_evaluables |   denominateur_evaluables |   taux_conformite_pct |
|:----------------------------------|:--------------|------------:|----------------:|-----------------:|--------------------------:|----------------------:|
| id_present                        | bloquante     |        3184 |               0 |                0 |                      3184 |                 100   |
| transaction_interpretable         | bloquante     |        3123 |              61 |                0 |                      3184 |                  98.1 |
| prix_valide                       | bloquante     |        3086 |              98 |                0 |                      3184 |                  96.9 |
| surface_valide                    | bloquante     |        3096 |              88 |                0 |                      3184 |                  97.2 |
| date_valide                       | bloquante     |        3178 |               6 |                0 |                      3184 |                  99.8 |
| date_pas_future_si_conclue        | bloquante     |        1848 |               1 |             1335 |                      1849 |                  99.9 |
| type_bien_dans_referentiel        | bloquante     |        3184 |               0 |                0 |                      3184 |                 100   |
| surface_non_atypique              | avertissement |        3096 |               4 |               84 |                      3100 |                  99.9 |
| prix_vente_non_atypique           | avertissement |        2608 |               3 |              573 |                      2611 |                  99.9 |
| loyer_non_atypique                | avertissement |         177 |               0 |             3007 |                       177 |                 100   |
| periodicite_connue                | avertissement |         177 |             266 |             2741 |                       443 |                  40   |
| prix_dans_fourchette_categorie    | avertissement |        2528 |              83 |              573 |                      2611 |                  96.8 |
| surface_dans_fourchette_categorie | avertissement |        3093 |               7 |               84 |                      3100 |                  99.8 |
| ville_connue                      | avertissement |        3176 |               0 |                8 |                      3176 |                 100   |
| region_ville_coherentes           | avertissement |        3172 |               4 |                8 |                      3176 |                  99.9 |
| chambres_non_atypiques            | avertissement |        2309 |               0 |              875 |                      2309 |                 100   |
| sdb_non_atypiques                 | avertissement |        1778 |             121 |             1285 |                      1899 |                  93.6 |
