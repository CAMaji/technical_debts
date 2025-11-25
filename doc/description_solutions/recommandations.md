## Solution actuelle

La solution actuelle est dépourvue d'un mécanisme de recommandation basé sur une analyse des statistiques de dettes techniques calculées. Nous aimerions ajouter ce mécanisme pour assister la prise de décision en lien avec la dette technique d'un projet de développement logiciel.

## Solution envisagée

Générer des recommandations à partir d'un lot de gabarits prédéfinis basés sur les statistiques et métriques calculées. Une recommandation peut être composée de plusieurs gabarits si le fichier contients plusieurs problèmes. La diversité des recommandations est limité dûe au faible nombre de métrique obtenu.

Liste de gabarits de problèmes:

- `ProblemEnum.NO_PROBLEM                  `:
    - `"No problems."`
    - Condition: Aucune
- `ProblemEnum.GLOBAL_RISK_PROBLEM         `:
    - `"50% of files in this commit have an average complexity ranked at or above @1."`
    - Condition: la médiane de la complexité des fichiers doit être supérieure à 10 (11 à 20 = risque moyen)
- `ProblemEnum.GLOBAL_DUPLICATION_PROBLEM  `:
    - `"@1 code duplication has been detected in over @2 files. Details in 'Duplication' section."`
    - Condition: au moins une duplication présente minimalement dans 5 fichiers différents
- `ProblemEnum.FILE_AVG_RISK_PROBLEM       `:
    - `"File @1 has an average complexity ranked at or above @2."`
    - Condition: la complexité d'un fichier doit être supérieure à 10 (11 à 20 = risque moyen)
- `ProblemEnum.FILE_FUNC_RISK_PROBLEM      `:
    - `"File @1 has complexity of function @2 ranked at or above @3."`
    - Condition: la complexité d'une fonction doit être supérieure à 10 (11 à 20 = risque moyen)
- `ProblemEnum.FILE_BUG_TO_FUNCTION_PROBLEM`:
    - `"File @1 has a ratio of @2 'todo-fixme' comments for @3 functions."`
    - Condition: le ratio du nombre de commentaire "todo" et "fix-me" dans un fichier divisé par le nombre de fonctions dans un fichier doit être supérieur à 0.5 (condition respectée s'il y a au maximum deux fois plus de fonction que de commentaires "todo" et "fixme")

List de gabarits de recommandations:

- `GLOBAL_RISK_RECOMMENDATION`
    - `"Simplify logic and reduce complexity by limiting the number of independent paths in your functions. Break appart large complex functions into smaller, simpler and testable functions."`
- `GLOBAL_DUPLICATION_RECOMMENDATION`
    - `"Move duplicated code into new coherent and cohesive functions and modules for reusability, readability, maintainability and testability."`
- `FILE_RISK_RECOMMENDATION` 
    - `"Simplify logic and reduce complexity by limiting the number of independent paths. Break appart large and complex logic blocks into smaller, loosely coupled and testable functions."`
- `FILE_FUNC_NUMBER_RECOMMENDATION`
    - `"Decrease the number of functions either by redesigning your architecture or creating a new module. A large number of functions can be signs of high coupling and low cohesion, and usually decreases readability and maintainability."`
- `FILE_BUG_TO_FUNCTION_RECOMMENDATION`
    - `"More efforts in bug fixing, refactoring and testing are needed. A high bug-to-function ratio can be signs of lack of tests, low testability and high logic complexity."`


