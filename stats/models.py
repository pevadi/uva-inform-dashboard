"""Database models used in the prediction app."""
from django.db import models
from django.utils import timezone
from course.models import Student, CourseGroup, Assignment

from datetime import datetime, timedelta
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
    last_consumed_activity_timestamp = models.DateTimeField(null=True, blank=True,)
    order = models.PositiveSmallIntegerField(default=0, blank=True)
    type = models.CharField(choices=VARIABLE_TYPES, default='IN', max_length=3)
    post_processing = models.CharField(choices=POST_PROCESSING_TYPES,
            default='NON', max_length=3)
    output_chart = models.CharField(choices=OUTPUT_CHART_TYPES, default='NON',
            max_length=3)

    def update_valuehistory(self):
        """Updates the valuehistory
        Based on new storage.models.Activity instances new observed values for
        this variable are calculated. These values are added as ValueHistory
        instances.
        """
        from storage.models import Activity
        from course.models import CourseGroup
        from stats.models import ValueHistory
        from datetime import datetime, timedelta, date
        from collections import Counter

        # Returns a range of dates between two provided dates
        def daterange(start_date, end_date):
            for n in range(int ((end_date - start_date).days)):
                yield start_date + timedelta(n)

        debug_out = open("../../../home/pepijn/update.log", "a")
        def debug(msg):
            if debug_out is not None:
                debug_out.write("[%s] %s \n" % (datetime.now().isoformat(), msg))
                print("[%s] %s" % (datetime.now().isoformat(), msg))

        today = datetime.combine(date.today(), datetime.min.time())
        # Retrieve all live course groups (ie episodes) and update each group separately
        course_groups = CourseGroup.objects.filter(end_date__gte=today)
        for course_group in course_groups:
            debug("Updating group: %s. Last updated: %s" % (course_group.label, course_group.last_updated))

            # get members
            group_members = course_group.members.all().values_list('identification', flat=True)
            debug("Number of students: %i" % len(group_members))

            # If updated for the first time initialize update date
            if course_group.last_updated == None:
                course_group.last_updated = datetime.combine(course_group.start_date-timedelta(days=1), datetime.min.time())
                course_group.save()
            # Get all course dates that have been passed up to today and create valuehistories
            for course_day in daterange(datetime.combine(course_group.last_updated + timedelta(days=1), datetime.min.time()), today + timedelta(days=1)):
                debug("Updating course day: %s" % course_day)
                time_range = [course_day, course_day+timedelta(days=1)]
                # All activity from before the start date is allocated to first course date
                if course_day == datetime.combine(course_group.start_date, datetime.min.time()):
                    time_range[0] -=  timedelta(days=7)
                # Retrieve relevant activity instances for this variable.
                ignored_objects = IgnoredObject.objects.all().values_list(
                        'object_id', flat=True)
                activity_chunk = Activity.objects.exclude(
                        activity__in=ignored_objects).filter(
                                course=self.course.url,
                                # course="http://studiegids.uva.nl/5082INKI6Y/",
                                # https://studiegids.uva.nl/5082INKI6Y/
                                type=self.types.all()[0],
                                verb=self.verbs.all()[0],
                                time__range=time_range)
                if len(activity_chunk) == 0:
                    debug("No activities found for this day (%s)" % course_day)
                    continue

                debug('Total activities: %i' % len(activity_chunk))
                annotated_value_history = []
                updated_students = []
                if len(activity_chunk) > 0:
                    # First update the valhistory for all students that have new activity
                    value_history, last_consumed = self.calculate_values_from_activities(
                        activity_chunk)

                    # If no activity was consumed, stop.
                    if last_consumed is None:
                        continue
                    
                    for value_history_item in value_history:
                        group = course_group

                        # Determine the attached student and create if not existent
                        student_id = value_history_item.student
                        student, _created = Student.objects.get_or_create(
                            identification=student_id, defaults={"label": student_id})

                        group.members.add(student)
                        value_history_item.group = group
                        # Set course timestamp relative to start
                        if course_day == course_group.start_date: 
                            value_history_item.course_datetime = (timezone.make_aware((datetime.combine(course_day, datetime.min.time()))) -
                                                timezone.make_aware(
                                                    datetime.combine(group.start_date,
                                                        datetime.min.time())))
                        else:
                            value_history_item.course_datetime = (
                                value_history_item.datetime -
                                timezone.make_aware(
                                    datetime.combine(group.start_date,
                                        datetime.min.time())))
                   

                        annotated_value_history.append(value_history_item)
                        updated_students.append(student_id)

                        # Update the variable's last consumed activity info if first time ever or if new info in available
                        latest_act = activity_chunk.latest('time')
                        if (self.last_consumed_activity_timestamp == None and self.last_consumed_activity_pk == 0) or latest_act.time > self.last_consumed_activity_timestamp:
                            self.last_consumed_activity_timestamp = latest_act.time
                            self.last_consumed_activity_pk = latest_act.pk
                            self.save()

                # Next update the val history for all students that did not have new activity
                # Value remains unchanged but will regardlessly be added to allow quick lookups
                remaining_students = [stud for stud in group_members if stud not in updated_students]
                for student_id in remaining_students:
                    student = Student.objects.get(identification=student_id)
                    personal_history = ValueHistory.objects.filter(student=student_id, variable=self)
                    # if no valuehistory is present we skip the student. We are not making up data.. Adding zeros is risky..
                    if len(personal_history) > 0:
                        value_history_item = personal_history.latest('datetime')
                        if value_history_item:
                            value_history_item.pk = None
                            actual_course_datetime = (timezone.make_aware((datetime.combine(course_day, datetime.min.time()))) -
                                                    timezone.make_aware(
                                                        datetime.combine(course_group.start_date,
                                                            datetime.min.time())))
                            value_history_item.group = course_group
                            value_history_item.course_datetime = actual_course_datetime
                            value_history_item.datetime = course_day
                            annotated_value_history.append(value_history_item)
                group_members = course_group.members.all().values_list('identification', flat=True)
                # Update the database by adding the new ValueHistory instances
                ValueHistory.objects.bulk_create(annotated_value_history)
                annotated_value_history = []

    def delete_valuehistory(self):
        """Deletes all valhue history of this variable"""
        from stats.models import ValueHistory
        ValueHistory.objects.filter(variable=self).delete()
        self.last_consumed_activity_pk = 0
        self.last_consumed_activity_timestamp = None
        self.save()

    def repopulate_valuehistory(self):
        """Updates the appropriate stats models based on date ranges.
        Repopulates the database with a valuehistory object for each course day
       
        """
        from storage.models import Activity
        from course.models import CourseGroup
        from stats.models import ValueHistory
        from datetime import datetime, timedelta
        from collections import Counter
        # Returns a range of dates between two provided dates
        def daterange(start_date, end_date):
            for n in range(int ((end_date - start_date).days)):
                yield start_date + timedelta(n)
       
        # Retrieve all existing course groups (ie episodes) and repopulate for each group
        course_groups = CourseGroup.objects.all()
        for course_group in course_groups:
            group_members = course_group.members.all().values_list('identification', flat=True)
            print 'Course group', course_group.name,course_group.start_date-timedelta(days=7), course_group.start_date, course_group.end_date, len(group_members)
            # Retrieve relevant activity instances for this variable.
            ignored_objects = IgnoredObject.objects.all().values_list(
                    'object_id', flat=True)
            activities = Activity.objects.exclude(
                    activity__in=ignored_objects).filter(
                            course=self.course.url,
                            type=self.types.all()[0],
                            verb=self.verbs.all()[0],
                            time__gte=course_group.start_date-timedelta(days=7),
                            time__lte=course_group.end_date)
            if len(activities) == 0:
                continue
            print 'Total activities', len(activities)

            for course_day in daterange(course_group.start_date, course_group.end_date):
                time_range = [course_day, course_day+timedelta(days=1)]
                # All activity from before the start date is allocated to first course date
                if course_day == course_group.start_date:
                    time_range[0] -=  timedelta(days=7)

                activity_chunk = activities.filter(time__range=time_range)
                print 'len chunk', len(activity_chunk)
                print 'last consumed', self.last_consumed_activity_pk, self.last_consumed_activity_timestamp

                annotated_value_history = []
                updated_students = []
                course_datetime_tmp = datetime(1,1,1)
                if len(activity_chunk) > 0:
                    # First update the valhistory for all students that have new activity
                    value_history, last_consumed = self.calculate_values_from_activities(
                        activity_chunk)

                    # If no activity was consumed, stop.
                    if last_consumed is None:
                        continue
                    
                    for value_history_item in value_history:
                        group = course_group

                        # Determine the attached student and create if not existent
                        student_id = value_history_item.student
                        student, _created = Student.objects.get_or_create(
                            identification=student_id, defaults={"label": student_id})

                        group.members.add(student)
                        value_history_item.group = group
                        # Set course timestamp relative to start
                        if course_day == course_group.start_date: 
                            value_history_item.course_datetime = (timezone.make_aware((datetime.combine(course_day, datetime.min.time()))) -
                                                timezone.make_aware(
                                                    datetime.combine(group.start_date,
                                                        datetime.min.time())))
                        else:
                            value_history_item.course_datetime = (
                                value_history_item.datetime -
                                timezone.make_aware(
                                    datetime.combine(group.start_date,
                                        datetime.min.time())))
                   
                        course_datetime_tmp = value_history_item.course_datetime

                        annotated_value_history.append(value_history_item)
                        updated_students.append(student_id)

                        latest_act = activity_chunk.latest('time')
                        if (self.last_consumed_activity_timestamp == None and self.last_consumed_activity_pk == 0) or latest_timestamp > self.last_consumed_activity_timestamp:
                            self.last_consumed_activity_timestamp = latest_act.time
                            self.last_consumed_activity_pk = latest_act.pk
                            self.save()

                # ValueHistory.objects.bulk_create(annotated_value_history)
                # Update the database by adding the new ValueHistory instances
                # ValueHistory.objects.bulk_create(annotated_value_history)
                # Next update the val history for all students that did not have new activity
                remaining_students = [stud for stud in group_members if stud not in updated_students]
                for student_id in remaining_students:
                    student = Student.objects.get(identification=student_id)
                    # Valuehistory remains unchanged but will regardlessly be added to allow quick lookups
                    personal_history = ValueHistory.objects.filter(student=student_id, variable=self)
                    if len(personal_history) > 0:
                        value_history_item = personal_history.latest('datetime')
                        if value_history_item:
                            value_history_item.pk = None
                            actual_course_datetime = (timezone.make_aware((datetime.combine(course_day, datetime.min.time()))) -
                                                    timezone.make_aware(
                                                        datetime.combine(course_group.start_date,
                                                            datetime.min.time())))
                            value_history_item.group = course_group
                            value_history_item.course_datetime = actual_course_datetime
                            course_datetime_tmp = value_history_item.course_datetime
                            value_history_item.datetime = course_day
                            annotated_value_history.append(value_history_item)

                group_members = course_group.members.all().values_list('identification', flat=True)
                ValueHistory.objects.bulk_create(annotated_value_history)
                annotated_value_history = []

                print 'course day', course_day, 'activity', len(activity_chunk), 'valuehist', len(annotated_value_history), 'groupmembers', len(group_members), 'updated', len(updated_students), 'remaining', len(remaining_students), 'datetime', course_datetime_tmp
                course_datetime_tmp = datetime(1,1,1)
                course_group.last_updated = datetime.combine(course_day, datetime.min.time())
                course_group.save()

                


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
        ("MIN", "Use the lowest value"),
        ("SCORE", "Use the latest score"))
    aggregation = models.CharField(max_length=5,
            choices=AGGREGATION_TYPES, default="AVG")
    types = models.ManyToManyField('storage.ActivityType')
    verbs = models.ManyToManyField('storage.ActivityVerb')
    extensions = models.ManyToManyField('storage.ActivityExtension', blank=True)

    def _get_aggregator(self):
        return ({
            "AVG": models.Avg,
            "COUNT": models.Count,
            "SUM": models.Sum,
            "MAX": models.Max,
            "MIN": models.Min,
            "SCORE": models.Max})[self.aggregation]

    def calculate_values_from_activities(self, activities):
        from operator import attrgetter
        from collections import Counter
        last_consumed_activity = None
        values = []
        renormalized_value = (
            lambda a: ((a.value-a.value_min)/(a.value_max-a.value_min))*10)
        for activity in activities:
            if activity.value != None or self.aggregation != "SCORE":
                values.append(ValueHistory(
                    student=activity.user,
                    variable=self,
                    value=activity.value,
                    datetime=activity.time))
                last_consumed_activity = activity

        if last_consumed_activity == None:
            return values, last_consumed_activity
        if self.aggregation == "SCORE":
            return values, last_consumed_activity
        if self.aggregation == "COUNT":
            students = [attrgetter('student')(obj) for obj in values]
            student_counts = Counter(students)
            latest_datetime = max([attrgetter('datetime')(obj) for obj in values])
            values = []
            for student in student_counts.keys():
                new_count = student_counts[student]
                # Get the last value history and accumulate
                latest_valuehistory = ValueHistory.objects.filter(student=student, variable=self)
                if len(latest_valuehistory) > 0:
                    new_count += latest_valuehistory.latest('datetime').value
                values.append(ValueHistory(
                    student=student,
                    variable=self,
                    value=new_count,
                    datetime=latest_datetime))
            return values, last_consumed_activity



    def calculate_statistics_from_values(self, value_history):
        from course.models import CourseGroup

        aggregator = self._get_aggregator()
        statistics = (value_history.values('student','group', 'value'))
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
    student = models.CharField(max_length=255, db_index=True)
    group = models.ForeignKey('course.CourseGroup')
    variable = models.ForeignKey('Variable', related_name="+")
    value = models.FloatField(db_index=True)
    course_datetime = models.DurationField()
    datetime = models.DateTimeField(auto_now_add=True) # should be relative to epoch

class IgnoredObject(models.Model):
    object_id = models.CharField(max_length=255)

    def __unicode__(self):
        return unicode(self.object_id)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return "IgnoredObject(%s)" % (self,)
