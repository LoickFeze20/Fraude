import streamlit as st
import pickle
import time
import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
load_dotenv()

# --- Configuration de Base de la Page Streamlit ---
st.set_page_config(
    page_title="Système Intelligent de Détection de Fraude",
    layout="wide",
    page_icon="🛡️"
)

# --- CSS Intégré Simplifié pour les Thèmes ---
def apply_theme_css(theme):
    if theme == 'dark':
        st.markdown(
            """
            <style>
            /* Couleurs pour le thème sombre */
            body { background-color: #1a1a2e; color: #e0e0e0; } /* Fond et texte général */
            .stApp { background-color: #1a1a2e; color: #e0e0e0; }
            
            /* Champs de saisie (texte, nombre, selectbox) */
            .stTextInput>div>div>input, 
            .stNumberInput>div>div>input, 
            .stSelectbox>div>div>div { 
                background-color: #2e2e4f; /* Fond des champs */
                color: #e0e0e0; /* Couleur du texte dans les champs */
                border-color: #5d5e66; /* Bordure des champs */
            }
            .stSelectbox>div>div>div>span {
                color: #e0e0e0; /* Couleur du texte sélectionné dans selectbox */
            }
            .stSelectbox>div>div {
                 background-color: #2e2e4f; /* Fond de la selectbox */
                 border-color: #5d5e66; /* Bordure de la selectbox */
            }
            .stSelectbox [data-testid="stOption"] {
                background-color: #2e2e4f; /* Fond des options de selectbox */
                color: #e0e0e0; /* Texte des options de selectbox */
            }
            .stSelectbox [data-testid="stOption"]:hover {
                background-color: #5d5e66; /* Fond des options de selectbox au survol */
            }

            /* Boutons */
            .stButton>button { 
                background-color: #f75d59; /* Rouge corail pour les boutons */
                color: white; 
                border: none;
                padding: 0.6em 1.2em;
                border-radius: 0.3em;
            }
            .stButton>button:hover {
                background-color: #e04a46; /* Rouge plus foncé au survol */
            }

            /* Titres */
            h1, h2, h3, h4, h5, h6 { color: #8dacec; } /* Bleu clair pour les titres */
            .main-title { color: #f75d59 !important; } /* Surcharger le titre principal si nécessaire */

            /* Messages d'alerte */
            .stSuccess { background-color: #4CAF50; color: white; border-radius: 0.5rem; }
            .stError { background-color: #F44336; color: white; border-radius: 0.5rem; }
            .stWarning { background-color: #FFC107; color: black; border-radius: 0.5rem; }
            .stInfo { background-color: #2196F3; color: white; border-radius: 0.5rem; }

            /* Texte gras et markdown */
            strong { color: #e0e0e0; } /* Rendre le texte en gras plus visible */
            a { color: #8dacec; } /* Liens */

            /* Ajustements pour les éléments Streamlit par défaut */
            .stAlert { color: inherit; } 
            div[data-testid="stVerticalBlock"] > div { /* Pour s'assurer que le fond des colonnes est le même */
                background-color: #1a1a2e; 
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else: # Light theme styles - Pale Green background
        st.markdown(
            """
            <style>
            /* Couleurs pour le thème clair avec fond vert pâle */
            body { background-color: #E6F7E6; color: #333; } /* Fond vert pâle */
            .stApp { background-color: #E6F7E6; color: #333; }
            
            /* Champs de saisie (texte, nombre, selectbox) */
            .stTextInput>div>div>input, 
            .stNumberInput>div>div>input, 
            .stSelectbox>div>div>div { 
                background-color: #ffffff; 
                color: #333; 
                border-color: #ced4da; 
            }
            .stSelectbox>div>div>div>span {
                color: #333;
            }
            .stSelectbox>div>div {
                background-color: #ffffff;
                border-color: #ced4da;
            }
            .stSelectbox [data-testid="stOption"] {
                background-color: #ffffff;
                color: #333;
            }
            .stSelectbox [data-testid="stOption"]:hover {
                background-color: #e9ecef;
            }

            /* Boutons */
            .stButton>button { 
                background-color: #007bff; 
                color: white; 
                border: none;
                padding: 0.6em 1.2em;
                border-radius: 0.3em;
            }
            .stButton>button:hover {
                background-color: #0056b3;
            }

            /* Titres */
            h1, h2, h3, h4, h5, h6 { color: #007bff; }
            .main-title { color: #f75d59 !important; }

            /* Messages d'alerte */
            .stSuccess { background-color: #e8f5e9; color: #388e3c; border-radius: 0.5rem; }
            .stError { background-color: #ffebee; color: #d32f2f; border-radius: 0.5rem; }
            .stWarning { background-color: #fff3cd; color: #856404; border-radius: 0.5rem; }
            .stInfo { background-color: #d1ecf1; color: #0c5460; border-radius: 0.5rem; }

            /* Texte gras et markdown */
            strong { color: #333; }
            a { color: #007bff; }

            /* Ajustements pour les éléments Streamlit par défaut */
            .stAlert { color: inherit; }
            div[data-testid="stVerticalBlock"] > div {
                background-color: #E6F7E6;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

# --- Gestion du Thème (session_state) ---
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'light'

apply_theme_css(st.session_state['theme'])

def toggle_theme():
    st.session_state['theme'] = 'dark' if st.session_state['theme'] == 'light' else 'light'
    # Pas de st.rerun() explicite, le changement de session_state provoque déjà un rerun.

# --- Bouton de Bascule de Thème (positionnement standard) ---
theme_button_label = "☀️" if st.session_state['theme'] == 'dark' else "🌙"
st.button(theme_button_label, on_click=toggle_theme, key="theme_toggle_button_actual")


# --- Fonction de Chargement du Modèle (mise à jour pour st.cache_resource) ---
@st.cache_resource # Utilisez st.cache_resource pour les modèles
def load_fraud_model():
    try:
        with open("model.pkl", "rb") as f:
            model = pickle.load(f)
        return model
    except FileNotFoundError:
        st.error("❌ Erreur : Le fichier 'model.pkl' est introuvable. Veuillez vous assurer qu'il est dans le répertoire correct.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement du modèle : {e}")
        st.stop()

model = load_fraud_model()

# --- Fonction pour convertir en PDF ---
def create_pdf_report(prediction_data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b><font size='20' color='#007bff'>Rapport de Prédiction de Fraude</font></b>", styles['h1']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"Date du rapport : <b>{time.strftime('%Y-%m-%d %H:%M:%S')}</b>", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("<h2><font color='#4CAF50'>Informations Saisies :</font></h2>", styles['h2']))
    input_data_table_data = []
    input_data_table_data.append([
        Paragraph("<b>Caractéristique</b>", styles['Normal']),
        Paragraph("<b>Valeur</b>", styles['Normal'])
    ])
    for key, value in prediction_data.items():
        if key not in ["Prédiction", "Confiance"]:
            input_data_table_data.append([Paragraph(f"<b>{key}</b>", styles['Normal']), Paragraph(str(value), styles['Normal'])])

    table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e0e7ff')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#007bff')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f7faff')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cccccc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cccccc')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ])
    input_table = Table(input_data_table_data, colWidths=[2.5*inch, 3.5*inch])
    input_table.setStyle(table_style)
    story.append(input_table)
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("<h2><font color='#F44336'>Résultat de la Prédiction :</font></h2>", styles['h2']))
    result_color = '#F44336' if prediction_data['Prédiction'] == 'Fraude' else '#4CAF50'
    story.append(Paragraph(f"<b>Prédiction :</b> <font color='{result_color}'>{prediction_data['Prédiction']}</font>", styles['h3']))
    story.append(Paragraph(f"<b>Confiance du Modèle :</b> {prediction_data['Confiance']}", styles['h3']))
    story.append(Spacer(1, 0.5*inch))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- Contenu Principal de l'Application ---

st.markdown("<h1 style='text-align: center; color: #f75d59;' class='main-title'>Système Intelligent de Détection de Fraude 🛡️</h1>", unsafe_allow_html=True)
st.write("") # Espace pour la mise en page

# --- Navigation avec st.selectbox (remplace st.tabs pour anciennes versions) ---
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = "Accueil" # Initialisation avec un nom de page sans emoji

page_options = ["Accueil", "Prédiction de Fraude", "Dashboard Analytique"] # Noms simples sans emojis

# Mapper les noms des pages avec emojis vers les noms sans emojis pour la compatibilité
# C'est pour le cas où st.session_state.current_page contiendrait une ancienne valeur avec emoji
page_name_mapping = {
    '🔮 Prédiction de Fraude': 'Prédiction de Fraude',
    '📊 Dashboard Analytique': 'Dashboard Analytique',
    'Accueil': 'Accueil' # S'assurer que l'accueil est aussi dans le mapping
}

# Assurez-vous que la valeur de st.session_state.current_page est valide pour l'index
current_page_for_index = st.session_state.current_page
if current_page_for_index in page_name_mapping:
    current_page_for_index = page_name_mapping[current_page_for_index]
elif current_page_for_index not in page_options:
    # Si la valeur n'est ni dans les nouvelles options ni dans le mapping, réinitialiser
    current_page_for_index = "Accueil"
    st.session_state['current_page'] = "Accueil"


selected_page = st.selectbox(
    "Naviguer vers :",
    options=page_options,
    key="navigation_selectbox",
    index=page_options.index(current_page_for_index)
)

# Mettre à jour l'état de la page si l'utilisateur change l'option
if selected_page != st.session_state.current_page:
    st.session_state.current_page = selected_page
    # Pas besoin de st.rerun() explicite, le selectbox déclenche déjà un rerun.

st.markdown("---") # Séparateur

# --- Contenu des Pages basé sur selected_page ---

# Page d'Accueil
if st.session_state['current_page'] == "Accueil":
    st.markdown("<h2 style='color: #8dacec;'>Bienvenue dans votre solution de sécurité financière avancée.</h2>", unsafe_allow_html=True)
    st.write(
        """
        Découvrez la puissance de l'intelligence artificielle pour protéger vos transactions.
        Notre système intelligent analyse les données en temps réel pour identifier et prévenir les activités frauduleuses avec une précision inégalée.
        """
    )
    st.markdown("---")
    col_intro1, col_intro2 = st.columns(2)
    with col_intro1:
        st.subheader("🚀 Détection Rapide et Précise")
        st.write(
            """
            Utilisant un modèle de Machine Learning entraîné sur des milliers de transactions, notre application
            vous fournit des prédictions instantanées sur la probabilité de fraude.
            Chaque résultat est accompagné d'un pourcentage de confiance pour une décision éclairée.
            """
        )
        st.subheader("📊 Visualisation Intuitive")
        st.write(
            """
            Explorez les tendances et les modèles de fraude grâce à notre tableau de bord interactif.
            Obtenez des insights précieux sur votre dataset pour renforcer vos stratégies de sécurité.
            """
        )
    with col_intro2:
        st.image("https://images.pexels.com/photos/730547/pexels-photo-730547.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
                 caption="Protégez vos actifs avec l'IA", use_column_width=True)
    st.markdown("---")
    st.write("Pour commencer, naviguez vers l'option **'Prédiction de Fraude'** ou explorez vos données dans le **'Dashboard Analytique'**.")


# Page de Prédiction
elif st.session_state['current_page'] == "Prédiction de Fraude":
    st.markdown("<h2 style='color: #8dacec;'>Effectuer une Nouvelle Prédiction</h2>", unsafe_allow_html=True)
    st.markdown("Renseignez les informations de la transaction ci-dessous pour obtenir une analyse instantanée.")

    # Formulaire de Saisie des Données
    with st.form("prediction_form", clear_on_submit=False):
        st.markdown("### Informations du Client et de la Transaction")
        col_pred1, col_pred2 = st.columns(2)
        with col_pred1:
            age = st.number_input("Âge du Client", min_value=0, max_value=120, step=1, value=30, key="age_input")
            genre = st.selectbox("Genre du Client", ["Male", "Femme"], index=0, key="genre_input")
            region = st.selectbox("Région de la Transaction", ["Houston", "Orlando", "Miami"], index=0, key="region_input")
            salaire = st.number_input("Salaire Annuel (€)", min_value=0.0, step=500.0, value=50000.0, key="salaire_input")
        with col_pred2:
            type_carte = st.selectbox("Type de Carte Utilisée", ["MasterCard", "Visa"], index=0, key="type_carte_input")
            score_credit = st.number_input("Score de Crédit (0-100)", min_value=0.0, max_value=100.0, step=1.0, value=75.0, key="score_credit_input")
            montant_transaction = st.number_input("Montant de la Transaction (€)", min_value=0.0, step=50.0, value=100.0, key="montant_transaction_input")
            anciennete_compte = st.number_input("Ancienneté du Compte (années)", min_value=0.0, step=0.5, value=5.0, key="anciennete_compte_input")

        st.markdown("---")
        submit_button = st.form_submit_button("🚀 Lancer la Prédiction")

    if submit_button:
        # Garde l'état de la page pour rester sur la prédiction
        st.session_state.current_page = "Prédiction de Fraude"

        with st.spinner("Analyse intelligente en cours... Veuillez patienter."):
            time.sleep(1.5)

            genre_e = 1 if genre.lower() == "male" else 0
            type_carte_e = 1 if type_carte == "Visa" else 0
            region_map = {"Houston": 0.3950, "Orlando": 0.3168, "Miami": 0.2881}
            region_e = region_map.get(region, 0.0)

            input_vector = np.array([[
                age, genre_e, salaire, region_e, type_carte_e, score_credit,
                montant_transaction, anciennete_compte
            ]])

            if hasattr(model, 'predict_proba'):
                prediction_proba = model.predict_proba(input_vector)[0]
                prediction_class = np.argmax(prediction_proba)
                confidence_percentage = prediction_proba.max() * 100
            else:
                prediction_class = model.predict(input_vector)[0]
                confidence_percentage = 100.0
                st.warning("⚠️ Votre modèle ne supporte pas `predict_proba`. Le pourcentage de confiance est affiché à 100% par défaut.")

        st.markdown("---")
        st.subheader("✨ Résultat de l'Analyse")
        if prediction_class == 1:
            st.error(f"🚨 **ALERTE FRAUDE POTENTIELLE !**")
            st.markdown(f"<h3 style='color: #F44336;'>Confiance du Modèle : <span style='font-size: 1.2em;'>{confidence_percentage:.2f}%</span></h3>", unsafe_allow_html=True)
            st.write("Nous avons détecté une forte probabilité que cette transaction soit frauduleuse. Une investigation plus approfondie est recommandée.")
        else:
            st.success(f"✅ **TRANSACTION SÉCURISEÉE**")
            st.markdown(f"<h3 style='color: #4CAF50;'>Confiance du Modèle : <span style='font-size: 1.2em;'>{confidence_percentage:.2f}%</span></h3>", unsafe_allow_html=True)
            st.write("Cette transaction semble légitime selon notre analyse. Confiance élevée.")

        st.markdown("---")
        st.subheader("📊 Détails des Entrées Fournies")
        prediction_data_display = {
            "Âge": age,
            "Genre": genre,
            "Région": region,
            "Salaire": f"{salaire:,.2f} €".replace(",", " "),
            "Type de Carte": type_carte,
            "Score de Crédit": f"{score_credit:.1f}",
            "Montant Transaction": f"{montant_transaction:,.2f} €".replace(",", " "),
            "Ancienneté du Compte": f"{anciennete_compte:.1f} années",
            "Prédiction": "Fraude" if prediction_class == 1 else "Non Fraude",
            "Confiance": f"{confidence_percentage:.2f}%"
        }

        col_data1, col_data2 = st.columns(2)
        data_keys = list(prediction_data_display.keys())
        for i, key in enumerate(data_keys[:len(data_keys)//2]):
            with col_data1:
                st.markdown(f"**{key}:** {prediction_data_display[key]}")
        for i, key in enumerate(data_keys[len(data_keys)//2:]):
            with col_data2:
                st.markdown(f"**{key}:** {prediction_data_display[key]}")

        st.markdown("---")
        st.subheader("📄 Générer un Rapport PDF")
        pdf_buffer = create_pdf_report(prediction_data_display)
        st.download_button(
            label="💾 Télécharger le Rapport Complet (PDF)",
            data=pdf_buffer,
            file_name=f"rapport_prediction_fraude_{time.strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            # 'type' argument supprimé pour compatibilité avec anciennes versions
        )
        st.info("Ce rapport PDF inclut toutes les informations saisies et le résultat de la prédiction.")

# Page Dashboard
elif st.session_state['current_page'] == "Dashboard Analytique":
    st.markdown("<h2 style='color: #8dacec;'>Dashboard Analytique des Transactions 📊</h2>", unsafe_allow_html=True)
    st.write("Explorez les tendances et les caractéristiques de vos données de transactions.")

    # --- Chargement du Dataset (mise à jour pour st.cache_data) ---
    @st.cache_data # Utilisez st.cache_data pour les DataFrames
    def load_transaction_data(file_path="fraude_bancaire_synthetique_final.csv"):
        try:
            df = pd.read_csv(file_path)
            return df
        except FileNotFoundError:
            st.error(f"❌ Erreur : Le fichier '{file_path}' est introuvable. Veuillez le placer dans le même répertoire que l'application ou spécifier le chemin correct.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement du dataset : {e}")
            st.stop()

    df = load_transaction_data()

    if df is not None:
        st.success("✅ Dataset chargé avec succès ! Voici un aperçu :")
        st.dataframe(df.head())
        st.markdown("---")

        fraud_column_candidates = ['IsFraud', 'fraude', 'Fraude', 'Target', 'is_fraud']
        fraud_column = None
        for col in fraud_column_candidates:
            if col in df.columns:
                fraud_column = col
                break

        if fraud_column is None:
            st.warning("⚠️ Impossible de détecter la colonne de fraude (ex: 'IsFraud'). Certains graphiques ne pourront pas être générés.")
        else:
            st.info(f"Colonne de fraude détectée : **'{fraud_column}'**")
            df[fraud_column] = df[fraud_column].astype(str)
            st.markdown("---")

            st.subheader("📈 Indicateurs Clés des Transactions")
            total_transactions = len(df)
            fraudulent_transactions = df[df[fraud_column] == '1'].shape[0]
            non_fraudulent_transactions = total_transactions - fraudulent_transactions
            fraud_rate = (fraudulent_transactions / total_transactions) * 100 if total_transactions > 0 else 0

            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
            with col_kpi1:
                st.metric(label="Total Transactions", value=f"{total_transactions:,}".replace(",", " "))
            with col_kpi2:
                st.metric(label="Transactions Frauduleuses", value=f"{fraudulent_transactions:,}".replace(",", " "), delta=f"{fraud_rate:.2f}% Taux de Fraude")
            with col_kpi3:
                st.metric(label="Transactions Non-Frauduleuses", value=f"{non_fraudulent_transactions:,}".replace(",", " "))
            st.markdown("---")

        st.subheader("📊 Visualisations Détaillées")

        if "montant_transaction" in df.columns:
            st.markdown("<h4>Distribution des Montants de Transaction</h4>", unsafe_allow_html=True)
            fig1 = px.histogram(df, x="montant_transaction", nbins=50,
                                 title="Distribution des Montants de Transaction",
                                 color_discrete_sequence=['#4CAF50'])
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("La colonne 'montant_transaction' est introuvable pour ce graphique.")

        if fraud_column and "montant_transaction" in df.columns:
            st.markdown("<h4>Montant de Transaction par Catégorie de Fraude</h4>", unsafe_allow_html=True)
            fig_box = px.box(df, x=fraud_column, y="montant_transaction",
                             title="Montant de Transaction par Type de Fraude",
                             color=fraud_column,
                             color_discrete_map={'0': '#4CAF50', '1': '#F44336'})
            st.plotly_chart(fig_box, use_container_width=True)

        if fraud_column and "region" in df.columns:
            st.markdown("<h4>Répartition des Fraudes par Région</h4>", unsafe_allow_html=True)
            df_region_fraud = df.groupby(["region", fraud_column]).size().reset_index(name='Count')
            fig2 = px.bar(df_region_fraud, x="region", y="Count", color=fraud_column,
                              title="Nombre de Transactions par Région et Statut de Fraude",
                              color_discrete_map={'0': '#4CAF50', '1': '#F44336'})
            st.plotly_chart(fig2, use_container_width=True)

        if fraud_column and "type_carte" in df.columns:
            st.markdown("<h4>Taux de Fraude par Type de Carte</h4>", unsafe_allow_html=True)
            df_card_fraud = df.groupby("type_carte")[fraud_column].value_counts(normalize=True).unstack().fillna(0)
            if '1' in df_card_fraud.columns:
                df_card_fraud['Fraud_Rate'] = df_card_fraud['1'] * 100
                fig3 = px.bar(df_card_fraud.reset_index(), x="type_carte", y="Fraud_Rate",
                                 title="Taux de Fraude par Type de Carte",
                                 color_discrete_sequence=['#F44336'])
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("Pas de transactions frauduleuses enregistrées pour le type de carte dans le dataset actuel.")

        if fraud_column and "age" in df.columns:
            st.markdown("<h4>Distribution de l'Âge et Statut de Fraude</h4>", unsafe_allow_html=True)
            fig4 = px.violin(df, y="age", x=fraud_column, box=True, points="all",
                             title="Distribution de l'Âge par Statut de Fraude",
                             color=fraud_column,
                             color_discrete_map={'0': '#4CAF50', '1': '#F44336'})
            st.plotly_chart(fig4, use_container_width=True)

        if fraud_column and "salaire" in df.columns and "score_credit" in df.columns:
            st.markdown("<h4>Salaire vs Score de Crédit par Statut de Fraude</h4>", unsafe_allow_html=True)
            fig5 = px.scatter(df, x="salaire", y="score_credit", color=fraud_column,
                             title="Salaire vs Score de Crédit par Statut de Fraude",
                             color_discrete_map={'0': '#4CAF50', '1': '#F44336'},
                             hover_data=["age", "region", "montant_transaction"])
            st.plotly_chart(fig5, use_container_width=True)
        else:
            if fraud_column:
                missing_cols = []
                if "salaire" not in df.columns: missing_cols.append("'salaire'")
                if "score_credit" not in df.columns: missing_cols.append("'score_credit'")
                if missing_cols:
                    st.warning(f"Les colonnes {', '.join(missing_cols)} sont introuvables pour le graphique 'Salaire vs Score de Crédit'.")
    else:
        st.warning("Veuillez fournir un fichier CSV pour le Dashboard. Nom de fichier attendu: `fraude_bancaire_synthetique_final.csv`.")
        st.info("Vous pouvez placer votre fichier CSV dans le même répertoire que cette application.")