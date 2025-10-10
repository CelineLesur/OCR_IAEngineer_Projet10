import azure.functions as func

app = func.FunctionApp()

@app.function_name(name="hello")
@app.route(route="hello")
def hello(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello Azure!", status_code=200)
