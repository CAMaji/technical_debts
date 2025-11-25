## Situation actuelle: 

Nous aimerions que le système calcule, trie et affiche les fichiers contenus dans un commit ayant une forte dette technique. Nous croyons qu'un fichier ayant une lourde dette mérite d'être priorisé et d'attirer l'attention des développeurs et mainteneurs. 

## Solution envisagée:  

Les fichiers seront priorisés sur une échelle de 0 à 1, 0 étant le moins prioritaire et 1 étant le plus. 

La pondération de chaque métrique sera distribué ainsi: 
- Complexité cyclomatique: 40 % 
- Duplications : 30 %
- Commentaires "TODO" et "FIX ME": 30 %

Le poid d'une métrique est calculé par rapport au poid le plus élevé de cette même métrique, exemple: le fichier A a une complexité de 10, et la complexité maximale trouvé est de 30. Le poid de cette métrique sera de 10 / 30 = 0.33, et la contribution au score sera de 0.33 * 0.40 = 0,132.

### complexité
Étant donné que la complexité est associée aux fonctions d'un fichiers,  nous calculerons la moyenne des complexités de chaque fonction d'un fichier. 

### duplication
La pondération total de cette métrique est la somme de deux sous-métriques, totalisant une pondération de 30%. 

La pondération des deux-sous métrique est distribuée ainsi: 
- Nombre d'instance de duplication par fichier: 20%
- Somme des lignes dupliquées pour un fichier: 10%

la table d'association `file_code_duplication` lie un fichier à des instances de duplication de code. On peut obtenir le nombre d'instance de duplication par fichier en faisant la somme des instances de duplication liées à un fichier donné, alors que la somme des lignes dupliquées pour un fichier se calcule à partir du nombre de ligne dupliqué, inscrit dans la table d'association.

### Commentaires _TODO_ et _FIXME_
La table d'association `file_identifiable_entity` lie un fichier à une ou plusieurs entités identifiables (autrement dit, un mot ou un petit bout de texte). Ainsi, il nous est possible de compter le nombre d'association liant un fichier à l'identité "todo/fixme". 
