import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import unicodedata

# --- CONFIGURATION (Mode TV Plein Écran) ---
st.set_page_config(page_title="DSI TV Dashboard", layout="wide", initial_sidebar_state="collapsed")

# --- CSS MODERNE (Style inspiré du design SVG) ---
st.markdown("""
<style>
    /* Réduire les marges au maximum */
    .block-container { 
        padding-top: 0.3rem; 
        padding-bottom: 0rem; 
        padding-left: 1rem; 
        padding-right: 1rem; 
        max-width: 100%;
    }
    header { visibility: hidden; height: 0px; }
    footer { visibility: hidden; height: 0px; }
    
    /* Fond moderne */
    .stApp { 
        background: linear-gradient(135deg, #0E1117 0%, #1a1f2e 100%);
    }
    
    /* Style des cartes KPI - Plus compact */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
        padding: 18px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 6px 24px 0 rgba(0,0,0,0.3);
        backdrop-filter: blur(4px);
        text-align: center;
    }
    
    div[data-testid="stMetricValue"] { 
        font-size: 2.2rem !important; 
        font-weight: 700 !important;
        background: linear-gradient(120deg, #00d4ff, #0099ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
    }
    
    div[data-testid="stMetricLabel"] { 
        font-size: 0.8rem !important; 
        color: #FFFFFF !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.3px;
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
    
    /* Titre principal - compact */
    h1 {
        color: #FFFFFF !important;
        text-align: center;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        margin-top: 0rem !important;
        font-size: 1.6rem !important;
    }
    
    /* Sous-titres - compact */
    h3 {
        color: #00d4ff !important;
        font-weight: 600 !important;
        margin-top: 0.3rem !important;
        margin-bottom: 0.5rem !important;
        font-size: 0.95rem !important;
    }
    
    h5 {
        color: #00d4ff !important;
        font-weight: 600 !important;
        margin-top: 0.3rem !important;
        margin-bottom: 0.4rem !important;
        font-size: 0.85rem !important;
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
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTN1Jwosf-2KEvw6HSBx4s01S24_Tzy9SM38LoGaHUrGc-cSn0vf19ugAiNnA_6InNBQxBnyI7JN3wa/pub?gid=0&single=true&output=csv"
    try:
        df = pd.read_csv(csv_url)

        # 1. Conversion Date
        df['Date_Obj'] = pd.to_datetime(df['Horodateur'], dayfirst=True, errors='coerce')
        df['Heure'] = df['Date_Obj'].dt.hour
        df['Date_Simple'] = df['Date_Obj'].dt.date
        df['Semaine'] = df['Date_Obj'].dt.isocalendar().week
        df['Annee'] = df['Date_Obj'].dt.year

        # 2. Nettoyage Statuts - Normalisation ROBUSTE (sans accents + upper)
        if 'ETAT DE LA DEMANDE' in df.columns:
            df['Status_Clean'] = (df['ETAT DE LA DEMANDE']
                                  .astype(str)
                                  .str.strip()
                                  .str.upper()
                                  .str.replace('É', 'E')
                                  .str.replace('È', 'E')
                                  .str.replace('Ê', 'E')
                                  .str.replace('À', 'A')
                                  .str.replace('Ç', 'C')
                                  .str.replace('  ', ' '))
        else:
            df['Status_Clean'] = "INCONNU"

        return df
    except Exception as e:
        st.error(f"❌ Erreur de lecture des données: {e}")
        return pd.DataFrame()

df = load_data()

# --- TITRE ---
st.markdown("# 📊 DGID/DSI - GESTION HEBDO DES REQUETES")

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

# --- OUTIL DE NORMALISATION (pour les comparaisons KPI) ---
def norm_noaccent_lower(x: str) -> str:
    x = "" if x is None else str(x)
    x = x.strip().lower()
    x = "".join(c for c in unicodedata.normalize("NFD", x) if unicodedata.category(c) != "Mn")
    # harmoniser "en cours" / "en_cours" / "en-cours" / "encours"
    x = x.replace(" ", "").replace("_", "").replace("-", "")
    return x

# --- CALCULS ---
if not df.empty:
    today = datetime.now().date()

    # Début/fin semaine
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Catégorisation : retourne UNIQUEMENT nontraite / encours / effectue (sans accents)
    def categorize_status(status_clean):
        s = "" if pd.isna(status_clean) else str(status_clean).strip().upper()

        if s == "" or s == "NAN":
            return "non traite"

        for mot in MOTS_TERMINES:
            if mot in s:
                return "effectue"

        for mot in MOTS_EN_COURS:
            if mot in s:
                return "encours"

        return "non traite"

    df['Etat_Calculé'] = df['Status_Clean'].apply(categorize_status)

    # Filtre semaine
    df_week = df[(df['Date_Simple'] >= start_of_week) & (df['Date_Simple'] <= end_of_week)].copy()

    # (debug temporaire si besoin)
    # st.write("Valeurs uniques Etat_Calculé:", df_week["Etat_Calculé"].dropna().unique())
    # st.write(df_week[["Etat_Calculé"]])

    # KPI (comparaison exacte avec les valeurs renvoyées par categorize_status)
    total_semaine = len(df_week)
    non_traites_semaine = (df_week['Etat_Calculé'] == 'non traite').sum()
    en_cours_semaine = (df_week['Etat_Calculé'] == 'encours').sum()
    effectue_semaine = (df_week['Etat_Calculé'] == 'effectue').sum()

    taux_traitement = (effectue_semaine / total_semaine * 100) if total_semaine > 0 else 0
    taux_encours = (en_cours_semaine / total_semaine * 100) if total_semaine > 0 else 0
    heure_actuelle = datetime.now().strftime("%H:%M")

    # ============ SECTION EN-TÊTE ============
    st.markdown(f"### 📅 Semaine du {start_of_week.strftime('%d/%m')} au {end_of_week.strftime('%d/%m/%Y')}")

    # ============ LIGNE 1 : KPI + PLATEFORMES ============
    col1, col2 = st.columns([1, 1], gap="small")

    # GAUCHE : KPI 2x2
    with col1:
        kpi1, kpi2 = st.columns(2, gap="small")
        with kpi1:
            st.metric("📅 TOTAL REQUÊTES", int(total_semaine))
        with kpi2:
            st.metric("⚠️ NON EFFECTUÉ", int(non_traites_semaine))

        kpi3, kpi4 = st.columns(2, gap="small")
        with kpi3:
            st.metric("⏳ EN COURS", int(en_cours_semaine))
        with kpi4:
            st.metric("✅ EFFECTUÉ", int(effectue_semaine))

    # DROITE : Répartition Plateformes
    with col2:
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
                textfont=dict(size=11, color='white')
            )

            fig_pie.update_layout(
                title="🖥️ Répartition Plateformes",
                height=260,
                margin=dict(l=10, r=10, t=40, b=10),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=11),
                showlegend=True,
                legend=dict(font=dict(size=10), orientation="h", yanchor="bottom",
                            y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # ============ LIGNE 2 : ACTIVITÉ + TOP 5 CENTRES ============
    col_activity, col_centres = st.columns([1, 1])

    with col_activity:
        daily_counts = df_week.groupby(df_week['Date_Obj'].dt.day_name()).size().reset_index(name='Requetes')

        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        days_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

        daily_counts['Order'] = daily_counts['Date_Obj'].apply(lambda x: days_order.index(x) if x in days_order else 7)
        daily_counts = daily_counts.sort_values('Order')
        daily_counts['Jour_FR'] = daily_counts['Date_Obj'].map(dict(zip(days_order, days_fr)))

        fig_activity = go.Figure()
        fig_activity.add_trace(go.Bar(
            x=daily_counts['Jour_FR'],
            y=daily_counts['Requetes'],
            marker=dict(
                color=daily_counts['Requetes'],
                colorscale='Blues',
                line=dict(color='rgba(0, 212, 255, 0.5)', width=2)
            )
        ))

        fig_activity.update_layout(
            title="📈 Activité par Jour (Semaine Courante)",
            height=280,
            margin=dict(l=40, r=20, t=50, b=60),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=11),
            xaxis=dict(tickangle=-30, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)', showgrid=True),
            showlegend=False
        )
        st.plotly_chart(fig_activity, use_container_width=True)

    with col_centres:
        if 'CENTRE FISCAL' in df.columns:
            top_centres = df_week['CENTRE FISCAL'].value_counts().head(5).reset_index()
            top_centres.columns = ['Centre Fiscal', 'Requêtes']
            top_centres.index = range(1, len(top_centres) + 1)
            top_centres.index.name = '#'

            st.markdown("##### 🏢 Top 5 Centres Fiscaux")
            st.dataframe(top_centres, use_container_width=True, height=245)

    # ============ LIGNE 3 : BILAN + STATS ============
    col_bilan, col_stats = st.columns([1, 1])

    with col_bilan:
        st.markdown("##### 📊 Bilan Global (Toutes Périodes)")

        if 'OBJET' in df.columns:
            df['TYPE'] = df['OBJET'].apply(
                lambda x: 'Incident' if isinstance(x, str) and
                any(w in x.lower() for w in ['panne', 'bug', 'erreur', 'incident', 'problème', 'dysfonction'])
                else 'Demande'
            )
        else:
            df['TYPE'] = 'Demande'

        summary = df.pivot_table(
            index='TYPE',
            columns='Etat_Calculé',
            aggfunc='size',
            fill_value=0
        )
        summary['TOTAL'] = summary.sum(axis=1)

        # colonnes existantes (sans accents)
        wanted_cols = ['TOTAL', 'effectue']
        existing_cols = [c for c in wanted_cols if c in summary.columns]

        st.dataframe(summary[existing_cols], use_container_width=True, height=150)

    with col_stats:
        st.markdown("##### 📈 Statistiques")

        stat1, stat2 = st.columns(2)
        with stat1:
            st.metric("✅ Taux Traitement", f"{taux_traitement:.1f}%")
        with stat2:
            st.metric("⏳ Taux En Cours", f"{taux_encours:.1f}%")

        stat3, stat4 = st.columns(2)
        with stat3:
            st.metric("📅 Aujourd'hui", today.strftime("%d/%m"))
        with stat4:
            st.metric("🕐 MAJ", heure_actuelle)

else:
    st.info("⏳ Chargement des données...")

# Auto-refresh toutes les 5 minutes
time.sleep(300)
st.rerun()
