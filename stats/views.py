from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest,\
        HttpResponseNotAllowed

from .models import Variable, Prediction, Statistic, ValueBin
from identity import identity_required

def get_prediction_table(request, output_label):
    """Returns a 2D-array mapping output values to probabilities.

    Parameters:
        output_label    -   The unique identifier of the output variable
                            that is being predicted.

    GET Parameters:
        input_label     -   The unique identifier of the input variable
                            that is being used to predict the output values.
        input_value     -   The selected value of the input variable.

    Returns:
        A JSON-encoded list of tuples, mapping output values to probabilities.
    """
    # Ensure the request uses the GET method.
    if not request.method == "GET":
        return HttpResponseNotAllowed(['GET'])
    # Retrieve the values of the GET parameters, if available
    input_label = request.GET.get('input_label', None)
    input_value = request.GET.get('input_value', None)
    # If the required GET parameters were not provided, return an error
    if input_label is None or input_value is None:
        return HttpResponseBadRequest(("You need to specify input_label"
            " and input_value URL parameters."))
    # Validate the input_value. If the values is not a float, return an error
    try:
        input_value = float(input_value)
    except ValueError:
        return HttpResponseBadRequest("Param input_value needs to be a float")
    # Attempt to retrieve the input variable by its label, else return an error
    input_variable = get_object_or_404(Variable, pk=input_label)
    # Attempt to retrieve the output variable by its label, else return an error
    output_variable = get_object_or_404(Variable, pk=output_label)
    # Retrieve the prediction table
    table = Prediction.get_table(input_variable, input_value,
            output_variable)
    # Return the table encoded in JSON
    return JsonResponse(table, safe=False)

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
