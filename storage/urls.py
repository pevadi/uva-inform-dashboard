from django.conf.urls import include, url
from views import *

urlpatterns = [
    url(r'^storage/store/compile/?$', "zips.views.log_compile", name="log_compile"),
    url(r'^storage/store/?$', store_event, name="store_event"),
    url(r'^storage/events/video/watch/?$', store_video_watch_event,
        name="store_video_watch_event"),
    url(r'^storage/events/webpage/ping/?$', store_webpage_ping_event,
        name="store_webpage_ping_event"),
    url(r'^storage/events/dashboard/interacted/?$', store_interacted_event,
        name="store_interacted_event"),
]
