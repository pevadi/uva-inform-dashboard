from django.conf.urls import include, url
from views import *

urlpatterns = [
    url(r'^events/video/watch/?$', store_video_watch_event,
        name="store_video_watch_event"),
    url(r'^events/webpage/ping/?$', store_webpage_ping_event,
        name="store_webpage_ping_event"),
    url(r'^events/dashboard/accessed/?$', store_accessed_event,
        name="store_accessed_event"),
    url(r'^events/dashboard/interacted/?$', store_interacted_event,
        name="store_interacted_event"),
    url(r'^events/code/compile/?$', store_compile_event,
        name="store_compile_event"),
]
