from django.shortcuts import render

def render_dashboard(request):
    return render(request, "dashboard.html", {});
