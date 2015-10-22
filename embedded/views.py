from django.shortcuts import render

def bootstrap(request):
    return render(request, "js/bootstrap.js",
        content_type="application/javascript")

def get_ping_script(request):
    return render(request, "js/ping_logger.js",
        content_type="application/javascript")

def get_video_script(request):
    return render(request, "js/video_logger.js",
        content_type="application/javascript")

def get_dashboard_script(request):
    return render(request, "js/dashboard_loader.js",
        content_type="application/javascript")
