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

### Lizard

Lizard est un analyseur de complexité cyclomatique supportant plusieurs langages de programmation populaires, tels que C++, Python, Java, etc. Sur la page de présentation de l'outil, il est inscrit qu'il est possible d'obtenir des métriques de duplication de code. Cet outil peut être utilisé comme librairie Python.

La principale lacune de cet outil est le manque de documentation sur l'utilisation du module détectant les duplications de code : la seule information fournie indique comment lancer l'analyse depuis un terminal, mais rien n'indique comment obtenir les métriques de duplications à partir de la librairie Python et le format du rapport n'est pas précisé. 

Lizard a été mis de côté en raison du manque de documentation et d'un format non-standard des rapport générés. Un outil étant mieux documenté semblait être un choix plus judicieux pour assurer un futur transfert de responsabilité vers une autre équipe de développement. 

### PMD (Copy-Paste-Detector)

PMD est un analyseur statique de code, multilangage et extensible, qui inclut un détecteur de duplications de code, nommé Copy-Paste-Detector (CPD). Selon la page de présentation, CPD supporte une grande variété de langages, tels que Python, C++, Typescript, etc. 

Contrairement à Lizard, la documentation de CPD est plus complète : on y retrouve les langages supportés, les formats de rapports, des exemples d'utilisation et de la documentation sur les arguments de ligne de commande. 

Les lacunes de CPD sont toutefois multiples : l'outil doit être lancé par ligne de commande, le runtime de Java est nécessaire pour utiliser CPD et il est nécessaire de télécharger PMD pour pouvoir utiliser CPD. 

Toutefois, par manque d'alternatives, CPD semblait être la solution répondant le mieux à nos besoins. 

## Intégration 

### Environnement 

Dans le projet, nous utilisions un Dockerfile pour automatiser et uniformiser l'environnement d'exécution. Initialement, notre Dockerfile se basait sur l'image de Python, mais PMD requiert Java pour s'exécuter et PMD ne peut être téléchargé avec le gestionnaire de paquet Python (Pip). Nous avons modifié le Dockerfile pour utiliser une image Ubuntu afin de pouvoir télécharger et configurer les dépendances nécessaires à l'exécution de PMD dans un environnement Docker. 

### Utilisation

CPD est utilisé dans le code pour obtenir un rapport de format XML contenant les bouts de codes dupliqués ainsi que les endroits et les fichiers où la duplication a été trouvée. Étant donné que CPD ne peut être utilisé comme librairie Python, un processus enfant est créé (avec `subprocess.run(...)`) pour exécuter l'outil. Le rapport XML est obtenu en capturant le texte contenu dans le descripteur de fichier `stdout` (si aucun nom de fichier n'est fourni à PMD, l'outil écrira le rapport dans `stdout`, soit l'affichage d'un terminal). 

Les paramètres utilisés pour exécuter CPD sont: 
- le chemin de l'exécutable: `/pmd/pmd-bin-7.18.0/bin/pmd cpd`
- le nombre minimal de jeton pour détecter une duplication: `--minimum-tokens <un nombre entier>` 
- le langage sélectionné : `--language <un langage>` (voir note 1 & 2)
- le format utilisé (XML): `--format XML`
- le dossier où se situant les fichiers à analyser: `--dir <un chemin>`

** note 1: les identifiants de chaque langage supportés sont identifiés [ici](https://pmd.github.io/pmd/tag_CpdCapableLanguage.html).
** note 2: L'argument `--language` 

### Rapport

Bien que CPD peut générer un rapport dans d'autres formats, il est conseillé d'utiliser le format XML. Le format Texte est conçu pour la lecture humaine, alors que le format CSV contient moins d'informations pertinentes. 

La structure d'un rapport XML est la suivante: 
- `<pmd-cpd ...>` : C'est le noeud racine du document. Les paramètres de balises sont omis pour simplicité. 
    - `<file path="" totalNumberOfTokens="">` : Indique le chemin d'un fichier et son nombre de jetons. Le nombre de noeuds de ce type sera égal au nombre de fichiers trouvé par PMD dans le dossier sélectionné. 
    - `<duplication lines="" tokens="">`: Indique le nombre de lignes et le nombre de tokens pour un bout de code dupliqué. Le nombre de noeud de ce type sera égal au nombre de duplications distinctes que PMD détectera. 
        - `<file begintoken="" column="" endcolumn="" endline="" endtoken="" line="" path="">`: Indique l'emplacement d'une duplication. Le nombre de noeuds de ce type sera égal au nombre de fois qu'un même bout de code est dupliqué. Il peut y avoir plusieurs fois le même fichier si un fichier contient plusieurs fois le même bout de code. 
        - `<codefragment>`: Échantillon du bout de code dupliqué. 

Exemple de rapport: 
```
<?xml version="1.0" encoding="UTF-8"?>
<pmd-cpd ...>
    <file path="/.../file_a.py" totalNumberOfTokens="141"/>
    <file path="/.../file_b.py" totalNumberOfTokens="141"/>
    <duplication lines="8" tokens="27">
        <file begintoken="22" column="5" endcolumn="23" endline="19" endtoken="48" line="12" path="/.../file_a.py"/>
        <file begintoken="164" column="5" endcolumn="23" endline="19" endtoken="190" line="12" path="/.../file_b.py"/>
        <codefragment>
            <![CDATA[
    numbers = [1, 2, 3]
    total = 0
    for n in numbers:
        total += n
    return total

def duplicate_three():
]]>
        </codefragment>
    </duplication>
</pmd-cpd>
```

## Conception et Implémentation

### Base de données

Nous nous sommes inspirés du rapport XML généré par PMD pour organiser les métriques dans la base de donnée. Initialement, notre base de données avait une table `file` contenant un identifiant unique, le nom du fichier et l'identifiant du commit Git associé. Les métriques de duplications sont conservées dans deux tables: `duplication` et `code_fragment`. La table `duplication` sert de table d'association entre la table `file` et la table `code_fragment` puisque la relation entre ces deux tables est de type plusieurs-à-plusieurs (many-to-many).

```
|-----------------|         |---------------------------|         |-----------------|
| file            |         | duplication               |         | code_fragment   |
|-----------------| 1     * |---------------------------| *     1 |-----------------|
| PK | id         |<--------| PK | id                   |-------->| PK | id         |
| FK | commit_id  |         | FK | file_id              |         |    | line_count |
|    | name       |         | FK | code_fragment_id     |         |    | text       |
|-----------------|         |    | line_count           |         |-----------------|
                            |    | from_line            |
                            |    | to_line              |
                            |    | from_column          |
                            |    | to_column            |
                            |---------------------------|
```
### Couche dorsale 

#### Emballage (Wrapper)

Initialement, PMD était fortement couplé avec le service de duplication et la lecture du rapport XML : nous avions une grosse fonction qui exécutait PMD, faisait la lecture du rapport XML et insérait les objets modèles `Duplication` et `CodeFragment` dans la base de données. Pour découpler PMD de notre logique et faciliter un potentiel remplacement vers un autre outil (ou même permettre à plusieurs outils de coexister), nous avons encapsulé le code exécutant PMD dans une classe emballage (wrapper en anglais), de même pour le code lisant le rapport XML de PMD. 

![](images/wrapper_diagrams.svg)

Puisque la classe lisant le XML ne peut pas directement insérer les données dans la base de données, nous avons implémenté une classe servant à l'échange de données entre les différents objets.

#### Service 

Nous avons ajouté une classe nommée `CodeDuplicationService` qui serait responsable de insérer et obtenir des rapports de duplications. 

#### Communication avec la base de données




### Interface utilisateur

----

##### Références

1. Houssem Sebouai. (2025, April 2). What Is Code Duplication and How to Fix It. Axify.io; Axify. 
https://axify.io/blog/code-duplication

2. Yin, T. (2022, September 3). Lizard. GitHub. 
https://github.com/terryyin/lizard

3. Documentation Index | PMD Source Code Analyzer. (n.d.). Pmd.github.io. 
https://pmd.github.io/pmd/index.html

‌