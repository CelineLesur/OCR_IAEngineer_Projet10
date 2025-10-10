import azure.functions as func 
import logging 
import json 
import pickle 
import pandas as pd 
# from azure.storage.blob import BlobServiceClient 

app = func.FunctionApp()

@app.function_name(name="hello")
@app.route(route="hello")
def hello(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello Azure!", status_code=200)
