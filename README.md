Disclaimer
===========

:fr: : Ce dépot contient les codes d'un bot Discord spécifiquement conçu pour des serveurs particuliers.
Les codes ne sont pas directement applicable à d'autres serveurs et ne sont proposés ici que comme inspirations.

Pour les curieux, ce bot est utilisé sur une famille de serveurs fracophones dédiés au jeu compétitif du jeu de carte Magic the Gathering.

:gb: :us: : This repository provides the source code for a Discord bot tailored towards very specific servers.
The codes are not applicable to any other server and are only proposed here as inspiration.

For the curious, this bot is used on a family of Fracophone servers dedicated to the competitive play of the card game Magic the Gathering

Fonctionnalités accessibles par une commande
==================

Toutes les commandes sont accessibles sur tous les PERF'.
Certaines commandes requiert que l'utilisateur possède le rôle 'Planeswalkers' pour être utilisée.


[Enregistrement d'un résultat : `%score`]()
-------------------------------------------

*Disponible pour tous.*

**Exemple d'appel** : `%score NbVictoires NbDéfaites`

Enregistre `NbVictoires` et `NbDéfaites` pour le deck discuté dans le salon où la commande est appelé.
Le win-rate est ensuite mis-à-jour pour être disponible aux autres fonctions ainsi que stocker dans un fichier de backup.
La commade est effacée par le bot ainsi que ses messages pour éviter de surcharger les salons.

[Correction des résultat : `%correct`]()
-------------------------------------------

*Planswalkers uniquement.*

**Exemple d'appel** : `%correct NbVictoires NbDéfaites`

Écrase les résultats enregistrés pour ce salon par ceux entrés. 
Le win-rate est ensuite mis-à-jour pour être disponible aux autres fonctions ainsi que stocker dans un fichier de backup.
La commade est effacée par le bot ainsi que ses messages pour éviter de surcharger les salons.

[Correction des résultat : `%winrate`]()
-------------------------------------------

*Disponible pour tous.*

**Exemple d'appel** : `%winrate`

Cette commande demande au bot d'afficher les résultats enregistrés dans ce salon (winrate et nombre de parties).

[Correction des résultat : `%move`]()
-------------------------------------------

*Planswalkers uniquement.*

**Exemple d'appel** : `%move IdSalon`

Cette commande demande au bot de recopier l'ensemble des messages du salon donné en argument à l'endoit où la commande est appelée.
Pour obtenir l'id d'un salon, suivre cette procédure :
 1. Activer le mode développeur sur Discord si ce n'est pas déjà fait. 
    1. Ouvrir les réglages de Discord.
    1. Dans Avancés, activer le mode développeur. 
 1. Clic droit sur le nom du salon, une option pour copier l'ID est disponible.

Fonctionnalités passives
==================

Toutes les quelques heures, le bot ressence tous les salons appartenant à une catégorie dont le nom contient "color"
Il peut ensuite réaliser l'une ou plusieurs des tâches suivantes selon qu'elles soient active ou non sur chacun des serveurs.
Chaque fonction peut être activée ou non d'un serveur à l'autre.
Toutes les fonction cherchant des mots dans les noms de catégories sont insensible à la casse.

[Mise en avant de l'activité]()
-------------------------------------------

*Actif dans PERF' Innovation et PERF' Historique.*

Pour chaque salon, le bot décompte le nombre de messages écrits durant le laps de temps fixé en excluant les messages des bots.
Le bot modifie ensuite le nom du salon pour que le nombre de ⚡ corresponde au seuil prévus.

### Paramètres de réglages actuels
 
| Paramètre | Valeur actuelle |
|:---------:|:---------------:|
| Période d'étude | 3 jours |
| Seuil pour ⚡ | 3 messages |
| Seuil pour ⚡⚡ | 15 messages |
| Seuil pour ⚡⚡⚡ | 45 messages |

[Archivage des salons inactifs]()
-------------------------------------------

*Actif dans PERF' Innovation.*

Pour chaque salon, le bot détermine le temps écoulé depuis le dernier message n'appartenant pas à un bot.
Si le temps est supérieur à un premier seuil, le bot averti de l'archivage prochain du serveur.
Si le temps est supérieur au second seuil, le bot déplace le salon dans la catégorie contenant 'archive' dans son nom.

### Paramètres de réglages actuels
 
| Paramètre | Valeur actuelle |
|:---------:|:---------------:|
| Délai avant avertissement | 7 jours |
| Délai avant archivage | 8 jours |

[Désarchivage des salons archivés]()
-------------------------------------------

*Actif dans PERF' Innovation.*

Pour chaque salon, dans la catégorie contenant 'archive' dans son nom, le bot compte le nombre de messages humains au cours de la période fixée.
Si le nombre dépasse le seuil, le salon est déplacé dans la catégorie contenant 'nouvelles idees' ou 'labo' dans son nom.

### Paramètres de réglages actuels
 
| Paramètre | Valeur actuelle |
|:---------:|:---------------:|
| Période d'étude | 3 jours |
| Nombre de messages pour désarchiver | 2 messages |

[Inventaire des decks]()
-------------------------------------------

*Actif dans PERF' Innovation et PERF' Historique.*

Le bot commence par trier les decks selon qu'ils appartiennent au standard ('STD' dans le nom de la catégorie) ou à l'historique ('histo' dans le nom de la catégorie ou dans le nom du serveur) 
Ensuite, pour chacune des catégories contenant au moins un deck, un tableau récapitulatif est posté dans tous les salons contenant 'inventaire' dans leurs noms.
Le tableau est ensuite mis à jour par édition à chaque nouvelle passe et la date de mise à jour est indiquée.

### Paramètres de réglages actuels
 
Aucun
