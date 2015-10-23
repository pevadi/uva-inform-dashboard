from .models import *

def get_students_by_variable_values(variable, lower, upper, bin_index,
        min_students=5, **filter_kwargs):
    statistics = variable.calculate_statistics_from_values(
            ValueHistory.objects.filter(variable=variable, **filter_kwargs))

    if bin_index == 0:
        assignment_fn = (lambda s: s['value'] <= upper and s['value'] >= lower)
    else:
        assignment_fn = (lambda s: s['value'] <= upper and s['value'] > lower)

    strict_bin_members = filter(assignment_fn, statistics)
    if len(strict_bin_members) >= min_students:
        return map(lambda x: x['student'], strict_bin_members)
    else:
        mean = (lower+upper)/2.0
        return map(lambda x: x['student'],
                sorted(statistics, key=lambda x: abs(x['value']-mean))[:5])

def get_gauss_params(variable, **filter_kwargs):
    statistics = variable.calculate_statistics_from_values(
            ValueHistory.objects.filter(variable=variable, **filter_kwargs))

    values = map(lambda x: x['value'], statistics)
    len_values = float(len(values))
    mean = sum(values)/len_values
    variance = sum([(value - mean)**2 for value in values])/len_values
    return {'mean': mean, 'variance': variance}
