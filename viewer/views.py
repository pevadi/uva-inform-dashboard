from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

from identity import identity_required
from storage.helpers import store_event_in_remote_storage
from .helpers import generate_viewer_access_event

@identity_required
@xframe_options_exempt
def render_dashboard(request):
    user = request.session.get("authenticated_user")
    if not request.user.is_staff:
        store_event_in_remote_storage(
            generate_viewer_access_event(),
            user
        )
    return render(request, "dashboard.html", {});
