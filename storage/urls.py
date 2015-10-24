from django.conf.urls import include, url
from views import *

urlpatterns = [
    url(r'^store/compile/?$', "zips.views.log_compile", name="log_compile"),
    url(r'^store/?$', store_event, name="store_event"),
    url(r'^events/video/watch/?$', store_video_watch_event,
        name="store_video_watch_event"),
    url(r'^events/webpage/ping/?$', store_webpage_ping_event,
        name="store_webpage_ping_event"),
    url(r'^events/dashboard/interacted/?$', store_interacted_event,
        name="store_interacted_event"),
]
