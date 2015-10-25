from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.clickjacking import xframe_options_exempt

from identity import identity_required
from .helpers import treatment_required
from .models import GroupAssignment
from storage.helpers import *
from course.models import Course

@identity_required
@treatment_required
@xframe_options_exempt
def render_dashboard(request):
    user = request.authenticated_user

    course = get_object_or_404(Course, url=request.authenticated_course)

    DashboardAccessEvent(user, course.url).store()

    return render(request, "dashboard.html", {
        'input_variables': course.variable_set.filter(type='IN')
    });

@identity_required
def has_treatment(request):
    user = request.authenticated_user
    return JsonResponse(GroupAssignment.get_or_assign(user).has_treatment,
            safe=False)
