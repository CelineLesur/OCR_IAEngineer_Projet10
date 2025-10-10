import sys
sys.path.append(".python_packages/lib/site-packages"))
import azure.functions as func 
import logging 
import json 
import pickle 
import csv
import io
from collections import Counter
try:
    from azure.storage.blob import BlobServiceClient 
except ImportError:
    BlobServiceClient = None
    erreur =f'{e}'
    

app = func.FunctionApp()

@app.function_name(name="hello")
@app.route(route="hello")
def hello(req: func.HttpRequest) -> func.HttpResponse:
    if BlobServiceClient is None:
        return func.HttpResponse(f"Blob SDK non disponible.{erreur}", status_code=500)
    return func.HttpResponse("Hello Azure!", status_code=200)

