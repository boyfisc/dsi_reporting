import streamlit as st
from naema_data import SECTIONS, DIVISIONS, GROUPS, get_divisions_for_section, get_groups_for_division

st.set_page_config(page_title="DGID — Portail d'immatriculation fiscale", page_icon="🏛️", layout="centered")

# ─── CSS DGID Sénégal : Marron / Or / Blanc ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Source+Sans+3:wght@300;400;500;600;700&display=swap');

    :root {
        --brown-900: #3E2723;
        --brown-800: #4E342E;
        --brown-700: #5D4037;
        --brown-600: #6D4C41;
        --brown-500: #795548;
        --brown-400: #8D6E63;
        --brown-300: #A1887F;
        --brown-200: #BCAAA4;
        --brown-100: #D7CCC8;
        --brown-50:  #EFEBE9;
        --gold-600:  #B8860B;
        --gold-500:  #DAA520;
        --gold-400:  #E6B422;
        --gold-300:  #F0C850;
        --gold-200:  #F5D77A;
        --gold-100:  #FBF0D0;
        --gold-50:   #FFFBF0;
        --white:     #FFFFFF;
        --off-white: #FAF8F5;
        --text-dark: #2C1810;
        --text-mid:  #5D4037;
        --text-light:#8D6E63;
        --border:    #E8DDD5;
        --success:   #2E7D32;
        --success-bg:#E8F5E9;
    }

    /* ── Global ── */
    .stApp {
        background: var(--off-white) !important;
    }

    .stApp > header {
        background: transparent !important;
    }

    /* ── Top banner ── */
    .dgid-banner {
        background: linear-gradient(135deg, var(--brown-900) 0%, var(--brown-700) 60%, var(--brown-600) 100%);
        padding: 1.8rem 2rem 1.5rem;
        border-radius: 0 0 20px 20px;
        margin: -1rem -1rem 1.5rem -1rem;
        position: relative;
        overflow: hidden;
    }
    .dgid-banner::before {
        content: '';
        position: absolute;
        top: 0; right: 0;
        width: 300px; height: 100%;
        background: radial-gradient(ellipse at 80% 40%, rgba(218,165,32,0.15), transparent 70%);
    }
    .dgid-banner::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--gold-500), var(--gold-300), var(--gold-500));
    }
    .dgid-banner h1 {
        color: var(--white) !important;
        font-family: 'Playfair Display', serif !important;
        font-size: 1.65rem !important;
        font-weight: 700 !important;
        margin: 0 0 0.25rem 0 !important;
        letter-spacing: 0.3px;
    }
    .dgid-banner .subtitle {
        color: var(--gold-300);
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.9rem;
        font-weight: 400;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }
    .dgid-banner .emblem {
        font-size: 2rem;
        margin-right: 0.8rem;
    }

    /* ── Step bar ── */
    .step-bar {
        display: flex;
        gap: 6px;
        margin: 0.5rem 0 1.5rem;
        padding: 0.75rem;
        background: var(--white);
        border-radius: 14px;
        border: 1px solid var(--border);
        box-shadow: 0 2px 8px rgba(62,39,35,0.06);
    }
    .step-item {
        flex: 1;
        text-align: center;
        padding: 0.65rem 0.5rem;
        border-radius: 10px;
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.82rem;
        font-weight: 600;
        transition: all 0.3s ease;
        position: relative;
    }
    .step-item.active {
        background: linear-gradient(135deg, var(--gold-500), var(--gold-400));
        color: var(--brown-900);
        box-shadow: 0 4px 14px rgba(218,165,32,0.35);
    }
    .step-item.completed {
        background: var(--brown-800);
        color: var(--gold-300);
    }
    .step-item.pending {
        background: var(--brown-50);
        color: var(--brown-300);
    }
    .step-num {
        display: inline-block;
        width: 22px; height: 22px;
        line-height: 22px;
        border-radius: 50%;
        font-size: 0.72rem;
        font-weight: 700;
        margin-right: 5px;
        vertical-align: middle;
    }
    .step-item.active .step-num {
        background: var(--brown-900);
        color: var(--gold-300);
    }
    .step-item.completed .step-num {
        background: var(--gold-500);
        color: var(--brown-900);
    }
    .step-item.pending .step-num {
        background: var(--brown-100);
        color: var(--brown-300);
    }

    /* ── Section card ── */
    .section-card {
        background: var(--white);
        border-radius: 14px;
        border: 1px solid var(--border);
        padding: 1.6rem 1.8rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(62,39,35,0.05);
    }
    .section-card h3 {
        font-family: 'Playfair Display', serif !important;
        color: var(--brown-800) !important;
        font-size: 1.1rem !important;
        margin: 0 0 1rem 0 !important;
        padding-bottom: 0.6rem;
        border-bottom: 2px solid var(--gold-200);
    }

    /* ── Confirmation card ── */
    .confirm-card {
        background: var(--white);
        padding: 1.6rem 1.8rem;
        border-radius: 14px;
        border: 1px solid var(--border);
        border-left: 5px solid var(--gold-500);
        margin: 0.8rem 0;
        box-shadow: 0 2px 10px rgba(62,39,35,0.05);
    }
    .info-row {
        display: flex;
        align-items: baseline;
        padding: 0.7rem 0;
        border-bottom: 1px solid var(--brown-50);
    }
    .info-row:last-child { border-bottom: none; }
    .info-label {
        font-family: 'Source Sans 3', sans-serif;
        font-weight: 700;
        color: var(--brown-700);
        width: 200px;
        flex-shrink: 0;
        font-size: 0.9rem;
    }
    .info-value {
        font-family: 'Source Sans 3', sans-serif;
        color: var(--text-dark);
        font-size: 0.92rem;
        flex: 1;
    }

    /* ── Regime result box ── */
    .regime-header {
        background: linear-gradient(135deg, var(--brown-900) 0%, var(--brown-700) 100%);
        padding: 1.8rem 2rem;
        border-radius: 14px;
        text-align: center;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }
    .regime-header::before {
        content: '';
        position: absolute;
        top: -40%; left: -20%;
        width: 140%; height: 180%;
        background: radial-gradient(ellipse at center, rgba(218,165,32,0.08), transparent 60%);
    }
    .regime-header h2 {
        color: var(--gold-400) !important;
        font-family: 'Playfair Display', serif !important;
        font-size: 1.55rem !important;
        margin: 0 !important;
        position: relative;
    }
    .regime-header .regime-icon {
        font-size: 2.2rem;
        margin-bottom: 0.3rem;
    }
    .regime-header .regime-label {
        color: var(--brown-200);
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.8rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        position: relative;
    }

    .regime-detail-card {
        background: var(--gold-50);
        border: 1px solid var(--gold-200);
        border-radius: 14px;
        padding: 1.6rem 1.8rem;
        margin: 1rem 0;
    }
    .regime-detail-card h3 {
        color: var(--brown-800) !important;
        font-family: 'Playfair Display', serif !important;
        margin: 0 0 0.4rem 0 !important;
        font-size: 1.15rem !important;
    }
    .regime-detail-card p {
        color: var(--brown-600);
        font-family: 'Source Sans 3', sans-serif;
        font-size: 0.95rem;
        margin: 0;
    }

    /* ── Next steps ── */
    .next-steps {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
    }
    .next-steps h4 {
        font-family: 'Playfair Display', serif !important;
        color: var(--brown-800) !important;
        font-size: 1rem !important;
        margin: 0 0 1rem 0 !important;
    }
    .ns-item {
        display: flex;
        align-items: flex-start;
        gap: 0.8rem;
        padding: 0.6rem 0;
    }
    .ns-num {
        flex-shrink: 0;
        width: 28px; height: 28px;
        line-height: 28px;
        text-align: center;
        border-radius: 50%;
        background: var(--gold-100);
        color: var(--brown-800);
        font-family: 'Source Sans 3', sans-serif;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .ns-text {
        font-family: 'Source Sans 3', sans-serif;
        color: var(--text-mid);
        font-size: 0.9rem;
        line-height: 1.45;
    }

    /* ── Streamlit overrides ── */
    .stSelectbox label, .stTextInput label, .stTextArea label, .stNumberInput label {
        font-family: 'Source Sans 3', sans-serif !important;
        color: var(--brown-700) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    div[data-testid="stExpander"] {
        background: var(--white);
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        margin-bottom: 0.6rem;
        box-shadow: 0 1px 4px rgba(62,39,35,0.04);
        overflow: hidden;
    }
    div[data-testid="stExpander"] > details > summary {
        font-family: 'Source Sans 3', sans-serif !important;
        color: var(--white) !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, var(--brown-800), var(--brown-700)) !important;
        padding: 0.8rem 1.2rem !important;
        border-radius: 0 !important;
    }
    div[data-testid="stExpander"] > details > summary:hover {
        background: linear-gradient(135deg, var(--brown-700), var(--brown-600)) !important;
    }
    div[data-testid="stExpander"] > details > summary svg {
        color: var(--gold-300) !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--gold-500), var(--gold-400)) !important;
        color: var(--brown-900) !important;
        border: none !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        box-shadow: 0 4px 14px rgba(218,165,32,0.3) !important;
        transition: all 0.25s !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(218,165,32,0.45) !important;
        transform: translateY(-1px);
    }

    .stButton > button:not([kind="primary"]) {
        background: var(--white) !important;
        color: var(--brown-700) !important;
        border: 1.5px solid var(--brown-200) !important;
        font-family: 'Source Sans 3', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        transition: all 0.25s !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        border-color: var(--gold-500) !important;
        color: var(--brown-900) !important;
        background: var(--gold-50) !important;
    }

    .stCheckbox label span,
    .stCheckbox label span p {
        font-family: 'Source Sans 3', sans-serif !important;
        color: var(--brown-800) !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
    }

    /* alert boxes */
    .stAlert > div[data-testid="stNotification"] {
        font-family: 'Source Sans 3', sans-serif !important;
        border-radius: 10px !important;
    }

    hr {
        border-color: var(--border) !important;
    }

    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: var(--brown-800) !important;
    }

    /* scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--brown-50); }
    ::-webkit-scrollbar-thumb { background: var(--brown-200); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── Données NAEMA (inchangées) ───
LEGAL_FORM_TO_SECTORS = {
    "Entreprise Individuelle": ["Commerce de détail", "Artisanat", "Services de proximité"],
    "GIE": ["Pêche", "Agriculture", "Groupements de promotion féminine"],
    "SARL / SUARL": ["PME", "Import-Export", "Services aux entreprises", "Transport"],
    "SCI": ["Gestion de patrimoine", "Location immobilière (résidentielle/bureaux)"],
    "SAS / SASU": ["Startups Tech", "Conseil", "Projets à investissements multiples"],
    "SA": ["Banques", "Assurances", "Industrie lourde", "Mines et Hydrocarbures"],
}

SECTOR_TO_NAEMA = {
    "Commerce de détail": [
        ("G47.11", "Commerce de détail en magasin non spécialisé (alimentation)"),
        ("G47.19", "Autre commerce de détail en magasin non spécialisé"),
        ("G47.91", "Vente à distance / e-commerce"),
    ],
    "Artisanat": [
        ("C31.01", "Fabrication de meubles (artisanat)"),
        ("C14.13", "Confection de vêtements (artisanat)"),
        ("C25.11", "Fabrication de structures métalliques (atelier)"),
    ],
    "Services de proximité": [
        ("S96.02", "Coiffure et soins de beauté"),
        ("S95.29", "Réparation d'autres biens personnels et domestiques"),
        ("I56.10", "Restauration (petite restauration / proximité)"),
    ],
    "Pêche": [
        ("A03.11", "Pêche en mer"),
        ("A03.12", "Pêche en eau douce"),
        ("A03.22", "Aquaculture en eau douce"),
    ],
    "Agriculture": [
        ("A01.11", "Culture de céréales (hors riz)"),
        ("A01.13", "Culture de légumes"),
        ("A01.25", "Culture de fruits tropicaux et subtropicaux"),
    ],
    "Groupements de promotion féminine": [
        ("S94.11", "Activités d'organisations professionnelles"),
        ("S94.99", "Autres organisations associatives n.c.a."),
    ],
    "PME": [
        ("C10.89", "Autres industries alimentaires n.c.a."),
        ("C13.20", "Tissage de textiles"),
        ("C22.29", "Fabrication d'articles en plastique n.c.a."),
    ],
    "Import-Export": [
        ("G46.19", "Intermédiaires du commerce en produits divers"),
        ("G46.90", "Commerce de gros non spécialisé (import/export)"),
        ("H52.29", "Autres services auxiliaires des transports"),
    ],
    "Services aux entreprises": [
        ("N82.99", "Autres activités de soutien aux entreprises n.c.a."),
        ("M69.20", "Comptabilité, audit, conseil fiscal"),
        ("N80.10", "Activités de sécurité privée"),
    ],
    "Transport": [
        ("H49.41", "Transport routier de fret"),
        ("H49.31", "Transport urbain et suburbain de voyageurs"),
        ("H52.10", "Entreposage et stockage"),
    ],
    "Gestion de patrimoine": [
        ("L68.20", "Location et exploitation de biens immobiliers propres ou loués"),
        ("K64.99", "Autres activités de services financiers (hors assurance) n.c.a."),
    ],
    "Location immobilière (résidentielle/bureaux)": [
        ("L68.20", "Location et exploitation de biens immobiliers propres ou loués"),
        ("L68.32", "Administration de biens immobiliers pour le compte de tiers"),
    ],
    "Startups Tech": [
        ("J62.01", "Programmation informatique"),
        ("J62.02", "Conseil en systèmes et logiciels informatiques"),
        ("J63.11", "Traitement de données, hébergement, activités connexes"),
    ],
    "Conseil": [
        ("M70.22", "Conseil pour les affaires et autres conseils de gestion"),
        ("M74.90", "Autres activités spécialisées, scientifiques et techniques n.c.a."),
    ],
    "Projets à investissements multiples": [
        ("K64.99", "Autres activités de services financiers n.c.a. (holding/projets)"),
        ("M70.10", "Activités des sièges sociaux"),
    ],
    "Banques": [
        ("K64.19", "Autres intermédiations monétaires"),
        ("K64.11", "Banque centrale (si applicable)"),
    ],
    "Assurances": [
        ("K65.12", "Assurance (vie)"),
        ("K65.20", "Réassurance"),
        ("K66.22", "Activités des agents et courtiers d'assurances"),
    ],
    "Industrie lourde": [
        ("C24.10", "Sidérurgie (industrie lourde)"),
        ("C23.51", "Fabrication de ciment"),
        ("D35.11", "Production d'électricité"),
    ],
    "Mines et Hydrocarbures": [
        ("B06.10", "Extraction de pétrole brut"),
        ("B06.20", "Extraction de gaz naturel"),
        ("B09.10", "Activités de soutien à l'extraction d'hydrocarbures"),
    ],
}

# ─── Helpers ───
def reset_form():
    for k in list(st.session_state.keys()):
        del st.session_state[k]


def determine_regime_fiscal(legal_form, employees, naema_code=""):
    """
    Détermine le régime fiscal en fonction de la forme juridique,
    du nombre d'employés et optionnellement du code NAEMA
    """
    if legal_form == "Entreprise Individuelle":
        if employees <= 5:
            return "Régime Réel Simplifié d'Imposition (RSI)", "Adapté aux petites structures avec comptabilité simplifiée"
        else:
            return "Régime du Réel Normal", "Recommandé pour une structure en croissance"
    elif legal_form in ["SARL / SUARL", "SAS / SASU"]:
        if employees < 20:
            return "Régime du Réel Simplifié", "Obligations comptables allégées pour PME"
        else:
            return "Régime du Réel Normal", "Avec obligations comptables complètes"
    elif legal_form == "SA":
        return "Régime du Réel Normal", "Obligatoire pour les sociétés anonymes"
    elif legal_form == "GIE":
        return "Régime Transparent", "Les bénéfices sont imposés au niveau des membres"
    elif legal_form == "SCI":
        return "Régime de la Transparence Fiscale", "Imposition des associés sur leur quote-part"
    return "Régime du Réel Normal", "Régime standard"


# ─── Init ───
if "step" not in st.session_state:
    st.session_state["step"] = 0

step = st.session_state["step"]
steps_names = ["Questionnaire", "Confirmation", "Régime Fiscal"]

# ═══════════════════════════════════════════════════════════
# HEADER BANNER
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div class="dgid-banner">
    <div style="display:flex; align-items:center;">
        <span class="emblem">🏛️</span>
        <div>
            <h1>Portail d'Immatriculation Fiscale</h1>
            <div class="subtitle">Direction Générale des Impôts et des Domaines — Sénégal</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# STEP BAR
# ═══════════════════════════════════════════════════════════
bar_html = '<div class="step-bar">'
for i, name in enumerate(steps_names):
    if i < step:
        cls = "completed"
        icon = "✓"
    elif i == step:
        cls = "active"
        icon = str(i + 1)
    else:
        cls = "pending"
        icon = str(i + 1)
    bar_html += f'<div class="step-item {cls}"><span class="step-num">{icon}</span> {name}</div>'
bar_html += '</div>'
st.markdown(bar_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# ÉTAPE 0 : QUESTIONNAIRE
# ═══════════════════════════════════════════════════════════
if step == 0:
    st.markdown("#### 📋 Questionnaire d'orientation NAEMA")
    st.caption("Répondez aux questions pour déterminer votre catégorie d'activité")

    # Q1
    with st.expander("**① Forme juridique de l'entreprise**", expanded=True):
        legal_forms = list(LEGAL_FORM_TO_SECTORS.keys())
        legal_form = st.selectbox(
            "Sélectionnez la forme juridique",
            options=["— Sélectionner —"] + legal_forms,
            key="legal_form",
        )
        if legal_form != "— Sélectionner —":
            st.success(f"Forme juridique : **{legal_form}**")

    if legal_form == "— Sélectionner —":
        st.info("Veuillez choisir une forme juridique pour continuer.")
        st.stop()

    # Q2 - Navigation hiérarchique NAEMA
    with st.expander("**② Classification NAEMA de votre activité**", expanded=True):
        st.markdown("📂 **Navigation hiérarchique : Section → Division → Groupe**")

        # Étape 1 : Sélection de la Section
        section_options = [f"{code} — {label}" for code, label in SECTIONS.items()]
        section_choice = st.selectbox(
            "Sélectionnez une section d'activité",
            options=["— Sélectionner —"] + section_options + ["🔸 Autre (à préciser)"],
            key="naema_section",
        )

        if section_choice == "🔸 Autre (à préciser)":
            autre_section = st.text_input(
                "Précisez votre secteur d'activité",
                placeholder="Ex: Activité spécifique non listée...",
                key="autre_section"
            )
            if autre_section.strip():
                st.success(f"✅ Activité personnalisée : **{autre_section}**")
                # Sauvegarder directement comme code NAEMA
                st.session_state["final_naema"] = f"AUTRE — {autre_section}"
        elif section_choice != "— Sélectionner —":
            section_code = section_choice.split(" — ")[0]
            st.info(f"📍 Section sélectionnée : **{section_choice}**")

            # Étape 2 : Sélection de la Division
            divisions_dict = get_divisions_for_section(section_code)
            if divisions_dict:
                division_options = [f"{code} — {label}" for code, label in divisions_dict.items()]
                division_choice = st.selectbox(
                    "Sélectionnez une division",
                    options=["— Sélectionner —"] + division_options + ["🔸 Autre (à préciser)"],
                    key="naema_division",
                )

                if division_choice == "🔸 Autre (à préciser)":
                    autre_division = st.text_input(
                        "Précisez votre activité",
                        placeholder="Ex: Activité spécifique dans cette section...",
                        key="autre_division"
                    )
                    if autre_division.strip():
                        st.success(f"✅ Activité personnalisée : **{autre_division}**")
                        st.session_state["final_naema"] = f"{section_code}.AUTRE — {autre_division}"
                elif division_choice != "— Sélectionner —":
                    division_code = division_choice.split(" — ")[0]
                    st.info(f"📍 Division sélectionnée : **{division_choice}**")

                    # Étape 3 : Sélection du Groupe
                    groups_dict = get_groups_for_division(division_code)
                    if groups_dict:
                        group_options = [f"{code} — {label}" for code, label in groups_dict.items()]
                        group_choice = st.selectbox(
                            "Sélectionnez un groupe (code détaillé)",
                            options=["— Sélectionner —"] + group_options + ["🔸 Autre (à préciser)"],
                            key="naema_group",
                        )

                        if group_choice == "🔸 Autre (à préciser)":
                            autre_group = st.text_input(
                                "Précisez votre activité",
                                placeholder="Ex: Activité spécifique dans cette division...",
                                key="autre_group"
                            )
                            if autre_group.strip():
                                st.success(f"✅ Code NAEMA personnalisé : **{division_code}.AUTRE — {autre_group}**")
                                st.session_state["final_naema"] = f"{division_code}.AUTRE — {autre_group}"
                        elif group_choice != "— Sélectionner —":
                            st.success(f"✅ Code NAEMA sélectionné : **{group_choice}**")
                            st.session_state["final_naema"] = group_choice
                    else:
                        # Pas de groupes, utiliser la division directement
                        st.success(f"✅ Code NAEMA sélectionné : **{division_choice}**")
                        st.session_state["final_naema"] = division_choice

    # Vérifier si un code NAEMA final a été sélectionné
    naema_choice = st.session_state.get("final_naema", "")
    if not naema_choice:
        st.info("Veuillez sélectionner ou préciser votre catégorie d'activité NAEMA.")
        st.stop()

    # Q3 - Détails de l'activité
    with st.expander("**③ Détails de votre activité**", expanded=True):
        activity_desc = st.text_area(
            "Décrivez brièvement votre activité",
            placeholder="Ex : Vente de vêtements prêts-à-porter via boutique et réseaux sociaux…",
            key="activity_desc",
            height=100,
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
    can_continue = bool(activity_desc.strip()) if 'activity_desc' in dir() else False

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        if st.button("Passer à la confirmation →", type="primary", use_container_width=True, disabled=not can_continue):
            # Sauvegarder les données du formulaire dans des clés dédiées
            st.session_state["data_legal_form"] = st.session_state.get("legal_form", "")
            st.session_state["data_naema"] = st.session_state.get("final_naema", "")
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
        st.warning("Veuillez compléter la description de votre activité pour continuer.")


# ═══════════════════════════════════════════════════════════
# ÉTAPE 1 : CONFIRMATION
# ═══════════════════════════════════════════════════════════
elif step == 1:
    st.markdown("#### ✅ Confirmation de vos informations")
    st.caption("Vérifiez attentivement avant validation définitive")

    # Lire depuis les clés sauvegardées (stables, pas liées aux widgets)
    legal_form = st.session_state.get("data_legal_form", "")
    naema_choice = st.session_state.get("data_naema", "")
    activity_desc = st.session_state.get("data_activity_desc", "")
    employees = st.session_state.get("data_employees", 0)
    capital = st.session_state.get("data_capital", 0)
    phone = st.session_state.get("data_phone", "")
    email = st.session_state.get("data_email", "")

    st.markdown(f"""
    <div class="confirm-card">
        <div class="info-row">
            <div class="info-label">Forme juridique</div>
            <div class="info-value">{legal_form}</div>
        </div>
        <div class="info-row">
            <div class="info-label">Code NAEMA</div>
            <div class="info-value">{naema_choice}</div>
        </div>
        <div class="info-row">
            <div class="info-label">Description de l'activité</div>
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
            st.session_state["step"] = 2
            st.rerun()
    with col3:
        if st.button("Annuler", use_container_width=True):
            reset_form()
            st.rerun()

    if not can_validate:
        st.info("Veuillez cocher les deux attestations pour valider.")


# ═══════════════════════════════════════════════════════════
# ÉTAPE 2 : RÉSULTAT
# ═══════════════════════════════════════════════════════════
elif step == 2:
    st.balloons()

    legal_form = st.session_state.get("data_legal_form", "")
    naema_code = st.session_state.get("data_naema", "")
    employees = st.session_state.get("data_employees", 0)

    regime, description = determine_regime_fiscal(legal_form, employees, naema_code)

    st.markdown("""
    <div class="regime-header">
        <div class="regime-icon">🏛️</div>
        <div class="regime-label">Votre régime fiscal</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="regime-detail-card">
        <h3>📋 {regime}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="confirm-card">
        <div class="info-row">
            <div class="info-label">Forme juridique</div>
            <div class="info-value">{legal_form}</div>
        </div>
        <div class="info-row">
            <div class="info-label">Effectif</div>
            <div class="info-value">{employees} employé(s)</div>
        </div>
        <div class="info-row">
            <div class="info-label">Code NAEMA</div>
            <div class="info-value">{naema_code}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("""
    <div class="next-steps">
        <h4>Prochaines étapes</h4>
        <div class="ns-item">
            <div class="ns-num">1</div>
            <div class="ns-text">Vous recevrez un email de confirmation avec votre numéro d'immatriculation</div>
        </div>
        <div class="ns-item">
            <div class="ns-num">2</div>
            <div class="ns-text">Téléchargez et complétez les formulaires requis</div>
        </div>
        <div class="ns-item">
            <div class="ns-num">3</div>
            <div class="ns-text">Soumettez vos pièces justificatives</div>
        </div>
        <div class="ns-item">
            <div class="ns-num">4</div>
            <div class="ns-text">Recevez votre certificat d'immatriculation fiscale</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Télécharger le récapitulatif", use_container_width=True):
            st.info("Fonctionnalité à implémenter : génération PDF")
    with col2:
        if st.button("📧 Envoyer par email", use_container_width=True):
            st.success("Email envoyé avec succès ! (simulation)")
    with col3:
        if st.button("Nouvelle immatriculation", type="primary", use_container_width=True):
            reset_form()
            st.rerun()