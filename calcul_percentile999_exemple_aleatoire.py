import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
import os
from data_loader import charger_donnees

# Fonction pour changer le répertoire de travail
def changer_repertoire_script():
    # Obtenir le répertoire du script actuel
    repertoire_script = os.path.dirname(os.path.abspath(__file__))
    # Changer le répertoire de travail courant
    os.chdir(repertoire_script)
    print(f"Répertoire de travail changé pour : {repertoire_script}")

changer_repertoire_script()

donnees_combinees = charger_donnees()

# Convertir la colonne 'DATE' en datetime et extraire l'année
donnees_combinees['DATE'] = pd.to_datetime(donnees_combinees['AAAAMMJJ'], format='%Y%m%d')
donnees_combinees['ANNEE'] = donnees_combinees['DATE'].dt.year

# Filtrer les données entre 1960 et 1990
donnees_filtrees = donnees_combinees[(donnees_combinees['ANNEE'] >= 1960) & (donnees_combinees['ANNEE'] <= 1990)]

# Sélectionner une station au hasard
stations = donnees_combinees['NOM_USUEL'].unique()
station_aleatoire = random.choice(stations)

# Filtrer les données pour la station sélectionnée
donnees_station = donnees_combinees[donnees_combinees['NOM_USUEL'] == station_aleatoire]

# Calculer la moyenne des températures quotidiennes (TM)
temperatures = donnees_station['TX'].dropna()

# Calculer le 99.9ème percentile
percentile_99_9 = np.percentile(temperatures, 99.9)

# Créer l'histogramme
plt.figure(figsize=(10, 6))
plt.hist(temperatures, bins=50, edgecolor='black')
plt.axvline(percentile_99_9, color='red', linestyle='dashed', linewidth=2)

# Ajouter des étiquettes et un titre
plt.xlabel('Température moyenne quotidienne (°C)')
plt.ylabel('Fréquence')
plt.title(f'Distribution des températures journalières 1960-1990 pour la station {station_aleatoire}. Nb de valeurs: {len(temperatures)}')

# Ajouter une légende pour la ligne du percentile
plt.legend([f'99.9ème percentile: {percentile_99_9:.2f}°C'])

# Afficher le graphique
plt.show()

# Afficher des informations sur la station et les températures
print(f"Station sélectionnée : {station_aleatoire}")
print(f"Nombre total de jours : {len(temperatures)}")
print(f"Température moyenne : {temperatures.mean():.2f}°C")
print(f"Température minimale : {temperatures.min():.2f}°C")
print(f"Température maximale : {temperatures.max():.2f}°C")
print(f"99.9ème percentile : {percentile_99_9:.2f}°C")