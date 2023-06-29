from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import json
from libs.multi_class import select_ranking
from django.conf import settings
# Create your views here.
from django.http import HttpResponse

def index(requeset):
    return HttpResponse("hi!")

#{"hpo_ids": [64, 67]}
@api_view(http_method_names = ['GET', 'POST'])
def diagnose(request):
    if request.method == "GET":
        return Response({"msg": "Please post with json form data with key hpo_ids of type list[int]"})
    
    try:
        json_data = json.loads(request.body)
        hpo_ids = json_data["hpo_ids"]
    except KeyError:
        return Response({"msg": "request body should be of json format with hpo_ids as key and list[int] as value"})
    

    for hpo_id in hpo_ids:
        if not isinstance(hpo_id, int):
            return Response({"msg": "hpo_id should be integer"})
    
    #print(len(settings.DISEASES))
    res = select_ranking(settings.DISEASES, hpo_ids, 10)
    response = {"disorder_ids": res}

    return  HttpResponse(json.dumps(response))
    