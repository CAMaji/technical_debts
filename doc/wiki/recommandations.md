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




