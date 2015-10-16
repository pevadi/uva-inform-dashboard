from django.conf.urls import include, url
from views import *

urlpatterns = [
    url(r'^prediction/(?P<output_label>[^/]+)/', get_prediction_table,
        name='prediction'),
    url(r'^(?P<variable_name>[^/]+)/', get_variable_stats,
        name='variable_stats'),
]
