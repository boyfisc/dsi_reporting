import streamlit as st

st.set_page_config(page_title="Portail d'immatriculation fiscale (Mockup)", page_icon="🧾", layout="centered")

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
    for k in [
        "started", "legal_form", "sector", "naema", "activity_desc",
        "employees", "phone", "email"
    ]:
        if k in st.session_state:
            del st.session_state[k]


# -----------------------------
# Page
# -----------------------------
st.title("🧾 Portail d’immatriculation aux impôts — Mockup (début)")

st.markdown(
    """
Ce prototype illustre :
- un bouton **S’immatriculer**
- un **questionnaire en 4 questions**
- une orientation des choix via la **forme juridique**
- une **suggestion NAEMA** (exemples) pour qualifier l’activité.
"""
)

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("✅ S'immatriculer", use_container_width=True):
        st.session_state["started"] = True
with col2:
    if st.button("🔄 Réinitialiser", use_container_width=True):
        reset_form()
        st.rerun()

if not st.session_state.get("started"):
    st.info("Cliquez sur **S’immatriculer** pour démarrer le questionnaire.")
    st.stop()

st.divider()
st.subheader("Questionnaire d’orientation (NAEMA)")

# -----------------------------
# Q1 - Forme juridique (oriente le reste)
# -----------------------------
legal_forms = list(LEGAL_FORM_TO_SECTORS.keys())
legal_form = st.selectbox(
    "1) Quelle est la forme juridique de l'entreprise ?",
    options=["— Sélectionner —"] + legal_forms,
    key="legal_form",
)

if legal_form == "— Sélectionner —":
    st.warning("Veuillez choisir une forme juridique pour continuer.")
    st.stop()

allowed_sectors = LEGAL_FORM_TO_SECTORS.get(legal_form, [])

# -----------------------------
# Q2 - Secteur principal (filtré par Q1)
# -----------------------------
sector = st.selectbox(
    "2) Quel est le secteur d’activité principal ?",
    options=["— Sélectionner —"] + allowed_sectors,
    key="sector",
)

if sector == "— Sélectionner —":
    st.warning("Veuillez choisir un secteur d’activité principal.")
    st.stop()

# -----------------------------
# Q3 - Choix NAEMA (exemples) dépendant de Q2
# -----------------------------
naema_options = SECTOR_TO_NAEMA.get(sector, [])
if not naema_options:
    st.error(
        "Aucune option NAEMA (mock) n’est configurée pour ce secteur. "
        "Ajoutez des codes dans SECTOR_TO_NAEMA."
    )
    st.stop()

naema_label_list = [f"{code} — {label}" for (code, label) in naema_options]
naema_choice = st.selectbox(
    "3) Sélectionnez la catégorie NAEMA la plus proche (exemples) :",
    options=["— Sélectionner —"] + naema_label_list,
    key="naema",
)

if naema_choice == "— Sélectionner —":
    st.warning("Veuillez sélectionner une catégorie NAEMA.")
    st.stop()

# -----------------------------
# Q4 - Détails minimaux (texte + effectif)
# -----------------------------
activity_desc = st.text_area(
    "4) Décrivez brièvement votre activité (produits/services, clientèle, etc.)",
    placeholder="Ex: Vente de vêtements prêts-à-porter via boutique et réseaux sociaux...",
    key="activity_desc",
)

employees = st.number_input(
    "Nombre d’employés (estimation)",
    min_value=0,
    max_value=100000,
    value=0,
    step=1,
    key="employees",
)

# Optionnel (hors des 4 questions principales) : contact
with st.expander("Informations de contact (optionnel)"):
    st.text_input("Téléphone", placeholder="+221 ...", key="phone")
    st.text_input("Email", placeholder="contact@entreprise.sn", key="email")

# -----------------------------
# Résumé + "soumission" mock
# -----------------------------
st.divider()
st.subheader("Résumé (mock)")

code_selected = naema_choice.split("—")[0].strip()

st.write("**Forme juridique :**", legal_form)
st.write("**Secteur principal :**", sector)
st.write("**NAEMA suggéré :**", f"{code_selected}")
st.write("**Description :**", activity_desc if activity_desc.strip() else "—")
st.write("**Employés :**", employees)

# Démo d'un "enregistrement" sans base de données
can_submit = bool(activity_desc.strip())

if st.button("📨 Valider et continuer (démo)", type="primary", use_container_width=True, disabled=not can_submit):
    # Ici on simule une sauvegarde (ex: DB, API, etc.)
    st.success("Données enregistrées (démo). Étape suivante : création du compte + pièces justificatives.")
    st.code(
        {
            "forme_juridique": legal_form,
            "secteur": sector,
            "naema_code": code_selected,
            "description": activity_desc.strip(),
            "employees": employees,
            "phone": st.session_state.get("phone", ""),
            "email": st.session_state.get("email", ""),
        },
        language="python",
    )

if not can_submit:
    st.info("Ajoutez une description d’activité pour activer la validation.")
