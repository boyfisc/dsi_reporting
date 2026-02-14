import streamlit as st
import json
from pathlib import Path

st.set_page_config(
    page_title="DGID — Portail d'immatriculation fiscale",
    page_icon="🏛️",
    layout="centered",
)

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    json_path = Path(__file__).parent / "naema_data.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def get_groupes_activites(items):
    """Retourne la liste ordonnée et unique des Col C."""
    seen = []
    seen_set = set()
    for it in items:
        k = it["grp_act"]
        if k and k not in seen_set:
            seen.append(k)
            seen_set.add(k)
    return seen


@st.cache_data
def build_labels_for_group(items, grp_act_value):
    """Construit les labels de recherche uniquement pour un groupe donné."""
    labels = []
    mapping = {}
    for p in items:
        if p["grp_act"] != grp_act_value:
            continue
        lbl = f"{p['prod_lib']}  ·  {p['act_lib']}  ({p['prod_code']})"
        labels.append(lbl)
        mapping[lbl] = p
    return labels, mapping


ALL_ITEMS = load_data()
GROUPES = get_groupes_activites(ALL_ITEMS)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Source+Sans+3:wght@300;400;500;600;700&display=swap');
:root{
    --brown-900:#3E2723;--brown-800:#4E342E;--brown-700:#5D4037;
    --brown-600:#6D4C41;--brown-500:#795548;--brown-400:#8D6E63;
    --brown-300:#A1887F;--brown-200:#BCAAA4;--brown-100:#D7CCC8;--brown-50:#EFEBE9;
    --gold-600:#B8860B;--gold-500:#DAA520;--gold-400:#E6B422;
    --gold-300:#F0C850;--gold-200:#F5D77A;--gold-100:#FBF0D0;--gold-50:#FFFBF0;
    --white:#FFF;--off-white:#FAF8F5;--text-dark:#2C1810;--text-mid:#5D4037;--border:#E8DDD5;
}
.stApp{background:var(--off-white)!important}
.stApp>header{background:transparent!important}

/* Banner */
.dgid-banner{
    background:linear-gradient(135deg,var(--brown-900),var(--brown-700) 60%,var(--brown-600));
    padding:1.8rem 2rem 1.5rem;border-radius:0 0 20px 20px;
    margin:-1rem -1rem 1.5rem;position:relative;overflow:hidden;
}
.dgid-banner::after{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,var(--gold-500),var(--gold-300),var(--gold-500))}
.dgid-banner h1{color:var(--white)!important;font-family:'Playfair Display',serif!important;
    font-size:1.65rem!important;font-weight:700!important;margin:0 0 .25rem 0!important}
.dgid-banner .subtitle{color:var(--gold-300);font-family:'Source Sans 3',sans-serif;
    font-size:.9rem;letter-spacing:1.5px;text-transform:uppercase}

/* Step bar */
.step-bar{display:flex;gap:6px;margin:.5rem 0 1.5rem;padding:.75rem;
    background:var(--white);border-radius:14px;border:1px solid var(--border);
    box-shadow:0 2px 8px rgba(62,39,35,.06)}
.step-item{flex:1;text-align:center;padding:.65rem .5rem;border-radius:10px;
    font-family:'Source Sans 3',sans-serif;font-size:.82rem;font-weight:600}
.step-item.active{background:linear-gradient(135deg,var(--gold-500),var(--gold-400));
    color:var(--brown-900);box-shadow:0 4px 14px rgba(218,165,32,.35)}
.step-item.completed{background:var(--brown-800);color:var(--gold-300)}
.step-item.pending{background:var(--brown-50);color:var(--brown-300)}
.step-num{display:inline-block;width:22px;height:22px;line-height:22px;border-radius:50%;
    font-size:.72rem;font-weight:700;margin-right:5px;vertical-align:middle}
.step-item.active .step-num{background:var(--brown-900);color:var(--gold-300)}
.step-item.completed .step-num{background:var(--gold-500);color:var(--brown-900)}
.step-item.pending .step-num{background:var(--brown-100);color:var(--brown-300)}

/* Cards */
.confirm-card{background:var(--white);padding:1.6rem 1.8rem;border-radius:14px;
    border:1px solid var(--border);border-left:5px solid var(--gold-500);
    margin:.8rem 0;box-shadow:0 2px 10px rgba(62,39,35,.05)}
.info-row{display:flex;align-items:baseline;padding:.7rem 0;border-bottom:1px solid var(--brown-50)}
.info-row:last-child{border-bottom:none}
.info-label{font-family:'Source Sans 3',sans-serif;font-weight:700;color:var(--brown-700);
    width:200px;flex-shrink:0;font-size:.9rem}
.info-value{font-family:'Source Sans 3',sans-serif;color:var(--text-dark);font-size:.92rem;flex:1}

.act-card{background:var(--gold-50);border:1px solid var(--gold-200);border-radius:10px;
    padding:.75rem 1rem;margin:.4rem 0;font-family:'Source Sans 3',sans-serif}
.act-card .act-role{font-size:.7rem;font-weight:700;text-transform:uppercase;
    letter-spacing:1px;color:var(--gold-600);margin-bottom:2px}
.act-card .act-name{font-weight:600;color:var(--brown-900);font-size:.92rem}
.act-card .act-detail{color:var(--brown-400);font-size:.8rem;margin-top:2px}
.act-card .act-auto{display:flex;flex-wrap:wrap;gap:.4rem 1.2rem;margin-top:6px;padding-top:6px;
    border-top:1px dashed var(--gold-200);font-size:.78rem}
.act-card .act-auto span{color:var(--brown-300)}
.act-card .act-auto strong{color:var(--brown-700)}

.recap-select{
    background:linear-gradient(135deg,#FFFBF0,#FFF8E7);
    border:2px solid var(--gold-400);border-radius:14px;
    padding:1.2rem 1.4rem;margin:.8rem 0;
    font-family:'Source Sans 3',sans-serif;
    box-shadow:0 4px 16px rgba(218,165,32,.12);
}
.recap-select .rs-header{display:flex;align-items:center;gap:.5rem;margin-bottom:.8rem}
.recap-select .rs-icon{font-size:1.5rem}
.recap-select .rs-title{font-weight:700;color:var(--brown-900);font-size:1.05rem}
.recap-select .rs-row{display:flex;align-items:baseline;padding:.45rem 0;
    border-bottom:1px solid rgba(218,165,32,.2)}
.recap-select .rs-row:last-child{border-bottom:none}
.recap-select .rs-label{font-weight:600;color:var(--brown-600);width:170px;flex-shrink:0;font-size:.85rem}
.recap-select .rs-val{color:var(--brown-900);font-size:.88rem;font-weight:500}

/* Next steps */
.next-steps{background:var(--white);border:1px solid var(--border);border-radius:14px;padding:1.4rem 1.6rem}
.next-steps h4{font-family:'Playfair Display',serif!important;color:var(--brown-800)!important;
    font-size:1rem!important;margin:0 0 1rem 0!important}
.ns-item{display:flex;align-items:flex-start;gap:.8rem;padding:.6rem 0}
.ns-num{flex-shrink:0;width:28px;height:28px;line-height:28px;text-align:center;border-radius:50%;
    background:var(--gold-100);color:var(--brown-800);font-family:'Source Sans 3',sans-serif;
    font-weight:700;font-size:.8rem}
.ns-text{font-family:'Source Sans 3',sans-serif;color:var(--text-mid);font-size:.9rem;line-height:1.45}

/* Streamlit overrides */
.stSelectbox label,.stTextInput label,.stTextArea label,.stNumberInput label{
    font-family:'Source Sans 3',sans-serif!important;color:var(--brown-700)!important;
    font-weight:600!important;font-size:.88rem!important}
div[data-testid="stExpander"]{background:var(--white);border:1px solid var(--border)!important;
    border-radius:12px!important;margin-bottom:.6rem;box-shadow:0 1px 4px rgba(62,39,35,.04);overflow:hidden}
div[data-testid="stExpander"]>details>summary{font-family:'Source Sans 3',sans-serif!important;
    color:var(--white)!important;font-weight:700!important;
    background:linear-gradient(135deg,var(--brown-800),var(--brown-700))!important;
    padding:.8rem 1.2rem!important}
div[data-testid="stExpander"]>details>summary:hover{
    background:linear-gradient(135deg,var(--brown-700),var(--brown-600))!important}
div[data-testid="stExpander"]>details>summary svg{color:var(--gold-300)!important}
.stButton>button[kind="primary"]{
    background:linear-gradient(135deg,var(--gold-500),var(--gold-400))!important;
    color:var(--brown-900)!important;border:none!important;
    font-family:'Source Sans 3',sans-serif!important;font-weight:700!important;
    font-size:.92rem!important;border-radius:10px!important;
    box-shadow:0 4px 14px rgba(218,165,32,.3)!important}
.stButton>button[kind="primary"]:hover{box-shadow:0 6px 20px rgba(218,165,32,.45)!important}
.stButton>button:not([kind="primary"]){background:var(--white)!important;color:var(--brown-700)!important;
    border:1.5px solid var(--brown-200)!important;font-family:'Source Sans 3',sans-serif!important;
    font-weight:600!important;border-radius:10px!important}
.stButton>button:not([kind="primary"]):hover{border-color:var(--gold-500)!important;
    background:var(--gold-50)!important}
.stCheckbox label span,.stCheckbox label span p{font-family:'Source Sans 3',sans-serif!important;
    color:var(--brown-800)!important;font-weight:600!important;font-size:.92rem!important}
hr{border-color:var(--border)!important}
h1,h2,h3{font-family:'Playfair Display',serif!important;color:var(--brown-800)!important}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def reset_form():
    for k in list(st.session_state.keys()):
        del st.session_state[k]


def fmt_grp(raw):
    """'1_COMMERCE (ACHAT& REVENTE)' → '1 — COMMERCE (ACHAT& REVENTE)'"""
    if not raw:
        return ""
    parts = raw.split("_", 1)
    return f"{parts[0]} — {parts[1]}" if len(parts) == 2 else raw


def render_activity_card(act, role_label):
    return f"""
    <div class="act-card">
        <div class="act-role">{role_label}</div>
        <div class="act-name">{act['prod_lib']}</div>
        <div class="act-detail">Code produit : {act['prod_code']}  ·  Activité : {act['act_lib']}</div>
        <div class="act-auto">
            <div><span>Groupe d'activités :</span> <strong>{fmt_grp(act['grp_act'])}</strong></div>
        </div>
        <div class="act-auto" style="border-top:none;padding-top:0;margin-top:2px;">
            <div><span>Section :</span> <strong>{act['sec_code']} — {act['sec_lib']}</strong></div>
            <div><span>Division :</span> <strong>{act['div_code']} — {act['div_lib']}</strong></div>
        </div>
        <div class="act-auto" style="border-top:none;padding-top:0;margin-top:2px;">
            <div><span>Groupe NAEMA :</span> <strong>{act['grp_code']} — {act['grp_lib']}</strong></div>
        </div>
    </div>
    """


def render_selection_recap(act):
    return f"""
    <div class="recap-select">
        <div class="rs-header">
            <div class="rs-icon">📌</div>
            <div class="rs-title">{act['prod_lib']}</div>
        </div>
        <div class="rs-row">
            <div class="rs-label">Code produit</div>
            <div class="rs-val">{act['prod_code']}</div>
        </div>
        <div class="rs-row">
            <div class="rs-label">Activité</div>
            <div class="rs-val">{act['act_code']} — {act['act_lib']}</div>
        </div>
        <div class="rs-row">
            <div class="rs-label">Groupe d'activités</div>
            <div class="rs-val">{fmt_grp(act['grp_act'])}</div>
        </div>
        <div class="rs-row">
            <div class="rs-label">Section</div>
            <div class="rs-val">{act['sec_code']} — {act['sec_lib']}</div>
        </div>
        <div class="rs-row">
            <div class="rs-label">Division</div>
            <div class="rs-val">{act['div_code']} — {act['div_lib']}</div>
        </div>
        <div class="rs-row">
            <div class="rs-label">Groupe NAEMA</div>
            <div class="rs-val">{act['grp_code']} — {act['grp_lib']}</div>
        </div>
    </div>
    """


def clear_picker_keys():
    for k in list(st.session_state.keys()):
        if str(k).startswith("sel_act_") or str(k).startswith("grp_act_"):
            del st.session_state[k]


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state["step"] = 0
if "activities" not in st.session_state:
    st.session_state["activities"] = []
if "search_mode" not in st.session_state:
    st.session_state["search_mode"] = "pick"

step = st.session_state["step"]
steps_names = ["Questionnaire", "Récapitulatif"]

# ═════════════════════════════════════════════
# HEADER + STEP BAR
# ═════════════════════════════════════════════
st.markdown("""
<div class="dgid-banner">
    <div style="display:flex;align-items:center;">
        <span style="font-size:2rem;margin-right:.8rem;">🏛️</span>
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


# ═════════════════════════════════════════════
# ÉTAPE 0 : QUESTIONNAIRE
# ═════════════════════════════════════════════
if step == 0:
    st.markdown("#### 📋 Questionnaire d'immatriculation")
    st.caption("NAEMA Rév. 1 — Nomenclature d'Activités des États Membres d'AFRISTAT")

    activities = st.session_state["activities"]

    # ── Activités déjà validées ──
    if activities:
        with st.expander(f"**✅ Activités validées ({len(activities)})**", expanded=True):
            for idx, act in enumerate(activities):
                role = "Activité principale" if idx == 0 else f"Activité secondaire {idx}"
                col_i, col_d = st.columns([6, 1])
                with col_i:
                    st.markdown(render_activity_card(act, role), unsafe_allow_html=True)
                with col_d:
                    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_{act['prod_code']}_{idx}", help="Supprimer"):
                        st.session_state["activities"] = [a for i, a in enumerate(activities) if i != idx]
                        if not st.session_state["activities"]:
                            st.session_state["search_mode"] = "pick"
                        st.rerun()

    # ──────────────────────────────────────────
    # PICK MODE — 2 niveaux de filtrage
    # ──────────────────────────────────────────
    if st.session_state["search_mode"] == "pick":
        label_num = len(activities) + 1
        if not activities:
            title = "**① Quelle est votre activité principale ?**"
        else:
            title = f"**➕ Ajouter une activité secondaire (n°{label_num})**"

        with st.expander(title, expanded=True):

            # ━━━ FILTRE 1 : Groupe d'activités (Col C) ━━━
            st.markdown("##### <span style='color:#4E2A0A'>🏷️ Étape 1 — Groupe d'activités</span>", unsafe_allow_html=True)
            st.caption("Sélectionnez le grand domaine qui correspond à votre activité.")

            grp_display = [fmt_grp(g) for g in GROUPES]
            grp_options = ["— Choisissez votre groupe d'activités —"] + grp_display

            grp_choice = st.selectbox(
                "Groupe d'activités",
                grp_options,
                key=f"grp_act_{label_num}",
                label_visibility="collapsed",
            )

            # Retrouver la valeur brute
            selected_grp_raw = None
            if grp_choice != grp_options[0]:
                idx_sel = grp_display.index(grp_choice)
                selected_grp_raw = GROUPES[idx_sel]

            # ━━━ FILTRE 2 : Recherche live (multiselect) dans le sous-arbre ━━━
            if selected_grp_raw:
                group_labels, group_map = build_labels_for_group(ALL_ITEMS, selected_grp_raw)

                st.divider()
                st.markdown("##### <span style='color:#4E2A0A'>🔍 Étape 2 — Recherchez votre activité / produit</span>", unsafe_allow_html=True)
                st.caption(
                    f"{len(group_labels)} produits dans **{grp_choice}** — "
                    "tapez directement pour filtrer en temps réel."
                )

                pick_key = f"sel_act_{label_num}"
                choice = st.multiselect(
                    "Recherche live",
                    group_labels,
                    default=None,
                    max_selections=1,
                    key=pick_key,
                    placeholder="Tapez ici pour filtrer (ex : banque, transport, vente…)",
                    label_visibility="collapsed",
                )

                if choice:
                    sel = group_map[choice[0]]
                    st.markdown(render_selection_recap(sel), unsafe_allow_html=True)

                    existing_codes = [a["prod_code"] for a in st.session_state["activities"]]
                    if sel["prod_code"] in existing_codes:
                        st.info("✓ Cette activité est déjà dans votre liste.")
                    else:
                        if st.button(
                            f"✅  Valider « {sel['prod_lib']} »",
                            type="primary",
                            use_container_width=True,
                        ):
                            st.session_state["activities"].append(sel)
                            st.session_state["search_mode"] = "validated"
                            st.rerun()

    # ──────────────────────────────────────────
    # VALIDATED MODE
    # ──────────────────────────────────────────
    elif st.session_state["search_mode"] == "validated":
        last = st.session_state["activities"][-1] if st.session_state["activities"] else None
        if last:
            st.success(f"✅ **{last['prod_lib']}** ajoutée avec succès !")
            st.markdown(render_selection_recap(last), unsafe_allow_html=True)

            col_add, col_next = st.columns(2)
            with col_add:
                if st.button("➕ Ajouter activité secondaire", use_container_width=True):
                    st.session_state["search_mode"] = "pick"
                    clear_picker_keys()
                    st.rerun()
            with col_next:
                if st.button("Continuer →", type="primary", use_container_width=True):
                    st.session_state["search_mode"] = "details"
                    st.rerun()

    # ──────────────────────────────────────────
    # DETAILS MODE
    # ──────────────────────────────────────────
    elif st.session_state["search_mode"] == "details":
        with st.expander("**② Détails complémentaires**", expanded=True):
            st.text_area(
                "Décrivez brièvement votre activité",
                placeholder="Ex : Vente de vêtements prêts-à-porter via boutique et réseaux sociaux…",
                key="activity_desc",
                height=100,
            )
            col1, col2 = st.columns(2)
            with col1:
                st.number_input("Nombre d'employés", min_value=0, max_value=100000, value=0, step=1, key="employees")
            with col2:
                st.number_input("Capital social (FCFA)", min_value=0, value=0, step=100000, key="capital")

            st.markdown("**Informations de contact**")
            col3, col4 = st.columns(2)
            with col3:
                st.text_input("Téléphone", placeholder="+221 …", key="phone")
            with col4:
                st.text_input("Email", placeholder="contact@entreprise.sn", key="email")

        st.divider()
        can_continue = bool(st.session_state.get("activity_desc", "").strip())

        col_back, col_add, col_next = st.columns([1, 1, 2])
        with col_back:
            if st.button("← Activités", use_container_width=True):
                st.session_state["search_mode"] = "validated"
                st.rerun()
        with col_add:
            if st.button("➕ Ajouter activité secondaire", use_container_width=True):
                st.session_state["search_mode"] = "pick"
                clear_picker_keys()
                st.rerun()
        with col_next:
            if st.button("Passer au récapitulatif →", type="primary", use_container_width=True, disabled=not can_continue):
                st.session_state["data_activities"] = list(st.session_state["activities"])
                st.session_state["data_activity_desc"] = st.session_state.get("activity_desc", "")
                st.session_state["data_employees"] = st.session_state.get("employees", 0)
                st.session_state["data_capital"] = st.session_state.get("capital", 0)
                st.session_state["data_phone"] = st.session_state.get("phone", "")
                st.session_state["data_email"] = st.session_state.get("email", "")
                st.session_state["step"] = 1
                st.rerun()

        if not can_continue:
            st.warning("Veuillez compléter la description de votre activité.")

    # Bottom reset
    st.divider()
    if st.button("🔄 Réinitialiser tout", use_container_width=False):
        reset_form()
        st.rerun()


# ═════════════════════════════════════════════
# ÉTAPE 1 : RÉCAPITULATIF FINAL
# ═════════════════════════════════════════════
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

    # En-tête recap
    st.markdown(f"""
    <div class="confirm-card">
        <div class="info-row">
            <div class="info-label">Groupe d'activités</div>
            <div class="info-value"><strong>{fmt_grp(principal.get('grp_act',''))}</strong></div>
        </div>
        <div class="info-row">
            <div class="info-label">Section</div>
            <div class="info-value">{principal.get('sec_code','')} — {principal.get('sec_lib','')}</div>
        </div>
        <div class="info-row">
            <div class="info-label">Division</div>
            <div class="info-value">{principal.get('div_code','')} — {principal.get('div_lib','')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Cartes activités
    for idx, act in enumerate(activities):
        role = "Activité principale" if idx == 0 else f"Activité secondaire {idx}"
        st.markdown(render_activity_card(act, role), unsafe_allow_html=True)

    # Détails
    st.markdown(f"""
    <div class="confirm-card">
        <div class="info-row"><div class="info-label">Description</div>
            <div class="info-value">{activity_desc}</div></div>
        <div class="info-row"><div class="info-label">Nombre d'employés</div>
            <div class="info-value">{employees}</div></div>
        <div class="info-row"><div class="info-label">Capital social</div>
            <div class="info-value">{capital:,.0f} FCFA</div></div>
        <div class="info-row"><div class="info-label">Téléphone</div>
            <div class="info-value">{phone if phone else 'Non renseigné'}</div></div>
        <div class="info-row"><div class="info-label">Email</div>
            <div class="info-value">{email if email else 'Non renseigné'}</div></div>
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
            st.session_state["search_mode"] = "details"
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
            if st.button("Nouvelle immatriculation", type="primary", use_container_width=True):
                reset_form()
                st.rerun()
    with col3:
        if st.button("Annuler", use_container_width=True):
            reset_form()
            st.rerun()

    if not (confirm1 and confirm2):
        st.info("Veuillez cocher les deux attestations pour valider.")
