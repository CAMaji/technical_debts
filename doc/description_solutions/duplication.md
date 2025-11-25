## Situation actuelle: 

Nous aimerions que le système puisse analyser les fichiers d'un commit, puis trouver les fichiers ayant des bouts de code identiques. Nous croyons qu'un ou plusieurs fichiers partageant le même bout de code est indicateur de dette technique et mérite d'être mesuré et analysé. Selon **Houssem Sebouai, de Axify**, la duplication de code est souvent indicateur de mauvaise pratiques (copy-paste coding), d'une mauvaise architecture ou d'une déficience en lisibilité (code illisible, code mal documenté, séquence difficile à suivre). De plus, la duplication de code rendrait la refactorisation plus complexe et ralentirait le développement. 

## Solution envisagée:  

Il est envisagé d'utiliser Lizard pour détecter la duplication de code sur plusieurs fichiers dans un dossier et ses sous-dossiers. Nous avons finalement opté pour le logiciel _PMD_ et son module _Copy Paste Detector_ pour obtenir la liste des fichiers partageant une duplication puisque que Lizard contient peu d'information et de documentation sur son outil de détection de duplication. 

_PMD_ supporte l'analyse de duplication pour plusieurs langages de programmation et donne les résultats de son analyse dans le format XML. Voici un exemple: 
```
<?xml version="1.0" encoding="UTF-8"?>
<pmd-cpd xmlns="https://pmd-code.org/schema/cpd-report"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         pmdVersion="7.18.0"
         timestamp=""
         version="1.0.0"
         xsi:schemaLocation="https://pmd-code.org/schema/cpd-report https://pmd.github.io/schema/cpd-report_1_0_0.xsd">
   <file path="/app/unit_tests/tools/pmd_cpd_wrapper_test_directory/file_a.py"
         totalNumberOfTokens="141"/>
   <file path="/app/unit_tests/tools/pmd_cpd_wrapper_test_directory/file_b.py"
         totalNumberOfTokens="141"/>
   <duplication lines="8" tokens="27">
      <file begintoken="22"
            column="5"
            endcolumn="23"
            endline="19"
            endtoken="48"
            line="12"
            path="/app/unit_tests/tools/pmd_cpd_wrapper_test_directory/file_a.py"/>
      <file begintoken="164"
            column="5"
            endcolumn="23"
            endline="19"
            endtoken="190"
            line="12"
            path="/app/unit_tests/tools/pmd_cpd_wrapper_test_directory/file_b.py"/>
      <codefragment><![CDATA[    numbers = [1, 2, 3]
    total = 0
    for n in numbers:
        total += n
    return total


def duplicate_three():
]]></codefragment>
   </duplication>
   <duplication lines="5" tokens="27">
      <file begintoken="108"
            column="30"
            endcolumn="11"
            endline="39"
            endtoken="134"
            line="35"
            path="/app/unit_tests/tools/pmd_cpd_wrapper_test_directory/file_a.py"/>
      <file begintoken="250"
            column="30"
            endcolumn="11"
            endline="39"
            endtoken="276"
            line="35"
            path="/app/unit_tests/tools/pmd_cpd_wrapper_test_directory/file_b.py"/>
      <codefragment><![CDATA[    print("=== file_a.py ===")
    print("duplicate_one():", duplicate_one())
    print("duplicate_two():", duplicate_two())
    print("duplicate_three():", duplicate_three())
    print("unique_function_a():", unique_function_a())
]]></codefragment>
   </duplication>
</pmd-cpd>

```

Une table `code_duplication` sera créée pour persister le code dupliqué. De plus,  une table d'association `file_code_duplication` sera crée étant donné la relation plusieurs-à-plusieurs entre la table `file` et la table `code_duplication`. Cette table d'association va contenir les informations qui décrivent la duplication dans un fichier (exemple: la ligne de début, la ligne de fin, etc.)

---
#### Référence(s): 

Houssem Sebouai. (2025, April 2). What Is Code Duplication and How to Fix It. Axify.io; Axify. 
https://axify.io/blog/code-duplication

Documentation de PMD Copy Paste Detector:
https://pmd.github.io/pmd/pmd_userdocs_cpd.html

---