# GaliTime - Photomaton de Galileo
> Version 3.2.4
---
## Principe
Le but de ce projet est la construction, le maintien et l'amélioration du Photomaton de Galiléo, appelé GaliTime (nom etant sujet à changements).

Ce projet en est actuellement a sa version 3 et a ete réecrit par Antoine LANGUILLE et amelioré par les equipes de Galileo.

Les differentes parties du système sont développées ci-dessous.
---
## Description
Le boitier Photomaton se compose d'une base roulante non motorisée sur laquelle repose le photomaton en lui-même.

De l'extérieur, 7 ouvertures sont amenagées dans le chassis:
- 2 pour les écrans dont un tactile
- 2 pour l'appareil er son flash
- 2 ventilateurs
- 1 porte d'accès et maintenance à serrure 

Deux panneaux LED sont accrochés en exterieur face a l'écran de visualisation.
---
## Electronique
Le système repose sur un PC peu puissant foirni avec Linux Ubuntu relié au secteur par un câble filaire sortant a l'arriere du photomaton.

L'appareil est un Canon D50 alimenté par un adaptateur filaire et connecté par un cable USB-B vers USB au PC.

Les panneaux LED sont connectés au secteur par l'intermediaire de blocs d'alimentation 220VAC - 5VDC.

---
## Logiciel
### Présentation

La version 3 du logiciel vise a remplacer le précédent logiciel en PHP par une version plus légère et rapide ecrite en Python.

Cette version 3 utilise principalement 2 librairies python extérieures pour ses opérations:
-PyQt5 pour le GUI
-gphoto2 pour le contrôle de la caméra

Le code est reparti en plusieurs classes multi responsables pour faciliter le développement et isoler les rôles de chaque classe.

Chaque fichier essaie de respzcter au possible les bonnes pratiques PEP par l'intermediaire des librairies `black` et `pylint`.

### Particularités
1. Le code de la classe ControlWindow a été séparé en deux fichiers:
- `controlwindow.py` contenant le code graphique de génération des fenêtres et menus
- `controlfunctions.py` contenant les fonctions de contrôle, d'interaction, de sauvegarde etc.


Cette approche est discutable, elle a principalement été choisie pour éviter une naviguation chaotique.
Le principal inconvenient est dans la syntaxe des fonctions de commande, devant explicitement inclure un argument `self` lorsque celles-ci operent sur la classe.
Des syntaxes irrévérencieuses type `x = method(self, args)` sont donc nécessaires.

2. La librairie py-gphoto2 ne supporte pas l'enregistrement de videos, nécessaire à l'aperçu avant photo. Le paquet linux lui le supporte.
Ainsi, un appel a la console avec la librairie `subprocess` est nécessaire pour déclencher l'acquisition.

3. Le format `.mjpg` n'etant pas supporté par PyQt5 et son format étant simple, le fichier d'output generé par la capture est directement lu. La derniere frame `.jpeg` est alors extraite et affichee en tant qu'image.

4. Pour limiter la taille du fichier `movie.mjpg`, la capture est redemarrée toutes les 30 secondes pour clear ce fichier.

---
## TODO
- Driver imprimante
- Bot envoi mail
- Gestionnaire de mails 
- Organisation en albums / pages
- Photo supprimée si pas de destinataire