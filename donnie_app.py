"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import os
import pandas as pd
import numpy as np
import time

os.curdir="C:/Users/donnie.mounguengui/Documents/2025_IEF_Spécialité/Stage_aux_Impots/Travaux_Python_Sujet1"

#1
st.title("Tous les contrib. avec indicateurs et leur score")

# Importation du fichier Excel
risque_contrib=pd.read_excel(os.curdir+"/"+"Liste_risques_contrib.xlsx")

# Tri du fichier par score
risque_contrib_masq=risque_contrib[["Num_contrib.","Secteur_d'activité", 'Statut_contrib',
       "Etat_d'adhésion", "Date_d'immatriculation",
       'Ratio_ca_alarm', 'Décla_hors_délai', 'Plus_de_7_décla_tard_2024',
       'Part_det_fisc', 'Part_dégrèv', 'Plus_d_AMR', 'AMR_forcé',
       'Décla_tva_tardive', 'Pay_TVA_sans_décla', 'A_plus_de_7_crédit_TVA',
       'Score']]
risque_contrib_tri=risque_contrib_masq.sort_values(by="Score", ascending=False)
st.dataframe(risque_contrib_tri)

# 2
st.title("Contrib. par niveau de risque")

# Définition des seuils

seuil=st.selectbox("Choisissez le niveau de risque des contribuables", 
                   ("Nul", "Faible", "Moyen", "Elevé"))

def filtre_contrib(base, selection) :
  if selection=="Nul":
    return base[base["Score"]==0]
  elif selection=="Faible" :
    return base[(base["Score"]>=1) & (base["Score"]<4)]
  elif selection=="Moyen" :
    return base[(base["Score"]>=4) & (base["Score"]<7)]
  else :
    return base[base["Score"]>=7]

contrib_filtr=filtre_contrib(risque_contrib_tri, seuil)

# Afficher

st.write(f"{contrib_filtr.shape[0]} Contribuables avec un risque {seuil}")
st.dataframe(contrib_filtr)
