import pandas as pd
import numpy as np
import os
import glob
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

donnees = charger_donnees()

# Convertir la colonne 'DATE' en objet datetime, plus pratique
donnees['DATE'] = pd.to_datetime(donnees['AAAAMMJJ'].astype(str), format='%Y%m%d')

nombre_total_stations = donnees['NUM_POSTE'].nunique()
print(f"Nombre total de stations météorologiques : {nombre_total_stations}")

# Filtrer les données et ne garder que de 1960 à 2022
donnees = donnees[donnees['DATE'].dt.year >= 1960]
donnees = donnees[donnees['DATE'].dt.year <= 2022]

# On s'assure que la colonne 'DATE' est au format datetime
donnees['DATE'] = pd.to_datetime(donnees['DATE'])

donnees = donnees.sort_values('DATE')

# Calculer le percentile 99.9 pour chaque station pour la période 1960-1990
periode_reference = donnees[(donnees['DATE'].dt.year >= 1960) & (donnees['DATE'].dt.year <= 1990)]
percentile_999 = periode_reference.groupby('NUM_POSTE')['TX'].quantile(0.999)

# ne garder que à partir de 1960
donnees = donnees[(donnees['DATE'].dt.year >= 1960)]

# Créer une colonne indiquant si la température dépasse le percentile 99.9
donnees['depasse_percentile'] = donnees.apply(lambda row: row['TX'] > percentile_999.get(row['NUM_POSTE'], np.inf), axis=1)
# Grouper par année et station, et vérifier s'il y a au moins un dépassement
depassements_annuels = donnees.groupby([donnees['DATE'].dt.year, 'NUM_POSTE'])['depasse_percentile'].any().reset_index()
# Compter le nombre de stations dépassant le seuil pour chaque année, ici DATE ne contient plus que l'année
resultats = depassements_annuels.groupby('DATE')['depasse_percentile'].sum().reset_index()
resultats.columns = ['Année', 'Nombre_Stations_Depassant']
# Calculer le nombre total de stations par année pour comparaison
stations_totales = donnees.groupby(donnees['DATE'].dt.year)['NUM_POSTE'].nunique().reset_index()
stations_totales.columns = ['Année', 'Nombre_Stations_pour_cette_annee']
# Fusionner les résultats
resultats = pd.merge(resultats, stations_totales, on='Année')
# Calculer le pourcentage de stations dépassant le seuil
resultats['Pourcentage_Stations_Depassant'] = (resultats['Nombre_Stations_Depassant'] / resultats['Nombre_Stations_pour_cette_annee']) * 100.0
# Trier les résultats par année
resultats = resultats.sort_values('Année')

# Afficher les résultats
print(resultats)

# Créer la figure avec deux sous-graphiques

# Graphique du pourcentage de stations au-dessus du percentile 99.9
plt.plot(resultats['Année'], resultats['Pourcentage_Stations_Depassant'], marker='o')
plt.set_ylabel('Pourcentage de stations (%)')
plt.set_title('Pourcentage de stations au-dessus du percentile 99.9 1960-1990')
plt.grid(True, linestyle='--', alpha=0.7)

# Ajuster la disposition des sous-graphiques
plt.tight_layout()

# Rotation des étiquettes de l'axe x pour une meilleure lisibilité
plt.xticks(rotation=45)

plt.show()

##
stations_percentile = pd.DataFrame({
    'NOM_USUEL': donnees.groupby('NUM_POSTE')['NOM_USUEL'].first(),
    'Percentile_99': percentile_999
}).reset_index()

# Trier les stations par percentile décroissant et prendre les 30 premières
top_stations = stations_percentile.sort_values('Percentile_99', ascending=False).head(25)

print(stations_percentile.sort_values('Percentile_99', ascending=False).head(100))

# Créer le graphique
plt.figure(figsize=(15, 8))
bars = plt.bar(top_stations['NOM_USUEL'], top_stations['Percentile_99'])
plt.xlabel('Nom de la station')
plt.ylabel('percentile 99.9 de température (1960-1990)')
plt.title(f'percentile 99.9 de température par station (1960-1990), TOP 25 sur un total de {nombre_total_stations} stations')
plt.xticks(rotation=90)

# Ajouter les valeurs sur les barres
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}°C',
             ha='center', va='bottom', rotation=0)

plt.tight_layout()
plt.savefig('percentile_99_par_station.png')
plt.show()


## carte des stations
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np

# Créer une nouvelle figure
plt.figure(figsize=(10, 10))

# Créer la carte
m = Basemap(llcrnrlat=41, urcrnrlat=52, llcrnrlon=-5, urcrnrlon=10,
            resolution='i', projection='tmerc', lat_0=46, lon_0=2)

# Dessiner les côtes, pays, et états
m.drawcoastlines()
m.drawcountries()
m.fillcontinents(color='lightgrey', lake_color='white')
m.drawmapboundary(fill_color='white')

# Convertir les coordonnées lat/lon en coordonnées de la carte
x, y = m(donnees['LON'].values, donnees['LAT'].values)

# Tracer les points des stations
m.scatter(x, y, marker='o', color='red', s=10, zorder=5)

# Ajouter un titre
plt.title(f'{nombre_total_stations} stations météorologiques en France gardées')

# Sauvegarder la carte
plt.savefig('carte_stations_france_simple.png', dpi=300, bbox_inches='tight')

# Afficher la carte
plt.show()