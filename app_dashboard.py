import streamlit as st
import pandas as pd
import plotly.express as px
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="DSI Monitor", layout="wide", initial_sidebar_state="collapsed")

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=300)
def load_data():
    # URL modifiée pour l'export CSV
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTN1Jwosf-2KEvw6HSBx4s01S24_Tzy9SM38LoGaHUrGc-cSn0vf19ugAiNnA_6InNBQxBnyI7JN3wa/pub?output=csv"
    try:
        df = pd.read_csv(sheet_url)
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# --- CSS SOMBRE (Pour TV) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: white; }
    div[data-testid="stMetricValue"] { font-size: 3rem; }
</style>
""", unsafe_allow_html=True)

# --- AFFICHAGE ---
st.title("📡 DSI MONITORING - LIVE")

if not df.empty:
    # Filtres
    df_pending = df[df['ETAT DE LA DEMANDE'] != 'Traité']
    df_done = df[df['ETAT DE LA DEMANDE'] == 'Traité']

    # Ligne 1 : Les Gros Chiffres
    col1, col2, col3 = st.columns(3)
    col1.metric("🔴 EN ATTENTE", len(df_pending))
    col2.metric("✅ TRAITÉS", len(df_done))
    
    # Point chaud (Centre Fiscal avec le plus de demandes en attente)
    if not df_pending.empty:
        top_center = df_pending['CENTRE FISCAL'].mode()[0]
        col3.metric("🔥 POINT CHAUD", top_center)
    else:
        col3.metric("🔥 POINT CHAUD", "R.A.S")

    st.divider()

    # Ligne 2 : Les Graphiques
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Par Centre Fiscal")
        if not df_pending.empty:
            fig1 = px.bar(df_pending, x='CENTRE FISCAL', color='CENTRE FISCAL')
            st.plotly_chart(fig1, use_container_width=True)
    
    with c2:
        st.subheader("Par Plateforme")
        if not df_pending.empty:
            fig2 = px.pie(df_pending, names='LA PLATEFORME')
            st.plotly_chart(fig2, use_container_width=True)

    # Ligne 3 : Urgences (Tableau)
    st.subheader("⚠️ URGENCES (Tickets en attente)")
    if not df_pending.empty:
        st.dataframe(df_pending[['Horodateur', 'CENTRE FISCAL', 'OBJET', 'WAITING TIME']].head(10), use_container_width=True, hide_index=True)

else:
    st.error("Impossible de lire la Google Sheet. Vérifiez le lien.")

# --- AUTO REFRESH (10 min) ---
time.sleep(600)
st.rerun()