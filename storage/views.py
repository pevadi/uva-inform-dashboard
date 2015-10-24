from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from identity import identity_required
from .helpers import store_event_in_remote_storage, VideoWatchEvent

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

@csrf_exempt
@identity_required
def store_video_watch_event(request):
    video_id = request.POST.get("video", None)
    duration = request.POST.get("duration", None)

    if video_id is None or duration is None:
        return HttpResponseBadRequest('`video` and `duration` must be provided')

    try:
        duration = float(duration)
    except ValueError:
        return HttpResponseBadRequest('duration must an integer or float')

    event = VideoWatchEvent(request.session.get("authenticated_user"),
        course=request.session.get("authenticated_course"))
    event.set_object(video_id)
    event.set_duration(seconds=duration)
    resp = event.store()
    if resp is None or resp.status_code == 200:
        return HttpResponse(status=204)

@csrf_exempt
@identity_required
def store_webpage_ping_event(request):
    location = request.POST.get("location", None)
    duration = request.POST.get("duration", None)

    if duration is None or location is None:
        return HttpResponseBadRequest(
                "`duration` and `location` must be provided")

    event = WebsitePingEvent(request.session.get("authenticated_user"),
        course=request.session.get("authenticated_course"))

    event.set_object(location)
    event.set_duration(seconds=duration)
    resp = event.store()
    if resp is None or resp.status_code == 200:
        return HttpResponse(status=204)

@csrf_exempt
@identity_required
def store_interacted_event(request):
    pass

@csrf_exempt
@identity_required
def store_compile_event(request):
    pass
