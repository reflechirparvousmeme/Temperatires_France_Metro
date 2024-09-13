import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
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

# Charger les données
donnees_combinees = charger_donnees()

# Convertir la colonne 'DATE' en datetime et extraire l'année
donnees_combinees['DATE'] = pd.to_datetime(donnees_combinees['AAAAMMJJ'], format='%Y%m%d')
donnees_combinees['ANNEE'] = donnees_combinees['DATE'].dt.year

# Filtrer les données entre 1960 et 2022
donnees_filtrees = donnees_combinees[(donnees_combinees['ANNEE'] >= 1960) & (donnees_combinees['ANNEE'] <= 2022)]

# Compter le nombre de stations uniques par année
stations_par_annee = donnees_filtrees.groupby('ANNEE')['NUM_POSTE'].nunique()

# Créer le graphique
fig, ax1 = plt.subplots(figsize=(15, 8))

# Tracer le nombre de stations par année
color = 'tab:blue'
ax1.set_xlabel('Année')
ax1.set_ylabel('Nombre de stations actives', color=color)
ax1.plot(stations_par_annee.index, stations_par_annee.values, color=color, marker='o')
ax1.tick_params(axis='y', labelcolor=color)

# Ajouter un titre
plt.title('Nombre de stations météorologiques par année (1960-2022)')

# Améliorer la lisibilité de l'axe des x
plt.xticks(range(1960, 2023, 5), rotation=45)

# Ajouter une grille pour une meilleure lisibilité
ax1.grid(True, linestyle='--', alpha=0.7)

# Ajouter des étiquettes de nombre de stations tous les 5 ans
for annee in range(1960, 2023, 5):
    if annee in stations_par_annee.index:
        nombre_stations = stations_par_annee[annee]
        ax1.text(annee, nombre_stations, f'{nombre_stations}', 
                 ha='center', va='bottom', fontweight='bold', color='tab:blue')

# Ajuster la mise en page et les marges
fig.tight_layout()
plt.margins(y=0.1)  # Ajouter un peu d'espace en haut pour les étiquettes

# Afficher le graphique
plt.show()

# Afficher quelques statistiques
print(f"Nombre minimum de stations actives : {stations_par_annee.min()} (Année : {stations_par_annee.idxmin()})")
print(f"Nombre maximum de stations actives : {stations_par_annee.max()} (Année : {stations_par_annee.idxmax()})")
print(f"Nombre moyen de stations actives par an : {stations_par_annee.mean():.2f}")