import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import unicodedata

# --- CONFIGURATION ---
st.set_page_config(page_title="DSI TV Dashboard", layout="wide", initial_sidebar_state="collapsed")

# --- CSS ÉPURÉ & RESPONSIVE ---
st.markdown("""
<style>
    /* === RESET & BASE === */
    .block-container {
        padding: 0.5rem 1rem 0rem 1rem;
        max-width: 100%;
    }
    header, footer, #MainMenu { visibility: hidden; height: 0; margin: 0; padding: 0; }
    .stApp { background: #0d1117; }

    /* === VARIABLES DE DESIGN === */
    :root {
        --cyan: #00d4ff;
        --orange: #ff9800;
        --blue: #2196f3;
        --green: #4caf50;
        --red: #f44336;
        --card-bg: rgba(255,255,255,0.04);
        --card-border: rgba(255,255,255,0.1);
        --radius: 10px;
        --shadow: 0 2px 8px rgba(0,0,0,0.3);
    }

    /* === TITRES === */
    .main-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 800;
        color: #fff;
        letter-spacing: 2px;
        margin: 0 0 0.2rem 0;
        padding: 0;
    }
    .sub-title {
        text-align: center;
        font-size: 1.1rem;
        color: var(--cyan);
        font-weight: 600;
        margin: 0 0 0.6rem 0;
        opacity: 0.9;
    }

    /* === KPI CARD === */
    .kpi-card {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: var(--radius);
        padding: 12px 8px;
        text-align: center;
        box-shadow: var(--shadow);
        height: 100%;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.7);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.1;
    }
    .kpi-delta {
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 2px;
    }
    .kpi-delta.positive { color: var(--green); }
    .kpi-delta.negative { color: var(--red); }

    /* === SECTION TITLE === */
    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--cyan);
        margin: 0.3rem 0 0.3rem 0;
        letter-spacing: 0.5px;
    }

    /* === CACHE LES ÉLÉMENTS STREAMLIT INUTILES === */
    div[data-testid="stMetric"] { display: none; }
    .stSelectbox label { color: rgba(255,255,255,0.7) !important; font-size: 0.85rem !important; }
    .stDateInput label { color: rgba(255,255,255,0.7) !important; font-size: 0.85rem !important; }
    
    /* === SELECTBOX & DATE INPUT COMPACT === */
    .stSelectbox, .stDateInput { max-width: 280px; }
    .stSelectbox > div > div, .stDateInput > div > div { 
        background: rgba(255,255,255,0.06) !important; 
        border-color: rgba(255,255,255,0.15) !important;
    }

    /* === SCROLLBAR CACHÉE === */
    ::-webkit-scrollbar { display: none; }

    /* === LIGNE SEPARATOR === */
    hr { border-color: rgba(255,255,255,0.08) !important; margin: 0.4rem 0 !important; }
    
    /* === FIX PLOTLY OVERFLOW === */
    .stPlotlyChart { overflow: hidden; }
    
    /* Empêcher les colonnes de déborder */
    [data-testid="column"] { overflow: hidden; }
    
    /* === TABLE STYLING === */
    .dataframe-container {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: var(--radius);
        padding: 10px;
        overflow-x: auto;
    }
    
    /* Style pour le dataframe */
    div[data-testid="stDataFrame"] {
        background: transparent;
    }
</style>
""", unsafe_allow_html=True)


# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=300)
def load_data():
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTN1Jwosf-2KEvw6HSBx4s01S24_Tzy9SM38LoGaHUrGc-cSn0vf19ugAiNnA_6InNBQxBnyI7JN3wa/pub?gid=0&single=true&output=csv"
    try:
        df = pd.read_csv(csv_url)
        df["Date_Obj"] = pd.to_datetime(df["Horodateur"], dayfirst=True, errors="coerce")
        df["Heure"] = df["Date_Obj"].dt.hour
        df["Date_Simple"] = df["Date_Obj"].dt.date
        df["Semaine"] = df["Date_Obj"].dt.isocalendar().week
        df["Annee"] = df["Date_Obj"].dt.year

        if "ETAT DE LA DEMANDE" in df.columns:
            df["Status_Clean"] = (
                df["ETAT DE LA DEMANDE"]
                .astype(str).str.strip().str.upper()
                .str.replace("É", "E").str.replace("È", "E")
                .str.replace("Ê", "E").str.replace("À", "A")
                .str.replace("Ç", "C").str.replace("  ", " ")
            )
        else:
            df["Status_Clean"] = "INCONNU"
        return df
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
        return pd.DataFrame()


df = load_data()

# --- MOTS CLÉS ---
MOTS_TERMINES = ["TRAITE", "TRAITEE", "EFFECTUE", "EFFECTUEE", "OK", "FAIT", "FAITE",
                  "CLOTURE", "CLOTUREE", "TERMINE", "TERMINEE", "RESOLU", "RESOLUE"]
MOTS_EN_COURS = ["ENCOURS", "EN COURS", "ATTENTE", "EN ATTENTE", "TRAITEMENT",
                  "EN TRAITEMENT", "ENCOUR", "COURS"]


def categorize_status(status):
    s = "" if pd.isna(status) else str(status).strip().upper()
    if s == "" or s == "NAN":
        return "non traite"
    if "NON" in s or "PAS" in s:
        return "non traite"
    for mot in MOTS_TERMINES:
        if mot in s:
            return "effectue"
    for mot in MOTS_EN_COURS:
        if mot in s:
            return "encours"
    return "non traite"


# --- COMPOSANT KPI HTML ---
def kpi_html(label, value, color, delta=None, icon=""):
    delta_html = ""
    if delta is not None and delta != "":
        cls = "positive" if (isinstance(delta, (int, float)) and delta >= 0) else "negative"
        if isinstance(delta, float):
            delta_html = f'<div class="kpi-delta {cls}">{delta:+.1f}%</div>'
        elif isinstance(delta, int):
            delta_html = f'<div class="kpi-delta {cls}">{delta:+d}</div>'
    return f"""<div class="kpi-card">
<div class="kpi-label">{icon} {label}</div>
<div class="kpi-value" style="color:{color};">{value}</div>
{delta_html}</div>"""


# --- LAYOUT PLOTLY COMMUN ---
def base_layout(height=240, t=40, b=30, l=30, r=20):
    return dict(
        height=height,
        margin=dict(l=l, r=r, t=t, b=b),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", size=13, family="Arial"),
        showlegend=False,
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickfont=dict(size=12)),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickfont=dict(size=12), showgrid=True),
    )


# === MAIN ===
if not df.empty:
    today = datetime.now().date()
    
    # Catégorisation des statuts
    df["Etat_Calculé"] = df["Status_Clean"].apply(categorize_status)
    
    # Calcul du TYPE (Incident vs Demande)
    if "OBJET" in df.columns:
        df["TYPE"] = df["OBJET"].apply(
            lambda x: "Incident" if isinstance(x, str)
            and any(w in x.lower() for w in ["panne", "bug", "erreur", "incident", "problème", "dysfonction"])
            else "Demande"
        )
    else:
        df["TYPE"] = "Demande"

    # --- HEADER : filtre date + titre + filtre plateforme ---
    h_left, h_center, h_right = st.columns([1, 3, 1])
    
    with h_left:
        # Filtre de dates
        min_date = df["Date_Simple"].min()
        max_date = df["Date_Simple"].max()
        
        # Vérifier que les dates sont valides
        if pd.isna(min_date) or pd.isna(max_date):
            min_date = today - timedelta(days=30)
            max_date = today
        
        date_range = st.date_input(
            "Période",
            value=(today - timedelta(days=today.weekday()), today),
            min_value=min_date,
            max_value=max_date,
            label_visibility="collapsed"
        )
        
        # Gérer le cas où l'utilisateur sélectionne une seule date
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range if not isinstance(date_range, tuple) else date_range[0]
    
    with h_center:
        st.markdown('<div class="main-title">📊 DGID/DSI — GESTION HEBDO DES REQUÊTES</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sub-title">Période du {start_date.strftime("%d/%m")} au {end_date.strftime("%d/%m/%Y")} · MAJ {datetime.now().strftime("%H:%M")}</div>',
            unsafe_allow_html=True
        )
    
    with h_right:
        plateforme_selectionnee = "TOUTES"
        if "LA PLATEFORME" in df.columns:
            opts = ["TOUTES"] + sorted(df["LA PLATEFORME"].dropna().unique().tolist())
            plateforme_selectionnee = st.selectbox("Plateforme", options=opts, index=0, label_visibility="collapsed")

    # Filtrage des données selon la période sélectionnée
    df_period = df[(df["Date_Simple"] >= start_date) & (df["Date_Simple"] <= end_date)].copy()
    
    # Calcul de la période précédente (même durée)
    period_duration = (end_date - start_date).days
    start_of_prev_period = start_date - timedelta(days=period_duration + 1)
    end_of_prev_period = start_date - timedelta(days=1)
    df_prev_period = df[(df["Date_Simple"] >= start_of_prev_period) & (df["Date_Simple"] <= end_of_prev_period)].copy()

    # Filtre plateforme
    if "LA PLATEFORME" in df.columns and plateforme_selectionnee != "TOUTES":
        df_period = df_period[df_period["LA PLATEFORME"] == plateforme_selectionnee].copy()
        df_prev_period = df_prev_period[df_prev_period["LA PLATEFORME"] == plateforme_selectionnee].copy()

    # --- CALCULS KPI ---
    total = len(df_period)
    non_traites = (df_period["Etat_Calculé"] == "non traite").sum()
    en_cours = (df_period["Etat_Calculé"] == "encours").sum()
    effectue = (df_period["Etat_Calculé"] == "effectue").sum()
    taux = (effectue / total * 100) if total > 0 else 0

    total_prev = len(df_prev_period)
    effectue_prev = (df_prev_period["Etat_Calculé"] == "effectue").sum()
    taux_prev = (effectue_prev / total_prev * 100) if total_prev > 0 else 0

    delta_total = total - total_prev if total_prev > 0 else None
    delta_taux = taux - taux_prev if total_prev > 0 else None

    taux_color = "#4caf50" if taux >= 75 else "#ff9800" if taux >= 50 else "#f44336"
    taux_encours = (en_cours / total * 100) if total > 0 else 0

    # =============================================
    # LIGNE 1 : KPI (6 cartes en ligne)
    # =============================================
    k1, k2, k3, k4, k5, k6 = st.columns(6, gap="small")
    with k1:
        st.markdown(kpi_html("Total Requêtes", int(total), "#00d4ff", delta=delta_total, icon="📋"), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_html("Non Effectué", int(non_traites), "#ff9800", icon="⚠️"), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_html("En Cours", int(en_cours), "#2196f3", icon="⏳"), unsafe_allow_html=True)
    with k4:
        st.markdown(kpi_html("Effectué", int(effectue), "#4caf50", icon="✅"), unsafe_allow_html=True)
    with k5:
        st.markdown(kpi_html("Taux Traitement", f"{taux:.0f}%", taux_color, delta=delta_taux, icon="📊"), unsafe_allow_html=True)
    with k6:
        st.markdown(kpi_html("En Cours", f"{taux_encours:.0f}%", "#2196f3", icon="⏳"), unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # =============================================
    # LIGNE 2 : Top Centres Fiscaux + Pyramide Plateformes + Bilan Global
    # =============================================
    c1, c2, c3 = st.columns([1.2, 1, 1.2], gap="medium")

    # --- Top 5 Centres Fiscaux ---
    with c1:
        st.markdown('<div class="section-title">🏢 Top 5 Centres Fiscaux</div>', unsafe_allow_html=True)

        if "CENTRE FISCAL" in df.columns:
            top_c = df_period["CENTRE FISCAL"].value_counts().head(5).reset_index()
            top_c.columns = ["Centre", "Requêtes"]
            top_c = top_c.sort_values("Requêtes", ascending=True)

            fig_top = go.Figure()
            fig_top.add_trace(go.Bar(
                x=top_c["Requêtes"], y=top_c["Centre"], orientation="h",
                marker=dict(color=top_c["Requêtes"],
                            colorscale=[[0, "#0d3b4f"], [1, "#00d4ff"]],
                            line=dict(color="rgba(0,212,255,0.4)", width=1)),
                text=top_c["Requêtes"], textposition="outside",
                textfont=dict(size=14, color="white"),
            ))
            layout_h = base_layout(height=280, t=5, b=20, l=10, r=40)
            layout_h["yaxis"]["tickfont"] = dict(size=11, color="white")
            layout_h["yaxis"]["automargin"] = True
            fig_top.update_layout(**layout_h)
            st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Colonne 'CENTRE FISCAL' introuvable.")

    # --- Pyramide Plateformes ---
    with c2:
        st.markdown('<div class="section-title">🖥️ Plateformes</div>', unsafe_allow_html=True)

        if "LA PLATEFORME" in df.columns:
            plat = df_period["LA PLATEFORME"].fillna("INCONNU").astype(str).str.strip()
            pyramid_data = plat.value_counts().reset_index()
            pyramid_data.columns = ["Plateforme", "Volume"]
            pyramid_data = pyramid_data.sort_values("Volume", ascending=False)

            # Création du diagramme en pyramide (funnel chart)
            fig_pyramid = go.Figure()
            
            colors_pyramid = ['#00d4ff', '#2196f3', '#4caf50', '#ff9800', '#f44336', '#9c27b0']
            
            fig_pyramid.add_trace(go.Funnel(
                y=pyramid_data["Plateforme"],
                x=pyramid_data["Volume"],
                textposition="inside",
                textinfo="value+percent initial",
                marker=dict(
                    color=colors_pyramid[:len(pyramid_data)],
                    line=dict(color="rgba(255,255,255,0.3)", width=1)
                ),
                connector=dict(line=dict(color="rgba(255,255,255,0.2)", width=2)),
            ))
            
            fig_pyramid.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white", size=11),
                showlegend=False,
            )
            st.plotly_chart(fig_pyramid, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Colonne 'LA PLATEFORME' introuvable.")

    # --- Bilan Global (Toutes Périodes) ---
    with c3:
        st.markdown('<div class="section-title">📊 Bilan Global (Toutes Périodes)</div>', unsafe_allow_html=True)

        summary = df.pivot_table(index="TYPE", columns="Etat_Calculé", aggfunc="size", fill_value=0)

        cat_colors = {"effectue": "#4caf50", "encours": "#2196f3", "non traite": "#ff9800"}
        cat_labels = {"effectue": "Effectué", "encours": "En cours", "non traite": "Non traité"}

        fig_bilan = go.Figure()
        for col_name in ["effectue", "encours", "non traite"]:
            if col_name in summary.columns:
                fig_bilan.add_trace(go.Bar(
                    name=cat_labels[col_name], x=summary.index, y=summary[col_name],
                    marker_color=cat_colors[col_name],
                    text=summary[col_name], textposition="auto",
                    textfont=dict(size=13, color="white"),
                ))

        layout_b = base_layout(height=280, t=5, b=30)
        layout_b["barmode"] = "group"
        layout_b["showlegend"] = True
        layout_b["legend"] = dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
            font=dict(size=11, color="white")
        )
        layout_b["xaxis"]["tickfont"] = dict(size=13, family="Arial", color="white")
        fig_bilan.update_layout(**layout_b)
        st.plotly_chart(fig_bilan, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<hr>", unsafe_allow_html=True)

    # =============================================
    # LIGNE 3 : Liste des requêtes non effectuées avec waiting time
    # =============================================
    st.markdown('<div class="section-title">⚠️ Requêtes Non Effectuées (Toutes Périodes)</div>', unsafe_allow_html=True)

    # Filtrer les requêtes non effectuées
    df_non_effectue = df[df["Etat_Calculé"] == "non traite"].copy()
    
    if len(df_non_effectue) > 0:
        # Calculer le temps d'attente (waiting time)
        df_non_effectue["Waiting_Time_Days"] = (pd.Timestamp.now() - df_non_effectue["Date_Obj"]).dt.days
        df_non_effectue["Waiting_Time_Hours"] = (pd.Timestamp.now() - df_non_effectue["Date_Obj"]).dt.total_seconds() / 3600
        
        # Formater le waiting time
        def format_waiting_time(hours):
            if hours < 24:
                return f"{int(hours)}h"
            else:
                days = int(hours // 24)
                remaining_hours = int(hours % 24)
                return f"{days}j {remaining_hours}h"
        
        df_non_effectue["Temps d'attente"] = df_non_effectue["Waiting_Time_Hours"].apply(format_waiting_time)
        
        # Sélectionner et renommer les colonnes à afficher
        colonnes_display = []
        renommage = {}
        
        if "Date_Obj" in df_non_effectue.columns:
            colonnes_display.append("Date_Obj")
            renommage["Date_Obj"] = "Date"
        if "CENTRE FISCAL" in df_non_effectue.columns:
            colonnes_display.append("CENTRE FISCAL")
            renommage["CENTRE FISCAL"] = "Centre Fiscal"
        if "LA PLATEFORME" in df_non_effectue.columns:
            colonnes_display.append("LA PLATEFORME")
            renommage["LA PLATEFORME"] = "Plateforme"
        if "OBJET" in df_non_effectue.columns:
            colonnes_display.append("OBJET")
            renommage["OBJET"] = "Objet"
        if "TYPE" in df_non_effectue.columns:
            colonnes_display.append("TYPE")
            renommage["TYPE"] = "Type"
        
        colonnes_display.append("Temps d'attente")
        
        # Créer le DataFrame à afficher
        df_display = df_non_effectue[colonnes_display].copy()
        df_display = df_display.rename(columns=renommage)
        
        # Formater la date
        if "Date" in df_display.columns:
            df_display["Date"] = pd.to_datetime(df_display["Date"]).dt.strftime("%d/%m/%Y %H:%M")
        
        # Trier par temps d'attente (décroissant)
        df_display = df_display.sort_values("Temps d'attente", ascending=False)
        
        # Afficher le dataframe avec style
        st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=400,
            column_config={
                "Date": st.column_config.TextColumn("Date", width="medium"),
                "Centre Fiscal": st.column_config.TextColumn("Centre Fiscal", width="medium"),
                "Plateforme": st.column_config.TextColumn("Plateforme", width="small"),
                "Objet": st.column_config.TextColumn("Objet", width="large"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Temps d'attente": st.column_config.TextColumn("Temps d'attente", width="small"),
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Statistique rapide
        avg_waiting = df_non_effectue["Waiting_Time_Days"].mean()
        max_waiting = df_non_effectue["Waiting_Time_Days"].max()
        
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Non Effectué</div><div class="kpi-value" style="color:#ff9800;font-size:1.8rem;">{len(df_non_effectue)}</div></div>', unsafe_allow_html=True)
        with stat_col2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Attente Moyenne</div><div class="kpi-value" style="color:#2196f3;font-size:1.8rem;">{avg_waiting:.1f}j</div></div>', unsafe_allow_html=True)
        with stat_col3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Attente Maximale</div><div class="kpi-value" style="color:#f44336;font-size:1.8rem;">{max_waiting:.0f}j</div></div>', unsafe_allow_html=True)
    else:
        st.success("✅ Aucune requête non effectuée ! Excellent travail !")

else:
    st.info("⏳ Chargement des données...")

# --- AUTO-REFRESH via st.rerun (5 min) ---
import time
time.sleep(300)
st.rerun()