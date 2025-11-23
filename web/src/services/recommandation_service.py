
class RecommandationService:

    # todo:
    # - analyser la médiane. 
    #   - médiane complexité > 20 : la moitié des fichiers ont un risque élevé; réduire la taille des fonctions et simplifier la logique
    #   - médiane duplication > 10 : la moitié des fichiers ont plus de 10 duplications; éliminer les duplications en maximisant la réutilisation de code
    #   - médiane entités > 20 : la moitié des fichiers ont plus de 20 commentaires todo-fix me; écrire des tests unitaires et d'intégrations et faire les refactorisations, si nécessaire.
    #   - médiane lignes dupliquées > 100 : la moitié des fichiers ont plus de 100 lignes de code dupliqué; éliminer les duplications en maximisant la réutilisation de code
    #   - médiane nb de fonction > 25: la moitié des fichiers ont plus de 15 fonctions; augmenter la cohérence et réduire le nombre de responsabilité par fichiers. 
    #
    # - trier par priorité poser recommandations sur les fichiers prioritaires
    #   - complexité > 20 : la complexité moyenne est trop élevé dans ce fichier; refactoriser le fichier pour simplifier la logique, augmenter la testabilité et réduire les probabilités de bogues.
    #   - duplication > 10 : le nombre de duplication est de 10; mettre le code dupliqué dans une fonction pour réduire la taille du fichier, augmenter la lisibilité et augmenter la maintenabilité.
    #   - entités > 10: le nombre de todo-fix me est élevé; faire des tests pour les corriger et faire la refactorisation si nécessaire.
    #   - nb de fonction > 50: le nombre de fonction est élevé; réduire le nombre de responsabilité en limitant le nombre de responsabilités par fichiers. 

    def __init__(self): 
        return