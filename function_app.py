import sys
sys.path.append("./.python_packages/lib/site-packages")
import azure.functions as func 
import logging 
import json 
import pickle 
import csv
import io
from collections import Counter
from azure.storage.blob import BlobServiceClient 

app = func.FunctionApp()

@app.function_name(name="hello")
@app.route(route="hello")
def hello(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello Azure!", status_code=200)

