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
    
    /* === SELECTBOX COMPACT === */
    .stSelectbox { max-width: 280px; }
    .stSelectbox > div > div { 
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
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    start_of_prev_week = start_of_week - timedelta(days=7)
    end_of_prev_week = end_of_week - timedelta(days=7)

    df["Etat_Calculé"] = df["Status_Clean"].apply(categorize_status)
    df_week = df[(df["Date_Simple"] >= start_of_week) & (df["Date_Simple"] <= end_of_week)].copy()
    df_prev_week = df[(df["Date_Simple"] >= start_of_prev_week) & (df["Date_Simple"] <= end_of_prev_week)].copy()

    # --- HEADER : titre + filtre sur même ligne ---
    h_left, h_center, h_right = st.columns([1, 3, 1])
    with h_center:
        st.markdown('<div class="main-title">📊 DGID/DSI — GESTION HEBDO DES REQUÊTES</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sub-title">Semaine du {start_of_week.strftime("%d/%m")} au {end_of_week.strftime("%d/%m/%Y")} · MAJ {datetime.now().strftime("%H:%M")}</div>',
            unsafe_allow_html=True
        )
    with h_right:
        plateforme_selectionnee = "TOUTES"
        if "LA PLATEFORME" in df.columns:
            opts = ["TOUTES"] + sorted(df["LA PLATEFORME"].dropna().unique().tolist())
            plateforme_selectionnee = st.selectbox("Plateforme", options=opts, index=0, label_visibility="collapsed")

    # Filtre plateforme
    if "LA PLATEFORME" in df.columns and plateforme_selectionnee != "TOUTES":
        df_week = df_week[df_week["LA PLATEFORME"] == plateforme_selectionnee].copy()
        df_prev_week = df_prev_week[df_prev_week["LA PLATEFORME"] == plateforme_selectionnee].copy()

    # --- CALCULS KPI ---
    total = len(df_week)
    non_traites = (df_week["Etat_Calculé"] == "non traite").sum()
    en_cours = (df_week["Etat_Calculé"] == "encours").sum()
    effectue = (df_week["Etat_Calculé"] == "effectue").sum()
    taux = (effectue / total * 100) if total > 0 else 0

    total_prev = len(df_prev_week)
    effectue_prev = (df_prev_week["Etat_Calculé"] == "effectue").sum()
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
    # LIGNE 2 : Activité jour + Plateformes
    # =============================================
    c_left, c_right = st.columns([1, 1], gap="medium")

    with c_left:
        st.markdown('<div class="section-title">📈 Activité par Jour</div>', unsafe_allow_html=True)

        daily = df_week.groupby(df_week["Date_Obj"].dt.day_name()).size().reset_index(name="Requetes")
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days_fr = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        daily["Order"] = daily["Date_Obj"].apply(lambda x: days_order.index(x) if x in days_order else 7)
        daily = daily.sort_values("Order")
        daily["Jour"] = daily["Date_Obj"].map(dict(zip(days_order, days_fr)))

        fig_act = go.Figure()
        fig_act.add_trace(go.Bar(
            x=daily["Jour"], y=daily["Requetes"],
            marker=dict(color=daily["Requetes"], colorscale=[[0, "#1a3a5c"], [1, "#00d4ff"]],
                        line=dict(color="rgba(0,212,255,0.5)", width=1)),
            text=daily["Requetes"], textposition="outside",
            textfont=dict(size=14, color="white", family="Arial"),
        ))
        layout = base_layout(height=230, t=10, b=40)
        layout["xaxis"]["tickfont"] = dict(size=13, family="Arial", color="white")
        fig_act.update_layout(**layout)
        st.plotly_chart(fig_act, use_container_width=True, config={"displayModeBar": False})

    with c_right:
        st.markdown('<div class="section-title">🖥️ Répartition Plateformes</div>', unsafe_allow_html=True)

        if "LA PLATEFORME" in df.columns:
            plat = df_week["LA PLATEFORME"].fillna("INCONNU").astype(str).str.strip()
            pie_data = plat.value_counts().reset_index()
            pie_data.columns = ["Plateforme", "Volume"]

            colors_plat = px.colors.qualitative.Set3[:len(pie_data)]
            fig_pie = go.Figure(data=[go.Pie(
                labels=pie_data["Plateforme"], values=pie_data["Volume"],
                hole=0.45,
                textinfo="label+percent",
                textfont=dict(size=13, color="black"),
                marker=dict(colors=colors_plat, line=dict(color="rgba(0,0,0,0.3)", width=1)),
                hovertemplate="<b>%{label}</b><br>%{value} requêtes<br>%{percent}<extra></extra>",
            )])
            fig_pie.update_layout(
                height=230, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white", size=12),
                showlegend=False,
                annotations=[dict(text=f"<b>{total}</b><br>total", x=0.5, y=0.5,
                                  font=dict(size=18, color="white"), showarrow=False)]
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Colonne 'LA PLATEFORME' introuvable.")

    # =============================================
    # LIGNE 3 : Top Centres + Bilan Global
    # =============================================
    c_left2, c_right2 = st.columns([1, 1], gap="medium")

    with c_left2:
        st.markdown('<div class="section-title">🏢 Top 5 Centres Fiscaux</div>', unsafe_allow_html=True)

        if "CENTRE FISCAL" in df.columns:
            top_c = df_week["CENTRE FISCAL"].value_counts().head(5).reset_index()
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
            layout_h = base_layout(height=220, t=5, b=20, l=10, r=40)
            layout_h["yaxis"]["tickfont"] = dict(size=12, color="white")
            layout_h["yaxis"]["automargin"] = True
            fig_top.update_layout(**layout_h)
            st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Colonne 'CENTRE FISCAL' introuvable.")

    with c_right2:
        st.markdown('<div class="section-title">📊 Bilan Global (Toutes Périodes)</div>', unsafe_allow_html=True)

        if "OBJET" in df.columns:
            df["TYPE"] = df["OBJET"].apply(
                lambda x: "Incident" if isinstance(x, str)
                and any(w in x.lower() for w in ["panne", "bug", "erreur", "incident", "problème", "dysfonction"])
                else "Demande"
            )
        else:
            df["TYPE"] = "Demande"

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

        layout_b = base_layout(height=220, t=5, b=30)
        layout_b["barmode"] = "group"
        layout_b["showlegend"] = True
        layout_b["legend"] = dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5,
            font=dict(size=12, color="white")
        )
        layout_b["xaxis"]["tickfont"] = dict(size=14, family="Arial", color="white")
        fig_bilan.update_layout(**layout_b)
        st.plotly_chart(fig_bilan, use_container_width=True, config={"displayModeBar": False})

else:
    st.info("⏳ Chargement des données...")

# --- AUTO-REFRESH via st.rerun (5 min) ---
# Utilise st.empty pour ne pas bloquer l'UI
import time
time.sleep(300)
st.rerun()