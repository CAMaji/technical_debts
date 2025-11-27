## Situation actuelle: 

Nous aimerions que le système puisse analyser les fichiers d'un commit, puis trouver les fichiers ayant des bouts de code identiques. Nous croyons qu'un ou plusieurs fichiers partageant le même bout de code est indicateur de dette technique et mérite d'être mesuré et analysé. Selon **Houssem Sebouai, de Axify**, la duplication de code est souvent indicateur de mauvaise pratiques (copy-paste coding), d'une mauvaise architecture ou d'une déficience en lisibilité (code illisible, code mal documenté, séquence difficile à suivre). De plus, la duplication de code rendrait la refactorisation plus complexe et ralentirait le développement. 

## Solution envisagée:  

Il est envisagé d'utiliser Lizard pour détecter la duplication de code sur plusieurs fichiers dans un dossier et ses sous-dossiers. Nous avons finalement opté pour le logiciel _PMD_ et son module _Copy Paste Detector_ pour obtenir la liste des fichiers partageant une duplication puisque que Lizard contient peu d'information et de documentation sur son outil de détection de duplication. 

_PMD_ supporte l'analyse de duplication pour plusieurs langages de programmation et donne les résultats de son analyse dans le format XML. Voici un exemple: 

- Voir le fichier `doc/solutions-envisagees/exemples/duplication-exemple-pmd.xml`

---
#### Référence(s): 

Houssem Sebouai. (2025, April 2). What Is Code Duplication and How to Fix It. Axify.io; Axify. 
https://axify.io/blog/code-duplication

Documentation de PMD Copy Paste Detector:
https://pmd.github.io/pmd/pmd_userdocs_cpd.html

---
