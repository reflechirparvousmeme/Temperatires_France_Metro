import pandas as pd
import numpy as np
import os
import glob
from datetime import timedelta
import matplotlib.pyplot as plt
from data_loader import charger_donnees

# NUM_POSTE   : numero Meteo-France du poste sur 8 chiffres
# NOM_USUEL   : nom usuel du poste
# LAT         : latitude, negative au sud (en degres et millioniemes de degre)
# LON         : longitude, negative a  l'ouest de GREENWICH (en degres et millioniemes de degre)
# ALTI        : altitude du pied de l'abri ou du pluviometre si pas d'abri (en m)
# AAAAMMJJ    : date de la mesure (annee mois jour)
# RR          : quantite de precipitation tombee en 24 heures (de 06h FU le jour J a  06h FU le jour J+1). La valeur relevee a  J+1 est affectee au jour J (en mm et 1/10)
# TN          : temperature minimale sous abri (en °C et 1/10)
# HTN         : heure de TN (hhmm)
# TX          : temperature maximale sous abri (en °C et 1/10)
# HTX         : heure de TX (hhmm)
# TM          : moyenne quotidienne des temperatures horaires sous abri (en °C et 1/10)

def changer_repertoire_script():
    # Obtenir le répertoire du script actuel
    repertoire_script = os.path.dirname(os.path.abspath(__file__))
    # Changer le répertoire de travail actuel
    os.chdir(repertoire_script)
    print(f"Répertoire de travail changé pour : {repertoire_script}")

changer_repertoire_script()

# Concaténer tous les DataFrames
donnees = charger_donnees()

# Convertir la colonne 'DATE' en datetime, en considérant le format AAAAMMJJ
donnees['DATE'] = pd.to_datetime(donnees['AAAAMMJJ'].astype(str), format='%Y%m%d')

# Calculer le nombre de stations météorologiques gardées
nombre_stations = donnees['NUM_POSTE'].nunique()
print(f"Nombre gardé de stations météorologiques : {nombre_stations}")

# on evite 2024 car incomplet
donnees = donnees[(donnees['DATE'].dt.year <= 2022)]

# Calculer le 90eme percentile pour chaque station pour la période 1960-1990
periode_reference = donnees[
    (donnees['DATE'].dt.year >= 1960) & 
    (donnees['DATE'].dt.year <= 1990)
]
percentile_90 = periode_reference.groupby('NUM_POSTE')['TX'].quantile(0.90)

# Fonction pour identifier les vagues de chaleur
# vague de chaleur = pour une station donnée, periode de minimum 6 jours de température supérieure au 90eme percentile 1960-1990.
def identifier_vagues_chaleur(groupe):
    num_poste = groupe['NUM_POSTE'].iloc[0]
    if num_poste not in percentile_90.index:
        return pd.DataFrame()  # Retourner un DataFrame vide si la station n'a pas de données dans la période de référence
    
    seuil = percentile_90[num_poste]
    groupe = groupe.sort_values('DATE')
    groupe['au_dessus_percentile'] = groupe['TX'] > seuil
    groupe['debut_vague'] = (groupe['au_dessus_percentile'] != groupe['au_dessus_percentile'].shift()).cumsum()
    vagues = groupe[groupe['au_dessus_percentile']].groupby('debut_vague')
    vagues_6jours = vagues.filter(lambda x: len(x) >= 6)
    
    # Identifier les vagues de chaleur uniques
    vagues_uniques = vagues_6jours.drop_duplicates(subset=['debut_vague'])
    vagues_uniques['annee'] = vagues_uniques['DATE'].dt.year
    
    return vagues_uniques[['annee', 'debut_vague']]

# Filtrer les données à partir de 1994
donnees = donnees[donnees['DATE'].dt.year >= 1994]

# Calculer le nombre total de stations chaque année pour corriger le nombre de vagues de chaleur
stations_totales = donnees.groupby(donnees['DATE'].dt.year)['NUM_POSTE'].nunique().reset_index()

# Identifier les vagues de chaleur pour toutes les stations
vagues_chaleur = donnees.groupby('NUM_POSTE').apply(identifier_vagues_chaleur).reset_index(drop=True)

# Compter le nombre de vagues de chaleur par an
vagues_chaleur_par_an = vagues_chaleur.groupby('annee').size().reset_index(name='Nombre_Vagues_Chaleur')
vagues_chaleur_par_an = vagues_chaleur_par_an.rename(columns={'annee': 'Année'})

# Calculer le nombre total de stations chaque année pour corriger le nombre de vagues de chaleur
stations_totales = donnees.groupby(donnees['DATE'].dt.year)['NUM_POSTE'].nunique().reset_index()

# Afficher les résultats
print(vagues_chaleur_par_an)

# Sauvegarder les résultats dans un fichier CSV
vagues_chaleur_par_an.to_csv('vagues_chaleur_par_an.csv', index=False)

print(f"Nombre total de vagues de chaleur depuis 1994 : {vagues_chaleur_par_an['Nombre_Vagues_Chaleur'].sum()}")
print(f"Année avec le plus de vagues de chaleur : {vagues_chaleur_par_an.loc[vagues_chaleur_par_an['Nombre_Vagues_Chaleur'].idxmax(), 'Année']} ({vagues_chaleur_par_an['Nombre_Vagues_Chaleur'].max()} vagues)")

# Créer le graphique
import matplotlib.pyplot as plt

# Créer une figure et deux sous-graphes (subplots)
fig, (ax1,ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# Tracer le premier graphique : Nombre de vagues de chaleur par station
ax1.plot(vagues_chaleur_par_an['Année'].astype(int), 
         vagues_chaleur_par_an['Nombre_Vagues_Chaleur'] / stations_totales['NUM_POSTE'], 
         marker='o', color='b', label="Vagues de chaleur par station")
ax1.set_xlabel('Année')
ax1.set_ylabel('Nombre de vagues de chaleur par station', color='b')
ax1.tick_params(axis='y', labelcolor='b')
ax1.set_title(f"Nombre de vagues de chaleur par année\n"
              f"(Basé sur {nombre_stations} stations météorologiques en France métropolitaine).\n"
              "Vague de chaleur = période de minimum 6 jours consécutifs de température maximale\n"
              "supérieure au 90ème percentile 1960-1990.")

# Ajouter la grille pour le premier axe
ax1.grid(True, linestyle='--', alpha=0.7)

# Rotation des étiquettes de l'axe x pour une meilleure lisibilité
ax1.set_xticks(vagues_chaleur_par_an['Année'])
ax1.set_xticklabels(vagues_chaleur_par_an['Année'], rotation=45)

# Créer un deuxième axe y pour tracer le nombre total de stations météorologiques
ax2.plot(vagues_chaleur_par_an['Année'].astype(int), 
         stations_totales['NUM_POSTE'], 
         marker='s', color='g', label="Nombre total de stations")
ax2.set_ylabel('Nombre de stations utilisées chaque année', color='g')
ax2.tick_params(axis='y', labelcolor='g')
ax2.grid(True, linestyle='--', alpha=0.7)
# Ajuster automatiquement les marges
fig.tight_layout()

# Sauvegarder le graphique
plt.savefig('vagues_chaleur_par_an_et_stations.png')

# Afficher le graphique (optionnel)
plt.show()
