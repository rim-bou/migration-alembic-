# README de synthèse – Intégration de nouvelles données (Option 2)

## 1. Contexte du projet
Dans la continuité du premier projet, l’entreprise FastIA souhaite enrichir ses modèles d’IA
en intégrant de nouvelles sources de données hétérogènes (données socio-démographiques,
indicateurs économiques, données sensibles).

L’objectif est de faire évoluer le schéma de données et le pipeline de traitement sans casser
l’API existante, tout en respectant les contraintes techniques et éthiques.

---

## 2. Analyse des nouvelles données
Le fichier data-all.csv apporte plusieurs colonnes supplémentaires par rapport au jeu de
données initial :
- nb_enfants
- quotient_caf
- orientation_sexuelle

L’analyse exploratoire a mis en évidence :
- un fort taux de valeurs manquantes sur certaines colonnes,
- des valeurs aberrantes (valeurs négatives pour nb_enfants, quotient_caf, loyer_mensuel),
- la présence de données sensibles.

Ces constats ont motivé la mise en place d’un pipeline de nettoyage dédié avant l’insertion
en base et l’entraînement du modèle.

---

## 3. Choix d’évolution du schéma relationnel (Option 2)

### 3.1 Table existante clients
La table clients issue du brief 1 est conservée.
Deux nouvelles colonnes ont été ajoutées :
- nb_enfants (INTEGER, nullable)
- quotient_caf (FLOAT, nullable)

Ces ajouts sont non bloquants et ne remettent pas en cause les données existantes.

### 3.2 Table séparée pour les données sensibles
Une nouvelle table client_sensitive a été créée afin de stocker :
- orientation_sexuelle

Cette table est liée à clients par une relation 1–1.

Justification :
- donnée sensible pouvant introduire des biais,
- limitation de l’exposition dans l’API,
- meilleure conformité éthique et RGPD.

---

## 4. Migration du schéma avec Alembic
L’évolution du schéma a été réalisée à l’aide d’Alembic :
- ajout des nouvelles colonnes dans clients,
- création de la table client_sensitive,
- aucune suppression de table ou de colonne existante.

La migration est versionnée, reproductible et n’entraîne aucune perte d’information.

---

## 5. Nettoyage et transformation des données

### 5.1 Avant insertion en base
Lors de l’ingestion de data-all.csv :
- normalisation des noms de colonnes (suppression des accents et espaces),
- conversion des types numériques,
- remplacement des valeurs aberrantes par NaN,
- imputation simple des valeurs manquantes si nécessaire.

### 5.2 Pour l’entraînement du modèle IA
Dans le pipeline ML :
- suppression des lignes sans variable cible (score_credit),
- imputation (médiane pour les numériques, inconnu pour les catégorielles),
- encodage one-hot des variables catégorielles,
- standardisation des variables numériques.

La colonne orientation_sexuelle est volontairement exclue du modèle.

---

## 6. Compatibilité avec l’API existante
Les routes développées lors du premier projet sont conservées :
- GET /clients
- GET /clients/{id}
- POST /clients
- DELETE /clients/{id}
- POST /train

Aucune rupture de compatibilité n’a été introduite.

---

## 7. Note éthique
La donnée orientation_sexuelle est considérée comme sensible.
Elle est :
- stockée dans une table séparée,
- non exposée via l’API,
- non utilisée pour l’entraînement du modèle IA.

Ce choix permet de limiter les biais potentiels et de respecter les principes de minimisation
des données.

---

## 8. Conclusion
Ce projet illustre une situation réaliste d’intégration de nouvelles données :
- analyse exploratoire,
- évolution contrôlée du schéma relationnel,
- migration sécurisée avec Alembic,
- maintien de la compatibilité avec un système existant,
- prise en compte des enjeux éthiques.

Il répond pleinement aux objectifs du brief et aux critères d’évaluation.