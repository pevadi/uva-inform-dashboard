from django.db import models
from django.utils import timezone

from datetime import datetime

class Student(models.Model):
    identification = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    grade_so_far = models.FloatField(db_index=True, blank=True, null=True)
    assignments_completion = models.FloatField(db_index=True, blank=True, null=True)
    predicted_grade = models.FloatField(db_index=True, blank=True, null=True)
    final_grade = models.FloatField(db_index=True, blank=True, null=True)
    passed_course = models.NullBooleanField(blank=True, null=True)

    @property
    def has_treatment(self):
        from viewer.models import GroupAssignment
        try:
            group = GroupAssignment.objects.get(student=self.identification)
        except GroupAssignment.DoesNotExist:
            return None
        else:
            return group.has_treatment

    @property
    def has_data(self):
        from storage.models import Activity
        return Activity.objects.filter(user=self.identification).exists()

    @property
    def label(self):
        if self.first_name != "" or self.last_name != "":
            return "%s %s" % (self.first_name, self.last_name)
        else:
            return self.identification

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u'%s' % (self.label,)

    def __repr__(self):
        return "Student(%s)" % (self.label,)


class Course(models.Model):
    url = models.URLField(max_length=255)
    title = models.CharField(max_length=255)
    active = models.BooleanField(default=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)

    @property
    def url_variations(self):
        """Return variations to the url to deal with inconsistencies."""
        from urlparse import urlsplit, urlunsplit
        scheme, netloc, path, query, fragment = urlsplit(self.url)
        scheme2 = 'https' if scheme == "http" else "http"
        path2 = path[:-1] if path[-1] == "/" else "%s/" % (path,)
        variations = [
            (scheme, netloc, path, query, fragment),
            (scheme, netloc, path2, query, fragment),
            (scheme2, netloc, path, query, fragment),
            (scheme2, netloc, path2, query, fragment)
        ]
        return [urlunsplit(variation) for variation in variations]

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u'%s' % (self.title,)

    def __repr__(self):
        return "Course(%s)" % (self.url,)

class CourseGroup(models.Model):
    course = models.ForeignKey('Course')
    start_date = models.DateField()
    end_date = models.DateField()
    name = models.CharField(max_length=50)
    label = models.CharField(max_length=255, blank=True)
    members = models.ManyToManyField('course.Student', blank=True,
            related_name='statistic_groups')
    last_updated = models.DateTimeField(null=True, blank=True)

    @classmethod
    def get_groups_by_date(cls, date, **kwargs):
	return cls.objects.filter(start_date__lte=date,
                end_date__gte=date, **kwargs)

    def calculate_course_datetime(self, datetime_value=None):
        datetime_value = datetime_value or timezone.now()
        course_datetime = datetime_value - timezone.make_aware(datetime.combine(
            self.start_date, datetime.min.time()))
        # A course takes 55 days (including day 0)
        # print type(course_datetime)
        # if course_datetime.days > 55:
        #     course_datetime.days = 55
        return course_datetime

    def __unicode__(self):
        return u"(%s - %s)" % (unicode(self.course),
                unicode(self.label or self.name))

    def __str__(self):
        return unicode(self).encode('ascii', 'xmlcharrefreplace')

    def __repr__(self):
        return "CourseGroup(%s::%s)" % (self.course.title, self.name)


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    date_available = models.DateTimeField(null=True, blank=True)
    date_due = models.DateTimeField(null=True, blank=True)
    course = models.ForeignKey(Course)
    weight = models.FloatField(blank=True, null=True)
    max_grade = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.title)

    def __str__(self):
        return unicode(self).encode('ascii', 'xmlcharrefreplace')

    def __repr__(self):
        return "Assignment(%s)" % (self.title,)
