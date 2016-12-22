from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest,\
        HttpResponseNotAllowed
from django.utils import timezone

from .helpers import *
from .models import Variable, ValueHistory
from course.models import CourseGroup, Student
from identity import identity_required
from datetime import date, timedelta

@identity_required
def get_variable_stats(request, variable_names):
    import numpy as np
    import csv
    from sklearn import svm, linear_model
    from sklearn.preprocessing import normalize
    from sklearn.metrics import explained_variance_score, mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
    from sklearn.model_selection import train_test_split, StratifiedKFold, KFold
    from math import sqrt
    from datetime import timedelta
    from django.contrib.auth.models import User

    """returns the most recent values of a variable.
    
    parameters:
        variable_name   -   the variable for which to lookup the values.
    """
    # Ensure the request uses the GET method.  
    if not request.method == "GET":
        return HttpResponseNotAllowed(['GET'])

    # Get the variable names
    var_names = variable_names.split(';')[1:]
    var_labels = []
    variables = []
    for x in xrange(len(var_names)):
        variables.append(get_object_or_404(Variable, name=var_names[x]))
        var_labels.append(variables[-1].label[:-6])

    # Get student
    if request.GET.get('selected_student'):
        print 'Student selected:', request.GET.get('selected_student')
        if User.objects.filter(username=request.session.get("authenticated_user"))[0].is_authenticated:
            try:
                student = Student.objects.get(identification=request.GET.get('selected_student'))
            except Student.DoesNotExist:
                return JsonResponse([], safe=False)
    else:
        try:
            student = Student.objects.get(identification=request.session.get("authenticated_user"))
        except Student.DoesNotExist:
            return JsonResponse([], safe=False)

    # The day shift parameter allows for admin's to look at the dashboard from
    # the perspective of a different day. Both negative and positive integers
    # are allowed to represent the number of days to substract or add.
    day_shift = timedelta(days=int(request.GET.get('day_shift', '0')))

    print '\nREPORT'
    print 'Day_shift', day_shift
    print 'Course', request.session.get('authenticated_course')
    groups = CourseGroup.get_groups_by_date(date.today()+day_shift,
            course__url=request.session.get('authenticated_course'),
            members=student)

    # Retrieve current group context
    if len(groups):
        group = groups[0]
    else:
        return HttpResponseBadRequest("User does not belong to a course group")

    # Calculate course-relative time context
    # This calculates the nr of days that the current course is running. This is used
    # to get all data from the course up to a particular moment in the course. This 
    # way comparable data can be retrieved from last year (same time in the course)
    course_datetime_now = group.calculate_course_datetime(timezone.now()+day_shift)

    print 'Group', group,'mul', groups
    print 'Datetime', course_datetime_now
    # Collect relevant statistics for prediction of this student
    student_statistics = []
    student_statistics_obj = []
    # Collect the statistics of the other students of his/her year in order to be able to viualise a comparison
    comparison_statistics = {}
    for variable in variables:
        value_history_student = ValueHistory.objects.filter(variable=variable, course_datetime__lte=course_datetime_now, student=student.identification, group=group)
        value_history_comparison = ValueHistory.objects.filter(variable=variable, course_datetime__lte=course_datetime_now, group=group)
        # This if statement is only here so I can see the dashboard with the natasa5 preview user. Of course she should not be included in the comparison data otherwise.
        if student.identification != "natasa5_previewuser":
            value_history_comparison = value_history_comparison.exclude(student="natasa5_previewuser")
        # Calc statistics
        if len(value_history_student) > 0:
            comparison_statistics[variable.name] = variable.calculate_statistics_from_values(value_history_comparison)
            student_statistics.append(variable.calculate_statistics_from_values(value_history_student)[0]['value'])
            student_statistics_obj.append(variable.calculate_statistics_from_values(value_history_student)[0])
        else:
            student_statistics.append(0)
            comparison_statistics[variable.name] = variable.calculate_statistics_from_values(value_history_comparison)


    # Collect relevant value statistics for model building. Y 2015-2016 (pk=2) was selected for this purpose
    var_statistics = {}
    print 'Variables:'
    for variable in variables:
        print '   ', variable, course_datetime_now
        value_history_1516 = ValueHistory.objects.filter(variable=variable.pk, group=2, course_datetime__lte=course_datetime_now)
        if len(value_history_1516) == 0:
            print 'Valuehistory used for model building not found. Check if variables are correctly stored to valuehistory for the following variable:', variable
            return JsonResponse([], safe=False)
        var_statistics[variable.name] = variable.calculate_statistics_from_values(value_history_1516)

    # Placeholder for the viewer's statement, as well as the bin it falls in.
    student_bin = -1
    
    # First get the y values i.e. grades needed for machine learning
    try:
        with open("/home/pepijn/data_2015.csv", mode='r') as infile:
            reader = csv.reader(infile)
            iki_grades = {rows[0]:rows[1] for rows in reader}
    except IOError, e:
        print e
        iki_grades = {}


    # Init reference to store the maximum and minimum value found in the
    #  extracted values. These will determine if all statistic values fit
    #  within the existing value bins for this variable.
    max_values = []
    min_values = []
    # Variable value dicts is a dictionary holding another dictionary for each individual variable. 
    # Eacht variable dictionary holds for each student as key his statistics as value.
    variable_value_dicts = {}
    variable_value_dicts_comparison = {}
    comparison_student_ids = []
    comparison_student_ids_nohash = []
    # Loop over all variables
    for var_name in var_names:
        all_values = []
        variable_value_dicts[var_name] = {}
        variable_value_dicts_comparison[var_name] = {}

        # Loop over individual student's statistics in the variable statistics
        var_statistic = var_statistics[var_name]
        for indv_student_statistic in var_statistic:
            # Add the student statistics to the dict
            student_id = encrypt_value(indv_student_statistic['student'])
            variable_value_dicts[var_name][student_id] = indv_student_statistic
            
        # Loop over individual student's statistics in the comparison statistics   
        comparison_statistic = comparison_statistics[var_name]
        for indv_student_statistic in comparison_statistic:
            # Add the student statistics to the dict
            student_id = encrypt_value(indv_student_statistic['student'])
            comparison_student_ids_nohash.append(indv_student_statistic['student'])
            comparison_student_ids.append(student_id)
            variable_value_dicts_comparison[var_name][student_id] = indv_student_statistic
            all_values.append(indv_student_statistic['value'])
            
        max_values.append(max(all_values))
        min_values.append(min(all_values))
    comparison_student_ids = list(set(comparison_student_ids))
    comparison_student_ids_nohash = list(set(comparison_student_ids_nohash))
    
    # extract data in matrix form from the value dicts
    X, Y = extract_xy_values(iki_grades.keys(), var_names, variable_value_dicts, iki_grades)  
    if len(X) == 0:
        print 'No training data available'
        return JsonResponse([], safe=False)
    X = normalize(X, axis=0, norm='max')

    # Extract data in matrix form from dicts
    X_comparison, _ = extract_xy_values(comparison_student_ids, var_names, variable_value_dicts_comparison, {}, x_only=True)
    X_comparison, norms =  normalize(X_comparison, axis=0, norm='max', return_norm=True)

    grade_ranges = [(0,6), (6,8), (8,10)]
    segments = []
    for grade_range in grade_ranges:
        temp_seg = [val.identification for val in Student.objects.filter(grade_so_far__range=grade_range)]
        temp_X_seg, _ = extract_xy_values([encrypt_value(val) for val in temp_seg], var_names, variable_value_dicts_comparison, {}, x_only=True)
        temp_X_seg = [normalize_instance(record, norms) for record in temp_X_seg]
        if len(temp_X_seg) > 0:
            segments.append(np.mean(temp_X_seg, axis = 0))
        else:
            segments.append([])

    mean_statistics = np.mean(X_comparison, axis = 0)
    student_statistics = normalize_instance(student_statistics, norms)

    bin_sizes = []
    bin_fns = []
    lower_points_bins = []
    upper_points_bins = []
    # Calculate bins
    print 'max', max_values
    print 'min', min_values
    for i in xrange(len(max_values)):
        num_bins = 10
        bin_sizes.append((max_values[i]-min_values[i])/float(num_bins))
        bin_fns.append(lambda x: round(min_values[i] + x * bin_sizes[-1], 2))
        lower_points_bins.append(map(bin_fns[-1], range(num_bins)))
        upper_points_bins.append(map(bin_fns[-1], range(1, num_bins+1)))


    #####################################################################################

    # Use machine learning to create a predictive model
    Y = np.array(Y).astype(dtype='float')
    # Y_binarized = [y>5.4 for y in Y]
    X = np.array(X).astype(dtype='float')
   
    from sklearn.neighbors import KNeighborsRegressor
    # Deal with low amounts of data
    if len(Y) < 5: 
        regr = KNeighborsRegressor(n_neighbors=1)
    else:
        regr = KNeighborsRegressor()

    # Evaluate the model 
    scores = stratified_cross_val_score(X, Y, regr, rounds = 50)

    # Baseline classifiers says always pass
    baseline_accuracy = (float)(len([x for x in Y if x > 5.4]))/len(Y)
    print 'Performance report:'
    print 'Baseline classifier (fail/pass)', baseline_accuracy
    print 'Mean absolute error', scores['mae']
    print 'Root mean square error', scores['rmse']
    print 'Fail/pass accuracy', scores['fpa']
    print 'Failing students recall:',scores['fsr'], '\n' #,'of', n_failing, 'failing students'

    # Now train again using all instances, this model is used for final prediction
    regr.fit(X, Y)

    # Get the already obtained grades from the activity db
    if student.assignments_completion > 0:
        grade_so_far = student.grade_so_far*student.assignments_completion
    else:
        grade_so_far = 0
        student.assignments_completion = 0
    total_weight = student.assignments_completion
    print total_weight, grade_so_far


    try:
        print 'Student info:'
        print student.identification, iki_grades[encrypt_value(student.identification)], regr.predict([student_statistics])[0]
    except KeyError:
        print student.identification, 'no grade', regr.predict([student_statistics])[0], grade_so_far + (regr.predict([student_statistics])[0]*(float(1)-total_weight))

    # Update predicted grade in database
    if len(student_statistics) > 5:
        student.predicted_grade = regr.predict([student_statistics])[0]
        student.save()

    ######################################################################################
    # In case of a single value a bar plot if given
    if len(max_values) == 1:
        upper_points = upper_points_bins[0]
        lower_points = lower_points_bins[0]
        bin_stats = []
        for index in range(num_bins):
            mean_bin = (float)(upper_points[index]+lower_points[index])/2
            if index == 0:
                assignment_fn = (lambda s: s['value'] <= upper_points[index] and
                        s['value'] >= lower_points[index])
            else:
                assignment_fn = (lambda s: s['value'] <= upper_points[index] and
                        s['value'] > lower_points[index])

            # Check if we found the viewer's bin
            if student_statistics_obj[0] is not None and assignment_fn(student_statistics_obj[0]):
                student_bin = index
            predictions = {}

            # Normalize mean bin following the max method from sklearn
            mean_bin=(float)(mean_bin - min_values[0])/(max_values[0]-min_values[0])
            if grade_so_far:
                predicted_grade = grade_so_far + (regr.predict([[mean_bin]])[0]*(float(1)-total_weight))
            else:
                predicted_grade = student.predicted_grade
            predictions['final_grade'] = {'mean': predicted_grade, 'variance':scores['rmse'][0]}
            predictions['final_grade']['chart'] = 'GSS'
            predictions['final_grade']['label'] = 'Final Grade'
            predictions['final_grade']['axis'] = 'final grade'
            bin_stats.append({
                'id': index,
                'lower': lower_points[index],
                'upper': upper_points[index],
                'count': len(filter(assignment_fn, comparison_statistics.values()[0])),
                'predictions': predictions
            });

        return JsonResponse({
            "student_bin": student_bin,
            "bins": bin_stats,
            "label": variable.label,
            "axis": variable.axis_label or variable.label
        },safe=False)

    ######################################################################################

    # Otherwise a radar diagram
    elif len(max_values) > 1:
        if grade_so_far:
            predicted_grade = grade_so_far + (regr.predict([student_statistics])[0]*(float(1)-total_weight))
        else:
            predicted_grade = student.predicted_grade
        prediction = {}
        prediction['final_grade'] = {'mean': predicted_grade, 'variance':scores['rmse'][0]}
        prediction['final_grade']['chart'] = 'GSS'
        prediction['final_grade']['label'] = 'Final Grade'
        prediction['final_grade']['axis'] = 'final grade'

        return JsonResponse({
            "variable_names": var_labels,
            "student_statistics": list(student_statistics),
            "mean_statistics" : list(mean_statistics),
            "A_statistics" : list(segments[0]),
            "B_statistics" : list(segments[1]),
            "C_statistics" : list(segments[2]),
            "prediction": prediction,
            "label": variable.label,
            "axis": variable.axis_label or variable.label
        },safe=False)





    
