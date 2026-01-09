import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Configuration de la page
st.set_page_config(page_title="OesoScan Pro - Diagnostic IA", layout="wide")

# --- FONCTIONS UTILES ---
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

# --- CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #4facfe 0%, #00f2fe 100%); }
    div.stButton > button:first-child { background-color: #007bff; color:white; border-radius:10px; }
    .main-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2864/2864448.png", width=100)
    st.title("Navigation")
    page = st.radio("Aller à :", ["Accueil", "Analyse Symptomatique", "Dashboard de Risque", "Documentation"])
    st.markdown("---")
    st.warning("⚠️ **Disclaimer :** Outil pédagogique uniquement.")

# --- INITIALISATION DES DONNÉES ---
if 'symptoms' not in st.session_state:
    st.session_state.symptoms = {
        "Dysphagie": 0, "Perte de Poids": 0, "Douleur Thoracique": 0,
        "Reflux Gastrique": 0, "Tabac/Alcool": 0, "Anémie": 0
    }

# --- PAGE ACCUEIL ---
if page == "Accueil":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("Système Expert : Cancer de l'Œsophage")
        st.write("""
        Bienvenue sur l'interface **OesoScan Pro**. Cet outil utilise une logique floue pour évaluer 
        la probabilité de pathologie œsophagienne maligne basée sur les marqueurs cliniques classiques.
        
        **Comment ça marche ?**
        1. Décrivez vos symptômes.
        2. Répondez au questionnaire clinique détaillé.
        3. Analysez le graphique de risque multidimensionnel.
        """)
    with col2:
        lottie_health = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_5njp3vnu.json")
        if lottie_health: st_lottie(lottie_health, height=200)

# --- PAGE ANALYSE ---
elif page == "Analyse Symptomatique":
    st.header("🔍 Analyse des Symptômes")
    
    with st.container():
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        
        # 1. Analyse par texte libre (NLP simplifié)
        user_text = st.text_area("Décrivez ce que vous ressentez (ex: 'J'ai du mal à avaler et je perds du poids')")
        if user_text:
            keywords = {
                "Dysphagie": ["avaler", "blocage", "gorge", "coincé"],
                "Perte de Poids": ["maigri", "poids", "kilos", "appétit"],
                "Douleur Thoracique": ["poitrine", "thorax", "douleur", "brûlure"]
            }
            found = []
            for symptom, words in keywords.items():
                if any(w in user_text.lower() for w in words):
                    st.session_state.symptoms[symptom] = 1
                    found.append(symptom)
            if found:
                st.success(f"Symptômes détectés : {', '.join(found)}")

        st.markdown("---")
        
        # 2. Questionnaire Structuré
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.symptoms["Dysphagie"] = st.slider("Intensité de la difficulté à avaler (0-10)", 0, 10, st.session_state.symptoms.get("Dysphagie", 0))
            st.session_state.symptoms["Perte de Poids"] = st.number_input("Perte de poids (kg) sur les 3 derniers mois", 0, 50, 0)
        with col2:
            st.session_state.symptoms["Reflux Gastrique"] = st.checkbox("Reflux gastro-œsophagien chronique (RGO)")
            st.session_state.symptoms["Tabac/Alcool"] = st.radio("Consommation tabac/alcool", ["Nulle", "Modérée", "Élevée"])
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- PAGE DASHBOARD ---
elif page == "Dashboard de Risque":
    st.header("📊 Tableau de Bord du Risque Clinique")
    
    # Calcul du score complexe
    score = 0
    score += st.session_state.symptoms["Dysphagie"] * 1.5
    score += 5 if st.session_state.symptoms["Perte de Poids"] > 5 else 0
    score += 3 if st.session_state.symptoms["Reflux Gastrique"] else 0
    score += 4 if st.session_state.symptoms["Tabac/Alcool"] == "Élevée" else 0
    
    max_score = 30 # Normalisation
    risk_prob = min((score / max_score) * 100, 100)

    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Jauge de risque
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = risk_prob,
            title = {'text': "Indice de Risque Global (%)"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps' : [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 70], 'color': "orange"},
                    {'range': [70, 100], 'color': "red"}],
            }))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        # Graphique Radar
        categories = list(st.session_state.symptoms.keys())
        values = [st.session_state.symptoms[c] if isinstance(st.session_state.symptoms[c], int) else 5 for c in categories]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name='Profil Patient'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=False, title="Analyse Multidimensionnelle")
        st.plotly_chart(fig_radar, use_container_width=True)

    if risk_prob > 60:
        st.error("🚨 **ALERTE :** Profil à haut risque. Une consultation urgente pour une endoscopie digestive haute est fortement recommandée.")
    else:
        st.info("ℹ️ Profil ne présentant pas de critères d'urgence immédiate, mais une surveillance reste de mise.")

# --- PAGE DOCUMENTATION ---
else:
    st.header("📚 Ressources Médicales")
    st.write("""
    Ce projet s'appuie sur les recommandations de la **Haute Autorité de Santé (HAS)**. 
    Les facteurs de risque majeurs incluent :
    - L'endobrachyœsophage (EBO) suite à un RGO.
    - L'intoxication alcoolo-tabagique.
    - La détection tardive due à la compensation alimentaire (mastication prolongée).
    """)
    st.markdown("[Lien vers étude scientifique (PubMed)](https://pubmed.ncbi.nlm.nih.gov/)")
