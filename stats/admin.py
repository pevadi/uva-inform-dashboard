from django.contrib import admin
from .models import *

class VariableValueAdmin(admin.ModelAdmin):
    list_display = ('variable','value')
    list_filter = ('variable',)

admin.site.register(Variable)
admin.site.register(VariableValue, VariableValueAdmin)
admin.site.register(Prediction)
admin.site.register(StatisticGroup)
admin.site.register(Statistic)
