# GaliTime - Photomaton de Galileo

> Version 3.3.1

---

## Principe

Le but de ce projet est la construction, le maintien et l'amélioration du Photomaton de Galiléo, appelé GaliTime (nom étant sujet à changements).

Ce projet en est actuellement à sa version 3. Le logiciel à été réecrit par Antoine LANGUILLE et le boitier amelioré par les équipes de Galileo.

Les differentes parties du système sont développées ci-dessous.

---

## Description

Le boitier Photomaton se compose d'une base roulante non motorisée immobilisable (pour l'instant avec des supports 3D) sur laquelle repose le photomaton en lui-même.

De l'extérieur, 7 ouvertures sont amenagées dans le chassis:
- 2 pour les écrans dont un tactile
- 2 pour l'appareil et son flash
- 2 ventilateurs
- 1 porte d'accès et maintenance à serrure 

Deux panneaux LED sont accrochés en exterieur face à l'écran de 
visualisation.

---

## Electronique

Le système repose sur un PC peu puissant fourni avec Linux Ubuntu relié au secteur par un câble filaire sortant a l'arriere du photomaton et idéalement relié au réseau pour un envoi par mail direct.

L'appareil est un Canon D50 alimenté par un adaptateur filaire et connecté par un cable USB-B vers USB au PC.

Les panneaux LED sont connectés au secteur par l'intermediaire de blocs d'alimentation 220VAC - 5VDC.

---

## Logiciel

### Présentation

La version 3 du logiciel vise à remplacer le précédent logiciel en PHP par une version plus légère et rapide ecrite en Python, ne dépendant pas d'un navigateur Web.

Cette version 3 utilise principalement 2 librairies python extérieures pour ses opérations:
-`PyQt5` pour le GUI
-`gphoto2` pour le contrôle de la caméra

Le code est reparti en plusieurs classes pour faciliter le développement et isoler les rôles de chaque classe.

Chaque fichier essaie de respecter au possible les bonnes pratiques PEP par l'intermediaire des librairies `black` et `pylint`.

### Particularités

1. La librairie gphoto2 ne supporte pas l'enregistrement de videos, nécessaire à l'aperçu avant photo. Le paquet linux supporte cette fonctionnalité et a donc été uilisé en complément.
Ainsi, un appel à la librairie `subprocess` est nécessaire pour déclencher l'acquisition.

3. Le format `.mjpg` n'etant pas supporté par PyQt5 et son format étant simple, le fichier d'output generé par la capture est directement lu. La derniere frame `.jpeg` est alors extraite et affichee en tant qu'image.

4. Pour limiter la taille du fichier `movie.mjpg`, la capture est redemarrée toutes les 30 secondes pour clear ce fichier.

---

## TODO

- Driver imprimante (à tester)
- Bot envoi mail (à tester)
- Organisation en albums / pages
- Photo supprimée si pas de destinataire