from django.contrib import admin
from .models import *

class PredictionVariableValueAdmin(admin.ModelAdmin):
    list_display = ('variable','value')
    list_filter = ('variable',)

admin.site.register(PredictionVariable)
admin.site.register(PredictionVariableValue, PredictionVariableValueAdmin)
admin.site.register(Prediction)
