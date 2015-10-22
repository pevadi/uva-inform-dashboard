from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt

from identity import identity_required

@identity_required
def bootstrap(request):
    return render(request, "js/bootstrap.js",
        { "user": request.session.get("user")},
        content_type="application/javascript")

@xframe_options_exempt
def framed(request):
    return render(request, "frame_loader.html")

@identity_required
def get_ping_script(request):
    return render(request, "js/ping_logger.js",
        content_type="application/javascript")

@identity_required
def get_video_script(request):
    return render(request, "js/video_logger.js",
        content_type="application/javascript")

@identity_required
def get_dashboard_script(request):
    return render(request, "js/dashboard_loader.js",
        content_type="application/javascript")
