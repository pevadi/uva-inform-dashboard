from django.conf.urls import include, url
from views import *

urlpatterns = [
    url(r'^prediction/(?P<output_label>[^/]+)/', get_prediction_table,
        name='prediction'),
]
