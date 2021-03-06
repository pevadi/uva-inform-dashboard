"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
import settings
from django.conf.urls import patterns

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^embed/', include('embedded.urls', namespace="embed",
        app_name="embed")),
    url(r'^course/add_students/?', "course.views.add_students",
        name="add_students"),
    url(r'^storage/', include('storage.urls', namespace="storage",
        app_name="storage")),
    url(r'^stats/', include('stats.urls', namespace="stats",
        app_name="stats")),
    url(r'^zips/', "zips.views.get_zip", name="get_zip"),
    url(r'^$', "viewer.views.render_dashboard", name="render"),
    url(r'^treatment/?$', "viewer.views.has_treatment", name="has_treatment"),
]


if settings.DEBUG is False:   #if DEBUG is True it will be served automatically
    urlpatterns += patterns('',
            url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )