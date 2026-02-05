import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# --- CONFIGURATION (Mode TV Plein Écran) ---
st.set_page_config(page_title="DSI TV Dashboard", layout="wide", initial_sidebar_state="collapsed")

# --- CSS MODERNE (Style inspiré du design SVG) ---
st.markdown("""
<style>
    /* Réduire les marges */
    .block-container { 
        padding-top: 0.5rem; 
        padding-bottom: 0rem; 
        padding-left: 1.5rem; 
        padding-right: 1.5rem; 
        max-width: 100%;
    }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Fond moderne */
    .stApp { 
        background: linear-gradient(135deg, #0E1117 0%, #1a1f2e 100%);
    }
    
    /* Style des cartes KPI */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3);
        backdrop-filter: blur(4px);
        text-align: center;
    }
    
    div[data-testid="stMetricValue"] { 
        font-size: 2.5rem !important; 
        font-weight: 700 !important;
        background: linear-gradient(120deg, #00d4ff, #0099ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
    }
    
    div[data-testid="stMetricLabel"] { 
        font-size: 0.85rem !important; 
        color: #FFFFFF !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        text-align: center;
    }
    
    /* Couleurs personnalisées pour chaque KPI */
    [data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 153, 255, 0.05) 100%);
        border-color: rgba(0, 212, 255, 0.3);
    }
    
    [data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.15) 0%, rgba(255, 193, 7, 0.05) 100%);
        border-color: rgba(255, 152, 0, 0.3);
    }
    [data-testid="column"]:nth-of-type(2) div[data-testid="stMetricValue"] {
        background: linear-gradient(120deg, #ff9800, #ffc107);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.15) 0%, rgba(3, 169, 244, 0.05) 100%);
        border-color: rgba(33, 150, 243, 0.3);
    }
    [data-testid="column"]:nth-of-type(3) div[data-testid="stMetricValue"] {
        background: linear-gradient(120deg, #2196f3, #03a9f4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="column"]:nth-of-type(4) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(139, 195, 74, 0.05) 100%);
        border-color: rgba(76, 175, 80, 0.3);
    }
    [data-testid="column"]:nth-of-type(4) div[data-testid="stMetricValue"] {
        background: linear-gradient(120deg, #4caf50, #8bc34a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Titre principal */
    h1 {
        color: #FFFFFF !important;
        text-align: center;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        font-size: 2rem !important;
    }
    
    /* Sous-titres */
    h3, h5 {
        color: #00d4ff !important;
        font-weight: 600 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
        font-size: 1rem !important;
    }
    
    /* Ligne de séparation */
    hr {
        border-color: rgba(255,255,255,0.1) !important;
        margin: 0.5rem 0 !important;
    }
    
    /* Style du tableau */
    .stDataFrame {
        text-align: center !important;
    }
    
    /* Centrer les en-têtes et données du tableau */
    thead tr th {
        text-align: center !important;
        background-color: rgba(0, 212, 255, 0.2) !important;
        color: white !important;
        font-weight: bold !important;
    }
    
    tbody tr td {
        text-align: center !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=300)
def load_data():
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTN1Jwosf-2KEvw6HSBx4s01S24_Tzy9SM38LoGaHUrGc-cSn0vf19ugAiNnA_6InNBQxBnyI7JN3wa/pub?output=csv"
    try:
        df = pd.read_csv(csv_url)
        
        # 1. Conversion Date
        df['Date_Obj'] = pd.to_datetime(df['Horodateur'], dayfirst=True, errors='coerce')
        df['Heure'] = df['Date_Obj'].dt.hour
        df['Date_Simple'] = df['Date_Obj'].dt.date
        df['Semaine'] = df['Date_Obj'].dt.isocalendar().week
        df['Annee'] = df['Date_Obj'].dt.year
        
        # 2. Nettoyage Statuts - Normalisation ROBUSTE
        if 'ETAT DE LA DEMANDE' in df.columns:
            df['Status_Clean'] = (df['ETAT DE LA DEMANDE']
                                  .astype(str)
                                  .str.strip()
                                  .str.upper()
                                  .str.replace('É', 'E')
                                  .str.replace('È', 'E')
                                  .str.replace('  ', ' '))
        else:
            df['Status_Clean'] = "INCONNU"
            
        return df
    except Exception as e:
        st.error(f"❌ Erreur de lecture des données: {e}")
        return pd.DataFrame()

df = load_data()

# --- TITRE ---
st.markdown("# 📊 DSI - Tableau de Bord Hebdomadaire")

# --- CONFIGURATION DES MOTS CLÉS ---
MOTS_TERMINES = [
    'TRAITE', 'TRAITEE', 'EFFECTUE', 'EFFECTUEE', 
    'OK', 'FAIT', 'FAITE', 'CLOTURE', 'CLOTUREE',
    'TERMINE', 'TERMINEE', 'RESOLU', 'RESOLUE'
] 

MOTS_EN_COURS = [
    'ENCOURS', 'EN COURS', 'ATTENTE', 'EN ATTENTE',
    'TRAITEMENT', 'EN TRAITEMENT', 'ENCOUR', 'COURS'
] 

# --- CALCULS ---
if not df.empty:
    today = datetime.now().date()
    
    # Calculer le début de la semaine (lundi)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Fonction de catégorisation
    def categorize_status(status):
        if pd.isna(status) or status == 'NAN':
            return 'Non Traité'
        
        for mot in MOTS_TERMINES:
            if mot in status:
                return 'Effectué'
        
        for mot in MOTS_EN_COURS:
            if mot in status:
                return 'En Cours'
        
        return 'Non Traité'

    # Appliquer la catégorisation
    df['Etat_Calculé'] = df['Status_Clean'].apply(categorize_status)
    
    # Filtre de la semaine
    df_week = df[(df['Date_Simple'] >= start_of_week) & (df['Date_Simple'] <= end_of_week)].copy()

    # --- RANGÉE 1 : KPI DE LA SEMAINE ---
    st.markdown(f"### 📅 Semaine du {start_of_week.strftime('%d/%m')} au {end_of_week.strftime('%d/%m/%Y')}")
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_semaine = len(df_week)
    non_traites_semaine = len(df_week[df_week['Etat_Calculé'] == 'Non Traité'])
    en_cours_semaine = len(df_week[df_week['Etat_Calculé'] == 'En Cours'])
    effectue_semaine = len(df_week[df_week['Etat_Calculé'] == 'Effectué'])
    
    with kpi1:
        st.metric("📅 TOTAL REQUÊTES", total_semaine)
    
    with kpi2:
        st.metric("⚠️ NON EFFECTUÉ", non_traites_semaine)
    
    with kpi3:
        st.metric("⏳ EN COURS", en_cours_semaine)
    
    with kpi4:
        st.metric("✅ EFFECTUÉ", effectue_semaine)

    st.markdown("---") 

    # --- RANGÉE 2 : VISUALISATIONS PRINCIPALES ---
    col_line, col_pie = st.columns([3, 2])
    
    GRAPH_HEIGHT = 320
    
    with col_line:
        # Activité par SEMAINE (dernières 12 semaines)
        df_last_weeks = df[df['Date_Obj'] >= (datetime.now() - timedelta(weeks=12))]
        weekly_counts = df_last_weeks.groupby(['Annee', 'Semaine']).size().reset_index(name='Requetes')
        weekly_counts['Semaine_Label'] = 'S' + weekly_counts['Semaine'].astype(str)
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=weekly_counts['Semaine_Label'],
            y=weekly_counts['Requetes'],
            mode='lines+markers',
            line=dict(color='#00d4ff', width=3),
            marker=dict(size=10, color='#00d4ff', line=dict(width=2, color='#0099ff')),
            fill='tozeroy',
            fillcolor='rgba(0, 212, 255, 0.1)'
        ))
        
        fig_line.update_layout(
            title="📈 Activité par Semaine (12 dernières semaines)",
            height=GRAPH_HEIGHT,
            margin=dict(l=40, r=20, t=50, b=40),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=11),
            xaxis=dict(
                title="Semaine",
                gridcolor='rgba(255,255,255,0.1)',
                showgrid=True
            ),
            yaxis=dict(
                title="Nombre de requêtes",
                gridcolor='rgba(255,255,255,0.1)',
                showgrid=True
            )
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col_pie:
        if 'LA PLATEFORME' in df.columns:
            pie_data = df_week['LA PLATEFORME'].value_counts().reset_index()
            pie_data.columns = ['App', 'Vol']
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=pie_data['App'],
                values=pie_data['Vol'],
                hole=.4,
                marker=dict(colors=['#00d4ff', '#0099ff', '#0077cc', '#005599', '#003366'])
            )])
            
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont=dict(size=10, color='white')
            )
            
            fig_pie.update_layout(
                title="🖥️ Répartition Plateformes (Semaine)",
                height=GRAPH_HEIGHT,
                margin=dict(l=0, r=0, t=50, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=11),
                showlegend=True,
                legend=dict(font=dict(size=9), orientation="v")
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # --- RANGÉE 3 : TOP 5 CENTRES (Tableau) ---
    st.markdown("##### 🏢 Top 5 Centres Fiscaux (Semaine)")
    
    if 'CENTRE FISCAL' in df.columns:
        top_centres = df_week['CENTRE FISCAL'].value_counts().head(5).reset_index()
        top_centres.columns = ['Centre Fiscal', 'Nombre de Requêtes']
        top_centres.index = range(1, len(top_centres) + 1)
        top_centres.index.name = 'Rang'
        
        # Affichage en tableau centré
        st.dataframe(
            top_centres,
            use_container_width=True,
            height=220
        )

    st.markdown("---")

    # --- RANGÉE 4 : TABLEAU SYNTHÈSE GLOBAL ---
    st.markdown("##### 📊 Bilan Global (Toutes Périodes)")
    
    # Création Type Incident/Demande
    if 'OBJET' in df.columns:
        df['TYPE'] = df['OBJET'].apply(
            lambda x: 'Incident' if isinstance(x, str) and 
            any(w in x.lower() for w in ['panne', 'bug', 'erreur', 'incident', 'problème', 'dysfonction']) 
            else 'Demande'
        )
    else:
        df['TYPE'] = 'Demande'

    # Tableau Pivot
    summary = df.pivot_table(
        index='TYPE', 
        columns='Etat_Calculé', 
        aggfunc='size', 
        fill_value=0
    )
    
    summary['TOTAL'] = summary.sum(axis=1)
    
    wanted_cols = ['TOTAL', 'Effectué', 'En Cours', 'Non Traité']
    existing_cols = [c for c in wanted_cols if c in summary.columns]
    
    # Affichage simple sans gradient
    st.dataframe(
        summary[existing_cols],
        use_container_width=True,
        height=150
    )
    
    # --- PIED DE PAGE : Statistiques ---
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        taux_traitement = (effectue_semaine / total_semaine * 100) if total_semaine > 0 else 0
        st.metric("📈 Taux Traitement", f"{taux_traitement:.1f}%")
    
    with col_stat2:
        taux_encours = (en_cours_semaine / total_semaine * 100) if total_semaine > 0 else 0
        st.metric("⏳ Taux En Cours", f"{taux_encours:.1f}%")
    
    with col_stat3:
        st.metric("📅 Aujourd'hui", today.strftime("%d/%m/%Y"))
    
    with col_stat4:
        heure_actuelle = datetime.now().strftime("%H:%M:%S")
        st.metric("🕐 Dernière MAJ", heure_actuelle)

else:
    st.info("⏳ Chargement des données...")

# Auto-refresh toutes les 5 minutes
time.sleep(300)
st.rerun()