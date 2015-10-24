from django.contrib import admin
from .models import *
from polymorphic.admin import PolymorphicParentModelAdmin,\
        PolymorphicChildModelAdmin

class ValueHistoryAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'variable', 'value', 'course_datetime',
            'datetime')
    list_filter = ('group__course',)

class AveragingVariableAdmin(PolymorphicChildModelAdmin):
    base_model = AveragingVariable

class VariableAdmin(PolymorphicParentModelAdmin):
    base_model = Variable
    child_models = (
        (AveragingVariable, AveragingVariableAdmin),
    )

admin.site.register(Variable, VariableAdmin)
admin.site.register(ValueHistory, ValueHistoryAdmin)
