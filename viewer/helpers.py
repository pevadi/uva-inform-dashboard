from django.http import HttpResponse

from .models import GroupAssignment
from course.models import Student

def treatment_required(func):
    def inner(request, *args, **kwargs):
        student = request.authenticated_user
        # only assign students that have data available (aka signed IC)
        if len(Student.objects.filter(identification=student)) > 0:
            if GroupAssignment.get_or_assign(student).has_treatment:
                return func(request, *args, **kwargs)
            else:
                return HttpResponse(status=204)

    return inner
