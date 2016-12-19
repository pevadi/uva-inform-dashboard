"""
In helpers.py several functions that are needed to generate the dashboard are
defined. The type of function differs from statistical to encryption...
"""
import sys
from scipy.stats import pearsonr
import numpy as np
import csv
import hashlib
from math import sqrt
from datetime import timedelta

from stats.models import ValueHistory, Variable
from storage.models import Activity
from course.models import Assignment, CourseGroup

from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from sklearn.preprocessing import normalize
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsRegressor

def encrypt_csv(file_name):
    """Encrypts grades to csv"""
    try:
        with open(file_name, mode='r') as infile:
            reader = csv.reader(infile)
            iki_grades_encrypted = [[encrypt_value(rows[0]),
                                        rows[1]] for rows in reader]
        with open("data_2015.csv", "wb") as data_2015:
            writer = csv.writer(data_2015)
            writer.writerows(iki_grades_encrypted)
    except IOError:
        print 'File "'+ file_name + '" not found (encrypt csv)'
        iki_grades_encrypted = []

    return iki_grades_encrypted

def encrypt_value(value):
    """Encrypts value"""
    return hashlib.sha1(value).hexdigest()

def fail_pass_error(y_true, y_pred):
    """Calculates the % of correct fail/pass predictions"""
    result = []
    for x in xrange(len(y_true)):
        res = ((y_true[x] < 5.5) == (y_pred[x] < 5.5))[0]
        result.append(res)
    error = (((float)(sum(result))) / len(result))
    return error

def fail_recall(y_true, y_pred):
    """Calculates the recall of the failing students"""
    result = []
    for x in xrange(len(y_true)):
        if y_true[x] < 5.5:
            res = y_pred[x] < 5.5
            result.append(res)
    try:
        error = (((float)(sum(result))) / len(result))
    except ZeroDivisionError:
        return None, 0
    return error, len(result)

def normalize_instance(instance, norms):
    """Given a norm this function normalizes a single instance"""
    if len(instance) == len(norms):
        return [instance[i]/float(norms[i]) for i in xrange(len(instance))]
    else:
        print "Number of instances should be equal to number of norms."
        return None


def extract_xy_values(student_ids, var_names, variable_value_dicts,
    grades_dict, x_only=False):
    """Given a list of student ids and a dictionary of variable dictionaries of
    students (wauw), this function returns machine learning and visualization
    ready datamatrix and grades vector."""
    Y = []
    X = []
    for student_id in student_ids:
        training_example = []
        # Loop over all variables and add values to training example
        for var_name in var_names:
            # holds student ids as keys and corresponding statictis as value
            variable_value_dict = variable_value_dicts[var_name]
            if student_id in variable_value_dict:
                training_example.append(
                                    variable_value_dict[student_id]['value'])
        if len(training_example) == len(variable_value_dicts):
            if student_id in grades_dict:
                X.append(training_example)
                Y.append(grades_dict[student_id])
            else:
                if x_only:
                    X.append(training_example)
    return X, Y


def stratified_cross_val_score(X, Y, pred, rounds=50, folds=10):
    """This function applies repeated stratified k fold cross validation with
    continious predictions. It takes X, the data to fit, Y the continious
    target, a predictor object (according to the sklearn library has to be
    passed as well. Rounds specifies the number of repeats and folds the
    number of folds used for cross validation. It returns an array with tuples
    of score metrics and correspondiong standard deviation calculated over all
    rounds. Scores include the mean absolute error, root meanm square error,
    the acuracy (according to the values in Y_binarized) and the recall of the
    least common class in Y_binarized."""

    # Check for low amounts of train/test samples
    if len(Y) < 10:
        folds = 2
    print 'Folds:', folds
    print 'N# of training examples:', len(X), len(Y)
    print 'Predictive model used:', pred
    # Repeat the kfold such that stable results can be obtained
    scores = {'mae':[], 'rmse':[], 'fpa': [], 'fsr':[]}
    # y_binarized the binarized target used for the stratification
    y_binarized = [y > 5.4 for y in Y]
    for _ in xrange(0, rounds):
        # K FOLD CROSS VALIDATION
        kfold_scores = {'mae':[], 'rmse':[], 'fpa': [], 'fsr':[]}
        # Stratified 10 fold cross validation
        skf = StratifiedKFold(n_splits=folds, random_state=None, shuffle=True)
        for train_index, test_index in skf.split(X, y_binarized):
            x_train, x_test = X[train_index], X[test_index]
            y_train, y_test = Y[train_index], Y[test_index]
            y_pred = []
            pred.fit(x_train, y_train)
            for x in xrange(len(y_test)):
                y_pred.append(pred.predict([x_test[x]]))
            y_pred = np.array(y_pred)
            kfold_scores['mae'].append(mean_absolute_error(y_test, y_pred))
            kfold_scores['rmse'].append(sqrt(mean_squared_error(y_test,
                y_pred)))
            kfold_scores['fpa'].append(fail_pass_error(y_test, y_pred))
            fsr_val, fsr_count = fail_recall(y_test, y_pred)
            # This if statement was necessary due to the small amount of data
            if fsr_count > 0:
                kfold_scores['fsr'].append(fsr_val)

        for name in scores.keys():
            score = kfold_scores[name]
            if score:
                scores[name].append(sum(score)/len(score))

    for name in scores.keys():
        score = scores[name]
        if score:
            scores[name] = (sum(score)/len(score), np.std(score))
        else:
            scores[name] = None
    return scores

def evaluate_variables(request=None, debug_out=None):
    """This function evaluates the predictive value of all the already stored
    variables in the ValueHistory in terms of correlation with the course final
    outcomes."""
    np.set_printoptions(threshold=sys.maxint)

    # Retrieve all existing variable keys and groups
    group = 3
    variable_keys = ValueHistory.objects.filter(group=group)\
        .order_by('variable').values('variable').distinct()
    print variable_keys
    variables = []
    for x in xrange(len(variable_keys)):
        variables.append(get_object_or_404(Variable,
            pk=variable_keys[x]['variable']))

    print 'var keys', variable_keys, variables

    student_ids = ValueHistory.objects.filter(group=group)\
        .order_by('student').values('student').distinct()
    # initialize data matrix
    data_matrix = [['variable / student_id'] + [d['student']\
        for d in student_ids]]
    # Loop over all variables
    for variable in variables:
        data_matrix[0] = ['variable / student_id']
        print 'var', variable
        variable_name = variable.name
        final_grades = ['final_grades']

        data_matrix.append([variable_name])
        # First get all timestamps and grades
        for student_id in student_ids:
            value_history = ValueHistory.objects.filter(variable=variable,
                student=student_id['student'], group=group)
            # Get the already obtained grades from the activity db
            assignments = Assignment.objects.all()
            total_weight = float(0)
            grade_so_far = 0
            for assignment in assignments:
                # Get highest grade assigned (in order to filter out zero
                # values and older grades. Assumes the highest grade is the
                # latest.)
                try:
                    assignment_activity = Activity.objects\
                        .filter(user=student_id['student'],
                            activity=assignment.url).latest('value')
                    if assignment_activity.value > 0:
                        total_weight += assignment.weight
                        grade_so_far += ((assignment_activity.value /
                            assignment.max_grade * 10) * assignment.weight)
                except ObjectDoesNotExist:
                    continue
            if total_weight > 0:
                data_matrix[0].append(student_id)
                final_grades.append(grade_so_far/total_weight)
                if value_history:
                    stats = variable.calculate_statistics_from_values(
                        value_history)
                    data_matrix[-1].append(stats[0]['value'])
                    # print student_id['student'], total_weight, grade_so_far,
                    #     grade_so_far/total_weight, stats[0]['value']
                else:
                    data_matrix[-1].append(None)

        print data_matrix
        print len(data_matrix[-1])


    # Calculate correlation between current variable-updatemoment and final
    # grade outcome. Check if any grades available.
    if len(list(set(final_grades[1:]))) > 1:
        for x in xrange(1, len(data_matrix)):
            # Due to the missing values np.ma.corrcoef is to be used.
            # This required some preposcessing of the arrays
            final_grades_masked = np.ma.array(np.array(final_grades[1:],
                    dtype=np.float),
                    mask=np.isnan(np.array(final_grades[1:],
                    dtype=np.float)))
            data_masked = np.ma.array(np.array(data_matrix[x][1:],
                    dtype=np.float),
                    mask=np.isnan(np.array(data_matrix[x][1:],
                    dtype=np.float)))
            data_matrix[x].append(np.ma.corrcoef(final_grades_masked,
                data_masked)[0][1])
            data_matrix[x].append(np.var(data_masked))


    # Finally add the grades
    data_matrix.append(final_grades)

    # Add some clearifying column titles
    data_matrix[0].append('Correlation')
    data_matrix[0].append('Variance')

    csv_ready_data_matrix = map(str, data_matrix)

    np.savetxt(str(group)+"_data_matrix.csv", csv_ready_data_matrix,
        delimiter=",", fmt='%s')



def evaluate_activities(request=None, debug_out=None):
    """This function is designed to detect new variables that can be extracted
    from the already stored activities in order to determine what types of
    variables should be added to new episodes of the course."""
    ignored_users = ['mlatour1', 'natasa5', 'nzupanc1']
    np.set_printoptions(threshold=sys.maxint)

    result_matrix = [['Verb', 'object', 'Correlation', 'p-value',
                    'n', 'Variance']]
    # result_matrix_by_week = [['Verb','object', 'before','week 1', 'week 2',
    # 'week 3', 'week 4', 'week 5', 'week 6', 'week 7', 'week 8', 'all time']]

    # 2014
    # episode = '2016'
    # group = "{'group': 3}"
    # Cummalative
    # time_ranges = ([["2014-10-01", "2014-10-27"],["2014-10-01",
    # "2014-11-03"],["2014-10-01", "2014-11-10"], ["2014-10-01",
    # "2014-11-17"],["2014-10-01", "2014-11-24"],["2014-10-01",
    # "2014-12-01"],["2014-10-01", "2014-12-08"],["2014-10-01",
    # "2014-12-15"],["2014-10-01", "2014-12-22"]])
    # Per week
    # time_ranges = [["2014-10-01", "2014-10-27"],["2014-10-27",
    # "2014-11-03"],["2014-11-03", "2014-11-10"], ["2014-11-10",
    # "2014-11-17"],["2014-11-17", "2014-11-24"],["2014-11-24",
    # "2014-12-01"],["2014-12-01", "2014-12-08"],["2014-12-08",
    # "2014-12-15"],["2014-12-15", "2014-12-22"]]

    # 2015
    episode = '2015'
    group = "{'group': 3}"
    # Cummalative
    time_ranges = [["2015-10-01", "2015-10-26"], ["2015-10-01", "2015-11-02"],
        ["2015-10-01", "2015-11-09"], ["2015-10-01", "2015-11-16"],
        ["2015-10-01", "2015-11-23"], ["2015-10-01", "2015-11-30"],
        ["2015-10-01", "2015-12-07"], ["2015-10-01", "2015-12-14"],
        ["2015-10-01", "2015-12-21"]]
    # Per week
    # time_ranges = [["2015-10-01", "2015-10-26"],["2015-10-26",
    # "2015-11-02"],["2015-11-02", "2015-11-09"], ["2015-11-09",
    # "2015-11-16"],["2015-11-16", "2015-11-23"],["2015-11-23",
    # "2015-11-30"],["2015-11-30", "2015-12-07"],["2015-12-07",
    # "2015-12-14"],["2015-12-14", "2015-12-21"]]

    # time_range = time_ranges[-1]

    # For each episode try to retrieve the final grades from an external file
    try:
        with open('../../iki_grades_'+str(group)+'.csv', mode='r') as infile:
            reader = csv.reader(infile)
            iki_grades = {rows[0]:rows[1] for rows in reader}
    except IOError:
        print 'File "'+ 'iki_grades_'+str(group)+'.csv'+ '" not found'
        iki_grades = {}

    # Loop over time ranges
    for time_range in time_ranges:
        print 'Evaluating time range ', time_range
        # Retrieve all possible verb/object combinations within a particular
        # episode of the course
        verb_obj_combinations = Activity.objects.filter(
            time__year=episode, time__range=time_range)\
                .order_by('verb', 'type').values('verb', 'type').distinct()

        # Loop over all verb/object combinations
        for possible_variable in verb_obj_combinations:
            print '\nTesting', possible_variable

            student_ids = [d['user'] for d in Activity.objects.filter(
                time__year=episode,
                time__range=time_range,
                verb=possible_variable['verb'],
                type=possible_variable['type']).order_by('user')\
                    .values('user').distinct()]
            data_vector = []
            final_grades = []
            # Loop over all students that were active during this episode and
            # have relevant data available
            for student_id in student_ids:
                if student_id not in ignored_users:
                    relevant_activities = Activity.objects.filter(
                        time__year=episode,
                        time__range=time_range,
                        user=student_id,
                        verb=possible_variable['verb'],
                        type=possible_variable['type'])
                    # data_vector.append(len(relevant_activities))

                    # Add final grades from external file (if present)
                    try:
                        final_grades.append(iki_grades[student_id])
                        data_vector.append(len(relevant_activities))
                    except KeyError:
                        pass
                        # final_grades.append(None)

            # Determine correlation of n# activity occurences and the final
            # grade. Due to the missing values np.ma.corrcoef is to be used.
            # This required some preprocessing of the arrays
            final_grades = np.ma.array(np.array(final_grades, dtype=np.float),
                mask=np.isnan(np.array(final_grades, dtype=np.float)))
            data_vector = np.ma.array(np.array(data_vector, dtype=np.float),
                mask=np.isnan(np.array(data_vector, dtype=np.float)))
            # print 'Correlation', np.ma.corrcoef(a,b)[0][1]
            # print 'Correlation', pearsonr(a,b)[0],
            #   'P-value (significance)', pearsonr(a,b)[1]
            # print 'Variance', np.var(b)
            # print a
            # print b
            print len(final_grades), len(data_vector)
            result_matrix.append([possible_variable['verb'],
                    possible_variable['type'],
                    pearsonr(final_grades, data_vector)[0],
                    pearsonr(final_grades, data_vector)[1],
                    len(final_grades), np.var(data_vector)])
            # result_matrix.append([possible_variable['verb'],
            # possible_variable['type'], np.ma.corrcoef(a,b)[0][1], np.var(b)])
        result_matrix.append([])
    # Save to csv
    csv_ready_matrix = map(str, result_matrix)
    np.savetxt(episode+"_correlation_analysis_perweek.csv",
        csv_ready_matrix, delimiter=",", fmt='%s')

def evaluate_predictive_model(request=None, debug_out=None):
    """Evaluates a predictive models quality on last years data"""
    result_matrix = [['course date time', 'sample size', 'mean absolute error',
        'variance', 'root mean square error', 'variance', 'fail/pass accuracy',
        'variance', 'at-risk recall', 'variance', 'baseline', 'variables']]
    # Get the variables
    variables = Variable.objects.filter(type='IN').exclude(
        label='Access Application Count').exclude(
        label='Interact Application Count')
    # var_names = variables.values_list("name", flat=True)
    # print var_names
    # Set group
    group = CourseGroup.objects.get(label='Year 2015 - 2016')

    # Get the y values a.k.a. grades needed for machine learning
    try:
        with open("/home/pepijn/data_2015.csv", mode='r') as infile:
            reader = csv.reader(infile)
            iki_grades = {rows[0]:rows[1] for rows in reader}
    except IOError, error:
        print error
        iki_grades = {}

    # Set measurement points
    course_datetimes = []
    for x in xrange(6, 60):
        course_datetimes.append(timedelta(x))
    # course_datetimes = [timedelta(7), timedelta(14), timedelta(21),
    # timedelta(28), timedelta(35), timedelta(42), timedelta(49),
    # timedelta(56), timedelta(63)]
    for course_datetime in course_datetimes:
        result_record = []
        result_record.append(course_datetime)
        print 'Course datetime', course_datetime

        # Collect relevant value statistics for model building. Y 2015-2016
        # (pk=2) was selected for this purpose
        var_statistics = {}
        print 'Variables:'
        for variable in variables:
            value_history_1516 = ValueHistory.objects.filter(
                variable=variable.pk,
                group=group,
                course_datetime__lte=course_datetime)
            if len(value_history_1516) == 0:
                print ("Valuehistory used for model building not found. Check"
                    "if variables are correctly stored to valuehistory for the"
                    "following variable:", variable)
            else:
                print '\t', variable, course_datetime
                var_statistics[variable.name] = variable\
                    .calculate_statistics_from_values(value_history_1516)


        # Variable value dicts is a dictionary holding another dictionary for
        # each individual variable. Eacht variable dictionary holds for each
        # student as key his statistics as value.
        variable_value_dicts = {}
        # Loop over all variables
        for var_name in var_statistics.keys():
            variable_value_dicts[var_name] = {}

            # Loop over individual statistics in the variable statistics
            var_statistic = var_statistics[var_name]
            for indv_student_statistic in var_statistic:
                # Add the student statistics to the dict
                student_id = encrypt_value(indv_student_statistic['student'])
                variable_value_dicts[var_name][student_id] = \
                    indv_student_statistic

        # extract data in matrix form from the value dicts
        X, Y = extract_xy_values(iki_grades.keys(), var_statistics.keys(),
            variable_value_dicts, iki_grades)
        if len(X) == 0:
            print 'No training data available'
            return JsonResponse([], safe=False)
        X = normalize(X, axis=0, norm='max')
        print len(X), len(Y)

        result_record.append(len(Y))

        # Use machine learning to create a predictive model
        Y = np.array(Y).astype(dtype='float')
        X = np.array(X).astype(dtype='float')

        # Deal with low amounts of data
        if len(Y) < 10:
            regr = KNeighborsRegressor(n_neighbors=1)
        else:
            regr = KNeighborsRegressor()

        # Evaluate the model
        scores = stratified_cross_val_score(X, Y, regr, rounds=50)
        # Do not use score.keys(), order is important for csv
        score_keys = ['mae', 'rmse', 'fpa', 'fsr']
        for name in score_keys:
            result_record.append(scores[name][0])
            result_record.append(scores[name][1])

        # (mean_abs_error, root_mean_square_error, fail_pass_accuracy,
        #     failing_students_recall) = stratified_cross_val_score(X, Y, regr,
        #         rounds=50)
        # result_record.append(mean_abs_error[0])
        # result_record.append(mean_abs_error[1])
        # result_record.append(root_mean_square_error[0])
        # result_record.append(root_mean_square_error[1])
        # result_record.append(fail_pass_accuracy[0])
        # result_record.append(fail_pass_accuracy[1])
        # result_record.append(failing_students_recall[0])
        # result_record.append(failing_students_recall[1])

        # Baseline classifiers says always pass
        baseline_accuracy = (float)(len([x for x in Y if x > 5.4]))/len(Y)
        result_record.append(baseline_accuracy)
        print 'Performance report:'
        print 'Baseline classifier (fail/pass)', baseline_accuracy
        print 'Mean absolute error', scores['mae']
        print 'Root mean square error', scores['rmse']
        print 'Fail/pass accuracy', scores['fpa']
        print 'Failing students recall:', scores['fsr'], '\n'
        result_record.append(len(var_statistics.keys()))
        print len(result_record)
        result_matrix.append(map(str, result_record))

    result_matrix = np.array(result_matrix)
    csv_name = '../../predictor_analysis/KNN_60.csv'
    np.savetxt(csv_name, result_matrix, delimiter=',', fmt='%s')
