# Duplication de code

## Mise en contexte 

Dans le cadre du développement d'un outil pour analyser la dette technique, nous avions à détecter les duplications dans un ou plusieurs fichiers. Selon **Houssem Sebouai, de Axify**, la duplication de code est souvent indicateur de mauvaise pratiques (copiés-collés), d'une mauvaise architecture ou de déficiences en lisibilité. 

Ajoutons que la duplication de code peut aussi réduire la maintenabilité d'un logiciel lorsqu'un ou plusieurs  développeurs copie-collent une logique défaillante (bogues) à travers le code source : il faudra corriger la logique défaillante à chaque endroit où elle a été dupliquée, ce qui augmente considérablement le temps nécessaire pour corriger les bogues et, conséquemment, réduit le temps disponible pour le développement.  

## Objectif

L'objectif était d'ajouter une fonctionnalité qui répertoriait les duplications de code contenues dans les fichiers d'un commit Git, dans le but d'aider les mainteneurs ou développeurs à garder trace des duplications et suivre l'évolution de celle-ci à travers le temps. 

## Analyse

Dans un premier temps, il a fallu analyser les solutions envisageables pour ajouter la visualisation des duplications de code au projet. 

Étant donné la multitude de langages de programmation actuellement utilisés, la popularité des projets utilisant plusieurs langages de programmation et la complexité lié à l'implémentation d'une solution logicielle détectant la duplication de code, une solution fait maison n'a pas été retenue

Lors de la rédaction du plan de projet, nous avions identifié quelques outils logiciels open-source pouvant détecter la duplication de code : Lizard et PMD. 

#### Lizard

Lizard est un analyseur de complexité cyclomatique supportant plusieurs langages de programmation populaires, tels que C++, Python, Java, etc. Sur la page de présentation de l'outil, il est inscrit qu'il est possible d'obtenir des métriques de duplication de code. Cet outil peut être utilisé comme librairie Python.

La principale lacune de cet outil est le manque de documentation sur l'utilisation du module détectant les duplications de code : la seule information fournie indique comment lancer l'analyse depuis un terminal, mais rien n'indique comment obtenir les métriques de duplications à partir de la librairie Python et le format du rapport n'est pas précisé. 

Lizard a été mis de côté en raison du manque de documentation et d'un format non-standard des rapport générés. Un outil étant mieux documenté semblait être un choix plus judicieux pour assurer un futur transfert de responsabilité vers une autre équipe de développement. 

#### PMD (Copy-Paste-Detector)

PMD est un analyseur statique de code, multilangage et extensible, qui inclut un détecteur de duplications de code, nommé Copy-Paste-Detector (CPD). Selon la page de présentation, CPD supporte une grande variété de langages, tels que Python, C++, Typescript, etc. 

Contrairement à Lizard, la documentation de CPD est plus complète : on y retrouve les langages supportés, les formats de rapports, des exemples d'utilisation et de la documentation sur les arguments de ligne de commande. 

Les lacunes de CPD sont toutefois multiples : l'outil doit être lancé par ligne de commande, le runtime de Java est nécessaire pour utiliser CPD et il est nécessaire de télécharger PMD pour pouvoir utiliser CPD. 

Toutefois, par manque d'alternatives, CPD semblait être la solution répondant le mieux à nos besoins. 

## Intégration 

#### Environnement 

Dans le projet, nous utilisions un Dockerfile pour automatiser et uniformiser l'environnement d'exécution. Initialement, notre Dockerfile se basait sur l'image de Python, mais PMD requiert Java pour s'exécuter et PMD ne peut être téléchargé avec le gestionnaire de paquet Python (Pip). Nous avons modifié le Dockerfile pour utiliser une image Ubuntu afin de pouvoir télécharger et configurer les dépendances nécessaires à l'exécution de PMD dans un environnement Docker. 

#### Utilisation

CPD est utilisé dans le code pour obtenir un rapport de format XML contenant les bouts de codes dupliqués ainsi que les endroits et les fichiers où la duplication a été trouvée. Étant donné que CPD ne peut être utilisé comme librairie Python, un processus enfant est créé (avec `subprocess.run(...)`) pour exécuter l'outil. Le rapport XML est obtenu en capturant le texte contenu dans le descripteur de fichier `stdout` (si aucun nom de fichier n'est fourni à PMD, l'outil écrira le rapport dans `stdout`, soit l'affichage d'un terminal). 

Les paramètres utilisés pour exécuter CPD sont: 
- le chemin de l'exécutable: `/pmd/pmd-bin-7.18.0/bin/pmd cpd`
- le nombre minimal de jeton pour détecter une duplication: `--minimum-tokens <un nombre entier>` 
- le langage sélectionné : `--language <un langage>`
(note: les identifiants de chaque langage supportés sont identifiés [ici](https://pmd.github.io/pmd/tag_CpdCapableLanguage.html).)
- le format utilisé (XML): `--format XML`
- le dossier où se situant les fichiers à analyser: `--dir <un chemin>`

## Implémentation



----

##### Références

1. Houssem Sebouai. (2025, April 2). What Is Code Duplication and How to Fix It. Axify.io; Axify. 
https://axify.io/blog/code-duplication

2. Yin, T. (2022, September 3). Lizard. GitHub. 
https://github.com/terryyin/lizard

3. Documentation Index | PMD Source Code Analyzer. (n.d.). Pmd.github.io. 
https://pmd.github.io/pmd/index.html

‌