"""
Mon application pour présenter les résultats de mon analyse risque
"""
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import time
import openpyxl
import io


st.set_page_config(page_title="Analyse du risque fiscal", layout="wide")

# =========================
# CHARGEMENT DES DONNÉES
# =========================
@st.cache_data
def charger_donnees():
    return pd.read_excel(
        "C:/Users/donnie.mounguengui/Documents/2025_IEF_Spécialité/Stage_aux_Impots/Travaux_Python_Sujet1/Liste_risques_contrib.xlsx"
    )

ana_risq = charger_donnees()

# =========================
# BARRE LATÉRALE – NAVIGATION
# =========================
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Choisissez une page",
    ("Page 1 – Indicateurs", "Page 2 – Scores", "Page 3 – Contribuables à risque")
)

st.sidebar.markdown("---")

# =========================
# BARRE LATÉRALE – FILTRES
# =========================
st.sidebar.title("Filtres principaux")
st.sidebar.markdown("---")

annee = st.sidebar.selectbox(
    "Année d'analyse",
    ("2023", "2024", "2025", "Global")
)

# Colonnes dynamiques selon l’année
if annee == "Global":
    col_score = "Score global"
    col_risque = "Niveau_de_risque_global"
    prefix_ind = ""
else:
    col_score = f"Score {annee}"
    col_risque = f"Niveau_de_risque_{annee}"
    prefix_ind = f"_{annee[-2:]}"

st.sidebar.markdown("---")

# Filtre niveau de risque
niveaux_disponibles = ana_risq[col_risque].dropna().unique()
niveau_risque = st.sidebar.multiselect(
    "Niveau de risque",
    options=niveaux_disponibles,
    default=niveaux_disponibles
)

st.sidebar.markdown("---")

# Bornes de score conditionnelles au niveau de risque
if niveau_risque:
    score_min_auto = int(
        ana_risq.loc[ana_risq[col_risque].isin(niveau_risque), col_score].min()
    )
    score_max_auto = int(
        ana_risq.loc[ana_risq[col_risque].isin(niveau_risque), col_score].max()
    )
else:
    score_min_auto = int(ana_risq[col_score].min())
    score_max_auto = int(ana_risq[col_score].max())

# Filtre score
score_min, score_max = st.sidebar.slider(
    "Score",
    min_value=score_min_auto,
    max_value=score_max_auto,
    value=(score_min_auto, score_max_auto)
)

# Application des filtres
base_filtree = ana_risq[
    (ana_risq[col_risque].isin(niveau_risque)) &
    (ana_risq[col_score] >= score_min) &
    (ana_risq[col_score] <= score_max)
].copy()

base_filtree = base_filtree.sort_values(by=col_score, ascending=False)

# =========================
# PAGE 1 – INDICATEURS
# =========================
if page == "Page 1 – Indicateurs":

    st.title(f"📊 Indicateurs de risque de la période {annee} pour le(s) risque(s) : {niveau_risque}")

    # Sélection des indicateurs de l’année
    if annee=="Global" :
      cols_indicateurs = [col for col in ana_risq.columns if col.endswith(("_23", "_24", "_25"))]  
    else : 
      cols_indicateurs = [c for c in ana_risq.columns if c.endswith(prefix_ind)]

    col1, col2 = st.columns(2)
    col1.metric(f"Nombre d’indicateurs", len(cols_indicateurs))
    col2.metric(f"Nombre de contribuables", base_filtree[base_filtree[col_risque].isin(niveau_risque)].shape[0])

    st.markdown("### 📌 Proportion des indicateurs")

    proportions1 = (
        base_filtree[cols_indicateurs]  # Utilisez cols_indicateurs (liste)
        .mean()                      # Moyenne par colonne = proportion 1's
        .sort_values(ascending=False)
        .round(3)
    )

    proportions=proportions1*100

    
# Tracé du diagramme en barre horizontal
    fig, ax = plt.subplots(figsize=(8, max(4, len(proportions) * 0.35)))

    proportions.sort_values().plot(
    kind="barh",
    ax=ax
    )

    ax.set_xlabel("Proportion (%)")
    ax.set_ylabel("Indicateurs")
    ax.set_title("Proportion d’activation des indicateurs (%)")

    # Affichage des pourcentages sur les barres
    for i, v in enumerate(proportions.sort_values()):
        ax.text(v + 0.5, i, f"{v:.1f}%", va="center")

    st.pyplot(fig)

    st.info(
            "Une proportion élevée signifie que l’indicateur est fréquemment activé "
            "dans la population analysée."
        )

# =========================
# PAGE 2 – SCORES
# =========================
elif page == "Page 2 – Scores":

    st.title(f"📈 Scores de la période {annee} pour le(s) risque(s) : {niveau_risque}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Score moyen", round(base_filtree[col_score].mean(), 2))
    col3.metric("Score maximal", base_filtree[col_score].max())

    st.markdown("### 📊 Distribution des scores")
    st.bar_chart(base_filtree[col_score].value_counts().sort_index())

    st.info(
        "Les boîtes à moustaches permettent d’évaluer la dispersion du risque "
    )

# =========================
# PAGE 3 – CONTRIBUABLES À RISQUE
# =========================
else:

    st.title(f"🧾 Contribuables à risque de la période {annee} pour le(s) risque(s) : {niveau_risque}")

    col1, col2 = st.columns(2)
    col1.metric(f"Nombre de contribuables : ", base_filtree[base_filtree[col_risque].isin(niveau_risque)].shape[0])
    col2.metric("Score maximal", base_filtree[col_score].max())
    
    if annee=="Global" :
      colonnes_affichage = (
        ["Num_contrib.", "Type_de_contribuable", "Centre_fiscal", col_score, col_risque] +
        [col for col in ana_risq.columns if col.endswith(("_23", "_24", "_25"))]
       ) 
    else :
      colonnes_affichage = (
        ["Num_contrib.", "Type_de_contribuable", "Centre_fiscal", col_score, col_risque] +
        [c for c in ana_risq.columns if c.endswith(prefix_ind) and not c.startswith("Niveau_de_ris")]
    )
    colonnes_affichage = [c for c in colonnes_affichage if c in ana_risq.columns]

    st.dataframe(
        base_filtree[colonnes_affichage],
        use_container_width=True
    )

    # Export
    def convertir_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Contribuables")
        return output.getvalue()

    excel = convertir_excel(base_filtree[colonnes_affichage])

    st.download_button(
        "⬇️ Télécharger la liste des contribuables",
        data=excel,
        file_name=f"Contribuables_risque_{annee}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# streamlit run c:/Users/donnie.mounguengui/Documents/2025_IEF_Spécialité/Stage_aux_Impots/Travaux_Python_Sujet1/donnie_app.py [ARGUMENTS]