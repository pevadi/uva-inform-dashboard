from django.conf.urls import include, url
from views import *

urlpatterns = [
    url(r'^bootstrap/?$', bootstrap, name='bootstrap'),
    url(r'^framed/?$', framed, name='framed'),
    url(r'^scripts/pset/?$', get_pset_script, name='pset_script'),
    url(r'^scripts/ping/?$', get_ping_script, name='ping_script'),
    url(r'^scripts/video/?$', get_video_script, name='video_script'),
    url(r'^scripts/dashboard/?$', get_dashboard_script,
        name='dashboard_loader'),
]
