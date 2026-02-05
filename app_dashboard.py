import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# --- CONFIGURATION (Mode TV Plein Écran) ---
st.set_page_config(page_title="DSI TV Dashboard", layout="wide", initial_sidebar_state="collapsed")

# --- CSS MODERNE (Style inspiré du design SVG) ---
st.markdown("""
<style>
    /* Réduire les marges */
    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 0rem; 
        padding-left: 2rem; 
        padding-right: 2rem; 
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
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3);
        backdrop-filter: blur(4px);
    }
    
    div[data-testid="stMetricValue"] { 
        font-size: 3rem !important; 
        font-weight: 700 !important;
        background: linear-gradient(120deg, #00d4ff, #0099ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    div[data-testid="stMetricLabel"] { 
        font-size: 0.95rem !important; 
        color: #FFFFFF !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
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
        margin-bottom: 2rem !important;
    }
    
    /* Sous-titres */
    h5 {
        color: #00d4ff !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
    }
    
    /* Ligne de séparation */
    hr {
        border-color: rgba(255,255,255,0.1) !important;
        margin: 1.5rem 0 !important;
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
        
        # 2. Nettoyage Statuts - Normalisation ROBUSTE
        if 'ETAT DE LA DEMANDE' in df.columns:
            # Conversion en string, strip espaces, UPPERCASE, remplacement des variations
            df['Status_Clean'] = (df['ETAT DE LA DEMANDE']
                                  .astype(str)
                                  .str.strip()
                                  .str.upper()
                                  .str.replace('É', 'E')  # Gérer les accents
                                  .str.replace('È', 'E')
                                  .str.replace('  ', ' '))  # Double espaces
        else:
            df['Status_Clean'] = "INCONNU"
            
        return df
    except Exception as e:
        st.error(f"❌ Erreur de lecture des données: {e}")
        return pd.DataFrame()

df = load_data()

# --- TITRE ---
st.markdown("# 📊 DSI - Tableau de Bord en Temps Réel")

# --- CONFIGURATION DES MOTS CLÉS ---
# Liste exhaustive pour capturer toutes les variations
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
    
    # Fonction de catégorisation stricte avec priorité
    def categorize_status(status):
        """Catégorise le statut avec logique claire"""
        if pd.isna(status) or status == 'NAN':
            return 'Non Traité'
        
        # Vérifier d'abord si c'est terminé (priorité haute)
        for mot in MOTS_TERMINES:
            if mot in status:
                return 'Effectué'
        
        # Ensuite vérifier si c'est en cours
        for mot in MOTS_EN_COURS:
            if mot in status:
                return 'En Cours'
        
        # Sinon c'est non traité
        return 'Non Traité'

    # Appliquer la catégorisation
    df['Etat_Calculé'] = df['Status_Clean'].apply(categorize_status)
    
    # Filtre du jour
    df_today = df[df['Date_Simple'] == today].copy()
    
    # DEBUG: Afficher un échantillon des statuts (commentez en production)
    # st.sidebar.write("### 🔍 Debug - Échantillon des statuts:")
    # st.sidebar.dataframe(df[['Status_Clean', 'Etat_Calculé']].drop_duplicates())

    # --- RANGÉE 1 : KPI DU JOUR ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_jour = len(df_today)
    non_traites_jour = len(df_today[df_today['Etat_Calculé'] == 'Non Traité'])
    en_cours_jour = len(df_today[df_today['Etat_Calculé'] == 'En Cours'])
    effectue_jour = len(df_today[df_today['Etat_Calculé'] == 'Effectué'])
    
    with kpi1:
        st.metric("📅 TOTAL JOUR", total_jour)
    
    with kpi2:
        st.metric("⚠️ À FAIRE", non_traites_jour)
    
    with kpi3:
        st.metric("⏳ EN COURS", en_cours_jour)
    
    with kpi4:
        st.metric("✅ EFFECTUÉ", effectue_jour)

    st.markdown("---") 

    # --- RANGÉE 2 : VISUALISATIONS ---
    c_line, c_pie, c_bar = st.columns([2, 1, 1])
    
    GRAPH_HEIGHT = 280
    
    with c_line:
        # Activité horaire (global pour avoir une belle courbe)
        hourly_counts = df.groupby('Heure').size().reset_index(name='Requetes')
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=hourly_counts['Heure'],
            y=hourly_counts['Requetes'],
            mode='lines+markers',
            line=dict(color='#00d4ff', width=3),
            marker=dict(size=8, color='#00d4ff', line=dict(width=2, color='#0099ff')),
            fill='tozeroy',
            fillcolor='rgba(0, 212, 255, 0.1)'
        ))
        
        fig_line.update_layout(
            title="📈 Activité par Heure",
            height=GRAPH_HEIGHT,
            margin=dict(l=30, r=20, t=50, b=30),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(
                title="Heure",
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
        
    with c_pie:
        if 'LA PLATEFORME' in df.columns:
            pie_data = df['LA PLATEFORME'].value_counts().reset_index()
            pie_data.columns = ['App', 'Vol']
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=pie_data['App'],
                values=pie_data['Vol'],
                hole=.4,
                marker=dict(colors=['#00d4ff', '#0099ff', '#0077cc', '#005599'])
            )])
            
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont=dict(size=11, color='white')
            )
            
            fig_pie.update_layout(
                title="🖥️ Plateformes",
                height=GRAPH_HEIGHT,
                margin=dict(l=0, r=0, t=50, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=True,
                legend=dict(font=dict(size=10))
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
    with c_bar:
        if 'CENTRE FISCAL' in df.columns:
            bar_data = df['CENTRE FISCAL'].value_counts().head(5).reset_index()
            bar_data.columns = ['Centre', 'Vol']
            
            fig_bar = go.Figure(data=[go.Bar(
                x=bar_data['Centre'],
                y=bar_data['Vol'],
                marker=dict(
                    color=bar_data['Vol'],
                    colorscale='Blues',
                    line=dict(color='rgba(0, 212, 255, 0.5)', width=2)
                )
            )])
            
            fig_bar.update_layout(
                title="🏢 Top 5 Centres",
                height=GRAPH_HEIGHT,
                margin=dict(l=30, r=20, t=50, b=70),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(
                    tickangle=-45,
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                yaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    showgrid=True
                ),
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # --- RANGÉE 3 : TABLEAU SYNTHÈSE ---
    st.markdown("##### 📊 BILAN GLOBAL (TOUTES PÉRIODES)")
    
    # Création Type Incident/Demande
    if 'OBJET' in df.columns:
        df['TYPE'] = df['OBJET'].apply(
            lambda x: 'Incident' if isinstance(x, str) and 
            any(w in x.lower() for w in ['panne', 'bug', 'erreur', 'incident', 'problème', 'dysfonction']) 
            else 'Demande'
        )
    else:
        df['TYPE'] = 'Demande'

    # Tableau Pivot avec réorganisation
    summary = df.pivot_table(
        index='TYPE', 
        columns='Etat_Calculé', 
        aggfunc='size', 
        fill_value=0
    )
    
    # Ajouter colonne TOTAL
    summary['TOTAL'] = summary.sum(axis=1)
    
    # Réorganiser les colonnes dans l'ordre souhaité
    wanted_cols = ['TOTAL', 'Effectué', 'En Cours', 'Non Traité']
    existing_cols = [c for c in wanted_cols if c in summary.columns]
    
    # Affichage avec styling
    st.dataframe(
        summary[existing_cols].style.background_gradient(
            cmap='Blues', 
            subset=[c for c in existing_cols if c != 'TOTAL']
        ).format("{:.0f}"),
        use_container_width=True
    )
    
    # Statistiques du jour en bas
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        taux_traitement = (effectue_jour / total_jour * 100) if total_jour > 0 else 0
        st.metric("📈 Taux de Traitement (Jour)", f"{taux_traitement:.1f}%")
    
    with col_stat2:
        st.metric("📅 Date", today.strftime("%d/%m/%Y"))
    
    with col_stat3:
        heure_actuelle = datetime.now().strftime("%H:%M:%S")
        st.metric("🕐 Dernière MAJ", heure_actuelle)

else:
    st.info("⏳ Chargement des données...")

# Auto-refresh toutes les 5 minutes
time.sleep(300)
st.rerun()