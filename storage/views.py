from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from identity import identity_required
from .helpers import *

import json

def update(request):
    from django.db.models import Max
    from course.models import Course
    from .models import Activity
    from storage import XAPIConnector
    from datetime import datetime
    xapi = XAPIConnector()
    count = 0
    for course in Course.objects.filter(active=True):
        res = Activity.objects.filter(course=course.url).aggregate(Max('time'))
        if res['time__max'] is not None:
            epoch = res['time__max']
        else:
            res = course.coursegroup_set.aggregate(Max('start_date'))
            epoch = datetime.combine(
                    res['start_date__max'], datetime.min.time())
        activities = xapi.getAllStatementsByRelatedActitity(course.url, epoch)
        for activity in activities:
            Activity.extract_from_statement(activity)
        count += len(activities)
        for variable in course.variable_set.all():
            variable.update_from_storage()
    return HttpResponse(count)


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
    else:
        return HttpResponse(status=resp.status_code)

@csrf_exempt
@identity_required
def store_webpage_ping_event(request):
    location = request.POST.get("location", None)
    duration = request.POST.get("duration", None)

    if duration is None or location is None:
        return HttpResponseBadRequest(
                "`duration` and `location` must be provided")

    try:
        duration = float(duration)
    except ValueError:
        return HttpResponseBadRequest('duration must an integer or float')

    event = WebsitePingEvent(request.session.get("authenticated_user"),
        course=request.session.get("authenticated_course"))

    event.set_object(location)
    event.set_duration(seconds=duration)
    resp = event.store()
    if resp is None or resp.status_code == 200:
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=resp.status_code)

@csrf_exempt
@identity_required
def store_accessed_event(request):
    resp = DashboardAccessEvent(
        request.authenticated_user,
        request.authenticated_course
    ).store()
    if resp is None or resp.status_code == 200:
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=resp.status_code)

@csrf_exempt
@identity_required
def store_interacted_event(request):
    resp = DashboardInteractedEvent(
        request.authenticated_user,
        request.authenticated_course
    ).store()
    if resp is None or resp.status_code == 200:
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=resp.status_code)

@csrf_exempt
@identity_required
def store_compile_event(request):
    pset = request.POST.get("pset", None)

    if pset is None:
        return HttpResponseBadRequest()

    event = CompileEvent(request.session.get("authenticated_user"),
        course=request.session.get("authenticated_course"))

    event.set_object(pset)
    resp = event.store()
    if resp is None or resp.status_code == 200:
        return HttpResponse(status=204)
    else:
        return HttpResponse(status=resp.status_code)
