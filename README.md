# GNS-Projet

## Objectif :

Création automatique des fichiers de configurations pour un projet GNS, depuis un fichier d'intention JSON.

## Fonctionnalité :

- Gestion automatique des ip des interfaces des routeurs
- Metric OSPF
- Intent file sobre
- OPSF
- RIP
- BGP (sans policies)
- BGP Full Mesh automatique


## Défauts majeurs :

- Ecriture du cfg de la mauvaise manière (Au début nous n'avions pas compris que la forme du cfg n'avait pas d'impacte)
- Ecriture depuis un cfg vierge apres démarage, mais dépend donc du type de routeur, donc un router qui n'a pas les memes interfaces, ça ne fonctionne probablement pas.
- La génération automatique des adresses ip est limité, et fera planter le programme, si le nombre de routeur dépasse 255.
- BGP Policies non implémenté
- Architecture principale du code chaotique, et pourrait être réorganisé

## Contrainte intent file :

- Une interface ne peut pas être connecté à plusieurs routeurs pour le moment
- Les interfaces doivent être listé dans l'ordre
- Problème de gestion du masque pour les plages d'adresses

