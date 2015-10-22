from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from identity import identity_required

import json

@csrf_exempt
@identity_required
def store_event(request):
    try:
        event = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest()
    event["actor"] = {
        "objectType": "Agent",
        "account": {
            "homePage": "https://secure.uva.nl",
            "name": request.session.get("user")
        }
    }
    return HttpResponse(json.dumps(event))
