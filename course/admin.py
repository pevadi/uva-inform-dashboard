from django.contrib import admin
from .models import *

from datetime import date

from identity import generate_signed_params

class StudentAdmin(admin.ModelAdmin):
    list_display = ("identification", "dashboard")

    def dashboard(self, instance):
        link_template = "<a href='/?%s'>%s/%s</a>"
        links = []

        for group in instance.statistic_groups.filter(
                start_date__lte=date.today(), end_date__gte=date.today()):
            if group.course.active:
                links.append(link_template % (
                    generate_signed_params(
                        instance.identification,
                        group.course.url
                    ),
                    group.course.title,
                    group.label
                ))
        return ", ".join(links)
    dashboard.allow_tags = True

class CourseGroupAdmin(admin.ModelAdmin):
    list_display = ("course", "label", "start_date", "end_date")

admin.site.register(Student, StudentAdmin)
admin.site.register(Course)
admin.site.register(CourseGroup, CourseGroupAdmin)
