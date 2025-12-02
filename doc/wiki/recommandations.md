# Recommandations

## Mise en contexte 

Dans le cadre du développement d'un outil pour analyser et suivre la dette technique, nous avions à implémenter une interface web afin d'y présenter les résultats d'analyse et de suivi. D'une maquette de l'interface web souhaitée, il était demandé d'implémenter une fonctionnalité de recommandations où s'afficherait des actions suggérées dans le but d'aider à la gestion de la dette technique. 


## Objectifs

L'objectif était d'afficher une liste d'actions recommandées, en lien avec la dette technique d'un projet.

## Analyse

Nous avons dirigé notre analyse selon les besoins exprimés dans une maquette, fournie au début du projet. L'image présentée ci-dessous est un extrait de la maquette fournie et présente les lignes directrices de la fonctionnalité de recommandations. 

Tel qu'indiqué dans cet extrait, les recommandations devaient être générées sur la base des métriques de dette technique : on y voit des étiquettes indiquant la/les catégorie(s) problématique(s), une suggestion d'action et une brève justification. 

---
![](./imgs/maquette-recommandations.png)

---

Afin de réaliser cette fonctionnalité, il a été décidé que les recommandations seraient générées, dans un premier temps, pour l'ensemble des fichiers d'un commit, puis dans un second temps, pour chaque fichier individuellement d'un commit. Les données de dette techniques détermineraient si une recommandation serait générée ou non en vérifiant si la donnée dépasse un seuil préétabli. 

## Conception et Implémentation

Cette fonctionnalité est supportée par une implémentation dans la couche dorsale (le serveur) ainsi qu'une implémentation dans la couche frontale (l'interface web). 

### Couche dorsale 

La fonctionnalité de recommandation s'intègre dans le processus d'analyse de dette technique pour un commit. Ce processus englobe l'analyse de dette technique et l'obtention des données pour chaque catégorie de métrique, soit la complexité, les bogues et la duplication de code. Étant donné que les recommandations font parties du processus d'analyse et que ce processus traite les données de dette techniques, la génération des recommandations est réalisée lorsque l'analyse du commit et l'obtention des données sont complétées : le processus de recommandation prendra ces données obtenues et les utilisera pour la génération des recommandations, évitant de devoir refaire le processus d'obtention. 

#### Compatibilité

Une classe de compatibilité a été créée pour faciliter l'utilisation des données fournies par les processus d'obtention de la complexité et des bogues : les fonctions qui obtiennent les données de dette technique sauvegardées dans la base de données nous retournent ces données dans des listes de dictionnaires. La classe de compatibilité vient réorganiser les données dans des collections d'instances de classes pour permettre à l'outil de suggestion de code de détecter les attributs de l'instance; cela a aussi pour effet de réduire les chances d'entrer une clé invalide dans un dictionnaire.

---
![](puml/recomm_compatibilite.svg)

---

Les classes `FunctionComplexityReport` et `EntityReport` contiennent une méthode `validate_keys` qui valide la présence de toutes les clés contenues dans l'attribut `FIELDS`. Une exception est soulevée lorsqu'une clée est introuvable. 

#### Générateur
 


---
![](puml/recomm_generator.svg)

---

#### Service & contrôlleur

Une classe Contrôlleur a été créée pour servir d'interface entre les autres services et le service de recommandation afin de minimiser les dépendances et assurer un faible couplage. Le contrôlleur est aussi responsable de l'exécution de la conversion des données brutes en données structurées afin de converser une haute cohésion et un nombre limité de responsabilité dans la classe Service. La classe Contrôlleur est nommée `RecommendationController` et la classe Service est nommée `RecommendationService`. 

---
![](puml/recomm_service.svg)

---