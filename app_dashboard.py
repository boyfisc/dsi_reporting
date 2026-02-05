import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

# --- CONFIGURATION (Mode TV Plein Écran) ---
st.set_page_config(page_title="DSI TV", layout="wide", initial_sidebar_state="collapsed")

# --- CSS SPÉCIAL TV (Pour supprimer les espaces vides et éviter le scroll) ---
st.markdown("""
<style>
    /* Réduire drastiquement les marges */
    .block-container { padding-top: 0rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Style des gros chiffres (KPI) */
    div[data-testid="stMetricValue"] { font-size: 2rem !important; color: #4F8BF9; }
    div[data-testid="stMetricLabel"] { font-size: 0.9rem !important; color: #BBBBBB; }
    
    /* Fond sombre */
    .stApp { background-color: #0E1117; }
</style>
""", unsafe_allow_html=True)

# --- CHARGEMENT ---
@st.cache_data(ttl=300)
def load_data():
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTN1Jwosf-2KEvw6HSBx4s01S24_Tzy9SM38LoGaHUrGc-cSn0vf19ugAiNnA_6InNBQxBnyI7JN3wa/pub?output=csv"
    try:
        df = pd.read_csv(csv_url)
        
        # 1. Conversion Date
        df['Date_Obj'] = pd.to_datetime(df['Horodateur'], dayfirst=True, errors='coerce')
        df['Heure'] = df['Date_Obj'].dt.hour
        df['Date_Simple'] = df['Date_Obj'].dt.date
        
        # 2. Nettoyage Statuts (Mise en MAJUSCULE pour comparaison fiable)
        if 'ETAT DE LA DEMANDE' in df.columns:
            # On met tout en majuscule : "traite" devient "TRAITE"
            df['Status_Clean'] = df['ETAT DE LA DEMANDE'].astype(str).str.strip().str.upper()
        else:
            df['Status_Clean'] = "INCONNU"
            
        return df
    except Exception as e:
        st.error(f"Erreur lecture: {e}")
        return pd.DataFrame()

df = load_data()

# --- CONFIGURATION DES MOTS CLÉS (SANS ACCENTS) ---
# Le script compare avec la version MAJUSCULE de ton fichier.
MOTS_TERMINES = ['TRAITE', 'EFFECTUE', 'OK', 'FAIT', 'CLOTURE'] 
MOTS_EN_COURS = ['ENCOURS', 'EN COURS', 'ATTENTE'] 

# --- CALCULS ---
if not df.empty:
    today = datetime.now().date()
    
    # Fonction de catégorisation stricte
    def categorize_status(status):
        if status in MOTS_TERMINES: return 'Effectué'
        if status in MOTS_EN_COURS: return 'En Cours'
        return 'Non Traité' # Tout le reste

    # On applique la logique
    df['Etat_Calculé'] = df['Status_Clean'].apply(categorize_status)
    
    # Filtre Jour
    df_today = df[df['Date_Simple'] == today]

    # --- RANGÉE 1 : KPI DU JOUR (Compact) ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    kpi1.metric("📅 TOTAL (JOUR)", len(df_today))
    
    # Non traité du jour (ni fait, ni encours)
    non_traites_jour = len(df_today[df_today['Etat_Calculé'] == 'Non Traité'])
    kpi2.metric("⚠️ A FAIRE (JOUR)", non_traites_jour)
    
    # En cours du jour (encours)
    en_cours_jour = len(df_today[df_today['Etat_Calculé'] == 'En Cours'])
    kpi3.metric("⏳ ENCOURS (JOUR)", en_cours_jour)
    
    # Effectué du jour (traite, effectue)
    effectue_jour = len(df_today[df_today['Etat_Calculé'] == 'Effectué'])
    kpi4.metric("✅ FAIT (JOUR)", effectue_jour)

    st.markdown("---") 

    # --- RANGÉE 2 : VISUALISATIONS (Hauteur forcée pour TV) ---
    # Layout : Graph Courbe (Large) + Camembert (Moyen) + Barres (Moyen)
    c_line, c_pie, c_bar = st.columns([2, 1, 1])
    
    GRAPH_HEIGHT = 220 # Hauteur fixe pour éviter le scroll vertical
    
    with c_line:
        # Progression horaire (Toutes dates confondues pour voir l'activité type, ou filtre df_today pour auj)
        # Ici j'affiche le global pour avoir une belle courbe s'il y a peu de données aujourd'hui
        hourly_counts = df.groupby('Heure').size().reset_index(name='Requetes')
        fig_line = px.line(hourly_counts, x='Heure', y='Requetes', title="Activité par Heure", markers=True)
        fig_line.update_layout(height=GRAPH_HEIGHT, margin=dict(l=20, r=20, t=30, b=10))
        st.plotly_chart(fig_line, use_container_width=True)
        
    with c_pie:
        if 'LA PLATEFORME' in df.columns:
            pie_data = df['LA PLATEFORME'].value_counts().reset_index()
            pie_data.columns = ['App', 'Vol']
            fig_pie = px.pie(pie_data, names='App', values='Vol', title="Plateforme")
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            # Légende forcée grande
            fig_pie.update_layout(height=GRAPH_HEIGHT, margin=dict(l=0, r=0, t=30, b=0), 
                                  legend=dict(font=dict(size=10)))
            st.plotly_chart(fig_pie, use_container_width=True)
            
    with c_bar:
        if 'CENTRE FISCAL' in df.columns:
            bar_data = df['CENTRE FISCAL'].value_counts().head(5).reset_index()
            bar_data.columns = ['Centre', 'Vol']
            fig_bar = px.bar(bar_data, x='Centre', y='Vol', title="Top Centres", color='Vol')
            fig_bar.update_layout(height=GRAPH_HEIGHT, margin=dict(l=20, r=20, t=30, b=20), showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- RANGÉE 3 : TABLEAU SYNTHÈSE (ANNUEL) ---
    st.markdown("##### 📊 BILAN GLOBAL (ANNÉE)")
    
    # Création catégorisation Incident/Demande (simulé via Objet)
    if 'OBJET' in df.columns:
        df['TYPE'] = df['OBJET'].apply(lambda x: 'Incident' if isinstance(x, str) and any(w in x.lower() for w in ['panne', 'bug', 'erreur']) else 'Demande')
    else:
        df['TYPE'] = 'Demande'

    # Tableau Pivot
    summary = df.pivot_table(index='TYPE', columns='Etat_Calculé', aggfunc='size', fill_value=0)
    summary['TOTAL'] = summary.sum(axis=1) # Colonne Total
    
    # Réorganisation des colonnes dans l'ordre demandé
    wanted_cols = ['TOTAL', 'Effectué', 'Non Traité', 'En Cours']
    existing_cols = [c for c in wanted_cols if c in summary.columns]
    
    st.dataframe(summary[existing_cols], use_container_width=True)

else:
    st.info("Chargement...")

# Refresh 5 min
time.sleep(300)
st.rerun()