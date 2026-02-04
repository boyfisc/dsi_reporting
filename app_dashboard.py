import streamlit as st
import pandas as pd
import plotly.express as px
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="DSI Monitor", layout="wide", initial_sidebar_state="collapsed")

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=300) # Mise en cache de 5 minutes
def load_data():
    # C'est TON lien valide qui déclenche le téléchargement
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTN1Jwosf-2KEvw6HSBx4s01S24_Tzy9SM38LoGaHUrGc-cSn0vf19ugAiNnA_6InNBQxBnyI7JN3wa/pub?output=csv"
    
    try:
        # On lit le CSV directement depuis l'URL
        df = pd.read_csv(csv_url)
        return df
    except Exception as e:
        # Si erreur, on l'affiche pour comprendre (ex: problème de format)
        st.error(f"Erreur technique : {e}")
        return pd.DataFrame()

df = load_data()

# --- STYLE VISUEL (Dark Mode force) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 3rem; }
</style>
""", unsafe_allow_html=True)

# --- AFFICHAGE ---
st.title("📡 DSI MONITORING - LIVE")

if not df.empty:
    # --- NETTOYAGE ET FILTRES ---
    # On s'assure que les colonnes existent (évite le crash si le fichier change)
    if 'ETAT DE LA DEMANDE' in df.columns:
        df_pending = df[df['ETAT DE LA DEMANDE'] != 'Traité']
        df_done = df[df['ETAT DE LA DEMANDE'] == 'Traité']
    else:
        st.warning("Colonne 'ETAT DE LA DEMANDE' introuvable.")
        df_pending = df
        df_done = pd.DataFrame()

    # --- LIGNE 1 : KPI ---
    col1, col2, col3 = st.columns(3)
    col1.metric("🔴 EN ATTENTE", len(df_pending))
    col2.metric("✅ TRAITÉS", len(df_done))
    
    # Point chaud
    if not df_pending.empty and 'CENTRE FISCAL' in df.columns:
        top_center = df_pending['CENTRE FISCAL'].mode()[0]
        col3.metric("🔥 POINT CHAUD", str(top_center))
    else:
        col3.metric("🔥 POINT CHAUD", "R.A.S")

    st.divider()

    # --- LIGNE 2 : GRAPHIQUES ---
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Par Centre Fiscal")
        if not df_pending.empty and 'CENTRE FISCAL' in df.columns:
            fig1 = px.bar(df_pending, x='CENTRE FISCAL', color='CENTRE FISCAL')
            st.plotly_chart(fig1, use_container_width=True)
    
    with c2:
        st.subheader("Par Plateforme")
        if not df_pending.empty and 'LA PLATEFORME' in df.columns:
            fig2 = px.pie(df_pending, names='LA PLATEFORME')
            st.plotly_chart(fig2, use_container_width=True)

    # --- LIGNE 3 : URGENCES ---
    st.subheader("⚠️ URGENCES (Dernières demandes en attente)")
    if not df_pending.empty:
        # On sélectionne les colonnes intéressantes si elles existent
        cols_to_show = [c for c in ['Horodateur', 'CENTRE FISCAL', 'OBJET', 'WAITING TIME'] if c in df.columns]
        st.dataframe(df_pending[cols_to_show].head(10), use_container_width=True, hide_index=True)

else:
    st.info("Chargement des données en cours ou fichier vide...")

# --- AUTO REFRESH (Toutes les 10 minutes) ---
time.sleep(300)
st.rerun()

