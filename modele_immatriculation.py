import streamlit as st
import streamlit.components.v1 as components
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
    with open(Path(__file__).parent / "naema_catalogue.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    items = []
    for section in data["sections"]:
        for division in section.get("divisions", []):
            for groupe in division.get("groupes", []):
                for activite in groupe.get("activites", []):
                    for produit in activite.get("produits", []):
                        items.append({
                            "sec_code": section["code"],
                            "sec_lib": section["libelle"],
                            "grp_lib": groupe["libelle"],
                            "act_lib": activite["libelle"],
                            "prod_code": produit["code"],
                            "prod_lib": produit["libelle"],
                        })
    return items

ALL_PRODUITS = load_data()

@st.cache_data
def get_js_data():
    """Minified JSON for the JS autocomplete component."""
    mini = []
    for p in ALL_PRODUITS:
        mini.append({
            "s": p["sec_code"], "sl": p["sec_lib"],
            "g": p["grp_lib"], "a": p["act_lib"],
            "pc": p["prod_code"], "pl": p["prod_lib"],
        })
    return json.dumps(mini, ensure_ascii=False)

JS_DATA = get_js_data()

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
.act-card .act-auto{display:flex;gap:1.2rem;margin-top:6px;padding-top:6px;
    border-top:1px dashed var(--gold-200);font-size:.78rem}
.act-card .act-auto span{color:var(--brown-300)}
.act-card .act-auto strong{color:var(--brown-700)}
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

def render_activity_card(act, role_label):
    return f"""
    <div class="act-card">
        <div class="act-role">{role_label}</div>
        <div class="act-name">{act['prod_lib']}</div>
        <div class="act-detail">Code : {act['prod_code']} · Activité : {act['act_lib']}</div>
        <div class="act-auto">
            <div><span>Secteur :</span> <strong>{act['sec_code']} — {act['sec_lib']}</strong></div>
        </div>
        <div class="act-auto" style="border-top:none;padding-top:0;margin-top:2px;">
            <div><span>Groupe :</span> <strong>{act['grp_lib']}</strong></div>
        </div>
    </div>
    """

def build_autocomplete_html():
    """Build the full HTML/CSS/JS for the live autocomplete component."""
    return f"""
    <div id="ac-root">
        <div id="ac-wrap">
            <div id="ac-icon">🔍</div>
            <input id="ac-input" type="text" autocomplete="off"
                   placeholder="Tapez ici : riz, taxi, poisson, ciment, hôtel, comptabilité…" />
            <div id="ac-clear" onclick="clearInput()" title="Effacer">✕</div>
        </div>
        <div id="ac-count"></div>
        <div id="ac-results"></div>
    </div>

    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&display=swap');
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ background:transparent; font-family:'Source Sans 3',sans-serif; }}
    #ac-root {{ padding:4px 0; }}
    #ac-wrap {{
        display:flex; align-items:center; gap:8px;
        background:#fff; border:2px solid #D7CCC8; border-radius:12px;
        padding:10px 14px; transition:border-color .2s;
    }}
    #ac-wrap:focus-within {{ border-color:#DAA520; box-shadow:0 0 0 3px rgba(218,165,32,.15); }}
    #ac-icon {{ font-size:1.1rem; flex-shrink:0; }}
    #ac-input {{
        flex:1; border:none; outline:none; font-size:.95rem;
        font-family:'Source Sans 3',sans-serif; color:#2C1810; background:transparent;
    }}
    #ac-input::placeholder {{ color:#BCAAA4; }}
    #ac-clear {{
        cursor:pointer; color:#A1887F; font-size:1.1rem; padding:2px 4px;
        border-radius:4px; display:none;
    }}
    #ac-clear:hover {{ background:#EFEBE9; color:#5D4037; }}
    #ac-count {{
        font-size:.78rem; color:#8D6E63; padding:6px 4px 2px;
        min-height:22px;
    }}
    #ac-results {{
        max-height:350px; overflow-y:auto; padding:4px 0;
    }}
    #ac-results::-webkit-scrollbar {{ width:6px; }}
    #ac-results::-webkit-scrollbar-thumb {{ background:#D7CCC8; border-radius:3px; }}
    .ac-item {{
        padding:10px 12px; margin:3px 0; border-radius:10px;
        border:1px solid #E8DDD5; background:#fff;
        cursor:pointer; transition:all .15s;
    }}
    .ac-item:hover {{ border-color:#DAA520; background:#FFFBF0; transform:translateX(3px); }}
    .ac-item .ac-prod {{ font-weight:600; color:#3E2723; font-size:.9rem; }}
    .ac-item .ac-act {{ font-size:.78rem; color:#8D6E63; margin-top:2px; }}
    .ac-item .ac-tags {{
        display:flex; flex-wrap:wrap; gap:4px; margin-top:5px;
    }}
    .ac-item .ac-tag {{
        background:#EFEBE9; border:1px solid #D7CCC8; border-radius:5px;
        padding:1px 7px; font-size:.7rem; color:#5D4037;
    }}
    .ac-item .ac-tag b {{ color:#3E2723; }}
    .ac-empty {{
        text-align:center; padding:20px; color:#A1887F; font-size:.88rem;
    }}
    </style>

    <script>
    const DATA = {JS_DATA};

    const input = document.getElementById('ac-input');
    const results = document.getElementById('ac-results');
    const countEl = document.getElementById('ac-count');
    const clearBtn = document.getElementById('ac-clear');

    let debounceTimer;

    input.addEventListener('input', function() {{
        clearBtn.style.display = this.value ? 'block' : 'none';
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => search(this.value), 120);
    }});

    function clearInput() {{
        input.value = '';
        clearBtn.style.display = 'none';
        results.innerHTML = '';
        countEl.textContent = '';
        input.focus();
    }}

    function search(query) {{
        if (!query || query.length < 2) {{
            results.innerHTML = '';
            countEl.textContent = query.length === 1 ? 'Continuez à taper…' : '';
            return;
        }}

        const terms = query.toLowerCase().trim().split(/\\s+/);
        const matches = [];

        for (let i = 0; i < DATA.length && matches.length < 30; i++) {{
            const d = DATA[i];
            const hay = (d.pl + ' ' + d.a + ' ' + d.g + ' ' + d.sl).toLowerCase();
            if (terms.every(t => hay.includes(t))) {{
                matches.push(d);
            }}
        }}

        if (matches.length === 0) {{
            countEl.textContent = '';
            results.innerHTML = '<div class="ac-empty">Aucun résultat — essayez d\\'autres mots-clés</div>';
            return;
        }}

        const suffix = matches.length >= 30 ? '+ (affinez pour réduire)' : '';
        countEl.textContent = matches.length + ' résultat' + (matches.length > 1 ? 's' : '') + ' ' + suffix;

        let html = '';
        for (const m of matches) {{
            const dataAttr = encodeURIComponent(JSON.stringify(m));
            html += `
            <div class="ac-item" onclick="selectItem(this)" data-item="${{dataAttr}}">
                <div class="ac-prod">${{m.pl}}</div>
                <div class="ac-act">${{m.a}}</div>
                <div class="ac-tags">
                    <div class="ac-tag"><b>Secteur</b> ${{m.s}} — ${{m.sl}}</div>
                    <div class="ac-tag"><b>Groupe</b> ${{m.g}}</div>
                    <div class="ac-tag"><b>Code</b> ${{m.pc}}</div>
                </div>
            </div>`;
        }}
        results.innerHTML = html;
    }}

    function selectItem(el) {{
        const raw = decodeURIComponent(el.getAttribute('data-item'));
        const item = JSON.parse(raw);

        // Send data back to Streamlit
        const payload = {{
            prod_code: item.pc,
            prod_lib: item.pl,
            act_lib: item.a,
            grp_lib: item.g,
            sec_code: item.s,
            sec_lib: item.sl
        }};

        // Use Streamlit's setComponentValue to send data back
        window.parent.postMessage({{
            type: 'streamlit:setComponentValue',
            value: JSON.stringify(payload)
        }}, '*');

        // Visual feedback
        el.style.background = '#FBF0D0';
        el.style.borderColor = '#DAA520';
        el.style.borderWidth = '2px';
        setTimeout(() => {{
            el.style.background = '#FFFBF0';
        }}, 300);
    }}
    </script>
    """


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state["step"] = 0
if "activities" not in st.session_state:
    st.session_state["activities"] = []

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

    # ── Q1 : Live autocomplete search ──
    with st.expander("**① Déterminez votre activité**", expanded=True):
        st.markdown(
            "*Commencez à taper et les suggestions apparaissent instantanément. "
            "Cliquez sur l'activité qui correspond.*"
        )

        # Render the live autocomplete
        selected_json = components.html(build_autocomplete_html(), height=480, scrolling=False)

        # Fallback: manual selectbox for adding (since postMessage is limited)
        st.markdown("---")
        st.markdown("**Ou recherchez manuellement :**")

        search_q = st.text_input(
            "Recherche",
            placeholder="Tapez au moins 2 caractères…",
            key="manual_search",
            label_visibility="collapsed",
        )

        if search_q and len(search_q) >= 2:
            terms = search_q.lower().split()
            hits = []
            for p in ALL_PRODUITS:
                hay = f"{p['prod_lib']} {p['act_lib']} {p['grp_lib']} {p['sec_lib']}".lower()
                if all(t in hay for t in terms):
                    hits.append(p)
                    if len(hits) >= 30:
                        break

            if hits:
                nb = len(hits)
                if nb >= 30:
                    st.caption(f"**30+** résultats — *précisez pour réduire*")
                else:
                    st.caption(f"**{nb}** résultat(s)")

                opts = {}
                for p in hits:
                    lbl = f"{p['prod_lib']}  ·  {p['act_lib']}  ({p['prod_code']})"
                    opts[lbl] = p

                choice = st.selectbox(
                    "Choisir", ["— Sélectionner —"] + list(opts.keys()),
                    key="sel_act", label_visibility="collapsed",
                )
                if choice != "— Sélectionner —":
                    sel = opts[choice]
                    # Preview card
                    st.markdown(f"""
                    <div style="background:#FFFBF0;border:1px solid #F5D77A;border-left:4px solid #DAA520;
                        border-radius:10px;padding:.8rem 1rem;margin:.5rem 0;font-family:'Source Sans 3',sans-serif;">
                        <div style="font-weight:700;color:#3E2723;font-size:.92rem;">📌 {sel['prod_lib']}</div>
                        <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;">
                            <span style="background:#EFEBE9;border:1px solid #D7CCC8;border-radius:5px;
                                padding:1px 7px;font-size:.72rem;color:#5D4037;">
                                <b>Secteur</b> {sel['sec_code']} — {sel['sec_lib']}</span>
                            <span style="background:#EFEBE9;border:1px solid #D7CCC8;border-radius:5px;
                                padding:1px 7px;font-size:.72rem;color:#5D4037;">
                                <b>Groupe</b> {sel['grp_lib']}</span>
                            <span style="background:#EFEBE9;border:1px solid #D7CCC8;border-radius:5px;
                                padding:1px 7px;font-size:.72rem;color:#5D4037;">
                                <b>Code</b> {sel['prod_code']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    existing = [a["prod_code"] for a in st.session_state["activities"]]
                    if sel["prod_code"] not in existing:
                        if st.button(f"✅ Ajouter « {sel['prod_lib']} »", type="primary"):
                            st.session_state["activities"].append(sel)
                            st.rerun()
                    else:
                        st.info("✓ Déjà dans votre liste.")
            else:
                st.warning("Aucun résultat. Essayez d'autres mots-clés.")

        # ── Show selected activities ──
        activities = st.session_state["activities"]
        if activities:
            st.divider()
            st.markdown("**Vos activités sélectionnées :**")
            for idx, act in enumerate(activities):
                role = "Activité principale" if idx == 0 else f"Activité secondaire {idx}"
                col_i, col_d = st.columns([6, 1])
                with col_i:
                    st.markdown(render_activity_card(act, role), unsafe_allow_html=True)
                with col_d:
                    st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_{act['prod_code']}_{idx}", help="Supprimer"):
                        st.session_state["activities"] = [a for i, a in enumerate(activities) if i != idx]
                        st.rerun()
            st.caption("💡 *Recherchez ci-dessus pour ajouter d'autres activités secondaires.*")

    if not st.session_state["activities"]:
        st.info("Veuillez rechercher et sélectionner au moins une activité pour continuer.")
        st.stop()

    # ── Q2 : Détails complémentaires ──
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
    can_continue = bool(st.session_state.get("activity_desc", "").strip()) and len(st.session_state["activities"]) > 0

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
        st.warning("Complétez la description et sélectionnez au moins une activité.")


# ═════════════════════════════════════════════
# ÉTAPE 1 : RÉCAPITULATIF
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

    st.markdown(f"""
    <div class="confirm-card">
        <div class="info-row">
            <div class="info-label">Secteur d'activité</div>
            <div class="info-value"><strong>{principal.get('sec_code','')}</strong> — {principal.get('sec_lib','')}</div>
        </div>
        <div class="info-row">
            <div class="info-label">Groupe d'activité</div>
            <div class="info-value">{principal.get('grp_lib','')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    act_html = ""
    for idx, act in enumerate(activities):
        role = "Activité principale" if idx == 0 else f"Activité secondaire {idx}"
        act_html += render_activity_card(act, role)
    st.markdown(act_html, unsafe_allow_html=True)

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
    if not can_validate:
        st.info("Veuillez cocher les deux attestations pour valider.")
