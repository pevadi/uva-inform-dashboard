from django.http import HttpResponse

from .models import GroupAssignment

def treatment_required(func):
    def inner(request, *args, **kwargs):
        student = request.authenticated_user
        if GroupAssignment.get_or_assign(student).has_treatment:
            return func(request, *args, **kwargs)
        else:
            return HttpResponse(status=204)

    return inner
