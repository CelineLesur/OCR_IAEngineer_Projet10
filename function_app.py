import azure.functions as func 
import logging 
import json 
import pickle 
import csv
import io
from collections import Counter
import requests

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS) 
#Variables globales pour ne pas recharger à chaque requête 
EMBEDDINGS = None 
METADATA = None 
CLICK = None 
INDEX_TO_ARTICLE = None

# Paramètres Azure Blob 
ACCOUNT_NAME = "blobp10"
CONTAINER_NAME = "containerp10" 
SAS_TOKEN = '?sp=r&st=2025-10-10T13:22:45Z&se=2025-11-15T22:37:45Z&spr=https&sv=2024-11-04&sr=c&sig=WGKPoA4xI%2BmvUVuu3gy%2FE3Lx3hgS1MqbaWwEY2IqYgM%3D' #Ajout de ? au début pour que ça fonctionne

#  Fonction pour télécharger un blob via REST API + SAS Token
def download_blob(filename: str) -> bytes:
    url = f"https://{ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{filename}{SAS_TOKEN}"
    logging.info(f"📡 Tentative téléchargement: {url}")
    r = requests.get(url)
    try:
        r.raise_for_status()
    except Exception as e:
        logging.error(f"❌ Erreur téléchargement {filename}: {e} | Status={r.status_code} | Réponse={r.text}")
        raise
    return r.content

# Fonction pour charger les données une seule fois 
def load_data():
    global EMBEDDINGS, METADATA, CLICK, INDEX_TO_ARTICLE

    if EMBEDDINGS is None or METADATA is None or CLICK is None:
        logging.info("📥 Chargement des données depuis Azure Blob (REST + SAS)...")
        try:
            pickle_bytes = download_blob("topk_neighbors.pkl")
            EMBEDDINGS = pickle.loads(pickle_bytes)
            logging.info(f"✅ EMBEDDINGS chargé ({len(EMBEDDINGS)} lignes)")
        except Exception as e:
            logging.error(f"❌ Erreur chargement EMBEDDINGS: {e}")
            raise
        
        try:
            metadata_bytes = download_blob("articles_metadata.csv")
            METADATA = list(csv.DictReader(io.StringIO(metadata_bytes.decode('utf-8'))))
            logging.info(f"✅ METADATA chargé ({len(METADATA)} lignes)")
        except Exception as e:
            logging.error(f"❌ Erreur chargement METADATA: {e}")
            raise

        try:
            click_bytes = download_blob("df_filtered.csv")
            CLICK = list(csv.DictReader(io.StringIO(click_bytes.decode('utf-8'))))
            logging.info(f"✅ CLICK chargé ({len(CLICK)} lignes)")
        except Exception as e:
            logging.error(f"❌ Erreur chargement CLICK: {e}")
            raise

        try:
            INDEX_TO_ARTICLE = [row['article_id'] for row in METADATA]
            logging.info(f"✅ INDEX_TO_ARTICLE construit ({len(INDEX_TO_ARTICLE)} articles)")
        except Exception as e:
            logging.error(f"❌ Erreur création INDEX_TO_ARTICLE: {e}")
            raise

# Fonction de recommandation 
def recommend_for_user(user_id: int, top_n: int = 5): 
    # Charger les données une seule fois 
    load_data() 
    
    # Liste articles cliqués par l'utilisateur 
    click_articles = list({row['article_id'] for row in CLICK if int(row['user_id']) == user_id})
    if len(click_articles) == 0: 
        return [] 
    
    # Conversion en indices internes 
    click_indices = [INDEX_TO_ARTICLE.index(a) for a in click_articles if a in INDEX_TO_ARTICLE]
    if len(click_indices) == 0: 
        return [] 
    
    # Récupérer les voisins de chaque article cliqué
    neighbors = []
    for idx in click_indices:
        neighbors.extend(EMBEDDINGS[idx])

    # Compter les occurrences et trier
    counts = Counter(neighbors)
    top_recos = [idx for idx, count in counts.most_common(top_n) if idx not in click_indices]
    return [INDEX_TO_ARTICLE[i] for i in top_recos]


# --- 🌐 Azure Function HTTP --- 
@app.function_name(name="reco") #Nom interne à Azure 
@app.route(route="recommendations") #Utilisé pour l'URL publique
def main(req: func.HttpRequest) -> func.HttpResponse: 
    logging.info('Requête reçue pour recommandation content-based')

    # Récupérer user_id depuis l'URL
    user_id_str = req.params.get('user_id')
    if not user_id_str:
        return func.HttpResponse(
            "Paramètre 'user_id' manquant. Exemple : /api/recommendations?user_id=123",
            status_code=400
        )
    try:
        user_id = int(user_id_str)
    except ValueError:
        return func.HttpResponse(
            "Paramètre 'user_id' invalide. Il doit être un entier.",
            status_code=400
        )

    recos = recommend_for_user(user_id, 5)
    return func.HttpResponse(
        json.dumps(recos),
        mimetype="application/json"
    )

#  exemple d'appel : http://localhost:7071/api/recommendations?user_id=42