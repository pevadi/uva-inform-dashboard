from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest,\
        HttpResponseNotAllowed

from .helpers import *
from .models import Variable, ValueHistory
from course.models import CourseGroup, Student
from identity import identity_required

from datetime import date

@identity_required
def get_variable_stats(request, variable_name):
    """Returns the most recent values of a variable.

    Parameters:
        variable_name   -   The variable for which to lookup the values.
    """
    # Ensure the request uses the GET method.
    if not request.method == "GET":
        return HttpResponseNotAllowed(['GET'])
    variable = get_object_or_404(Variable, name=variable_name)

    # Retrieve current group context
    try:
       student = Student.objects.get(
            identification=request.session.get("authenticated_user"))
    except Student.DoesNotExist:
        return JsonResponse([], safe=False)

    groups = CourseGroup.get_groups_by_date(date.today(),
            course__url=request.session.get('authenticated_course'),
            members=student)
    if len(groups):
        group = groups[0]
    else:
        return HttpResponseBadRequest("User does not belong to a course group")

    from django.utils import timezone
    from datetime import timedelta
    fake_date = timezone.now() + timedelta(weeks=3)

    # Calculate course-relative time context
    course_datetime_now = group.calculate_course_datetime(fake_date)
    # Collect relevant value history
    value_history = ValueHistory.objects.filter(variable=variable, group=group,
            course_datetime__lte=course_datetime_now)
    if len(value_history) == 0:
        return JsonResponse([], safe=False)

    # Calculate variable statistics
    statistics = variable.calculate_statistics_from_values(value_history)

    # Placeholder for the viewer's statement, as well as the bin it falls in.
    student_statistic = None
    student_bin = 0

    # Init reference to store the maximum and minimum value found in the
    #  extracted values. These will determine if all statistic values fit
    #  within the existing value bins for this variable.
    max_value = float('-Inf')
    min_value = float('Inf')
    for statistic in statistics:
        if statistic['student'] == student.identification:
            student_statistic = statistic

        # Update the max and min value found if needed.
        value = statistic['value']
        max_value = value if max_value < value else max_value
        min_value = value if min_value > value else min_value

    # Calculate bins
    bin_size = (max_value-min_value)/float(variable.num_bins)
    bin_fn = lambda x: round(min_value + x * bin_size, 2)
    lower_points = map(bin_fn, range(variable.num_bins))
    upper_points = map(bin_fn, range(1, variable.num_bins+1))

    bin_stats = []
    for index in range(variable.num_bins):
        if index == 0:
            assignment_fn = (lambda s: s['value'] <= upper_points[index] and
                    s['value'] >= lower_points[index])
        else:
            assignment_fn = (lambda s: s['value'] <= upper_points[index] and
                    s['value'] > lower_points[index])

        # Check if we found the viewer's bin
        if assignment_fn(student_statistic):
            student_bin = index

        predictions = {}
        for output_variable in Variable.objects.filter(type='OUT',
                course=group.course):
            predictions[output_variable.name] = (
                get_gauss_params(output_variable,
                    student__in=get_students_by_variable_values(variable,
                        lower_points[index], upper_points[index], index)))

        bin_stats.append({
            'id': index,
            'lower': lower_points[index],
            'upper': upper_points[index],
            'count': len(filter(assignment_fn, statistics)),
            'predictions': predictions
        });

    return JsonResponse({"student_bin": student_bin, "bins": bin_stats},
            safe=False)
