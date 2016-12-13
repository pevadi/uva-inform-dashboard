from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from identity import identity_required
from .helpers import *

import json
import gc

# Removes all data of the ignored users from local database. Also sets all users to no dashboard.
# The coursegroup is fixed to 3, this is because this function should not be needed anymore in
# new episodes because of a bugfix. 
def remove_ignored_user_data(request=None, debug_out=None):
    from .models import IgnoredUser
    from stats.models import ValueHistory
    from viewer.models import GroupAssignment
    ignored_user_ids = [x.user for x in IgnoredUser.objects.all()]
    for user_id in ignored_user_ids:
        # Delete valuahistory from local db
        ValueHistory.objects.filter(student=user_id, group=3).delete()
        # Set treatment to NO DASHBOARD
        if GroupAssignment.objects.filter(student=user_id):
            tmp = GroupAssignment.objects.get(student=user_id)
            tmp.group = 'B'
            tmp.save()

# Removes all NONE values from LRS (cleaning func) 10 is the PK for scored school-assignment.
def remove_none_values_scores(request=None, debug_out=None):
    from storage.models import Activity
    Activity.objects.filter(verb="http://adlnet.gov/expapi/verbs/scored", type="http://id.tincanapi.com/activitytype/school-assignment", value=None).delete()


def get_grade_so_far(student_id):
    from storage.models import Activity
    from course.models import Assignment
    from django.core.exceptions import ObjectDoesNotExist 

    # Get the already obtained grades from the activity db
    assignments = Assignment.objects.all()
    total_weight = float(0)
    grade_so_far = 0    
    print student_id
    for assignment in assignments:
        # Get highest grade assigned (in order to filter out zero values and older grades. Assumes the highest grade is the latest.
        try:
            assignment_activity =  Activity.objects.filter(user=student_id, activity=assignment.url).latest('value')
            if assignment_activity.value != None and assignment_activity.value != 0:
                print assignment_activity, assignment.weight
                total_weight += assignment.weight
                grade_so_far += ((assignment_activity.value / assignment.max_grade * 10) * assignment.weight)
        except ObjectDoesNotExist:
            continue
    if total_weight > 0:
        return total_weight, grade_so_far
    else:
        return 0, None

# This function get ALL data from the LRS, yes, ALL data.
def update_all(request=None, debug_out=None):
    from django.db.models import Max, Min
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
    debug("Starting update activites. :)")
    for course in Course.objects.filter(active=True):
        debug("Selected course '%s'" % (course.url, ))
        ########### Load all data of all course groups ###########
        res = course.coursegroup_set.aggregate(Min('start_date'))
        epoch = datetime.combine(
                res['start_date__min'], datetime.min.time())
        ##########################################################
        debug("Selected epoch %s" % (epoch.isoformat(),))
        for url in course.url_variations:
            count = 0
            skipped = 0
            debug("Fetch URL variation '%s'" % (url,))
            activities = xapi.getAllStatementsByRelatedActitity(url, epoch)
            print 'n# of activities', len(activities)
            if activities is None:
                continue
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

# This functions gets the newest data from the LRS (very, very similar to the function above)
def update(request=None, debug_out=None):
    from django.db.models import Max, Min
    from course.models import Course, Student, CourseGroup
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
    debug("Starting update activites. :)")
    for course in Course.objects.filter(active=True):
        debug("Selected course '%s'" % (course.url, ))
        ########### Load only new data (based on last stored) ###########
        res = Activity.objects.filter(course=course.url).aggregate(
                Max('remotely_stored'))
        if res['remotely_stored__max'] is not None:
            epoch = res['remotely_stored__max']
        else:
            res = course.coursegroup_set.aggregate(Max('start_date'))
            epoch = datetime.combine(
                    res['start_date__max'], datetime.min.time())
            
        ##########################################################
        debug("Selected epoch %s" % (epoch.isoformat(),))
        for url in course.url_variations:
            count = 0
            skipped = 0
            debug("Fetch URL variation '%s'" % (url,))
            activities = xapi.getAllStatementsByRelatedActitity(url, epoch)
            print 'n# of activities', len(activities)
            if activities is None:
                continue
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

    debug("Starting update student grades.")
    debug('Updating grades for the following course groups')
    debug(CourseGroup.objects.filter(end_date__gte=datetime.now()))
    for active_course_group in CourseGroup.objects.filter(end_date__gte=datetime.now()):
        print len(active_course_group.members.all())
        for student in active_course_group.members.all():
            total_weight, updated_grade = get_grade_so_far(student.identification)
            print student.identification, updated_grade
            if total_weight > 0:
                print student.identification, updated_grade/total_weight
                student.grade_so_far = updated_grade/total_weight
                student.save()



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
        skipped = 0
        absent = []
        for student in group.members.all():
            if request.POST.get(str(student.pk)) == "on":
                event = PresenceEvent(student.identification, group.course.url)
                event.set_object(activity)
                resp = event.store()
                if resp is None:
                    skipped += 1
                elif resp.status_code == 200:
                    count += 1
                else:
                    return HttpResponse(resp.text, status=resp.status_code)
            else:
                absent.append(student.label)
        return HttpResponse("%d present, %d skipped, absent were: %s" % (count,
            skipped, absent))

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

@csrf_exempt
@identity_required
def store_grading_event(request):
    pset = request.POST.get("pset", None)
    if pset is None:
        return HttpResponseBadRequest("Expected pset in payload")

    attributes = ["scope", "correctness", "design", "style", "grade"]
    for attr_name in attributes:
        if attr_name not in request.POST:
            return HttpResponseBadRequest('Expected %s in payload' % (attr_name,))

    for attr_name in attributes:
        event = GradingEvent(request.authenticated_user,
                request.authenticated_course)
        event.set_object(pset)

        attr = request.POST.get(attr_name)
        if attr_name == "grade":
            event.set_result({'min': 10, 'max': 100, 'raw': int(float(attr)*10)},
                    result_type=attr_name)
        else:
            event.set_result({'min': 0, 'max': 50, 'raw': int(float(attr)*10)},
                    result_type=attr_name)

        resp = event.store()
        if resp is not None and resp.status_code != 200:
            return HttpResponse(status=resp.status_code)

    return HttpResponse(status=204)

