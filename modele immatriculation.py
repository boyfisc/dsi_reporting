import streamlit as st

st.set_page_config(page_title="Portail d'immatriculation fiscale", page_icon="🧾", layout="centered")

# CSS pour rendre l'interface plus interactive
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
        padding: 0 1rem;
    }
    .step {
        flex: 1;
        text-align: center;
        padding: 0.8rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .step.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transform: scale(1.05);
    }
    .step.completed {
        background: #4caf50;
        color: white;
    }
    .step.pending {
        background: #f0f0f0;
        color: #999;
    }
    .confirm-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .regime-box {
        background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 2rem 0;
        box-shadow: 0 8px 30px rgba(76,175,80,0.3);
    }
    .info-row {
        display: flex;
        padding: 0.8rem 0;
        border-bottom: 1px solid #e0e0e0;
    }
    .info-label {
        font-weight: 700;
        color: #667eea;
        width: 200px;
    }
    .info-value {
        color: #333;
        flex: 1;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Données (mock) - à remplacer par NAEMA complète
# -----------------------------
LEGAL_FORM_TO_SECTORS = {
    "Entreprise Individuelle": [
        "Commerce de détail",
        "Artisanat",
        "Services de proximité",
    ],
    "GIE": [
        "Pêche",
        "Agriculture",
        "Groupements de promotion féminine",
    ],
    "SARL / SUARL": [
        "PME",
        "Import-Export",
        "Services aux entreprises",
        "Transport",
    ],
    "SCI": [
        "Gestion de patrimoine",
        "Location immobilière (résidentielle/bureaux)",
    ],
    "SAS / SASU": [
        "Startups Tech",
        "Conseil",
        "Projets à investissements multiples",
    ],
    "SA": [
        "Banques",
        "Assurances",
        "Industrie lourde",
        "Mines et Hydrocarbures",
    ],
}

# Mini "catalogue NAEMA" (exemples fictifs/incomplets pour démo)
# Structure: secteur -> liste de (code, libellé)
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

# -----------------------------
# UI helpers
# -----------------------------
def reset_form():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

def determine_regime_fiscal(legal_form, employees, sector):
    """Détermine le régime fiscal suggéré basé sur les informations"""
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


# -----------------------------
# Page
# -----------------------------
# Initialiser l'étape si non définie
if "step" not in st.session_state:
    st.session_state["step"] = 0

# Indicateur de progression
step = st.session_state["step"]
steps_names = ["📋 Questionnaire", "✅ Confirmation", "🎯 Régime Fiscal"]

st.title("🧾 Portail d'immatriculation fiscale")

# Afficher la barre de progression
progress_html = '<div class="step-indicator">'
for i, name in enumerate(steps_names):
    if i < step:
        cls = "completed"
    elif i == step:
        cls = "active"
    else:
        cls = "pending"
    progress_html += f'<div class="step {cls}">{name}</div>'
progress_html += '</div>'
st.markdown(progress_html, unsafe_allow_html=True)

st.divider()

# ═══════════════════════════════════════════════════════════
# ÉTAPE 0 : QUESTIONNAIRE
# ═══════════════════════════════════════════════════════════
if step == 0:
    st.subheader("📋 Questionnaire d'orientation NAEMA")
    st.markdown("*Répondez aux questions suivantes pour déterminer votre catégorie d'activité*")

    # -----------------------------
    # Q1 - Forme juridique
    # -----------------------------
    with st.expander("**1️⃣ Forme juridique de l'entreprise**", expanded=True):
        legal_forms = list(LEGAL_FORM_TO_SECTORS.keys())
        legal_form = st.selectbox(
            "Sélectionnez la forme juridique",
            options=["— Sélectionner —"] + legal_forms,
            key="legal_form",
        )
        if legal_form != "— Sélectionner —":
            st.success(f"✓ Forme juridique sélectionnée : **{legal_form}**")

    if legal_form == "— Sélectionner —":
        st.info("👆 Veuillez choisir une forme juridique pour continuer.")
        st.stop()

    allowed_sectors = LEGAL_FORM_TO_SECTORS.get(legal_form, [])

    # -----------------------------
    # Q2 - Secteur principal
    # -----------------------------
    with st.expander("**2️⃣ Secteur d'activité principal**", expanded=True):
        sector = st.selectbox(
            "Sélectionnez votre secteur d'activité",
            options=["— Sélectionner —"] + allowed_sectors,
            key="sector",
        )
        if sector != "— Sélectionner —":
            st.success(f"✓ Secteur sélectionné : **{sector}**")

    if sector == "— Sélectionner —":
        st.info("👆 Veuillez choisir un secteur d'activité.")
        st.stop()

    # -----------------------------
    # Q3 - Choix NAEMA
    # -----------------------------
    naema_options = SECTOR_TO_NAEMA.get(sector, [])
    if not naema_options:
        st.error("Aucune option NAEMA n'est configurée pour ce secteur.")
        st.stop()

    with st.expander("**3️⃣ Catégorie NAEMA**", expanded=True):
        naema_label_list = [f"{code} — {label}" for (code, label) in naema_options]
        naema_choice = st.selectbox(
            "Sélectionnez la catégorie NAEMA la plus proche",
            options=["— Sélectionner —"] + naema_label_list,
            key="naema",
        )
        if naema_choice != "— Sélectionner —":
            st.success(f"✓ NAEMA sélectionné : **{naema_choice}**")

    if naema_choice == "— Sélectionner —":
        st.info("👆 Veuillez sélectionner une catégorie NAEMA.")
        st.stop()

    # -----------------------------
    # Q4 - Détails de l'activité
    # -----------------------------
    with st.expander("**4️⃣ Détails de votre activité**", expanded=True):
        activity_desc = st.text_area(
            "Décrivez brièvement votre activité",
            placeholder="Ex: Vente de vêtements prêts-à-porter via boutique et réseaux sociaux...",
            key="activity_desc",
            height=100,
        )

        col1, col2 = st.columns(2)
        with col1:
            employees = st.number_input(
                "Nombre d'employés",
                min_value=0,
                max_value=100000,
                value=0,
                step=1,
                key="employees",
            )
        with col2:
            capital = st.number_input(
                "Capital social (FCFA)",
                min_value=0,
                value=0,
                step=100000,
                key="capital",
            )

        st.markdown("**Informations de contact**")
        col3, col4 = st.columns(2)
        with col3:
            st.text_input("Téléphone", placeholder="+221 ...", key="phone")
        with col4:
            st.text_input("Email", placeholder="contact@entreprise.sn", key="email")

        if activity_desc.strip():
            st.success("✓ Description complétée")

    # Bouton pour passer à la confirmation
    st.divider()
    can_continue = bool(activity_desc.strip())

    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        if st.button("➡️ Passer à la confirmation", type="primary", use_container_width=True, disabled=not can_continue):
            st.session_state["step"] = 1
            st.rerun()
    with col_btn2:
        if st.button("🔄 Réinitialiser", use_container_width=True):
            reset_form()
            st.rerun()

    if not can_continue:
        st.warning("⚠️ Veuillez compléter la description de votre activité pour continuer.")

# ═══════════════════════════════════════════════════════════
# ÉTAPE 1 : CONFIRMATION DES INFORMATIONS
# ═══════════════════════════════════════════════════════════
elif step == 1:
    st.subheader("✅ Confirmation de vos informations")
    st.markdown("*Veuillez vérifier attentivement les informations saisies avant validation définitive*")

    # Récupérer les données
    legal_form = st.session_state.get("legal_form", "")
    sector = st.session_state.get("sector", "")
    naema_choice = st.session_state.get("naema", "")
    activity_desc = st.session_state.get("activity_desc", "")
    employees = st.session_state.get("employees", 0)
    capital = st.session_state.get("capital", 0)
    phone = st.session_state.get("phone", "")
    email = st.session_state.get("email", "")

    code_selected = naema_choice.split("—")[0].strip() if "—" in naema_choice else naema_choice

    # Affichage en carte
    st.markdown(f"""
    <div class="confirm-card">
        <div class="info-row">
            <div class="info-label">🏢 Forme juridique</div>
            <div class="info-value">{legal_form}</div>
        </div>
        <div class="info-row">
            <div class="info-label">🏭 Secteur d'activité</div>
            <div class="info-value">{sector}</div>
        </div>
        <div class="info-row">
            <div class="info-label">📊 Code NAEMA</div>
            <div class="info-value">{naema_choice}</div>
        </div>
        <div class="info-row">
            <div class="info-label">📝 Description</div>
            <div class="info-value">{activity_desc}</div>
        </div>
        <div class="info-row">
            <div class="info-label">👥 Nombre d'employés</div>
            <div class="info-value">{employees}</div>
        </div>
        <div class="info-row">
            <div class="info-label">💰 Capital social</div>
            <div class="info-value">{capital:,.0f} FCFA</div>
        </div>
        <div class="info-row">
            <div class="info-label">📞 Téléphone</div>
            <div class="info-value">{phone if phone else "Non renseigné"}</div>
        </div>
        <div class="info-row">
            <div class="info-label">📧 Email</div>
            <div class="info-value">{email if email else "Non renseigné"}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Cases à cocher de confirmation
    st.markdown("### 📋 Attestations")
    confirm1 = st.checkbox("✓ Je certifie l'exactitude des informations fournies", key="confirm1")
    confirm2 = st.checkbox("✓ J'accepte les conditions générales d'utilisation", key="confirm2")

    st.divider()

    # Boutons de navigation
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Retour", use_container_width=True):
            st.session_state["step"] = 0
            st.rerun()

    with col2:
        can_validate = confirm1 and confirm2
        if st.button("✅ CONFIRMER DÉFINITIVEMENT", type="primary", use_container_width=True, disabled=not can_validate):
            # Sauvegarder dans session_state
            st.session_state["validated"] = True
            st.session_state["step"] = 2
            st.rerun()

    with col3:
        if st.button("🔄 Annuler", use_container_width=True):
            reset_form()
            st.rerun()

    if not can_validate:
        st.info("ℹ️ Veuillez cocher les deux cases pour valider définitivement votre immatriculation.")

# ═══════════════════════════════════════════════════════════
# ÉTAPE 2 : AFFICHAGE DU RÉGIME FISCAL
# ═══════════════════════════════════════════════════════════
elif step == 2:
    st.balloons()

    st.subheader("🎉 Immatriculation réussie !")
    st.markdown("*Votre dossier a été enregistré avec succès*")

    # Récupérer les données
    legal_form = st.session_state.get("legal_form", "")
    sector = st.session_state.get("sector", "")
    employees = st.session_state.get("employees", 0)

    # Déterminer le régime fiscal
    regime, description = determine_regime_fiscal(legal_form, employees, sector)

    # Afficher le régime fiscal
    st.markdown(f"""
    <div class="regime-box">
        🎯 VOTRE RÉGIME FISCAL
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="confirm-card" style="border-left-color: #4caf50;">
        <h3 style="color: #4caf50; margin-top: 0;">📋 {regime}</h3>
        <p style="font-size: 1.1rem; color: #555; margin-bottom: 1.5rem;">{description}</p>

        <div class="info-row">
            <div class="info-label">🏢 Forme juridique</div>
            <div class="info-value">{legal_form}</div>
        </div>
        <div class="info-row">
            <div class="info-label">👥 Effectif</div>
            <div class="info-value">{employees} employé(s)</div>
        </div>
        <div class="info-row">
            <div class="info-label">🏭 Secteur</div>
            <div class="info-value">{sector}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Prochaines étapes
    st.markdown("### 📌 Prochaines étapes")
    st.info("""
    **1.** Vous recevrez un email de confirmation avec votre numéro d'immatriculation
    **2.** Téléchargez et complétez les formulaires requis
    **3.** Soumettez vos pièces justificatives
    **4.** Recevez votre certificat d'immatriculation fiscale
    """)

    st.divider()

    # Boutons finaux
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("📥 Télécharger le récapitulatif", use_container_width=True):
            st.info("Fonctionnalité à implémenter : génération PDF")

    with col2:
        if st.button("📧 Envoyer par email", use_container_width=True):
            st.success("Email envoyé avec succès ! (simulation)")

    with col3:
        if st.button("🏠 Nouvelle immatriculation", use_container_width=True):
            reset_form()
            st.rerun()
