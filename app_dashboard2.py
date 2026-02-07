import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import unicodedata

# --- CONFIGURATION (Mode TV Plein Écran) ---
st.set_page_config(page_title="DSI TV Dashboard", layout="wide", initial_sidebar_state="collapsed")

# --- CSS OPTIMISÉ POUR TV (Affichage Grand Format) ---
st.markdown("""
<style>
    /* Réduire les marges au maximum */
    .block-container {
        padding-top: 0.2rem;
        padding-bottom: 0rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
        max-width: 100%;
    }
    header { visibility: hidden; height: 0px; }
    footer { visibility: hidden; height: 0px; }

    /* Fond moderne avec texture */
    .stApp {
        background: linear-gradient(135deg, #0E1117 0%, #1a1f2e 100%);
    }

    /* Style des cartes KPI - Optimisé TV (sans effets lumineux) */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%);
        padding: 20px 16px;
        border-radius: 12px;
        border: 2px solid rgba(255,255,255,0.2);
        box-shadow: 0 4px 12px 0 rgba(0,0,0,0.5);
        backdrop-filter: blur(6px);
        text-align: center;
        transition: all 0.3s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px 0 rgba(0,0,0,0.6);
    }

    /* Valeurs KPI - Plus grandes pour TV (sans effets lumineux) */
    div[data-testid="stMetricValue"] {
        font-size: 4.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(120deg, #00d4ff, #0099ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
        line-height: 1.1;
    }

    /* Labels KPI - Plus lisibles pour TV */
    div[data-testid="stMetricLabel"] {
        font-size: 1.5rem !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        text-align: center;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
        margin-bottom: 8px;
    }
    
    /* Couleurs personnalisées pour chaque KPI - Renforcées pour TV */
    [data-testid="column"]:nth-of-type(1) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(0, 153, 255, 0.08) 100%);
        border-color: rgba(0, 212, 255, 0.5);
    }

    [data-testid="column"]:nth-of-type(2) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.2) 0%, rgba(255, 193, 7, 0.08) 100%);
        border-color: rgba(255, 152, 0, 0.5);
    }
    [data-testid="column"]:nth-of-type(2) div[data-testid="stMetricValue"] {
        background: linear-gradient(120deg, #ff9800, #ffc107);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    [data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.2) 0%, rgba(3, 169, 244, 0.08) 100%);
        border-color: rgba(33, 150, 243, 0.5);
    }
    [data-testid="column"]:nth-of-type(3) div[data-testid="stMetricValue"] {
        background: linear-gradient(120deg, #2196f3, #03a9f4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    [data-testid="column"]:nth-of-type(4) div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.2) 0%, rgba(139, 195, 74, 0.08) 100%);
        border-color: rgba(76, 175, 80, 0.5);
    }
    [data-testid="column"]:nth-of-type(4) div[data-testid="stMetricValue"] {
        background: linear-gradient(120deg, #4caf50, #8bc34a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Titre principal - Optimisé TV (sans effets lumineux) */
    h1 {
        color: #FFFFFF !important;
        text-align: center;
        font-weight: 800 !important;
        margin-bottom: 0.4rem !important;
        margin-top: 0rem !important;
        font-size: 3.5rem !important;
        text-shadow: 0 3px 8px rgba(0, 0, 0, 0.7);
        letter-spacing: 2px;
    }

    /* Sous-titres - Plus visibles (sans effets lumineux) */
    h3 {
        color: #00d4ff !important;
        font-weight: 700 !important;
        margin-top: 0.3rem !important;
        margin-bottom: 0.5rem !important;
        font-size: 2.2rem !important;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.6);
        letter-spacing: 1px;
    }

    h5 {
        color: #00d4ff !important;
        font-weight: 700 !important;
        margin-top: 0.3rem !important;
        margin-bottom: 0.4rem !important;
        font-size: 2.2rem !important;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.6);
        letter-spacing: 1px;
    }

    /* Ligne de séparation */
    hr {
        border-color: rgba(255,255,255,0.15) !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 1px 3px rgba(0, 212, 255, 0.2);
    }

    /* Style du tableau - Optimisé pour TV */
    .stDataFrame {
        text-align: center !important;
        font-size: 1.3rem !important;
    }

    /* En-têtes de tableau - Plus visibles */
    thead tr th {
        text-align: center !important;
        background-color: rgba(0, 212, 255, 0.3) !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 1.4rem !important;
        padding: 12px !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        border-bottom: 2px solid rgba(0, 212, 255, 0.5) !important;
    }

    /* Données de tableau - Zebra striping pour lisibilité */
    tbody tr td {
        text-align: center !important;
        color: white !important;
        font-size: 1.3rem !important;
        padding: 10px !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
    }

    tbody tr:nth-child(even) {
        background-color: rgba(255, 255, 255, 0.03) !important;
    }

    tbody tr:hover {
        background-color: rgba(0, 212, 255, 0.1) !important;
        transition: background-color 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=300)
def load_data():
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTN1Jwosf-2KEvw6HSBx4s01S24_Tzy9SM38LoGaHUrGc-cSn0vf19ugAiNnA_6InNBQxBnyI7JN3wa/pub?gid=0&single=true&output=csv"
    try:
        df = pd.read_csv(csv_url)

        # 1) Conversion Date
        df["Date_Obj"] = pd.to_datetime(df["Horodateur"], dayfirst=True, errors="coerce")
        df["Heure"] = df["Date_Obj"].dt.hour
        df["Date_Simple"] = df["Date_Obj"].dt.date
        df["Semaine"] = df["Date_Obj"].dt.isocalendar().week
        df["Annee"] = df["Date_Obj"].dt.year

        # 2) Nettoyage Statuts - Normalisation ROBUSTE (sans accents + upper)
        if "ETAT DE LA DEMANDE" in df.columns:
            df["Status_Clean"] = (
                df["ETAT DE LA DEMANDE"]
                .astype(str)
                .str.strip()
                .str.upper()
                .str.replace("É", "E")
                .str.replace("È", "E")
                .str.replace("Ê", "E")
                .str.replace("À", "A")
                .str.replace("Ç", "C")
                .str.replace("  ", " ")
            )
        else:
            df["Status_Clean"] = "INCONNU"

        return df

    except Exception as e:
        st.error(f"❌ Erreur de lecture des données: {e}")
        return pd.DataFrame()

df = load_data()

# --- TITRE ---
st.markdown("# 📊 DGID/DSI - GESTION HEBDO DES REQUETES")

# --- FILTRE PLATEFORME ---
plateforme_selectionnee = "TOUTES"
if not df.empty and "LA PLATEFORME" in df.columns:
    plateformes_disponibles = ["TOUTES"] + sorted(df["LA PLATEFORME"].dropna().unique().tolist())
    plateforme_selectionnee = st.selectbox(
        "🖥️ Filtrer par Plateforme",
        options=plateformes_disponibles,
        index=0,
        key="filtre_plateforme"
    )

# --- CONFIGURATION DES MOTS CLÉS ---
MOTS_TERMINES = [
    "TRAITE", "TRAITEE", "EFFECTUE", "EFFECTUEE",
    "OK", "FAIT", "FAITE", "CLOTURE", "CLOTUREE",
    "TERMINE", "TERMINEE", "RESOLU", "RESOLUE"
]

MOTS_EN_COURS = [
    "ENCOURS", "EN COURS", "ATTENTE", "EN ATTENTE",
    "TRAITEMENT", "EN TRAITEMENT", "ENCOUR", "COURS"
]

# --- OUTIL DE NORMALISATION (au besoin pour comparaisons) ---
def norm_noaccent_lower(x: str) -> str:
    x = "" if x is None else str(x)
    x = x.strip().lower()
    x = "".join(c for c in unicodedata.normalize("NFD", x) if unicodedata.category(c) != "Mn")
    x = x.replace(" ", "").replace("_", "").replace("-", "")
    return x

# --- CALCULS ---
if not df.empty:
    today = datetime.now().date()

    # Début/fin semaine (lundi -> dimanche)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Catégorisation : retourne UNIQUEMENT non traite / encours / effectue (sans accents)
    def categorize_status(status):
        s = "" if pd.isna(status) else str(status).strip().upper()

        if s == "" or s == "NAN":
            return "non traite"

        # IMPORTANT : gérer "NON ..." avant mots terminés (évite "TRAITE" qui match "NON TRAITE")
        if "NON" in s or "PAS" in s:
            return "non traite"

        # Terminés
        for mot in MOTS_TERMINES:
            if mot in s:
                return "effectue"

        # En cours
        for mot in MOTS_EN_COURS:
            if mot in s:
                return "encours"

        return "non traite"

    df["Etat_Calculé"] = df["Status_Clean"].apply(categorize_status)

    # Filtre semaine courante
    df_week = df[(df["Date_Simple"] >= start_of_week) & (df["Date_Simple"] <= end_of_week)].copy()

    # Semaine précédente (pour calcul évolution)
    start_of_prev_week = start_of_week - timedelta(days=7)
    end_of_prev_week = end_of_week - timedelta(days=7)
    df_prev_week = df[(df["Date_Simple"] >= start_of_prev_week) & (df["Date_Simple"] <= end_of_prev_week)].copy()

    # Application du filtre plateforme si sélectionné
    if "LA PLATEFORME" in df.columns and plateforme_selectionnee != "TOUTES":
        df_week = df_week[df_week["LA PLATEFORME"] == plateforme_selectionnee].copy()
        df_prev_week = df_prev_week[df_prev_week["LA PLATEFORME"] == plateforme_selectionnee].copy()

    # Contrôle des états inattendus
    etats_attendus = {"non traite", "encours", "effectue"}
    etats_inattendus = set(df_week["Etat_Calculé"].dropna().unique()) - etats_attendus
    if etats_inattendus:
        st.warning(f"Etats inattendus detectes: {sorted(etats_inattendus)}")

    # KPI Semaine Courante
    total_semaine = len(df_week)
    non_traites_semaine = (df_week["Etat_Calculé"] == "non traite").sum()
    en_cours_semaine = (df_week["Etat_Calculé"] == "encours").sum()
    effectue_semaine = (df_week["Etat_Calculé"] == "effectue").sum()

    taux_traitement = (effectue_semaine / total_semaine * 100) if total_semaine > 0 else 0
    taux_encours = (en_cours_semaine / total_semaine * 100) if total_semaine > 0 else 0

    # KPI Semaine Précédente (pour évolution)
    total_prev = len(df_prev_week)
    effectue_prev = (df_prev_week["Etat_Calculé"] == "effectue").sum()
    taux_traitement_prev = (effectue_prev / total_prev * 100) if total_prev > 0 else 0

    # Calcul évolution
    evolution_total = total_semaine - total_prev
    evolution_taux = taux_traitement - taux_traitement_prev

    heure_actuelle = datetime.now().strftime("%H:%M")

    # Fonction pour déterminer la couleur du taux
    def get_taux_color(taux):
        if taux >= 75:
            return "#4caf50"  # Vert
        elif taux >= 50:
            return "#ff9800"  # Orange
        else:
            return "#f44336"  # Rouge

    # ============ SECTION EN-TÊTE ============
    filtre_info = f" - {plateforme_selectionnee}" if "LA PLATEFORME" in df.columns and plateforme_selectionnee != "TOUTES" else ""
    st.markdown(f"### 📅 Semaine du {start_of_week.strftime('%d/%m')} au {end_of_week.strftime('%d/%m/%Y')}{filtre_info}")

    # ============ LIGNE 1 : KPI + PLATEFORMES ============
    col1, col2 = st.columns([1, 1], gap="small")

    # GAUCHE : KPI 2x2 avec style homogène
    with col1:
        kpi1, kpi2 = st.columns(2, gap="small")
        with kpi1:
            # Total Requêtes avec delta
            delta_display = f"{evolution_total:+d}" if total_prev > 0 else ""
            st.markdown(f"""<div style="background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%); padding: 16px; border-radius: 10px; border: 2px solid rgba(255,255,255,0.15); box-shadow: 0 4px 12px 0 rgba(0,0,0,0.4); text-align: center;">
<div style="font-size: 1.5rem; color: #FFFFFF; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">📅 TOTAL REQUÊTES</div>
<div style="font-size: 4.5rem; font-weight: 800; color: #00d4ff; line-height: 1.1;">{int(total_semaine)}</div>
<div style="font-size: 1.2rem; color: {'#4caf50' if evolution_total >= 0 else '#f44336'}; font-weight: 600; margin-top: 5px;">{delta_display}</div>
</div>""", unsafe_allow_html=True)

        with kpi2:
            # Non Effectué
            st.markdown(f"""<div style="background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%); padding: 16px; border-radius: 10px; border: 2px solid rgba(255,255,255,0.15); box-shadow: 0 4px 12px 0 rgba(0,0,0,0.4); text-align: center;">
<div style="font-size: 1.5rem; color: #FFFFFF; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">⚠️ NON EFFECTUÉ</div>
<div style="font-size: 4.5rem; font-weight: 800; color: #ff9800; line-height: 1.1;">{int(non_traites_semaine)}</div>
</div>""", unsafe_allow_html=True)

        kpi3, kpi4 = st.columns(2, gap="small")
        with kpi3:
            # En Cours
            st.markdown(f"""<div style="background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%); padding: 16px; border-radius: 10px; border: 2px solid rgba(255,255,255,0.15); box-shadow: 0 4px 12px 0 rgba(0,0,0,0.4); text-align: center;">
<div style="font-size: 1.5rem; color: #FFFFFF; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">⏳ EN COURS</div>
<div style="font-size: 4.5rem; font-weight: 800; color: #2196f3; line-height: 1.1;">{int(en_cours_semaine)}</div>
</div>""", unsafe_allow_html=True)

        with kpi4:
            # Effectué
            st.markdown(f"""<div style="background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%); padding: 16px; border-radius: 10px; border: 2px solid rgba(255,255,255,0.15); box-shadow: 0 4px 12px 0 rgba(0,0,0,0.4); text-align: center;">
<div style="font-size: 1.5rem; color: #FFFFFF; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">✅ EFFECTUÉ</div>
<div style="font-size: 4.5rem; font-weight: 800; color: #4caf50; line-height: 1.1;">{int(effectue_semaine)}</div>
</div>""", unsafe_allow_html=True)

    # DROITE : Répartition Plateformes (TREEMAP)
    with col2:
        if "LA PLATEFORME" in df.columns:
            plat = (
                df_week["LA PLATEFORME"]
                .fillna("INCONNU")
                .astype(str)
                .str.strip()
            )

            pie_data = plat.value_counts().reset_index()
            pie_data.columns = ["Plateforme", "Volume"]

            fig_tree = px.treemap(
                pie_data,
                path=["Plateforme"],
                values="Volume",
            )

            fig_tree.update_traces(
                textinfo="label+percent parent",
                textfont_size=20,
                textfont=dict(family="Arial Black", color="white"),
                hovertemplate="<b>%{label}</b><br>Requêtes: %{value}<br>Part: %{percentParent:.1%}<extra></extra>",
                marker=dict(line=dict(color="rgba(255,255,255,0.3)", width=2))
            )

            fig_tree.update_layout(
                title=dict(
                    text="🖥️ Répartition Plateformes",
                    font=dict(size=24, color="#00d4ff", family="Arial Black"),
                    x=0.5,
                    xanchor="center"
                ),
                height=280,
                margin=dict(l=10, r=10, t=50, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white", size=16, family="Arial"),
            )

            st.plotly_chart(fig_tree, use_container_width=True)
        else:
            st.info("Colonne 'LA PLATEFORME' introuvable.")

    # ============ LIGNE 2 : ACTIVITÉ + TOP 5 CENTRES ============
    col_activity, col_centres = st.columns([1, 1])

    with col_activity:
        daily_counts = df_week.groupby(df_week["Date_Obj"].dt.day_name()).size().reset_index(name="Requetes")

        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

        daily_counts["Order"] = daily_counts["Date_Obj"].apply(
            lambda x: days_order.index(x) if x in days_order else 7
        )
        daily_counts = daily_counts.sort_values("Order")
        daily_counts["Jour_FR"] = daily_counts["Date_Obj"].map(dict(zip(days_order, days_fr)))

        fig_activity = go.Figure()
        fig_activity.add_trace(
            go.Bar(
                x=daily_counts["Jour_FR"],
                y=daily_counts["Requetes"],
                marker=dict(
                    color=daily_counts["Requetes"],
                    colorscale="Blues",
                    line=dict(color="rgba(0, 212, 255, 0.8)", width=3),
                ),
                text=daily_counts["Requetes"],
                textposition="outside",
                textfont=dict(size=18, color="white", family="Arial Black"),
            )
        )

        fig_activity.update_layout(
            title=dict(
                text="📈 Activité par Jour (Semaine Courante)",
                font=dict(size=24, color="#00d4ff", family="Arial Black"),
                x=0.5,
                xanchor="center"
            ),
            height=280,
            margin=dict(l=40, r=20, t=50, b=60),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white", size=16, family="Arial"),
            xaxis=dict(
                tickangle=-30,
                gridcolor="rgba(255,255,255,0.1)",
                tickfont=dict(size=15, family="Arial")
            ),
            yaxis=dict(
                gridcolor="rgba(255,255,255,0.1)",
                showgrid=True,
                tickfont=dict(size=15, family="Arial")
            ),
            showlegend=False,
        )

        st.plotly_chart(fig_activity, use_container_width=True)

    with col_centres:
        if "CENTRE FISCAL" in df.columns:
            top_centres = df_week["CENTRE FISCAL"].value_counts().head(5).reset_index()
            top_centres.columns = ["Centre Fiscal", "Requêtes"]

            st.markdown("##### 🏢 Top 5 Centres Fiscaux")

            # Inverser l'ordre pour avoir le plus grand en haut
            top_centres = top_centres.sort_values("Requêtes", ascending=True)

            fig_centres = go.Figure()
            fig_centres.add_trace(
                go.Bar(
                    x=top_centres["Requêtes"],
                    y=top_centres["Centre Fiscal"],
                    orientation="h",
                    marker=dict(
                        color=top_centres["Requêtes"],
                        colorscale="Teal",
                        line=dict(color="rgba(0, 212, 255, 0.8)", width=2),
                    ),
                    text=top_centres["Requêtes"],
                    textposition="outside",
                    textfont=dict(size=18, color="white", family="Arial Black"),
                )
            )

            fig_centres.update_layout(
                height=260,
                margin=dict(l=10, r=40, t=10, b=40),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white", size=14, family="Arial"),
                xaxis=dict(
                    gridcolor="rgba(255,255,255,0.1)",
                    showgrid=True,
                    tickfont=dict(size=14, family="Arial")
                ),
                yaxis=dict(
                    tickfont=dict(size=15, family="Arial Black"),
                    automargin=True
                ),
                showlegend=False,
            )

            st.plotly_chart(fig_centres, use_container_width=True)
        else:
            st.info("Colonne 'CENTRE FISCAL' introuvable.")

    # ============ LIGNE 3 : BILAN + STATS ============
    col_bilan, col_stats = st.columns([1, 1])

    with col_bilan:
        st.markdown("##### 📊 Bilan Global (Toutes Périodes)")

        if "OBJET" in df.columns:
            df["TYPE"] = df["OBJET"].apply(
                lambda x: "Incident"
                if isinstance(x, str)
                and any(w in x.lower() for w in ["panne", "bug", "erreur", "incident", "problème", "dysfonction"])
                else "Demande"
            )
        else:
            df["TYPE"] = "Demande"

        summary = df.pivot_table(
            index="TYPE",
            columns="Etat_Calculé",
            aggfunc="size",
            fill_value=0,
        )

        # Créer graphique en barres groupées
        fig_bilan = go.Figure()

        colors = {
            "effectue": "#4caf50",
            "encours": "#2196f3",
            "non traite": "#ff9800"
        }

        for col in ["effectue", "encours", "non traite"]:
            if col in summary.columns:
                fig_bilan.add_trace(
                    go.Bar(
                        name=col.replace("_", " ").title(),
                        x=summary.index,
                        y=summary[col],
                        marker_color=colors.get(col, "#00d4ff"),
                        text=summary[col],
                        textposition="auto",
                        textfont=dict(size=16, color="white", family="Arial Black"),
                    )
                )

        fig_bilan.update_layout(
            barmode="group",
            height=260,
            margin=dict(l=20, r=20, t=10, b=40),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white", size=14, family="Arial"),
            xaxis=dict(
                tickfont=dict(size=16, family="Arial Black"),
                gridcolor="rgba(255,255,255,0.1)"
            ),
            yaxis=dict(
                gridcolor="rgba(255,255,255,0.1)",
                showgrid=True,
                tickfont=dict(size=14, family="Arial")
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=14, family="Arial")
            ),
            showlegend=True,
        )

        st.plotly_chart(fig_bilan, use_container_width=True)

    with col_stats:
        st.markdown("##### 📈 Statistiques")

        stat1, stat2 = st.columns(2)
        with stat1:
            # Taux de traitement avec couleur conditionnelle
            taux_color = get_taux_color(taux_traitement)
            delta_display = f"{evolution_taux:+.1f}%" if total_prev > 0 else ""

            st.markdown(f"""<div style="background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%); padding: 16px; border-radius: 10px; border: 2px solid rgba(255,255,255,0.15); box-shadow: 0 4px 12px 0 rgba(0,0,0,0.4); text-align: center;">
<div style="font-size: 1.5rem; color: #FFFFFF; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">✅ TAUX TRAITEMENT</div>
<div style="font-size: 4.5rem; font-weight: 800; color: {taux_color}; line-height: 1.1;">{taux_traitement:.1f}%</div>
<div style="font-size: 1.2rem; color: {'#4caf50' if evolution_taux >= 0 else '#f44336'}; font-weight: 600; margin-top: 5px;">{delta_display}</div>
</div>""", unsafe_allow_html=True)

        with stat2:
            # Taux en cours avec style homogène
            st.markdown(f"""<div style="background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%); padding: 16px; border-radius: 10px; border: 2px solid rgba(255,255,255,0.15); box-shadow: 0 4px 12px 0 rgba(0,0,0,0.4); text-align: center;">
<div style="font-size: 1.5rem; color: #FFFFFF; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">⏳ TAUX EN COURS</div>
<div style="font-size: 4.5rem; font-weight: 800; color: #2196f3; line-height: 1.1;">{taux_encours:.1f}%</div>
</div>""", unsafe_allow_html=True)

        stat3, stat4 = st.columns(2)
        with stat3:
            # Aujourd'hui avec style homogène
            st.markdown(f"""<div style="background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%); padding: 16px; border-radius: 10px; border: 2px solid rgba(255,255,255,0.15); box-shadow: 0 4px 12px 0 rgba(0,0,0,0.4); text-align: center;">
<div style="font-size: 1.5rem; color: #FFFFFF; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">📅 AUJOURD'HUI</div>
<div style="font-size: 4.5rem; font-weight: 800; color: #00d4ff; line-height: 1.1;">{today.strftime("%d/%m")}</div>
</div>""", unsafe_allow_html=True)

        with stat4:
            # MAJ avec style homogène
            st.markdown(f"""<div style="background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%); padding: 16px; border-radius: 10px; border: 2px solid rgba(255,255,255,0.15); box-shadow: 0 4px 12px 0 rgba(0,0,0,0.4); text-align: center;">
<div style="font-size: 1.5rem; color: #FFFFFF; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">🕐 MAJ</div>
<div style="font-size: 4.5rem; font-weight: 800; color: #00d4ff; line-height: 1.1;">{heure_actuelle}</div>
</div>""", unsafe_allow_html=True)

else:
    st.info("⏳ Chargement des données...")

# Auto-refresh toutes les 5 minutes (300s)
time.sleep(300)
st.rerun()