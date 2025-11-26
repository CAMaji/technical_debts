## Situation actuelle: 

La solution actuelle est dépourvue d'une fonctionnalité qui permet de visualiser les fichiers ayant un risque de dette technique élevée. Nous aimerions ajouter cette fonctionnalité pour visualiser une liste de fichiers à haut risque pour un commit sélectionné. 

## Solution envisagée:  

Nous envisageons évaluer le risque d'un fichier à partir de la moyenne des complexités cyclomatique de ses fonctions. La moyenne résultante sera catégorisée en fonction de barèmes établis par l'auteur de la théorie de la complexité cyclomatique, M. McCabe. Le barème est le suivant: 

| Pointage | Risque |
| - | - |
| De 1 à 10  | Risque faible |
| De 11 à 20 |  Risque modéré |
| De 21 à 50 | Risque élevé  |
| Plus de 50 | Risque très élevé | 

Un risque faible indique généralement que la probabilité qu'il y ait des bogues est faible, que la logique est simple et qu'il est possible de tester facilement le code. Un fichier à faible complexité contient généralement plusieurs procédure simple, parfois de petite taille, ayant une logique claire et facilement testable. 

Un risque modéré indique généralement que la probabilité qu'il y ait des bogues est considérable, que le code peut contenir des failles de sécurité, que la logique est moins bien organisée et plus complexe et qu'il peut être plus difficile de tester le code. Un fichier à risque modéré contient généralement des procédures simple mais ayant une logique plus complexe et moins évidente. 

Un risque élevé indique généralement que la probabilité qu'il y ait des bogues est haute, que le code n'est pas sécuritaire, que la logique est très complexe et qu'il sera difficile de tester adéquatement la logique. Un fichier à haut risque contient généralement des procédures volumineuses ayant une logique peu évidente, mal structurée et complexe.

Un risque très élevé indique généralement de sévères lacunes de structure, de logique et sécurité. Les fichiers ayant un risque très élevé contiennent généralement de très grosses procédures avec une logique très mal structurée. Il est généralement impossible de bien tester des procédures de ce types. 

--- 

## Référence(s)

Murphy, James & Robinson III, John. (2007). Design of a Research Platform for En Route Conflict Detection and Resolution. 10.2514/6.2007-7803. 
https://www.researchgate.net/figure/Cyclomatic-Complexity-Thresholds_tbl2_238659831

McCabe, T. (2008). Software Quality Metrics to Identify Risk (p. 22, p. 36) [Review of Software Quality Metrics to Identify Risk]. Department of Homeland Security Software Assurance Working Group.
https://web.archive.org/web/20220329072759/http://www.mccabe.com/ppt/SoftwareQualityMetricsToIdentifyRisk.ppt