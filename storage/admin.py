from django.contrib import admin
from .models import *


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'time','verb', 'activity', 'course', 'value', 'type')
    list_filter = ('course', 'verb', 'type')
    search_fields = ('activity',)

admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityVerb)
admin.site.register(ActivityType)
admin.site.register(ActivityExtension)
admin.site.register(IgnoredUser)
