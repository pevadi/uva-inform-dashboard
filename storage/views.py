from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

import json

@csrf_exempt
def store_event(request):
    try:
        event = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest()
    event["actor"] = {
        "objectType": "Agent",
        "account": {
            "homePage": "https://secure.uva.nl",
            "name": "mlatour1"
        }
    }
    return HttpResponse(json.dumps(event))
