"""
UID Admin page configuration
"""
from django.contrib import admin
from .models import SingleEventVariable, AssignmentLinkedVariable,\
        Variable, ValueHistory, IgnoredObject
from polymorphic.admin import PolymorphicParentModelAdmin,\
        PolymorphicChildModelAdmin

class ValueHistoryAdmin(admin.ModelAdmin):
    """ValueHistory admin view"""
    list_display = ('student', 'group', 'variable', 'value', 'course_datetime',
            'datetime')
    list_filter = ('group', 'variable__name', 'student')

class SingleEventVariableAdmin(PolymorphicChildModelAdmin):
    """SingleEventVariable Admin view"""
    base_model = SingleEventVariable

class AssignmentLinkedVariableAdmin(PolymorphicChildModelAdmin):
    """AssignmentLinkedVariable Admin view"""
    base_model = AssignmentLinkedVariable

class VariableAdmin(PolymorphicParentModelAdmin):
    """Variable Admin view"""
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
