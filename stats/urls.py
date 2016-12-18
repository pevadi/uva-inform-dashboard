"""
UID URL Configuration
"""

from django.conf.urls import url
from stats.views import get_variable_stats

urlpatterns = [
    url(r'^(?P<variable_names>[^/]+)/', get_variable_stats,
        name='variable_stats'),
]
