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
 
Les méthodes de la classe `RecommendationGenerator` sont responsables de générer une recommandation lorsqu'un problème de dette technique est détecté. Le système peut détecter 6 problèmes de dette technique : pour chaque problème, il y a un modèle de message avec un ou plusieurs jetons de remplacement (exemple: `@1`, `@2`, ...). Ces jetons de remplacement sont utilisés pour insérer des informations dans le modèle de message afin de préciser la nature, l'origine ou l'importance du problème. De plus, chaque problème doit être jumelé à un message de recommandation.

Les modèles sont contenus dans la classe d'énumération `ProblemEnum`. La liste suivante présente le contenu du modèle, son seuil de détection et la définition de ses jetons de remplacement.

- <b>NO_PROBLEM</b> = "No problems."
    - Condition : la métrique est sous le seuil de détection. 
- <b>GLOBAL_RISK_PROBLEM</b> = "50% of files in this commit have an average complexity ranked at or above @1."
    - Condition : la médiane de la complexité de l'ensemble des fichiers d'un commit doit être supérieure à 10 (complexité modérée)
    - `@1`: le niveau de complexité (`MEDIUM_COMPLEXIY`, `HIGH_COMPLEXITY` ou `VERY_HIGH_COMPLEXITY`). 
- <b>GLOBAL_DUPLICATION_PROBLEM</b> = "@1 instances of code duplication has been detected in this commit. Details in 'Duplication' section."
    - Condition : le nombre d'instances de duplication, pour l'ensemble du commit, doit être supérieur à 4. 
    - `@1`: le nombre d'instances de duplication détecté. 
- <b>GLOBAL_BUG_PROBLEM</b> = "For a total of @1 files, @2 files reported at least one bug."
    - Condition : il doit y avoir au moins 7% des fichiers du commit qui contiennent au moins un bogue (bogue = commentaire "todo" ou "fixme")
    - `@1`: le nombre de fichiers total du commit.
    - `@2`: le nombre de fichiers dans le commit ayant au moins un bogue
- <b>FILE_AVG_RISK_PROBLEM</b> = "File @1 has an average complexity ranked at or above @2."
    - Condition : la complexité d'un fichier doit être supérieure à 10 (complexité modérée).
    - `@1`: nom du fichier.
    - `@2`: le niveau de complexité (`MEDIUM_COMPLEXIY`, `HIGH_COMPLEXITY` ou `VERY_HIGH_COMPLEXITY`). 
- <b>FILE_FUNC_RISK_PROBLEM</b> = "File @1 has complexity of function @2 ranked at or above @3."
    - Condition : la complexité d'un fonction doit être supérieure à 10 (complexité modérée).
    - `@1`: nom du fichier
    - `@2`: signature de la fonction
    - `@3`: le niveau de complexité (`MEDIUM_COMPLEXIY`, `HIGH_COMPLEXITY` ou `VERY_HIGH_COMPLEXITY`). 
- <b>FILE_FUNC_NUMBER_PROBLEM</b> = "File @1 has a total of @2 functions."
    - Condition : le nombre de fonctions contenues dans un fichier est supérieur à 29. 
    - `@1`: nom du fichier.
    - `@2`: nombre de fonctions contenues. 

Les messages de recommandation sont contenus dans la classe d'énumération `RecommendationEnum`. La liste suivante présente les messages de recommandation. À noter que ces messages sont dépourvus de jetons de remplacement étant donné les précisions contenues dans le message de problèmes généré.

- <b>NO_RECOMMENDATION</b> 
    - Jumelé à <i>NO_PROBLEM</i>
    - ""
- <b>GLOBAL_RISK_RECOMMENDATION</b>
    - Jumelé à <i>GLOBAL_RISK_PROBLEM</i>
    - "Simplify logic and reduce complexity by limiting the number of independent paths in your functions. Break appart large complex functions into smaller, simpler and testable functions."
- <b>GLOBAL_DUPLICATION_RECOMMENDATION</b>     
    - Jumelé à <i>GLOBAL_DUPLICATION_PROBLEM</i>
    - "Move duplicated code into new coherent and cohesive functions and modules for reusability, readability, maintainability and testability."
- <b>GLOBAL_BUG_RECOMMENDATION</b> 
    - Jumelé à <i>GLOBAL_BUG_PROBLEM</i>
    - "Dedicate more ressources to bug fixing. Consider refactoring and improving tests coverage."
- <b>FILE_RISK_RECOMMENDATION</b> 
    - Jumelé à <i>FILE_AVG_RISK_PROBLEM</i>
    - Jumelé à <i>FILE_FUNC_RISK_PROBLEM</i>
    - "Simplify logic and reduce complexity by limiting the number of independent paths. Break appart large and complex logic blocks into smaller, loosely coupled and testable functions."
- <b>FILE_FUNC_NUMBER_RECOMMENDATION</b> 
    - Jumelé à <i>FILE_FUNC_NUMBER_PROBLEM</i>
    - "Decrease the number of functions either by redesigning your architecture or creating a new module. A large number of functions can be signs of high coupling and low cohesion, and usually decreases readability and maintainability."

Les objets retournés par les méthodes de la classe de génération sont de type `Pair[str, str]`. Le premier élément correspond au message de problème, le second à la recommandation. 

Le diagramme de classes ci-dessous illustre la relation entre le générateur et les objets de rapport qui contiennent les métriques de dette technique. 

---
![](puml/recomm_generator.svg)

---

#### Service & contrôlleur

Une classe Contrôlleur a été créée pour servir d'interface entre les autres services et le service de recommandation afin de minimiser les dépendances et assurer un faible couplage. Le contrôlleur est aussi responsable de l'exécution de la conversion des données brutes en données structurées afin de converser une haute cohésion et un nombre limité de responsabilité dans la classe Service. La classe Contrôlleur est nommée `RecommendationController` et la classe Service est nommée `RecommendationService`. 

---
![](puml/recomm_service.svg)

---