"""Database models used in the prediction app."""
from django.db import models
from django.utils import timezone
from course.models import Student, CourseGroup

from datetime import datetime

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

        for value_history_item in value_history:
            # Determine the attached student
            student_id = value_history_item.student
            student, _created = Student.objects.get_or_create(
                identification=student_id, defaults={"label": student_id})
            # Determine the attached course groups. Technically someone could
            #  be in multiple groups in one course.
            groups = CourseGroup.get_groups_by_date(
                value_history_item.datetime.date(),
                course=self.course)

            for group in groups:
                group.members.add(student)
                value_history_item.group = group
                # Set course timestamp relative to start
                value_history_item.course_datetime = (
                    value_history_item.datetime -
                    timezone.make_aware(
                        datetime.combine(group.start_date,
                            datetime.min.time())))

        # Update the database by adding the new ValueHistory instances
        ValueHistory.objects.bulk_create(value_history)

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

    def calculate_statistics_from_values(self, value_history):
        from course.models import CourseGroup
        return (value_history.values('student','group').
            annotate(value=models.Avg('value')))


class ValueHistory(models.Model):
    """Model containing all calculated raw values for each variable"""
    student = models.CharField(max_length=255)
    group = models.ForeignKey('course.CourseGroup')
    variable = models.ForeignKey('Variable', related_name="+")
    value = models.FloatField()
    course_datetime = models.DurationField()
    datetime = models.DateTimeField(auto_now_add=True) # should be relative to epoch

