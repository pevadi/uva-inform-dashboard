from django.contrib import admin
from .models import *

class ValueHistoryAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'variable', 'value', 'course_datetime',
            'datetime')

admin.site.register(AveragingVariable)
admin.site.register(ValueHistory, ValueHistoryAdmin)
