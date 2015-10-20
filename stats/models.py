"""Database models used in the prediction app."""
from django.db import models
from course.models import Student, CourseGroup

import math

class Variable(models.Model):
    """Model containing information on variables used in predictions."""
    VARIABLE_TYPES = (('IN', "Input variable"), ('OUT', "Output variable"))

    name = models.CharField(max_length=100, primary_key=True, blank=True)
    label = models.CharField(max_length=255, blank=True)
    course = models.ForeignKey('course.Course')
    num_bins = models.PositiveSmallIntegerField(default=10, blank=True)
    last_consumed_activity_pk = models.PositiveIntegerField(
        default=0, blank=True)
    type = models.CharField(choices=VARIABLE_TYPES, default='IN', max_length=3)

    def update_from_storage(self):
        """Updates the appropriate stats models based on storage date.

        Based on new storage.models.Activity instances new observed values for
        this variable are calculated. These values are added as ValueHistory
        and Statistic instances. ValueBin instances linked to this variable are
        updated and if necessary redefined.

        The calculation of variable values based on storage data is delegated
        to the `calculate_values_from_activities` function of subclasses. This
        calculation function returns the extracted values as well as the latest
        Activity instance that was used in the calculation. The storage data
        provided is any Activity instance that has been stored after the latest
        consumed Activity instances for this variable.
        """
        # Retrieve new activity instances for this variable.
        from storage.models import Activity
        activities = Activity.objects.filter(
            course=self.course.url,
            pk__gt=self.last_consumed_activity_pk)
        # Return new ValueHistory instances and the last consumed Activity
        # instance based on the new activities.
        value_history, last_consumed = self.calculate_values_from_activities(
            activities)
        # If no activity was consumed, stop.
        if last_consumed is None:
            return

        for value_history_item in value_history:
            # Determine the attached student
            student_id = value_history_item.student
            _student, _created = Student.objects.get_or_create(
                identification=student_id, defaults={"label": student_id})
            # Determine the attached course groups. Technically someone could
            #  be in multiple groups in one course.
            groups = CourseGroup.get_groups_by_date(
                value_history_item.datetime.date(),
                course=self.course)
            for group in groups:
                value_history_item.group = group
        # Update the database by adding the new ValueHistory instances
        ValueHistory.objects.bulk_create(value_history)

        # Calculate new statistic values based on value history.
        statistics = self.calculate_statistics_from_values()
        # Init reference to store the maximum and minimum value found in the
        #  extracted values. These will determine if all statistic values fit
        #  within the existing value bins for this variable.
        max_value = float('-Inf')
        min_value = float('Inf')
        for statistic in statistics:
            value = statistic.value
            # Update the max and min value found if needed.
            max_value = value if max_value < value else max_value
            min_value = value if min_value > value else min_value

        # Retrieve the maximum and minimum values of the current value bins
        # If no bins were created yet, these values were default to None.
        value_bin_min, value_bin_max = ValueBin.objects.filter(variable=self).\
                aggregate(models.Min('lower'), models.Max('upper')).values()

        # If the max and min of the extracted values exceed the bin values.
        if (value_bin_min is None or value_bin_max is None or
                math.isnan(value_bin_min) or math.isnan(value_bin_max) or
                min_value < value_bin_min or max_value > value_bin_max):
            # Remove the current bins for this variable.
            ValueBin.objects.filter(variable=self).delete()
            # Recalculate the `Variable.num_bins` number of bins such that they
            #  divide the value range into equal parts.
            bin_size = (max_value-min_value)/float(self.num_bins)
            bin_fn = lambda x: round(min_value + x * bin_size, 2)
            lower_points = map(bin_fn, range(self.num_bins))
            upper_points = map(bin_fn, range(1, self.num_bins+1))
            value_bins = []
            # Using the calculated boundaries, create the new bins.
            # Note: this cannot be done in bulk as we'll need the pk to be set.
            for index in range(self.num_bins):
                value_bins.append(ValueBin.objects.create(
                    variable=self,
                    lower=lower_points[index],
                    upper=upper_points[index]
                ))
        else:
            # Retrieve the current bins and use those.
            value_bins = ValueBin.objects.filter(variable=self)

        # Assign the new statistic instances to each bin, where the value of
        # the instance must lie between the lower and upper bound of the bin.
        for value_bin in value_bins:
            for statistic_instance in statistics:
                value = round(statistic_instance.value, 2)
                if value_bin.lower == min_value:
                    if value <= value_bin.upper and value >= value_bin.lower:
                        statistic_instance.value_bin = value_bin
                else:
                    if value <= value_bin.upper and value > value_bin.lower:
                        statistic_instance.value_bin = value_bin

        # Update the database by replacing the Statistic instances for this
        # variable.
        Statistic.objects.filter(variable=self).delete()
        Statistic.objects.bulk_create(statistics)

        # For each bin, recalculate the count, mean and stddev stats.
        for value_bin in value_bins:
            count, mean, stddev = (
                Statistic.objects.filter(
                    value_bin=value_bin
                ).aggregate(
                    models.Count('value'),
                    models.Avg('value'),
                    models.StdDev('value')
                ).values())
            value_bin.count = count
            value_bin.mean = mean
            value_bin_stddev = stddev
            value_bin.save()
        # Set the last consumed activity
        self.last_consumed_activity_pk = last_consumed.pk
        self.save()

    def calculate_values_from_activities(self, activities):
        """Calculates the appropriate values based on the stored activities.

        This function initializes ValueHistory instances based on the provided
        activities list. The ValueHistory instances must not yet be created in
        the database. The group field will be set later, all other fields are
        set by this function.

        The activities list contains storage.Activity instances that have been
        stored since the last used activity instance. That means that some
        activities might have already been present in an earlier call, but that
        could not be consumed without other activites also being present.

        Parameters:
            activities  -   List of storage.Activity instances not yet consumed

        Returns:
            A tuple containing a list of ValueHistory instances and the latest
            Activity instance that was consumed.
        """
        raise NotImplementedError()

    def calculate_statistics_from_values(self):
        """Calculates the appropriate statistics based on the value history.

        This function initializes statistics instances based on ValueHistory
        queries. The Statistic instances must not yet be created in the DB. The
        value_bin field will be set later, all other fields are set by this
        function. The returned instances will replace the current Statistic
        instances for this variable.

        Returns:
            A list of Statistic instances.
        """
        raise NotImplementedError()

    def __unicode__(self):
        """Returns a unicode description of this object.

        Returns:
            The unicode description of the label if the label is set,
            else the unicode description of the name.
        """
        return unicode(self.label or self.name)

    def __str__(self):
        return unicode(self).encode('ascii', 'xmlcharrefreplace')

    def __repr__(self):
        return "Variable(%s)" % (self,)


class AvgGradeVariable(Variable):

    def __init__(self, *args, **kwargs):
        kwargs['name'] = 'avg_grade'
        super(AvgGradeVariable, self).__init__(*args, **kwargs)

    def calculate_values_from_activities(self, activities):
        last_consumed_activity = None
        values = []
        for activity in activities:
            if activity.verb == "http://adlnet.gov/expapi/verbs/scored":
                values.append(ValueHistory(
                    student=activity.user,
                    variable=self,
                    value=activity.value,
                    datetime=activity.time))
                last_consumed_activity = activity
        return values, last_consumed_activity

    def calculate_statistics_from_values(self):
        from course.models import CourseGroup
        annotated_stats = (ValueHistory.objects.filter(variable=self).
            values('student','group').
            annotate(when=models.Max('datetime'),avg=models.Avg('value')))

        statistics = []
        for value_history in annotated_stats:
            statistics.append(Statistic(
                student=value_history['student'],
                group=CourseGroup.objects.get(pk=value_history['group']),
                variable=self,
                value=value_history['avg'],
                datetime=value_history['when']))
        return statistics

class ValueHistory(models.Model):
    """Model containing all calculated raw values for each variable"""
    student = models.CharField(max_length=255)
    group = models.ForeignKey('course.CourseGroup')
    variable = models.ForeignKey('Variable', related_name="+")
    value = models.FloatField()
    datetime = models.DateTimeField(auto_now_add=True) # should be relative to epoch


class ValueBin(models.Model):
    """Model containing value bins for Statistic values."""
    variable = models.ForeignKey('Variable', related_name="+")
    lower = models.FloatField()
    upper = models.FloatField()
    count = models.PositiveSmallIntegerField(null=True, blank=True)
    mean = models.FloatField(null=True, blank=True)
    stddev = models.FloatField(null=True, blank=True)


class Statistic(models.Model):
    """Model containing calculated statistics for each variable."""
    student = models.CharField(max_length=255)
    group = models.ForeignKey('course.CourseGroup', blank=True)
    variable = models.ForeignKey('Variable', related_name="+")
    value_bin = models.ForeignKey('ValueBin', blank=True)
    value = models.FloatField()
    datetime = models.DateTimeField(auto_now_add=True) # should be relative to epoch

    @classmethod
    def get_students_by_bin(cls, variable, value_bin, min_students=5):
        if value_bin.count < min_students:
            students = cls.objects.filter(variable=variable).extra(
                    select={'distance':"ABS( value - %s )"},
                    select_params=(value_bin.mean,),
                    order_by=['distance'])[0:min_students]
        else:
            students = value_bin.statistics.all()
        return students.value_list('student', flat=True)

    @classmethod
    def get_values_by_students(cls, variable, students):
        return cls.objects.filter(variable=variable, student__in=students).\
                values_list('value', flat=True)

    @classmethod
    def get_gauss_params_by_students(cls, variable, students):
        return cls.objects.filter(variable=variable, student__in=students).\
                aggregate(mean=models.Avg('value'),
                        stddev=models.StdDev('value'))

    def __unicode__(self):
        return u"%s(%s): %s=%s [%s]" % (self.student, self.group,
                self.variable.name, self.value, self.datetime,)

    def __str__(self):
        return unicode(self).encode('ascii', 'xmlcharrefreplace')

    def __repr__(self):
        return "Statistic(%s(%s): %s=%s [%s])" % (self.student, self.group,
                self.variable.name, self.value, self.datetime,)


class Prediction(models.Model):
    """Model containing probabilistic mappings from input to output values."""
    input_variable = models.ForeignKey('Variable', related_name='+')
    input_value = models.FloatField()
    output_variable = models.ForeignKey('Variable', related_name='+')
    output_value = models.FloatField()
    probability = models.FloatField()

    def __unicode__(self):
        return u"P(%s=%s|%s=%s) = %s" % (
            self.output_variable.name, self.output_value,
            self.input_variable.name, self.input_value, self.probability)

    def __str__(self):
        return unicode(self).encode('ascii', 'xmlcharrefreplace')

    def __repr__(self):
        return "Prediction(%s)" % (self,)

    @classmethod
    def get_table(cls, input_variable, input_value, output_variable,
            as_dict=False):
        """Returns a mapping from output values to probabilities.

        Parameters:
            input_variable  -   The variable on which to base the prediction on
            input_value     -   The selected value of the input variable
            output_variable -   The variable that is being predicted
            as_dict         -   Whether the resulting mapping should be a dict
                                (default: False)

        Returns:
            A list of tuples (output_value, probability) when as_dict is False,
            else a dictionary (output_value: probability)
        """
        # Retrieve all possible output values
        values = output_variable.values.values_list('value', flat=True)
        # Retrieve known output value probabilities, given an input value
        predictions = cls.objects.filter(
            output_variable=output_variable,
            input_variable=input_variable,
            input_value=input_value).values_list('output_value', 'probability')
        if len(predictions) == 0:
            # If there are no predictions for the given input_value,
            #  try to use the closest input_value that does have predictions.
            predictions = cls.objects\
                    .filter(output_variable=output_variable,
                            input_variable=input_variable
                    ).extra(select={'distance':"ABS( input_value - %s )"},
                            select_params=(input_value,),
                            order_by=['distance']
                            ).values_list('output_value', 'probability')[:1]
        # Construct a prediction table
        table = dict(zip(values, [0.0]*len(values)))
        # Insert the predicted probabilities in the table
        table.update(dict(predictions))
        # Return the prediction table in the desired format
        return table if as_dict else table.items()
