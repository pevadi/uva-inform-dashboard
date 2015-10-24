from django.shortcuts import render, get_object_or_404
from django.views.decorators.clickjacking import xframe_options_exempt

from identity import identity_required
from storage.helpers import store_event_in_remote_storage
from .helpers import generate_viewer_access_event
from course.models import Course

@identity_required
@xframe_options_exempt
def render_dashboard(request):
    user = request.session.get("authenticated_user")

    course = get_object_or_404(Course,
            url=request.session.get("authenticated_course"))

    if not request.user.is_staff:
        store_event_in_remote_storage(
            generate_viewer_access_event(),
            user
        )
    return render(request, "dashboard.html", {
        'input_variables': course.variable_set.filter(type='IN')
    });
