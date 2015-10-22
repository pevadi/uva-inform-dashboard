from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

from identity import identity_required

@xframe_options_exempt
@identity_required
def render_dashboard(request):
    return render(request, "dashboard.html", {});
