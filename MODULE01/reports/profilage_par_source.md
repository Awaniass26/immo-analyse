# Profilage par source

Pour chaque source : volume, colonnes présentes, valeurs manquantes, doublons exacts, erreurs de conversion et distributions.

## Source : agence

- Lignes : **640**
- Colonnes absentes de cette source : type_transaction, quartier, devise, pieces
- Doublons exacts (colonnes brutes) : 0
- Erreurs de conversion : {'prix': 0, 'surface': 0, 'date': 0}

**Valeurs manquantes (colonnes présentes)**

|             |   manquants |   taux_pct |
|:------------|------------:|-----------:|
| id_local    |           0 |          0 |
| date        |           0 |          0 |
| type_bien   |           0 |          0 |
| region      |           0 |          0 |
| ville       |           0 |          0 |
| prix        |           0 |          0 |
| surface     |           0 |          0 |
| chambres    |           0 |          0 |
| salles_bain |           0 |          0 |
| statut      |           0 |          0 |

**Distribution du prix et de la surface (après conversion)**

|         |   prix_nombre |   surface_nombre |
|:--------|--------------:|-----------------:|
| nombre  | 640           |            640   |
| moyenne |   9.0903e+07  |            238   |
| minimum |   0           |            -30   |
| mediane |   6.4513e+07  |            154.8 |
| maximum |   5.36187e+08 |           1489.5 |

**Types de bien**

| type_bien_ref    |   count |
|:-----------------|--------:|
| Appartement      |     179 |
| Maison           |     149 |
| Villa            |     123 |
| Terrain          |      96 |
| Studio           |      67 |
| Chambre          |      17 |
| Local commercial |       9 |

**Villes principales**

| ville_ref   |   count |
|:------------|--------:|
| Koungheul   |      28 |
| Ourossogui  |      25 |
| Bounkiling  |      21 |
| Ziguinchor  |      20 |
| Guinguinéo  |      20 |

## Source : historique

- Lignes : **528**
- Colonnes absentes de cette source : type_transaction, quartier, devise, pieces, statut
- Doublons exacts (colonnes brutes) : 0
- Erreurs de conversion : {'prix': 0, 'surface': 0, 'date': 0}

**Valeurs manquantes (colonnes présentes)**

|             |   manquants |   taux_pct |
|:------------|------------:|-----------:|
| id_local    |           0 |        0   |
| date        |           0 |        0   |
| type_bien   |           0 |        0   |
| region      |           0 |        0   |
| ville       |           8 |        1.5 |
| prix        |          10 |        1.9 |
| surface     |           0 |        0   |
| chambres    |           0 |        0   |
| salles_bain |           0 |        0   |

**Distribution du prix et de la surface (après conversion)**

|         |   prix_nombre |   surface_nombre |
|:--------|--------------:|-----------------:|
| nombre  | 518           |            528   |
| moyenne |   9.27096e+07 |            223.6 |
| minimum |   5.492e+06   |             10.2 |
| mediane |   6.764e+07   |            135.2 |
| maximum |   4.40285e+08 |           1448.8 |

**Types de bien**

| type_bien_ref    |   count |
|:-----------------|--------:|
| Local commercial |      88 |
| Maison           |      82 |
| Appartement      |      79 |
| Chambre          |      73 |
| Terrain          |      71 |
| Villa            |      71 |
| Studio           |      64 |

**Villes principales**

| ville_ref   |   count |
|:------------|--------:|
| Vélingara   |      20 |
| Ourossogui  |      19 |
| Linguère    |      18 |
| Ziguinchor  |      17 |
| Goudomp     |      17 |

## Source : notaires

- Lignes : **410**
- Colonnes absentes de cette source : type_transaction, quartier, devise, pieces, salles_bain
- Doublons exacts (colonnes brutes) : 0
- Erreurs de conversion : {'prix': 0, 'surface': 0, 'date': 6}

**Valeurs manquantes (colonnes présentes)**

|           |   manquants |   taux_pct |
|:----------|------------:|-----------:|
| id_local  |           0 |        0   |
| date      |           0 |        0   |
| type_bien |           0 |        0   |
| region    |           0 |        0   |
| ville     |           0 |        0   |
| prix      |          14 |        3.4 |
| surface   |           0 |        0   |
| chambres  |           0 |        0   |
| statut    |           0 |        0   |

**Distribution du prix et de la surface (après conversion)**

|         |   prix_nombre |   surface_nombre |
|:--------|--------------:|-----------------:|
| nombre  | 396           |            410   |
| moyenne |   1.23726e+08 |            234.9 |
| minimum |   5.446e+06   |             12.7 |
| mediane |   8.16355e+07 |            154.2 |
| maximum |   5.67559e+08 |           1498   |

**Types de bien**

| type_bien_ref    |   count |
|:-----------------|--------:|
| Maison           |     106 |
| Villa            |      98 |
| Appartement      |      92 |
| Studio           |      51 |
| Terrain          |      43 |
| Chambre          |      15 |
| Local commercial |       5 |

**Villes principales**

| ville_ref   |   count |
|:------------|--------:|
| Kanel       |      16 |
| Gossas      |      15 |
| Kébémer     |      15 |
| Pikine      |      14 |
| Bounkiling  |      13 |

## Source : particuliers

- Lignes : **731**
- Colonnes absentes de cette source : quartier, devise, pieces
- Doublons exacts (colonnes brutes) : 0
- Erreurs de conversion : {'prix': 2, 'surface': 4, 'date': 0}

**Valeurs manquantes (colonnes présentes)**

|                  |   manquants |   taux_pct |
|:-----------------|------------:|-----------:|
| id_local         |           0 |        0   |
| date             |           0 |        0   |
| type_transaction |           0 |        0   |
| type_bien        |           0 |        0   |
| region           |           0 |        0   |
| ville            |           0 |        0   |
| prix             |          61 |        8.3 |
| surface          |          75 |       10.3 |
| chambres         |           0 |        0   |
| salles_bain      |           0 |        0   |
| statut           |           0 |        0   |

**Distribution du prix et de la surface (après conversion)**

|         |     prix_nombre |   surface_nombre |
|:--------|----------------:|-----------------:|
| nombre  |   668           |            652   |
| moyenne |     6.63204e+07 |            259.6 |
| minimum | 45000           |             10.6 |
| mediane |     4.30105e+07 |            147.4 |
| maximum |     5.10157e+08 |           1484.6 |

**Types de bien**

| type_bien_ref    |   count |
|:-----------------|--------:|
| Appartement      |     176 |
| Maison           |     153 |
| Terrain          |     142 |
| Villa            |     101 |
| Studio           |      94 |
| Chambre          |      43 |
| Local commercial |      22 |

**Villes principales**

| ville_ref   |   count |
|:------------|--------:|
| Kébémer     |      26 |
| Dakar       |      25 |
| Bignona     |      25 |
| Matam       |      23 |
| Koungheul   |      23 |

## Source : plateforme

- Lignes : **875**
- Colonnes absentes de cette source : chambres
- Doublons exacts (colonnes brutes) : 15
- Erreurs de conversion : {'prix': 6, 'surface': 0, 'date': 0}

**Valeurs manquantes (colonnes présentes)**

|                  |   manquants |   taux_pct |
|:-----------------|------------:|-----------:|
| id_local         |           0 |        0   |
| date             |           0 |        0   |
| type_transaction |           0 |        0   |
| type_bien        |           0 |        0   |
| region           |           0 |        0   |
| ville            |           0 |        0   |
| quartier         |           0 |        0   |
| prix             |           0 |        0   |
| devise           |           0 |        0   |
| surface          |           5 |        0.6 |
| pieces           |           0 |        0   |
| salles_bain      |           0 |        0   |
| statut           |           0 |        0   |

**Distribution du prix et de la surface (après conversion)**

|         |     prix_nombre |   surface_nombre |
|:--------|----------------:|-----------------:|
| nombre  |   869           |            870   |
| moyenne |     8.4478e+07  |            241   |
| minimum | 40000           |             10.2 |
| mediane |     5.7208e+07  |            145.8 |
| maximum |     5.51163e+08 |           1494.8 |

**Types de bien**

| type_bien_ref    |   count |
|:-----------------|--------:|
| Appartement      |     225 |
| Maison           |     188 |
| Villa            |     151 |
| Terrain          |     123 |
| Studio           |     107 |
| Chambre          |      41 |
| Local commercial |      40 |

**Villes principales**

| ville_ref          |   count |
|:-------------------|--------:|
| Kaffrine           |      29 |
| Médina Yoro Foulah |      29 |
| Goudomp            |      29 |
| Kébémer            |      27 |
| Goudiry            |      27 |
