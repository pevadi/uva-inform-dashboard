from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from identity import identity_required
from .helpers import *

import json
import gc

def update(request=None, debug_out=None):
    from django.db.models import Max
    from course.models import Course
    from stats.models import Variable
    from .models import Activity
    from storage import XAPIConnector
    from datetime import datetime
    xapi = XAPIConnector()
    def debug(msg):
        if debug_out is not None:
            debug_out.write("[%s] %s" % (datetime.now().isoformat(), msg))

    total_count = 0
    total_skipped = 0
    skipped_id = []
    debug("Starting update activites.")
    for course in Course.objects.filter(active=True):
        debug("Selected course '%s'" % (course.url, ))
        res = Activity.objects.filter(course=course.url).aggregate(
                Max('remotely_stored'))
        if res['remotely_stored__max'] is not None:
            epoch = res['remotely_stored__max']
        else:
            res = course.coursegroup_set.aggregate(Max('start_date'))
            epoch = datetime.combine(
                    res['start_date__max'], datetime.min.time())
        debug("Selected epoch %s" % (epoch.isoformat(),))
        for url in course.url_variations:
            count = 0
            skipped = 0
            debug("Fetch URL variation '%s'" % (url,))
            activities = xapi.getAllStatementsByRelatedActitity(url, epoch)
            debug("Fetched activities from storage count: %d" % (len(activities),))
            for activity in activities:
                try:
                    ctactivities = activity['context']['contextActivities']
                    ctactivities['grouping'][0]['id'] = course.url
                except:
                    pass
                obj, created = Activity.extract_from_statement(activity)
                if obj is None or not created:
                    skipped += 1
                    skipped_id.append(activity)
                else:
                    count += 1
            del activities
            debug("(Course url) Created: %d, Skipped: %d" % (count, skipped))
            total_count += count
            total_skipped += skipped
        debug("(Total) Created: %d, Skipped: %d" % (total_count, total_skipped))

    debug("Skipped id's:\n%s" % (
        [activity['object']['id'] for activity in skipped_id],))

    debug("Starting update variables.")
    for variable in Variable.objects.filter(course__in=Course.objects.filter(active=True)):
        debug("Updating variable %s" % (variable.name,))
        variable.update_from_storage()

    if request is not None:
        return HttpResponse(count)
    else:
        debug("Finished, imported %d activities." % (total_count,))


def store_presence_events(request):
    from course.models import CourseGroup
    from datetime import date
    group_pk = request.GET.get('group', None)
    group = get_object_or_404(CourseGroup, pk=group_pk)
    if request.method == "GET":
        return render(request, 'store_presence_form.html', {
            'group': group,
            'date': date.today(),
            'students': group.members.all().order_by('last_name')})
    else:
        activity_meeting_type = request.POST.get("activity_meeting_type",
                'hoorcollege')
        activity_meeting_date = request.POST.get("activity_meeting_date",
                date.today().isoformat())
        activity = "/".join([
            group.course.url,
            group.name,
            activity_meeting_type,
            activity_meeting_date])
        count = 0
        absent = []
        for student in group.members.all():
            if request.POST.get(str(student.pk)) == "on":
                event = PresenceEvent(student.identification, group.course.url)
                event.set_object(activity)
                event.store()
                count += 1
            else:
                absent.append(student.label)
        return HttpResponse("%d present, absent were: %s" % (count, absent))

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
