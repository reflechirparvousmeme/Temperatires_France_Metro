
Scripts Python et données utilisées pour la video Youtube de la Chaine "Réfléchir par vous meme" de debunk du Post Twitter/X.

Ce projet analyse les données climatiques des stations météorologiques françaises pour identifier les tendances (ou pas) des extêmes de température et les vagues de chaleur. Il comprend plusieurs scripts Python pour le traitement, l'analyse et la visualisation des données.

Lien de la vidéo Youtube: [https://youtu.be/YspWkjcXPek](https://youtu.be/YspWkjcXPek)

VOUS DEVEZ DÉZIPPER LES FICHIERS .zip dans le dossier `data` .

## Prérequis

- Python 3.x
- pandas
- numpy
- matplotlib
- Basemap (pour la visualisation cartographique)

## Installation

1. Clonez ce dépôt :
   ```
   git clone https://github.com/reflechirparvousmeme/Temperatures_France_Metro.git
   cd temperatures_france_metro
   ```

2. Installez les paquets requis :
   ```
   pip install pandas numpy matplotlib basemap
   ```

## Utilisation

1. Assurez-vous que vos fichiers de données sont dans le répertoire `./data`.
2. Exécutez le script souhaité :
   ```
   python nom_du_script.py
   ```

## Description des scripts

### data_loader.py
- Charge et combine les données à partir de fichiers CSV ou d'un fichier pickle.
- Filtre les colonnes inutiles et les valeurs nulles.

### check_stations.py
- Analyse le nombre de stations météorologiques actives par année.
- Génère un graphique montrant l'évolution des stations actives de 1960 à 2022.

### calcul_percentile999_exemple_aleatoire.py
- Sélectionne une station aléatoire et calcule le 99.9ème percentile des températures quotidiennes.
- Crée un histogramme de la distribution des températures pour la station sélectionnée.

### temperature_sup_95pc.py
- Calcule le pourcentage de stations dépassant la température du 99.9ème percentile (basé sur les données 1960-1990).
- Génère des graphiques montrant l'évolution des extrêmes de température.
- Crée une carte des stations météorologiques en France.

### vagues_chaleurs_France_metro.py
- Identifie les vagues de chaleur basées sur 6 jours consécutifs de températures maximales au-dessus du 90ème percentile (période de référence 1960-1990).
- Analyse la fréquence des vagues de chaleur de 1994 à 2022.
- Génère des graphiques montrant l'évolution des vagues de chaleur et le nombre de stations utilisées.

## Données

Les scripts s'attendent à des fichiers CSV contenant des données de température quotidiennes pour les stations météorologiques françaises. Les données doivent inclure les colonnes suivantes :

- NUM_POSTE : Identifiant de la station
- NOM_USUEL : Nom de la station
- LAT : Latitude
- LON : Longitude
- ALTI : Altitude
- AAAAMMJJ : Date de la mesure
- TX : Température maximale du jour, celcius, sous abris
- TN : Température minimale du jour, celcius, sous abris
- TM : Température moyenne du jour, celcius, sous abris

## Sortie

Les scripts génèrent divers fichiers de sortie :

- Fichiers PNG avec des graphiques et des visualisations
- Fichiers CSV avec des données traitées
- Un fichier pickle pour un chargement plus rapide des données lors des exécutions ultérieures
