from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest,\
        HttpResponseNotAllowed

from .models import Variable, Statistic, ValueBin
from identity import identity_required

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
    value_bins = ValueBin.objects.filter(variable=variable).order_by('lower')
    bin_stats = []
    for value_bin in value_bins:
        bin_stats.append({
            'id': value_bin.pk,
            'lower': value_bin.lower,
            'upper': value_bin.upper,
            'count': value_bin.count,
            'predictions': {
                variable_name: Statistic.get_gauss_params_by_students(variable,
                    Statistic.get_students_by_bin(value_bin))
            }
        });
    return JsonResponse(bin_stats, safe=False)

@identity_required
def get_variable_prediction(request, bin_pk, variable_name):
    value_bin = get_object_or_404(ValueBin, pk=bin_pk)
    variable = get_object_or_404(Variable, name=variable_name)
    params = Statistic.get_gauss_params_by_students(variable,
            Statistic.get_students_by_bin(value_bin))
    return JsonResponse(params)
