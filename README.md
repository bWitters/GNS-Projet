# GNS-Projet

## Lancement :

Le code principal se trouve dans test_copy.py, une fois le programme lancé il faut importer les configs dans les routeurs dans GNS, notre config avec 3 AS se trouve dans le dossier "test_cfg_plus grand".

## Objectif :

Création automatique des fichiers de configurations pour un projet GNS, depuis un fichier d'intention JSON.

## Fonctionnalité :

- Gestion automatique des IP des interfaces des routeurs
- Metric OSPF
- Intent file pas trop détaillé
- OPSF
- RIP
- BGP (sans policies)
- BGP Full Mesh automatique


## Défauts majeurs :

- Ecriture du cfg de la mauvaise manière. (Au début nous n'avions pas compris que la forme du cfg n'avait pas d'impact)
- Ecriture depuis un cfg vierge après démarrage, mais dépend donc du type de routeur, donc un routeur qui n'a pas les mêmes interfaces, ça ne fonctionne probablement pas.
- La génération automatique des adresses IP est limitée, et fera planter le programme si le nombre de routeurs dépasse 255.
- BGP Policies non implémenté
- Problème avec l'intent file et le code, on ne peut pas mettre deux interfaces eBGP sur le même routeur
- Architecture principale du code chaotique, et pourrait être réorganisée

## Contrainte intent file :

- Une interface ne peut pas être connectée à plusieurs routeurs pour le moment (pas d'utilisation de switch)
- Les interfaces doivent être listées dans l'ordre d'apparition dans la config par défaut après démarrage.
- Problème de gestion du masque pour les plages d'adresse

