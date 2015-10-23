from django.conf.urls import include, url
from views import *

urlpatterns = [
    url(r'^prediction/(?P<bin_pk>[^/]+)/(?P<variable_name>[^/]+)/',
        get_variable_prediction, name='prediction'),
    url(r'^(?P<variable_name>[^/]+)/', get_variable_stats,
        name='variable_stats'),
]
