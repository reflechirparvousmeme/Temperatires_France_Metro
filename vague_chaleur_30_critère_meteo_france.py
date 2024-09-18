import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from data_loader import charger_donnees
import random

# Charger les données
donnees = charger_donnees()

# Convertir la colonne 'DATE' en datetime
donnees['DATE'] = pd.to_datetime(donnees['AAAAMMJJ'], format='%Y%m%d')

# Filtrer les données à partir de 1960
donnees = donnees[donnees['DATE'].dt.year >= 1960]
donnees = donnees[donnees['DATE'].dt.year <= 2021]

# Fonction pour vérifier si une station a des données de température continues et non vides depuis 1960
def a_des_donnees_continues(groupe):
    donnees_annuelles = groupe.groupby(groupe['DATE'].dt.year).size()
    return (donnees_annuelles.index.min() == 1960 and 
            donnees_annuelles.index.max() == groupe['DATE'].dt.year.max() and
            donnees_annuelles.size == donnees_annuelles.index.max() - 1960 + 1 and
            groupe['TM'].notna().all())

# Obtenir les stations avec des données de température continues et non vides depuis 1960
stations_depuis_1960 = donnees.groupby('NUM_POSTE').filter(a_des_donnees_continues)['NUM_POSTE'].unique()

print(f"Nombre de stations avec des données continues depuis 1960 : {len(stations_depuis_1960)}")

# Sélectionner aléatoirement 30 stations
if len(stations_depuis_1960) < 30:
    raise ValueError(f"Pas assez de stations avec des données continues depuis 1960. Seulement {len(stations_depuis_1960)} disponibles.")

stations_selectionnees = random.sample(list(stations_depuis_1960), 117)

# Filtrer les données pour les stations sélectionnées
donnees_selectionnees = donnees[donnees['NUM_POSTE'].isin(stations_selectionnees)]

# Calculer la température moyenne quotidienne pour les stations sélectionnées
temp_moy_quotidienne = donnees_selectionnees.groupby('DATE')['TM'].mean().reset_index()

ff = 0.95

# Fonction pour identifier les canicules avec les critères mis à jour
def identifier_canicules(temperatures):
    canicule = np.zeros(len(temperatures), dtype=bool)
    i = 0
    while i < len(temperatures) - 2:
        if (temperatures[i] > 23.4*ff and 
            temperatures[i+1] > 23.4*ff and 
            temperatures[i+2] > 23.4*ff and 
            max(temperatures[i:i+3]) >= 25.3*ff):
            # Début d'une canicule
            debut_canicule = i
            i += 3
            # Continuer la canicule jusqu'à ce que les conditions de fin soient remplies
            while i < len(temperatures):
                if temperatures[i] < 22.4*ff or (i < len(temperatures) - 1 and temperatures[i] <= 23.4*ff and temperatures[i+1] <= 23.4*ff):
                    break
                i += 1
            # Marquer la période de canicule
            canicule[debut_canicule:i] = True
        else:
            i += 1
    return canicule

# Appliquer l'identification des canicules
temp_moy_quotidienne['canicule'] = identifier_canicules(temp_moy_quotidienne['TM'].values)

# Compter les canicules par année
canicules_par_annee = temp_moy_quotidienne.groupby(temp_moy_quotidienne['DATE'].dt.year)['canicule'].sum().reset_index()
canicules_par_annee.columns = ['Année', 'Jours_de_Canicule']

# Calculer le nombre de canicules (périodes continues)
temp_moy_quotidienne['debut_canicule'] = temp_moy_quotidienne['canicule'] & ~temp_moy_quotidienne['canicule'].shift(1).fillna(False)
nombre_canicules = temp_moy_quotidienne.groupby(temp_moy_quotidienne['DATE'].dt.year)['debut_canicule'].sum().reset_index()
nombre_canicules.columns = ['Année', 'Nombre_de_Canicules']

# Fusionner les résultats
resultats = pd.merge(canicules_par_annee, nombre_canicules, on='Année')

# Tracer les résultats
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

ax1.plot(resultats['Année'], resultats['Jours_de_Canicule'], marker='o')
ax1.set_ylabel('Nombre de jours de canicule')
ax1.set_title('Analyse des canicules pour 30 stations sélectionnées aléatoirement (depuis 1960)')
ax1.grid(True)

ax2.plot(resultats['Année'], resultats['Nombre_de_Canicules'], marker='o', color='red')
ax2.set_xlabel('Année')
ax2.set_ylabel('Nombre de canicules')
ax2.grid(True)

plt.tight_layout()
plt.savefig('analyse_canicules.png')


# Afficher quelques statistiques
print(f"Nombre total de canicules de 1960 à {resultats['Année'].max()} : {resultats['Nombre_de_Canicules'].sum()}")
print(f"Année avec le plus de canicules : {resultats.loc[resultats['Nombre_de_Canicules'].idxmax(), 'Année']} ({resultats['Nombre_de_Canicules'].max()} canicules)")
print(f"Année avec le plus de jours de canicule : {resultats.loc[resultats['Jours_de_Canicule'].idxmax(), 'Année']} ({resultats['Jours_de_Canicule'].max()} jours)")

# Sauvegarder les résultats dans un fichier CSV
resultats.to_csv('resultats_analyse_canicules.csv', index=False)

plt.show()