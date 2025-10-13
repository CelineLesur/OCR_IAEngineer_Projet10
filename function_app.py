import azure.functions as func
import logging
import json
import csv
import io
import requests

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

ACCOUNT_NAME = "blobp10"
CONTAINER_NAME = "containerp10"
SAS_TOKEN = '?sp=r&st=2025-10-10T13:22:45Z&se=2025-11-15T22:37:45Z&spr=https&sv=2024-11-04&sr=c&sig=WGKPoA4xI%2BmvUVuu3gy%2FE3Lx3hgS1MqbaWwEY2IqYgM%3D' #Ajout de ? au début pour que ça fonctionne

# Variable globale
USER_RECOS = None

def download_blob(filename: str) -> bytes:
    url = f"https://{ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}/{filename}{SAS_TOKEN}"
    logging.info(f"Téléchargement : {url}")
    r = requests.get(url)
    r.raise_for_status()
    return r.content

def load_recos():
    global USER_RECOS
    if USER_RECOS is None:
        logging.info("📥 Chargement des recommandations pré-calculées...")
        content = download_blob("precomputed_recos.csv")
        reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
        USER_RECOS = {int(row["user_id"]): row["recommended_articles"].split("|") for row in reader}
        logging.info(f"{len(USER_RECOS)} utilisateurs chargés")

@app.function_name(name="reco")
@app.route(route="recommendations")
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Requête reçue")
    user_id_str = req.params.get("user_id")
    if not user_id_str:
        return func.HttpResponse(
            "Paramètre 'user_id' manquant", status_code=400
        )
    try:
        user_id = int(user_id_str)
    except ValueError:
        return func.HttpResponse(
            "Paramètre 'user_id' invalide", status_code=400
        )

    load_recos()
    recos = USER_RECOS.get(user_id, [])
    return func.HttpResponse(
        json.dumps(recos),
        mimetype="application/json"
    )
