from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest,\
        HttpResponseNotAllowed
from django.utils import timezone

from .helpers import *
from .models import Variable, ValueHistory
from course.models import CourseGroup, Student
from identity import identity_required

from datetime import date, timedelta

# This function evaluates the predictive value of all the already stored variables in the
# ValueHistory in terms of correlation with the course final outcomes. 
def evaluate_variables(request=None, debug_out=None):
    import numpy as np
    import csv
    import sys
    np.set_printoptions(threshold=sys.maxint)
    from storage.models import Activity
    from course.models import Assignment
    from django.core.exceptions import ObjectDoesNotExist

    # Retrieve all existing variable keys and groups
    group = 3
    variable_keys =  ValueHistory.objects.filter(group=group).order_by('variable').values('variable').distinct()
    print variable_keys
    variables = []
    for x in xrange(len(variable_keys)):
        variables.append(get_object_or_404(Variable, pk=variable_keys[x]['variable']))

    print 'var keys', variable_keys, variables

    # For each group try to retrieve the final grades from an external file
    try:
        with open('iki_grades_'+str(group)+'.csv', mode='r') as infile:
            reader = csv.reader(infile)
            iki_grades = {rows[0]:rows[1] for rows in reader}
    except IOError:
        iki_grades = {}       

    student_ids =  ValueHistory.objects.filter(group=group).order_by('student').values('student').distinct()
    # initialize data matrix
    data_matrix = [['variable / student_id']+[d['student'] for d in student_ids]]
    # Loop over all variables
    for variable in variables:
        data_matrix[0] = ['variable / student_id']
        print 'var', variable
        variable_name = variable.name
        final_grades = ['final_grades']

        data_matrix.append([variable_name])
        # First get all timestamps and grades
        for student_id in student_ids:
            value_history = ValueHistory.objects.filter(variable=variable, student=student_id['student'], group=group)
            # Get the already obtained grades from the activity db
            assignments = Assignment.objects.all()
            total_weight = float(0)
            grade_so_far = 0    
            for assignment in assignments:
                # Get highest grade assigned (in order to filter out zero values and older grades. Assumes the highest grade is the latest.)
                try:
                    assignment_activity =  Activity.objects.filter(user=student_id['student'], activity=assignment.url).latest('value')
                    if assignment_activity.value > 0:
                        total_weight += assignment.weight
                        grade_so_far += ((assignment_activity.value / assignment.max_grade * 10) * assignment.weight)
                except ObjectDoesNotExist:
                    continue
            if total_weight > 0:
                data_matrix[0].append(student_id)
                final_grades.append(grade_so_far/total_weight)
                if value_history:
                    stats = variable.calculate_statistics_from_values(value_history)
                    data_matrix[-1].append(stats[0]['value'])
                    print student_id['student'], total_weight, grade_so_far, grade_so_far/total_weight, stats[0]['value']  
                else:
                    data_matrix[-1].append(None)

        print data_matrix
        print len(data_matrix[-1])

    
    # Calculate correlation between current variable-updatemoment and final grade outcome
    # Check if any grades available
    if len(list(set(final_grades[1:]))) > 1:
        for x in xrange(1,len(data_matrix)):
            # Due to the missing values np.ma.corrcoef is to be used. This required some preposcessing of the arrays
            a = np.ma.array(np.array(final_grades[1:], dtype=np.float), mask=np.isnan(np.array(final_grades[1:], dtype=np.float)))
            b = np.ma.array(np.array(data_matrix[x][1:], dtype=np.float), mask=np.isnan(np.array(data_matrix[x][1:], dtype=np.float)))
            data_matrix[x].append(np.ma.corrcoef(a,b)[0][1])
            data_matrix[x].append(np.var(b))


    # Finally add the grades
    data_matrix.append(final_grades)

    # Add some clearifying column titles
    data_matrix[0].append('Correlation')
    data_matrix[0].append('Variance')
    
    csv_ready_data_matrix =  map(str,data_matrix)

    np.savetxt(str(group)+"_data_matrix.csv", csv_ready_data_matrix, delimiter=",", fmt='%s')


# This function is designed to detect new variables that can be extracted from the already stored activities in 
# order to determine what types of variables should be added to new episodes of the course.
def evaluate_activities(request=None, debug_out=None):
    ignored_users = ['mlatour1', 'natasa5', 'nzupanc1']
    import numpy as np
    import csv
    import sys
    from storage.models import Activity
    np.set_printoptions(threshold=sys.maxint)

    result_matrix = [['Verb','object', 'Correlation', 'Variance']]
    # result_matrix_by_week = [['Verb','object', 'before','week 1', 'week 2', 'week 3', 'week 4', 'week 5', 'week 6', 'week 7', 'week 8', 'all time']]

    # 2014
    episode = '2016'
    group = "{'group': 3}"
    # Cummalative
    # time_ranges = [["2014-10-01", "2014-10-27"],["2014-10-01", "2014-11-03"],["2014-10-01", "2014-11-10"], ["2014-10-01", "2014-11-17"],["2014-10-01", "2014-11-24"],["2014-10-01", "2014-12-01"],["2014-10-01", "2014-12-08"],["2014-10-01", "2014-12-15"],["2014-10-01", "2014-12-22"]]
    # Per week
    time_ranges = [["2014-10-01", "2014-10-27"],["2014-10-27", "2014-11-03"],["2014-11-03", "2014-11-10"], ["2014-11-10", "2014-11-17"],["2014-11-17", "2014-11-24"],["2014-11-24", "2014-12-01"],["2014-12-01", "2014-12-08"],["2014-12-08", "2014-12-15"],["2014-12-15", "2014-12-22"]]

    # 2015
    # episode = '2015'
    # group = "{'group': 3}"
    # Cummalative
    # time_ranges = [["2015-10-01", "2015-10-26"],["2015-10-01", "2015-11-02"],["2015-10-01", "2015-11-09"], ["2015-10-01", "2015-11-16"],["2015-10-01", "2015-11-23"],["2015-10-01", "2015-11-30"],["2015-10-01", "2015-12-07"],["2015-10-01", "2015-12-14"],["2015-10-01", "2015-12-21"]]
    # Per week
    # time_ranges = [["2015-10-01", "2015-10-26"],["2015-10-26", "2015-11-02"],["2015-11-02", "2015-11-09"], ["2015-11-09", "2015-11-16"],["2015-11-16", "2015-11-23"],["2015-11-23", "2015-11-30"],["2015-11-30", "2015-12-07"],["2015-12-07", "2015-12-14"],["2015-12-14", "2015-12-21"]]

    # time_range = time_ranges[-1]

    # For each episode try to retrieve the final grades from an external file
    try:
        with open('iki_grades_'+str(group)+'.csv', mode='r') as infile:
            reader = csv.reader(infile)
            iki_grades = {rows[0]:rows[1] for rows in reader}
    except IOError:
        print 'File "'+ 'iki_grades_'+str(group)+'.csv'+ '" not found'
        iki_grades = {}

    # Loop over time ranges
    for time_range in time_ranges:
        print 'Evaluating time range ', time_range
        # Retrieve all possible verb/object combinations within a particular episode of the course
        verb_obj_combinations = Activity.objects.filter(time__year=episode, time__range=time_range).order_by('verb', 'type').values('verb', 'type').distinct()

        # Loop over all verb/object combinations 
        for possible_variable in verb_obj_combinations:
            print '\nTesting', possible_variable

            student_ids =[d['user'] for d in Activity.objects.filter(time__year=episode, time__range=time_range, verb=possible_variable['verb'], type=possible_variable['type']).order_by('user').values('user').distinct()]
            data_vector = []
            final_grades = []
            # Loop over all students that were active during this episode and have relevant data available
            for student_id in student_ids:
                if student_id not in ignored_users:
                    relevant_activities = Activity.objects.filter(time__year=episode, time__range=time_range, user=student_id, verb=possible_variable['verb'], type=possible_variable['type'])
                    data_vector.append(len(relevant_activities))

                    # Add final grades from external file (if present)
                    try:
                        final_grades.append(iki_grades[student_id])
                    except KeyError:
                        final_grades.append(None)

            # Determine correlation of n# activity occurences and the final grade
            # Due to the missing values np.ma.corrcoef is to be used. This required some preprocessing of the arrays
            a = np.ma.array(np.array(final_grades, dtype=np.float), mask=np.isnan(np.array(final_grades, dtype=np.float)))
            b = np.ma.array(np.array(data_vector, dtype=np.float), mask=np.isnan(np.array(data_vector, dtype=np.float)))
            print 'Correlation', np.ma.corrcoef(a,b)[0][1]
            print 'Variance', np.var(b)
            result_matrix.append([possible_variable['verb'], possible_variable['type'], np.ma.corrcoef(a,b)[0][1], np.var(b)])

    # Save to csv
    csv_ready_matrix =  map(str,result_matrix)
    np.savetxt(episode+"_correlation_analysis_perweek.csv", csv_ready_matrix, delimiter=",", fmt='%s')


def encrypt_csv(file_name):
    import csv
    try:
        with open(file_name, mode='r') as infile:
            reader = csv.reader(infile)
            iki_grades_encrypted = [[encrypt_value(rows[0]), rows[1]] for rows in reader]
            # iki_grades_encrypted = [[rows[0], rows[1]] for rows in reader]
        with open("data_2015.csv", "wb") as f:
            writer = csv.writer(f)
            writer.writerows(iki_grades_encrypted)
    except IOError:
        print 'File "'+ file_name + '" not found (encrypt csv)'
        iki_grades_encrypted = []

    return iki_grades_encrypted

def encrypt_value(value):
    import hashlib
    return hashlib.sha1(value).hexdigest()

# This function takes two lists as input. Both lists contain values including
# None values. It creates a new list containing less None values by merging the lists.
# It assumes l2 to be the most relevant and therefore when both lists have a value at
# a particular position the l2 value is used.
def merge_incomplete_lists(l1, l2):
    n = len(l1)
    merged_list = []
    for x in xrange(n):
        if l1[x] is None and l2[x] is None:
            merged_list.append(None)
        elif l1[x] is not None and l2[x] is not None:
            merged_list.append(l2[x])
        elif l1[x] is not None and l2[x] is None:
            merged_list.append(l1[x])
        elif l1[x] is None and l2[x] is not None:
            merged_list.append(l2[x])
    return merged_list


def fail_pass_error(Y_true, Y_pred):
    result = []
    for x in xrange(len(Y_true)):
        res = ((Y_true[x]<5.5) == (Y_pred[x]<5.5))[0]
        result.append(res)
    error =  (((float)(sum(result)))/len(result))
    return error

def fail_recall(Y_true, Y_pred):
    result = []
    for x in xrange(len(Y_true)):
        if Y_true[x]<5.5:
            # print Y_true[x], Y_pred[x]
            res = Y_pred[x]<5.5
            result.append(res)
    try:   
        error =  (((float)(sum(result)))/len(result))
    except ZeroDivisionError:
        # print Y_true
        return None, 0
    return error, len(result)

def normalize_instance(instance, norms):
    if len(instance) == len(norms):
        return [instance[i]/float(norms[i]) for i in xrange(len(instance))]
    else:
        print "Number of instances should be equal to number of norms."
        return None

def get_grade_so_far(student_id):
    from storage.models import Activity
    from course.models import Assignment
    from django.core.exceptions import ObjectDoesNotExist 

    # Get the already obtained grades from the activity db
    assignments = Assignment.objects.all()
    total_weight = float(0)
    grade_so_far = 0    
    for assignment in assignments:
        # Get highest grade assigned (in order to filter out zero values and older grades. Assumes the highest grade is the latest.
        try:
            assignment_activity =  Activity.objects.filter(user=student_id, activity=assignment.url).latest('value')
            if assignment_activity.value != None:
                total_weight += assignment.weight
                grade_so_far += ((assignment_activity.value / assignment.max_grade * 10) * assignment.weight)
        except ObjectDoesNotExist:
            continue
    if total_weight > 0:
        return total_weight, grade_so_far
    else:
        return 0,None

# # Returns all student ids within a given grade range based on actual grades
# def get_student_ids_by_grade_range(min_grade, max_grade, student_ids):
#     student_ids_within_range = []
#     for student_id in student_ids:
#         total_weight, grade_so_far = get_grade_so_far(student_id)
#         if total_weight > 0:
#             if grade_so_far/total_weight >= min_grade and grade_so_far/total_weight <= max_grade:
#                 student_ids_within_range.append(student_id)
#     return student_ids_within_range

# Given a list of student ids and a dictionary of variable dictionaries of students (wauw), this
# function returns machine learning and visualization ready datamatrix and grades vector.
def extract_xy_values(student_ids, var_names, variable_value_dicts, grades_dict, x_only=False):
    Y = []
    X = []
    for student_id in student_ids:
        X_training_example = []
        # Loop over all variables and add values to training example
        for var_name in var_names:
            # varibale value dict holds student ids as keys and corrsponding statictis as value
            variable_value_dict = variable_value_dicts[var_name]
            if student_id in variable_value_dict:
                X_training_example.append(variable_value_dict[student_id]['value'])
        if len(X_training_example) == len(variable_value_dicts):
            if student_id in grades_dict:
                X.append(X_training_example)
                Y.append(grades_dict[student_id])
            else:
                if x_only:
                    X.append(X_training_example)
    return X, Y

# This function applies repeated stratified k fold cross validation with continious predictions
# It takes X, the data to fit, Y the continious target and Y_binarized the binarized target used
# for the stratification. A predictor object (according to the sklearn library has to be passed
# as well. Rounds represents the number of repeats and folds the number of folds for cross
# validation. It returns an array with tuples of score metrics and correspondiong variance. Scores
# include the mean absolute error, root mean square error, the acuracy (according to the values
# in Y_binarized) and the recall of the least common class in Y_binarized. 
def stratified_cross_val_score(X, Y, pred, Y_binarized, rounds=50, folds=10):
    from sklearn.model_selection import StratifiedKFold
    import numpy as np
    from math import sqrt
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    # Check for low amounts of train/test samples
    if len(Y) < 10: folds = 2
    print 'Folds:', folds
    print 'N# of training examples:', len(X), len(Y)
    print 'Predictive model used:', pred
    # Repeat the kfold such that stable results can be obtained (needed for model evaluation)
    mae = []
    rmse = []
    fpa = []
    fsr = []
    for rep in xrange(0, rounds):
        # K FOLD CROSS VALIDATION
        mae_kfold = []
        rmse_kfold = []
        fpa_kfold = []
        fsr_kfold = []
        # Stratification 10 fold cross validation
        skf = StratifiedKFold(n_splits=folds, random_state=None, shuffle=True)
        for train_index, test_index in skf.split(X, Y_binarized):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = Y[train_index], Y[test_index]
            n_test_samples = len(y_test) 
            # print 'percentage fail in train', (float)(len([x for x in y_train if x < 5.5]))/len(y_train)
            # print 'percentage fail in test', (float)(len([x for x in y_test if x < 5.5]))/len(y_test)
            y_pred = []
            # regr = linear_model.BayesianRidge()
            pred.fit(X_train, y_train)
            for x in xrange(len(y_test)):
                y_pred.append(pred.predict([X_test[x]]))
            mae_kfold.append(mean_absolute_error(y_test, np.array(y_pred)))    
            rmse_kfold.append(sqrt(mean_squared_error(y_test, np.array(y_pred))))
            fpa_kfold.append(fail_pass_error(y_test, y_pred))
            fsr_val, fsr_count = fail_recall(y_test, y_pred)
            # This if statement was necessary due to the small amount of data available at the moment
            if fsr_count > 0:
                fsr_kfold.append(fsr_val)
        mae.append(sum(mae_kfold)/len(mae_kfold))
        rmse.append(sum(rmse_kfold)/len(rmse_kfold))
        fpa.append(sum(fpa_kfold)/len(fpa_kfold))
        if fsr_kfold:
            fsr.append(sum(fsr_kfold)/len(fsr_kfold))
    mean_abs_error = (sum(mae)/len(mae), np.var(mae)) 
    root_mean_square_error = (sum(rmse)/len(rmse), np.var(rmse))
    fail_pass_accuracy = (sum(fpa)/len(fpa), np.var(fpa))
    if fsr:
        failing_students_recall = (sum(fsr)/len(fsr), np.var(fsr))
    else:
        failing_students_recall = None
    return mean_abs_error, root_mean_square_error, fail_pass_accuracy, failing_students_recall



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
    # from storage.models import Activity
    # from course.models import Assignment
    # from django.core.exceptions import ObjectDoesNotExist

    """Returns the most recent values of a variable.
    
    Parameters:
        variable_name   -   The variable for which to lookup the values.
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


    # Collect relevant value statistics for model building. Y 2015-2016 (pk=2) was selected for this purpose
    var_statistics = {}
    print 'Variables:'
    for variable in variables:
        print '\t', variable, course_datetime_now
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

    grade_ranges = [(0,4), (6,7.5), (8.5,10)]
    segments = []
    for grade_range in grade_ranges:
        temp_seg = [val.identification for val in Student.objects.filter(grade_so_far__range=grade_range)]
        temp_X_seg, _ = extract_xy_values([encrypt_value(val) for val in temp_seg], var_names, variable_value_dicts_comparison, {}, x_only=True)
        temp_X_seg = [normalize_instance(record, norms) for record in temp_X_seg]
        segments.append(np.mean(temp_X_seg, axis = 0))


    print segments

    mean_statistics = np.mean(X_comparison, axis = 0)
    # mean_statistics = np.mean(X_comparison_segB, axis = 0)
    # seg_A_statistics = np.mean(X_comparison_segA, axis = 0)
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
    Y_binarized = [y>5.4 for y in Y]
    X = np.array(X).astype(dtype='float')
   
    from sklearn.neighbors import KNeighborsRegressor
    # Deal with low amounts of data
    if len(Y) < 5: 
        regr = KNeighborsRegressor(n_neighbors=1)
    else:
        regr = KNeighborsRegressor()

    # Evaluate the model 
    mean_abs_error, root_mean_square_error, fail_pass_accuracy, failing_students_recall = stratified_cross_val_score(X, Y, regr, Y_binarized, rounds = 10)

    # Baseline classifiers says always pass
    baseline_accuracy = (float)(len([x for x in Y if x > 5.4]))/len(Y)
    print 'Performance report:'
    print 'Baseline classifier (fail/pass)', baseline_accuracy
    print 'Mean absolute error', mean_abs_error
    print 'Root mean square error', root_mean_square_error
    print 'Fail/pass accuracy', fail_pass_accuracy
    print 'Failing students recall:',failing_students_recall, '\n' #,'of', n_failing, 'failing students'

    # Now train again using all instances, this model is used for final prediction
    regr.fit(X, Y)

    # Get the already obtained grades from the activity db
    total_weight, grade_so_far = get_grade_so_far(student.identification)
    # assignments = Assignment.objects.all()
    # total_weight = float(0)
    # grade_so_far = 0    
    # for assignment in assignments:
    #     # Get highest grade assigned (in order to filter out zero values and older grades. Assumes the highest grade is the latest.)
    #     try:
    #         assignment_activity =  Activity.objects.filter(user=student.identification, activity=assignment.url).latest('value')
    #         print assignment, assignment_activity.value, assignment.max_grade, assignment.weight
    #         if assignment_activity.value != None:
    #             total_weight += assignment.weight
    #             grade_so_far += ((assignment_activity.value / assignment.max_grade * 10) * assignment.weight)
    #     except ObjectDoesNotExist:
    #         continue
    print total_weight, grade_so_far

#grades_so_far = []
    #print 'grades heritant'
    #for tm in set(grades_so_far):
     #   print tm

    try:
        print 'Student info:'
        print student.identification, iki_grades[encrypt_value(student.identification)], regr.predict([student_statistics])[0]
    except KeyError:
        print student.identification, 'no grade', regr.predict([student_statistics])[0], grade_so_far + (regr.predict([student_statistics])[0]*(float(1)-total_weight))


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
            predicted_grade = grade_so_far + (regr.predict([[mean_bin]])[0]*(float(1)-total_weight))
            print 'met so far', predicted_grade
            predictions['final_grade'] = {'mean': predicted_grade, 'variance':root_mean_square_error[0]}
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
        predicted_grade = grade_so_far + (regr.predict([student_statistics])[0]*(float(1)-total_weight))
        prediction = {}
        prediction['final_grade'] = {'mean': predicted_grade, 'variance':root_mean_square_error[0]}
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





    
