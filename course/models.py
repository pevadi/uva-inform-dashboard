from django.db import models
from django.utils import timezone

from datetime import datetime

class Student(models.Model):
    label = models.CharField(max_length=255)
    identification = models.CharField(max_length=255)

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

    @classmethod
    def get_groups_by_date(cls, date, **kwargs):
        return cls.objects.filter(start_date__lte=date,
                end_date__gte=date, **kwargs)

    def calculate_course_datetime(self, datetime_value=None):
        datetime_value = datetime_value or timezone.now()
        return datetime_value - timezone.make_aware(datetime.combine(
            self.start_date, datetime.min.time()))

    def __unicode__(self):
        return unicode(self.label or self.name)

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
