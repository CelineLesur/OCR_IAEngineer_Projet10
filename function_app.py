import sys
sys.path.append("./.python_packages/lib/site-packages")
import azure.functions as func 
import logging 
import json 
import pickle 
import csv
import io
from collections import Counter
<<<<<<< HEAD
# import pandas as pd 
=======
>>>>>>> 61d03e4a51399d3498ee7cb7616c93289f66e51f
from azure.storage.blob import BlobServiceClient 

app = func.FunctionApp()

<<<<<<< HEAD
# Paramètres Azure Blob 
BLOB_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=blobp10;AccountKey=ngvw8NnAIqHg1qkStpi9pINYcOHYSpqfKelySJaJ81KgpmQLTy37YCULObnA815Sr3e8wh6c2DoR+AStocqpZQ==;EndpointSuffix=core.windows.net" 
CONTAINER_NAME = "containerp10" 

# Fonction pour charger les données une seule fois 
def load_data(): 
    global EMBEDDINGS, METADATA, CLICK, INDEX_TO_ARTICLE 
    if EMBEDDINGS is None or METADATA is None or CLICK is None: 
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING) 
        container_client = blob_service_client.get_container_client(CONTAINER_NAME) 
        
        # Télécharger topk_neighbors.pkl (matrice de similarité restreinte aux top-k voisins)
        blob_client = container_client.get_blob_client("topk_neighbors.pkl") 
        pickle_bytes = blob_client.download_blob().readall() 
        EMBEDDINGS = pickle.loads(pickle_bytes) 
        
        # Télécharger articles_metadata.csv 
        blob_client = container_client.get_blob_client("articles_metadata.csv") 
        metadata_bytes = blob_client.download_blob().readall() 
        METADATA = list(csv.DictReader(io.StringIO(metadata_bytes.decode('utf-8'))))
        # METADATA = pd.read_csv(pd.io.common.BytesIO(metadata_bytes)) 
        
        # Télécharger le dataframe filtrés des clicks 
        blob_client = container_client.get_blob_client("df_filtered.csv") 
        click_bytes = blob_client.download_blob().readall() 
        CLICK = list(csv.DictReader(io.StringIO(click_bytes.decode('utf-8'))))
        # CLICK = pd.read_csv(pd.io.common.BytesIO(click_bytes)) 
        
        # S'assurer que les indices des embeddings et des articles correspondent 
        INDEX_TO_ARTICLE = [row['article_id'] for row in METADATA]
        
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
    # counts = pd.Series(neighbors).value_counts()
    # top_recos = counts.head(top_n).index.tolist()
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
=======
@app.function_name(name="hello")
@app.route(route="hello")
def hello(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello Azure!", status_code=200)
>>>>>>> 61d03e4a51399d3498ee7cb7616c93289f66e51f
