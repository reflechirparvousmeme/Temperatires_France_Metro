import pandas as pd
import os
import pickle

def charger_donnees(nom_fichier_pickle='donnees_combinees.pickle', dossier_data='./data'):
    """
    Charge les données soit à partir d'un fichier pickle existant,
    soit en lisant et combinant tous les fichiers CSV dans le dossier spécifié.
    
    :param nom_fichier_pickle: Nom du fichier pickle à utiliser/créer
    :param dossier_data: Chemin du dossier contenant les fichiers CSV
    :return: DataFrame pandas contenant les données combinées
    """
    # Vérifier si le fichier pickle existe
    if os.path.exists(nom_fichier_pickle):
        print("Chargement des données depuis le fichier pickle...")
        with open(nom_fichier_pickle, 'rb') as f:
            return pickle.load(f)
    else:
        print("Fichier pickle non trouvé. Chargement des fichiers CSV...")
        # Colonnes à filtrer
        colonnes_a_supprimer = ['QHXI', 'FXI2', 'QFXI2', 'DXI2', 'QDXI2', 'HXI2', 'QHXI2', 
                                'FXI3S', 'QFXI3S', 'DXI3S', 'QDXI3S', 'HXI3S', 'QHXI3S', 
                                'DRR', 'QDRR', 'FF2M',  'QFF2M',  'FXY',  'QFXY',  'DXY',  'QDXY',  'HXY',  'QHXY', 
                                'TNSOL',  'QTNSOL',  'TN50',  'QTN50',  'DG',  'QDG',
                                'DXI',  'QDXI',  'HXI', 'DXY',  'QDXY', 'HTN',  'QHTN', 'HTX',  'QHTX']

        # Charger tous les fichiers CSV du dossier 'data'
        donnees_combinees = pd.DataFrame()

        for fichier in os.listdir(dossier_data):
            if fichier.endswith('.csv'):
                chemin_fichier = os.path.join(dossier_data, fichier)
                donnees = pd.read_csv(chemin_fichier, sep=';', encoding='utf-8')
                
                # Filtrer les données pour garder seulement les lignes où 'TN', 'TX', et 'TM' ne sont pas nuls
                donnees_filtrees = donnees.dropna(subset=['TN', 'TX', 'TM'])
                
                # Supprimer les colonnes inutilisées
                donnees_filtrees = donnees_filtrees.drop(columns=colonnes_a_supprimer, errors='ignore')
                
                donnees_combinees = pd.concat([donnees_combinees, donnees_filtrees], ignore_index=True)

        # Sauvegarder les données combinées dans un fichier pickle
        print("Sauvegarde des données dans un fichier pickle...")
        with open(nom_fichier_pickle, 'wb') as f:
            pickle.dump(donnees_combinees, f)

        return donnees_combinees