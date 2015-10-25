from django.contrib import admin
from .models import GroupAssignment

class GroupAssignmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'datetime')

admin.site.register(GroupAssignment, GroupAssignmentAdmin)
