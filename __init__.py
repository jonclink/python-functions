import logging
import azure.functions as func
import json
import os
from ..Services.SentimentService import SentimentService

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        req_body = req.get_json()
        article = req_body['Content'].split()

        s = SentimentService()
        pickle_path = os.environ["pickle_path"]
        logging.info(pickle_path)
        
        return func.HttpResponse(json.dumps(s.sentimentAnalysis(article)))
    except ValueError:
        pass
    else:
        content = req_body.get('Content')
        return func.HttpResponse(
             "Please pass content on the query string or in the request body",
             status_code=400
        )