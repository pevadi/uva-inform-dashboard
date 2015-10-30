"""Database models used in the prediction app."""
from django.db import models
from django.utils import timezone
from course.models import Student, CourseGroup, Assignment

from datetime import datetime
from polymorphic import PolymorphicModel

import math

class Variable(PolymorphicModel):
    """Model containing information on variables used in predictions."""
    VARIABLE_TYPES = (
        ('IN', "Input variable"),
        ('OUT', "Output variable"),
        ('I/O', "Both input and output variable")
    )

    POST_PROCESSING_TYPES = (
        ('S2M', 'Convert from seconds to minutes'),
        ('S2H', 'Convert from seconds to hours'),
        ('5.5', 'Convert to boolean whether bigger than 5.5'),
        ('NON', "Don't perform post processing"),
    )

    OUTPUT_CHART_TYPES = (
        ('NON', 'No output chart'),
        ('GSS', 'Gauss plot'),
        ('PIE', 'Pie chart'),
    )

    name = models.CharField(max_length=100, unique=True, blank=True)
    label = models.CharField(max_length=255, blank=True)
    axis_label = models.CharField(max_length=255, null=True, blank=True)
    course = models.ForeignKey('course.Course')
    num_bins = models.PositiveSmallIntegerField(default=10, blank=True)
    last_consumed_activity_pk = models.PositiveIntegerField(
        default=0, blank=True)
    order = models.PositiveSmallIntegerField(default=0, blank=True)
    type = models.CharField(choices=VARIABLE_TYPES, default='IN', max_length=3)
    post_processing = models.CharField(choices=POST_PROCESSING_TYPES,
            default='NON', max_length=3)
    output_chart = models.CharField(choices=OUTPUT_CHART_TYPES, default='NON',
            max_length=3)

    def update_from_storage(self):
        """Updates the appropriate stats models based on storage date.

        Based on new storage.models.Activity instances new observed values for
        this variable are calculated. These values are added as ValueHistory
        instances.

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

        annotated_value_history = []
        for value_history_item in value_history:
            # Determine the attached course groups. Technically someone could
            #  be in multiple groups in one course.
            groups = CourseGroup.get_groups_by_date(
                value_history_item.datetime.date(),
                course=self.course)

            if len(groups) == 0:
                continue
            group = groups[0]

            if value_history_item.value is None:
                continue

            # Determine the attached student
            student_id = value_history_item.student
            student, _created = Student.objects.get_or_create(
                identification=student_id, defaults={"label": student_id})

            group.members.add(student)
            value_history_item.group = group
            # Set course timestamp relative to start
            value_history_item.course_datetime = (
                value_history_item.datetime -
                timezone.make_aware(
                    datetime.combine(group.start_date,
                        datetime.min.time())))
            annotated_value_history.append(value_history_item)

        # Update the database by adding the new ValueHistory instances
        ValueHistory.objects.bulk_create(annotated_value_history)

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

    def calculate_statistics_from_values(self, value_history):
        """Calculates the appropriate statistics based on the value history.

        This function calculates variable statistics based on ValueHistory
        queries. This function returns a list of dictionaries containing all
        fields from the ValueHistory instances but with the `value` slot set to
        the calculated statistic.

        Returns:
            A list of dictionaries containing the statistics.
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


class SingleEventVariable(Variable):
    AGGREGATION_TYPES = (
        ("AVG", "Use the average value"),
        ("COUNT", "Count the number of values"),
        ("SUM", "Use the cumulative value"),
        ("MAX", "Use the highest value"),
        ("MIN", "Use the lowest value"))
    aggregation = models.CharField(max_length=5,
            choices=AGGREGATION_TYPES, default="AVG")
    types = models.ManyToManyField('storage.ActivityType')
    verbs = models.ManyToManyField('storage.ActivityVerb')

    def _get_aggregator(self):
        return ({
            "AVG": models.Avg,
            "COUNT": models.Count,
            "SUM": models.Sum,
            "MAX": models.Max,
            "MIN": models.Min})[self.aggregation]

    def calculate_values_from_activities(self, activities):
        last_consumed_activity = None
        values = []
        for activity in activities:
            if (self.types.filter(uri=activity.type).exists() and
                    self.verbs.filter(uri=activity.verb).exists()):
                values.append(ValueHistory(
                    student=activity.user,
                    variable=self,
                    value=activity.value,
                    datetime=activity.time))
                last_consumed_activity = activity
        return values, last_consumed_activity

    def calculate_statistics_from_values(self, value_history):
        from course.models import CourseGroup
        aggregator = self._get_aggregator()
        statistics = (value_history.values('student','group').
            annotate(value=models.Avg('value')))
        if self.post_processing == "S2M":
            for statistic in statistics:
                statistic['value'] = statistic['value'] / float(60)
        elif self.post_processing == "S2H":
            for statistic in statistics:
                statistic['value'] = statistic['value'] / float(3600)
        elif self.post_processing == "5.5":
            for statistic in statistics:
                statistic['value'] = int(statistic['value'] >= 5.5)
        return statistics


class AssignmentLinkedVariable(SingleEventVariable):
    COMPARE_TYPES = (
        ('A', 'Hours after assignment was made available.'),
        ('B', 'Hours before the assignment was due.')
    )
    compare_method = models.CharField(max_length=1, choices=COMPARE_TYPES,
            default='A')

    def calculate_values_from_activities(self, activities):
        last_consumed_activity = None
        values = []

        if self.compare_method == 'A':
            compare_fn = lambda a, c: a-c
        else:
            compare_fn = lambda a, c: c-a

        for activity in activities:
            try:
                assignment = Assignment.objects.get(url=activity.activity)
            except:
                continue

            if self.compare_method == 'A':
                compare_time = assignment.date_available
            else:
                compare_time = assignment.date_due

            if compare_time is None:
                return [], last_consumed_activity

            if not timezone.is_aware(compare_time):
                compare_time = timezone.make_aware(compare_time)

            if (self.types.filter(uri=activity.type).exists() and
                    self.verbs.filter(uri=activity.verb).exists()):
                if not timezone.is_aware(activity.time):
                    activity.time = timezone.make_aware(activity.time)

                difference = compare_fn(activity.time, compare_time)
                hours = math.ceil(difference.total_seconds()/60/60)

                values.append(ValueHistory(
                    student=activity.user,
                    variable=self,
                    value=hours,
                    datetime=activity.time))
                last_consumed_activity = activity
        return values, last_consumed_activity

class ValueHistory(models.Model):
    """Model containing all calculated raw values for each variable"""
    student = models.CharField(max_length=255)
    group = models.ForeignKey('course.CourseGroup')
    variable = models.ForeignKey('Variable', related_name="+")
    value = models.FloatField()
    course_datetime = models.DurationField()
    datetime = models.DateTimeField(auto_now_add=True) # should be relative to epoch

