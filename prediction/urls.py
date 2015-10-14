from django.conf.urls import include, url
from views import *

urlpatterns = [
    url(r'^table/(?P<output_label>[^/]+)/', get_prediction_table, name='table'),
]
