import streamlit as st
import pickle
import time
import base64
import numpy as np
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Détection de Fraude", layout="wide", page_icon="🛡️")

# CSS simple pour garder l’interface propre
st.markdown("""
<style>
/* Sidebar transparent */
[data-testid="stSidebar"] {
    background-color: transparent !important;
    color: inherit !important;
    padding: 2rem 1rem;
}

/* Inputs */
.stTextInput>div>div>input, .stNumberInput>div>input, .stSelectbox > div > div {
    border-radius: 6px !important;
    border: 1px solid #ccc !important;
    padding: 0.5rem !important;
}

/* Boutons */
.stButton>button {
    background-color: #005f73 !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.5rem !important;
    border: none !important;
    cursor: pointer;
    transition: background-color 0.3s ease;
}
.stButton>button:hover {
    background-color: #0a9396 !important;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Détection de Fraude")
menu = ["Home", "Prediction"]
choice = st.sidebar.selectbox("Board",menu)
st.sidebar.markdown("Entrez les données client et lancez la prédiction.")

if st.sidebar.button("🔄 Réinitialiser"):
    st.experimental_rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 • Projet détection de fraude")

# Page principale
if choice == "Home":
    st.title("🛡️ Application de Détection de Fraude")

    # Bloc d’introduction
    st.markdown(
        """
        <div style="text-align: center; padding: 1.5rem; background: rgba(0, 95, 115, 0.1); border-radius: 12px;">
            <h2 style="color: inherit;">Bienvenue sur notre outil d’analyse de fraude</h2>
            <p style="font-size: 1.1rem; color: inherit;">
                Cette application d’intelligence artificielle vous permet d’évaluer le risque de fraude d’un client à partir de ses caractéristiques.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Liste des fonctionnalités
    st.markdown(
        """
        <div style="margin-top: 2rem;">
            <h3 style="color: inherit;">🚀 Fonctionnalités clés :</h3>
            <ul style="font-size: 1.05rem; line-height: 1.6; padding-left: 1rem; color: inherit;">
                <li>✅ Prédictions rapides et fiables grâce à un modèle d’IA entraîné sur des données réelles.</li>
                <li>✅ Interface épurée et moderne, conçue pour être intuitive.</li>
                <li>✅ Protection et confidentialité des données utilisateur.</li>
                <li>✅ Design responsive, adapté aux écrans de toutes tailles.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Message d’invitation
    st.markdown(
        """
        <div style="text-align: center; margin-top: 2rem; color: inherit;">
            <p style="font-style: italic;">Prêt à tester ? Naviguez dans le menu à gauche pour accéder aux prédictions.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    
    
elif choice == "Prediction":
    tab1,tab2 = st.tabs(["Prediction💹","MultiPredict💹💹"])
    with tab1:
        st.title("🛡️ Prédiction de Fraude")

        col1, col2 = st.columns(2)

        with col1:
            age = st.number_input("Âge", min_value=0, max_value=120, step=1, value=0)
            genre = st.selectbox("Genre", ["Male", "Femme"], index=0)
            region = st.selectbox("Région", ["Houston", "Orlando", "Miami"], index=0)
            salaire = st.number_input("Salaire (€)", min_value=0.0, step=500.0, value=0.0)

        with col2:
            type_carte = st.selectbox("Type de Carte", ["MasterCard", "Visa"], index=0)
            score_credit = st.number_input("Score de Crédit", min_value=0.0, max_value=1000.0, step=1.0, value=0.0)
            montant_transaction = st.number_input("Montant Transaction (€)", min_value=0.0, step=50.0, value=0.0)
            anciennete_compte = st.number_input("Ancienneté du Compte (années)", min_value=0.0, step=0.5, value=0.0)

        with open("model.pkl", "rb") as f:
            model = pickle.load(f)

        genre_e = 1 if genre.lower() == "male" else 0
        type_carte_e = 1 if type_carte == "Visa" else 0
        region_map = {"Houston": 0.3950, "Orlando": 0.3168, "Miami": 0.2881}
        region_e = region_map[region]

        input_vector = [[age, genre_e, salaire, region_e, type_carte_e, score_credit, montant_transaction, anciennete_compte]]

        if st.button("🚀 Prédire la fraude"):
            with st.spinner("Analyse en cours..."):
                time.sleep(1)
                prediction = model.predict(input_vector)[0]

            if prediction == 1:
                st.error("🚨 Ce client est passible de fraude !")
            else:
                st.success("✅ Ce client est clean.")
    with tab2:
        st.title("🛡️ Prédiction de Fraude Multiple")
        @st.cache_data
        def load_data(dataset):
            data = pd.read_csv(dataset)
            return data
        
        def filedownload(data):
            csv = data.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
            href = f'<a href="data:file/csv;base64,{b64}" download="predictions.csv">Download CSV File</a>'
            return href
        
        uploaded_fraude = st.file_uploader('Fraude csv',type=['csv'])  
        if uploaded_fraude:
            df = load_data(uploaded_fraude)
            model_v = pickle.load(open('model.pkl','rb'))
            prediction = model_v.predict(df)
            st.subheader('Prediction de Fraude')
            #transforme du aré de stream en dataset et l'introduire dans le dataset fourni
            pp = pd.DataFrame(prediction,columns=['Prediction'])
            dfn = pd.concat([df,pp],axis=1)
            dfn.Prediction.replace(0,"✅ Ce client est clean.",inplace=True)
            dfn.Prediction.replace(1,"🚨 Ce client est passible de fraude !",inplace=True)
            st.write(dfn)
            button = st.button('Download')
            if button:
                st.markdown(filedownload(dfn),unsafe_allow_html=True)

st.markdown("---")
st.markdown("<footer style='text-align:center;color:#888;padding:1rem 0;'>© 2025 - Projet Détection de Fraude</footer>", unsafe_allow_html=True)
