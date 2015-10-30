from django.contrib import admin
from .models import *
from polymorphic.admin import PolymorphicParentModelAdmin,\
        PolymorphicChildModelAdmin

class ValueHistoryAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'variable', 'value', 'course_datetime',
            'datetime')
    list_filter = ('group__course',)

class SingleEventVariableAdmin(PolymorphicChildModelAdmin):
    base_model = SingleEventVariable

class AssignmentLinkedVariableAdmin(PolymorphicChildModelAdmin):
    base_model = AssignmentLinkedVariable

class VariableAdmin(PolymorphicParentModelAdmin):
    list_display = ('name', 'label', 'course')
    list_filter = ('type',)
    base_model = Variable
    child_models = (
        (SingleEventVariable, SingleEventVariableAdmin),
        (AssignmentLinkedVariable, AssignmentLinkedVariableAdmin),
    )

admin.site.register(Variable, VariableAdmin)
admin.site.register(ValueHistory, ValueHistoryAdmin)
admin.site.register(IgnoredObject)
