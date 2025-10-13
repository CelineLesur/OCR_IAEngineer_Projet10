import streamlit as st
import pandas as pd
import requests

# URL de l'Azure Function
AZURE_FUNCTION_URL = "https://p10reco-edfwceb2bgahdacb.francecentral-01.azurewebsites.net/api/recommendations"
# URL du CSV dans le Blob Storage
ACCOUNT_NAME = "blobp10"
CONTAINER_NAME = "containerp10"
SAS_TOKEN = '?sp=r&st=2025-10-10T13:22:45Z&se=2025-11-15T22:37:45Z&spr=https&sv=2024-11-04&sr=c&sig=WGKPoA4xI%2BmvUVuu3gy%2FE3Lx3hgS1MqbaWwEY2IqYgM%3D' #Ajout de ? au début pour que ça fonctionne
url = f"https://{ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/precomputed_recos.csv{SAS_TOKEN}"
st.set_page_config(page_title="Recommandations d'articles", page_icon="📰", layout="centered")

st.title("Recommandations d'articles")
# Fonction pour charger la liste des utilisateurs depuis le CSV
@st.cache_data
def load_user_ids():
    df = pd.read_csv(url)
    return df['user_id'].astype(str).tolist()

# Sélecteur d'utilisateur
user_ids = load_user_ids()
selected_user = st.selectbox("Choisissez un utilisateur :", user_ids)

# Bouton pour lancer la requête
if st.button("Obtenir les recommandations"):
    try:
        # Appel de l'API Azure Function
        response = requests.get(f"{AZURE_FUNCTION_URL}?user_id={selected_user}")
        if response.status_code == 200:
            recos = response.json() 
            st.success(f"Recommandations récupérées pour l'utilisateur {selected_user} :")
            # Les recommandations arrivent sous forme ["202819,206490,205844,202232,202119"]
#           # Découpage de la chaîne
            reco = recos[0].split(",")
            for i, article_id in enumerate(reco, start=1):
                st.write(f"**{i}.** Article ID: `{article_id}`")
        else:
            st.error(f"Erreur {response.status_code} : {response.text}")
    except Exception as e:
        st.error(f"Erreur lors de l'appel à l'API Azure : {e}")