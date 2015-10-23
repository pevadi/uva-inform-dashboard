from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from identity import identity_required
from .helpers import store_event_in_remote_storage

import json

@csrf_exempt
@identity_required
def store_event(request):
    try:
        event = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest()

    user = request.session.get("authenticated_user")
    stored_event = store_event_in_remote_storage(event, user)

    return HttpResponse(json.dumps(stored_event))
