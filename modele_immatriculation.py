import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="DGID — Portail d'immatriculation fiscale", page_icon="🏛️", layout="centered")

# ─── Load NAEMA catalogue ───
@st.cache_data
def load_catalogue():
    with open(Path(__file__).parent / "naema_catalogue.json", "r", encoding="utf-8") as f:
        return json.load(f)

catalogue = load_catalogue()
ALL_PRODUITS = catalogue["produits"]

# ─── CSS DGID Sénégal : Marron / Or / Blanc ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Source+Sans+3:wght@300;400;500;600;700&display=swap');

    :root {
        --brown-900: #3E2723; --brown-800: #4E342E; --brown-700: #5D4037;
        --brown-600: #6D4C41; --brown-500: #795548; --brown-400: #8D6E63;
        --brown-300: #A1887F; --brown-200: #BCAAA4; --brown-100: #D7CCC8;
        --brown-50:  #EFEBE9;
        --gold-600:  #B8860B; --gold-500:  #DAA520; --gold-400:  #E6B422;
        --gold-300:  #F0C850; --gold-200:  #F5D77A; --gold-100:  #FBF0D0;
        --gold-50:   #FFFBF0;
        --white: #FFFFFF; --off-white: #FAF8F5;
        --text-dark: #2C1810; --text-mid: #5D4037; --border: #E8DDD5;
    }

    .stApp { background: var(--off-white) !important; }
    .stApp > header { background: transparent !important; }

    .dgid-banner {
        background: linear-gradient(135deg, var(--brown-900) 0%, var(--brown-700) 60%, var(--brown-600) 100%);
        padding: 1.8rem 2rem 1.5rem; border-radius: 0 0 20px 20px;
        margin: -1rem -1rem 1.5rem -1rem; position: relative; overflow: hidden;
    }
    .dgid-banner::after {
        content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, var(--gold-500), var(--gold-300), var(--gold-500));
    }
    .dgid-banner h1 {
        color: var(--white) !important; font-family: 'Playfair Display', serif !important;
        font-size: 1.65rem !important; font-weight: 700 !important; margin: 0 0 0.25rem 0 !important;
    }
    .dgid-banner .subtitle {
        color: var(--gold-300); font-family: 'Source Sans 3', sans-serif;
        font-size: 0.9rem; letter-spacing: 1.5px; text-transform: uppercase;
    }

    .step-bar { display: flex; gap: 6px; margin: 0.5rem 0 1.5rem; padding: 0.75rem;
        background: var(--white); border-radius: 14px; border: 1px solid var(--border);
        box-shadow: 0 2px 8px rgba(62,39,35,0.06); }
    .step-item { flex: 1; text-align: center; padding: 0.65rem 0.5rem; border-radius: 10px;
        font-family: 'Source Sans 3', sans-serif; font-size: 0.82rem; font-weight: 600; }
    .step-item.active { background: linear-gradient(135deg, var(--gold-500), var(--gold-400));
        color: var(--brown-900); box-shadow: 0 4px 14px rgba(218,165,32,0.35); }
    .step-item.completed { background: var(--brown-800); color: var(--gold-300); }
    .step-item.pending { background: var(--brown-50); color: var(--brown-300); }
    .step-num { display: inline-block; width: 22px; height: 22px; line-height: 22px;
        border-radius: 50%; font-size: 0.72rem; font-weight: 700; margin-right: 5px; vertical-align: middle; }
    .step-item.active .step-num { background: var(--brown-900); color: var(--gold-300); }
    .step-item.completed .step-num { background: var(--gold-500); color: var(--brown-900); }
    .step-item.pending .step-num { background: var(--brown-100); color: var(--brown-300); }

    .confirm-card { background: var(--white); padding: 1.6rem 1.8rem; border-radius: 14px;
        border: 1px solid var(--border); border-left: 5px solid var(--gold-500);
        margin: 0.8rem 0; box-shadow: 0 2px 10px rgba(62,39,35,0.05); }
    .info-row { display: flex; align-items: baseline; padding: 0.7rem 0; border-bottom: 1px solid var(--brown-50); }
    .info-row:last-child { border-bottom: none; }
    .info-label { font-family: 'Source Sans 3', sans-serif; font-weight: 700;
        color: var(--brown-700); width: 200px; flex-shrink: 0; font-size: 0.9rem; }
    .info-value { font-family: 'Source Sans 3', sans-serif; color: var(--text-dark); font-size: 0.92rem; flex: 1; }

    .act-card {
        background: var(--gold-50); border: 1px solid var(--gold-200); border-radius: 10px;
        padding: 0.7rem 1rem; margin: 0.4rem 0;
        font-family: 'Source Sans 3', sans-serif;
    }
    .act-card .act-role {
        font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 1px; color: var(--gold-600); margin-bottom: 2px;
    }
    .act-card .act-name { font-weight: 600; color: var(--brown-900); font-size: 0.92rem; }
    .act-card .act-code { color: var(--brown-400); font-size: 0.8rem; }
    .act-card .act-branch { color: var(--brown-300); font-size: 0.78rem; margin-top: 2px; }

    .regime-header {
        background: linear-gradient(135deg, var(--brown-900) 0%, var(--brown-700) 100%);
        padding: 1.8rem 2rem; border-radius: 14px; text-align: center; margin: 1rem 0;
    }
    .regime-header h2 { color: var(--gold-400) !important; font-family: 'Playfair Display', serif !important;
        font-size: 1.55rem !important; margin: 0 !important; }
    .regime-header .regime-label { color: var(--brown-200); font-family: 'Source Sans 3', sans-serif;
        font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; }
    .regime-detail-card { background: var(--gold-50); border: 1px solid var(--gold-200);
        border-radius: 14px; padding: 1.6rem 1.8rem; margin: 1rem 0; }
    .regime-detail-card h3 { color: var(--brown-800) !important; font-family: 'Playfair Display', serif !important;
        margin: 0 0 0.4rem 0 !important; font-size: 1.15rem !important; }
    .regime-detail-card p { color: var(--brown-600); font-family: 'Source Sans 3', sans-serif;
        font-size: 0.95rem; margin: 0; }

    .next-steps { background: var(--white); border: 1px solid var(--border); border-radius: 14px; padding: 1.4rem 1.6rem; }
    .next-steps h4 { font-family: 'Playfair Display', serif !important; color: var(--brown-800) !important;
        font-size: 1rem !important; margin: 0 0 1rem 0 !important; }
    .ns-item { display: flex; align-items: flex-start; gap: 0.8rem; padding: 0.6rem 0; }
    .ns-num { flex-shrink: 0; width: 28px; height: 28px; line-height: 28px; text-align: center;
        border-radius: 50%; background: var(--gold-100); color: var(--brown-800);
        font-family: 'Source Sans 3', sans-serif; font-weight: 700; font-size: 0.8rem; }
    .ns-text { font-family: 'Source Sans 3', sans-serif; color: var(--text-mid); font-size: 0.9rem; line-height: 1.45; }

    /* Streamlit overrides */
    .stSelectbox label, .stTextInput label, .stTextArea label, .stNumberInput label {
        font-family: 'Source Sans 3', sans-serif !important; color: var(--brown-700) !important;
        font-weight: 600 !important; font-size: 0.88rem !important; }
    div[data-testid="stExpander"] {
        background: var(--white); border: 1px solid var(--border) !important;
        border-radius: 12px !important; margin-bottom: 0.6rem;
        box-shadow: 0 1px 4px rgba(62,39,35,0.04); overflow: hidden; }
    div[data-testid="stExpander"] > details > summary {
        font-family: 'Source Sans 3', sans-serif !important; color: var(--white) !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, var(--brown-800), var(--brown-700)) !important;
        padding: 0.8rem 1.2rem !important; }
    div[data-testid="stExpander"] > details > summary:hover {
        background: linear-gradient(135deg, var(--brown-700), var(--brown-600)) !important; }
    div[data-testid="stExpander"] > details > summary svg { color: var(--gold-300) !important; }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--gold-500), var(--gold-400)) !important;
        color: var(--brown-900) !important; border: none !important;
        font-family: 'Source Sans 3', sans-serif !important; font-weight: 700 !important;
        font-size: 0.92rem !important; border-radius: 10px !important;
        box-shadow: 0 4px 14px rgba(218,165,32,0.3) !important; }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(218,165,32,0.45) !important; }
    .stButton > button:not([kind="primary"]) {
        background: var(--white) !important; color: var(--brown-700) !important;
        border: 1.5px solid var(--brown-200) !important;
        font-family: 'Source Sans 3', sans-serif !important; font-weight: 600 !important;
        border-radius: 10px !important; }
    .stButton > button:not([kind="primary"]):hover {
        border-color: var(--gold-500) !important; background: var(--gold-50) !important; }

    .stCheckbox label span, .stCheckbox label span p {
        font-family: 'Source Sans 3', sans-serif !important; color: var(--brown-800) !important;
        font-weight: 600 !important; font-size: 0.92rem !important; }

    hr { border-color: var(--border) !important; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: var(--brown-800) !important; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ───
def reset_form():
    for k in list(st.session_state.keys()):
        del st.session_state[k]


def search_produits(query):
    """Search products by keywords in label, sub-branch and branch."""
    if not query or len(query) < 2:
        return []
    terms = query.lower().split()
    results = []
    for p in ALL_PRODUITS:
        text = f"{p['lib']} {p['sb_lib']} {p['br_lib']}".lower()
        if all(t in text for t in terms):
            results.append(p)
    return results[:30]


def render_activity_card(act, role_label):
    return f"""
    <div class="act-card">
        <div class="act-role">{role_label}</div>
        <div class="act-name">{act['lib']}</div>
        <div class="act-code">{act['id']} · {act['sb_lib']}</div>
        <div class="act-branch">Branche : {act['br_id']} — {act['br_lib']}</div>
    </div>
    """


# ─── Init ───
if "step" not in st.session_state:
    st.session_state["step"] = 0
if "activities" not in st.session_state:
    st.session_state["activities"] = []

step = st.session_state["step"]
steps_names = ["Questionnaire", "Récapitulatif"]

# ═══════════════════════════════════════
# HEADER
# ═══════════════════════════════════════
st.markdown("""
<div class="dgid-banner">
    <div style="display:flex; align-items:center;">
        <span style="font-size:2rem; margin-right:0.8rem;">🏛️</span>
        <div>
            <h1>Portail d'Immatriculation Fiscale</h1>
            <div class="subtitle">Direction Générale des Impôts et des Domaines — Sénégal</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

bar_html = '<div class="step-bar">'
for i, name in enumerate(steps_names):
    if i < step:
        cls, icon = "completed", "✓"
    elif i == step:
        cls, icon = "active", str(i + 1)
    else:
        cls, icon = "pending", str(i + 1)
    bar_html += f'<div class="step-item {cls}"><span class="step-num">{icon}</span> {name}</div>'
bar_html += '</div>'
st.markdown(bar_html, unsafe_allow_html=True)


# ═══════════════════════════════════════
# ÉTAPE 0 : QUESTIONNAIRE
# ═══════════════════════════════════════
if step == 0:
    st.markdown("#### 📋 Questionnaire d'immatriculation")
    st.caption("Remplissez les informations de votre entreprise — NAPS Rév. 2024")

    # ── Q1 : Activité(s) — recherche intelligente ──
    with st.expander("**① Quelle est votre activité principale ?**", expanded=True):
        st.markdown(
            "*Décrivez votre activité en quelques mots. "
            "Plus vous êtes précis, plus les suggestions se réduisent jusqu'au choix final.*"
        )

        search_query = st.text_input(
            "🔍 Rechercher une activité",
            placeholder="Ex : riz, vêtement, taxi, comptabilité, boulangerie, poisson…",
            key="search_query",
        )

        results = search_produits(search_query)

        if search_query and len(search_query) >= 2:
            if results:
                nb = len(results)
                if nb > 10:
                    st.caption(f"**{nb}** résultats — *affinez votre recherche pour réduire la liste*")
                else:
                    st.caption(f"**{nb}** résultat(s) trouvé(s)")

                options_map = {}
                for p in results:
                    label = f"{p['lib']}  ·  {p['sb_lib']}"
                    options_map[label] = p

                choice = st.selectbox(
                    "Sélectionnez l'activité correspondante",
                    options=["— Choisir parmi les résultats —"] + list(options_map.keys()),
                    key="activity_select",
                    label_visibility="collapsed",
                )

                if choice != "— Choisir parmi les résultats —":
                    selected = options_map[choice]
                    existing_ids = [a["id"] for a in st.session_state["activities"]]

                    # Show auto-determined hierarchy
                    st.markdown(f"""
                    <div class="act-card" style="border-left: 3px solid #DAA520;">
                        <div class="act-role">Hiérarchie déterminée automatiquement</div>
                        <div class="act-name">{selected['lib']}</div>
                        <div class="act-code">Code : {selected['id']} · Sous-branche : {selected['sb_lib']}</div>
                        <div class="act-branch">Secteur (Branche) : {selected['br_id']} — {selected['br_lib']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if selected["id"] not in existing_ids:
                        if st.button(f"✅ Ajouter « {selected['lib']} »", type="primary"):
                            st.session_state["activities"].append(selected)
                            st.rerun()
                    else:
                        st.info("✓ Cette activité est déjà dans votre liste.")
            else:
                st.warning("Aucun résultat. Essayez d'autres mots-clés (ex : riz, poisson, taxi, coiffure…)")

        # ── Display selected activities ──
        activities = st.session_state["activities"]
        if activities:
            st.divider()
            st.markdown("**Vos activités sélectionnées :**")

            for idx, act in enumerate(activities):
                role = "Activité principale" if idx == 0 else f"Activité secondaire {idx}"
                col_info, col_del = st.columns([6, 1])
                with col_info:
                    st.markdown(render_activity_card(act, role), unsafe_allow_html=True)
                with col_del:
                    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_{act['id']}_{idx}", help="Supprimer"):
                        st.session_state["activities"] = [
                            a for i, a in enumerate(activities) if i != idx
                        ]
                        st.rerun()

            st.caption("💡 *Recherchez ci-dessus pour ajouter des activités secondaires.*")

    if not st.session_state["activities"]:
        st.info("Veuillez rechercher et sélectionner au moins une activité pour continuer.")
        st.stop()

    # ── Q2 : Détails ──
    with st.expander("**② Détails complémentaires**", expanded=True):
        activity_desc = st.text_area(
            "Décrivez brièvement votre activité",
            placeholder="Ex : Vente de vêtements prêts-à-porter via boutique et réseaux sociaux…",
            key="activity_desc", height=100,
        )
        col1, col2 = st.columns(2)
        with col1:
            employees = st.number_input("Nombre d'employés", min_value=0, max_value=100000, value=0, step=1, key="employees")
        with col2:
            capital = st.number_input("Capital social (FCFA)", min_value=0, value=0, step=100000, key="capital")

        st.markdown("**Informations de contact**")
        col3, col4 = st.columns(2)
        with col3:
            st.text_input("Téléphone", placeholder="+221 …", key="phone")
        with col4:
            st.text_input("Email", placeholder="contact@entreprise.sn", key="email")

    st.divider()
    can_continue = (
        bool(st.session_state.get("activity_desc", "").strip())
        and len(st.session_state["activities"]) > 0
    )

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        if st.button("Passer à la confirmation →", type="primary", use_container_width=True, disabled=not can_continue):
            st.session_state["data_activities"] = list(st.session_state["activities"])
            st.session_state["data_activity_desc"] = st.session_state.get("activity_desc", "")
            st.session_state["data_employees"] = st.session_state.get("employees", 0)
            st.session_state["data_capital"] = st.session_state.get("capital", 0)
            st.session_state["data_phone"] = st.session_state.get("phone", "")
            st.session_state["data_email"] = st.session_state.get("email", "")
            st.session_state["step"] = 1
            st.rerun()
    with col_btn2:
        if st.button("Réinitialiser", use_container_width=True):
            reset_form()
            st.rerun()

    if not can_continue:
        st.warning("Veuillez compléter la description et sélectionner au moins une activité.")


# ═══════════════════════════════════════
# ÉTAPE 1 : RÉCAPITULATIF
# ═══════════════════════════════════════
elif step == 1:
    st.markdown("#### ✅ Récapitulatif de vos informations")
    st.caption("Vérifiez attentivement avant validation définitive")

    activities = st.session_state.get("data_activities", [])
    activity_desc = st.session_state.get("data_activity_desc", "")
    employees = st.session_state.get("data_employees", 0)
    capital = st.session_state.get("data_capital", 0)
    phone = st.session_state.get("data_phone", "")
    email = st.session_state.get("data_email", "")

    principal = activities[0] if activities else {}

    # Activities cards
    act_html = ""
    for idx, act in enumerate(activities):
        role = "Activité principale" if idx == 0 else f"Activité secondaire {idx}"
        act_html += render_activity_card(act, role)

    st.markdown(f"""
    <div class="confirm-card">
        <div class="info-row">
            <div class="info-label">Secteur d'activité</div>
            <div class="info-value"><strong>{principal.get('br_id','')}</strong> — {principal.get('br_lib','')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(act_html, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="confirm-card">
        <div class="info-row">
            <div class="info-label">Description</div>
            <div class="info-value">{activity_desc}</div>
        </div>
        <div class="info-row">
            <div class="info-label">Nombre d'employés</div>
            <div class="info-value">{employees}</div>
        </div>
        <div class="info-row">
            <div class="info-label">Capital social</div>
            <div class="info-value">{capital:,.0f} FCFA</div>
        </div>
        <div class="info-row">
            <div class="info-label">Téléphone</div>
            <div class="info-value">{phone if phone else "Non renseigné"}</div>
        </div>
        <div class="info-row">
            <div class="info-label">Email</div>
            <div class="info-value">{email if email else "Non renseigné"}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("##### Attestations")
    confirm1 = st.checkbox("Je certifie l'exactitude des informations fournies", key="confirm1")
    confirm2 = st.checkbox("J'accepte les conditions générales d'utilisation", key="confirm2")
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Retour", use_container_width=True):
            st.session_state["step"] = 0
            st.rerun()
    with col2:
        can_validate = confirm1 and confirm2
        if st.button("Confirmer définitivement", type="primary", use_container_width=True, disabled=not can_validate):
            st.session_state["validated"] = True
            st.balloons()
            st.success("🎉 Votre dossier a été enregistré avec succès !")

            st.markdown("""
            <div class="next-steps">
                <h4>Prochaines étapes</h4>
                <div class="ns-item"><div class="ns-num">1</div>
                    <div class="ns-text">Vous recevrez un email de confirmation avec votre numéro d'immatriculation</div></div>
                <div class="ns-item"><div class="ns-num">2</div>
                    <div class="ns-text">Téléchargez et complétez les formulaires requis</div></div>
                <div class="ns-item"><div class="ns-num">3</div>
                    <div class="ns-text">Soumettez vos pièces justificatives</div></div>
                <div class="ns-item"><div class="ns-num">4</div>
                    <div class="ns-text">Recevez votre certificat d'immatriculation fiscale</div></div>
            </div>
            """, unsafe_allow_html=True)

            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📥 Télécharger le récapitulatif", use_container_width=True):
                    st.info("Fonctionnalité à implémenter : génération PDF")
            with col_b:
                if st.button("Nouvelle immatriculation", type="primary", use_container_width=True):
                    reset_form()
                    st.rerun()

    with col3:
        if st.button("Annuler", use_container_width=True):
            reset_form()
            st.rerun()

    if not can_validate:
        st.info("Veuillez cocher les deux attestations pour valider.")
