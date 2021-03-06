from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.clickjacking import xframe_options_exempt

from identity import identity_required
from .helpers import treatment_required
from .models import GroupAssignment 
from stats.models import ValueHistory, CourseGroup, Student
from storage.helpers import *
from course.models import Course
from storage.models import IgnoredUser
from datetime import date, timedelta
import logging
from django.contrib.auth.models import User
import operator


@xframe_options_exempt
@identity_required
@treatment_required
def render_dashboard(request):
    log_access_event = bool(int(request.GET.get("log_access", "0")))
    course = get_object_or_404(Course, url=request.authenticated_course)
    day_shift = timedelta(days=int(request.GET.get('day_shift', '0')))
    
    if log_access_event:
        DashboardAccessEvent(request.authenticated_user, request.authenticated_course).store()

    # Retrieve student and current group context
    try:
        student = Student.objects.get(identification=request.session.get("authenticated_user"))
    except Student.DoesNotExist:
        print "Failed to find student", request.session.get("authenticated_user")
        return render(request, "dashboard.html", {
            'log_access': log_access_event,
            'day_shift': request.GET.get('day_shift', '0'),
            'input_variables': [],
        });
 
    groups = CourseGroup.get_groups_by_date(date.today()+day_shift, course__url=request.authenticated_course, members=student)
    if groups:
        group = groups[0]
    else:
        print 'Failed to find group with', student, request.authenticated_course
        return render(request, "dashboard.html", {
            'log_access': log_access_event,
            'day_shift': request.GET.get('day_shift', '0'),
            'input_variables': [],
        });


    # Check if user is instructor
    if User.objects.filter(username=request.session.get("authenticated_user")):
        if User.objects.filter(username=request.session.get("authenticated_user"))[0].is_authenticated:
            students = Student.objects.filter(statistic_groups=group)
            uid_students = []
            for x in xrange(len(students)):
                student = students[x]
                if student.grade_so_far and student.has_treatment:
                    uid_students.append(student)
            
            students = sorted(uid_students, key=operator.attrgetter('grade_so_far'))
             # Determine what variables the first student has data for (and thus will be forwarded to their dropdown menu)
            variables = course.variable_set.exclude(type='OUT').order_by('order')
            course_datetime_now = group.calculate_course_datetime(timezone.now()+day_shift)
            variables = [x for x in variables if not len(ValueHistory.objects.filter(variable=x, course_datetime__lte=course_datetime_now, student=students[0].identification, group=group)) == 0]
            return render(request, "instructor_dashboard.html", {
                'students': students,
                'input_variables':  variables,
                'day_shift': request.GET.get('day_shift', '0'),
            });
    # Student view
    else:
        # Determine what variables the student has data for (and thus will be forwarded to their dropdown menu)
        variables = course.variable_set.exclude(type='OUT').order_by('order')
        course_datetime_now = group.calculate_course_datetime(timezone.now()+day_shift)
        variables = [x for x in variables if not len(ValueHistory.objects.filter(variable=x, course_datetime__lte=course_datetime_now, student=student.identification, group=group)) == 0]
        return render(request, "dashboard.html", {
            'log_access': log_access_event,
            'day_shift': request.GET.get('day_shift', '0'),
            'input_variables': variables,
        });

@identity_required
def has_treatment(request):
    return JsonResponse(True, safe=False)
    user = request.authenticated_user
    return JsonResponse(GroupAssignment.get_or_assign(user).has_treatment,
            safe=False)
