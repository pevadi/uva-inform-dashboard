from django.db import models
from django.conf import settings

from dateutil import parser as dateparser

class ActivityType(models.Model):
    uri = models.URLField(max_length=255)

    def __unicode__(self):
        return unicode(self.uri)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return "ActivityType(%s)" % (self,)


class ActivityVerb(models.Model):
    uri = models.URLField(max_length=255)

    def __unicode__(self):
        return unicode(self.uri)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return "ActivityVerb(%s)" % (self,)


class ActivityExtension(models.Model):
    EXTENSION_LOCATIONS = (
        ('R', 'Result extension'),
    )

    key = models.URLField(max_length=255)
    value = models.CharField(max_length=255)
    location = models.CharField(max_length=2, choices=EXTENSION_LOCATIONS,
            default="R")

    def __unicode__(self):
        return u"%s=%s" % (self.key, self.value,)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return "ActivityExtension(%s)" % (self,)


class Activity(models.Model):
    user = models.CharField(max_length=255)
    course = models.URLField(max_length=255, blank=True)
    type = models.URLField(max_length=255)
    verb = models.URLField(max_length=255)
    activity = models.URLField(max_length=255)
    value = models.FloatField(null=True)  # Progress/score depending on type *
    value_min = models.FloatField(null=True)
    value_max = models.FloatField(null=True)
    extensions = models.ManyToManyField('ActivityExtension')
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    time = models.DateTimeField(null=True)
    remotely_stored = models.DateTimeField(null=True)
    stored = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "activities"

    @classmethod
    def extract_from_statement(cls, statement):
        statement_type = statement['object']['definition']['type']
        if 'mbox' in statement['actor']:
            user = statement['actor']['mbox']
        elif 'account' in statement['actor']:
            account = statement['actor']['account']
            if account['homePage'] == settings.XAPI_ACTOR_HOMEPAGE:
                user = account['name']
            else:
                return None, None
        else:
            return None, None

        if IgnoredUser.objects.filter(user=user).exists():
            return None, None

        activity = statement['object']['id']
        verb = statement['verb']['id']
        try:
            name = statement['object']['definition']['name']['en-US']
        except KeyError:
            name = ""

        try:
            description = statement['object']['definition']['description']['en-US']
        except KeyError:
            description = ""

        time = dateparser.parse(statement['timestamp'])
        stored = dateparser.parse(statement['stored'])

        value = None
        min_score = None
        max_score = None
        extensions = []
        if 'result' in statement:
            result = statement['result']
            if 'score' in result and 'raw' in result['score']:
                raw_score = result['score']['raw']
                min_score = result['score'].get("min", None)
                max_score = result['score'].get("max", None)
                if min_score is None or max_score is None:
                    value = raw_score
                else:
                    value = (raw_score - min_score) / float(max_score - min_score)
            if 'extensions' in result:
                for ext_key, ext_value in result['extensions'].items():
                    extension, _c = ActivityExtension.objects.get_or_create(
                            key=ext_key, value=ext_value, location='R')
                    extensions.append(extension)
            if 'duration' in result:
                from isodate import ISO8601Error, parse_duration
                try:
                    duration = parse_duration(statement['result']['duration'])
                except ISO8601Error, TypeError:
                    value = None
                else:
                    value = duration.total_seconds()

        if 'context' in statement and 'contextActivities' in statement['context']:
            course = statement['context']['contextActivities']['grouping'][0]['id']
        else:
            course = None

        for activity in cls.objects.filter(user=user, verb=verb,
                course=course, activity=activity, time=time,
                type=statement_type, value=value, name=name,
                value_min=min_score, value_max=max_score,
                description=description):
            if set(activity.extensions.all()) == set(extensions):
                created = False
                break
        else:
            created = True
            activity = cls.objects.create(user=user, verb=verb,
                    course=course, activity=activity, time=time,
                    type=statement_type, value=value, name=name,
                    value_min=min_score, value_max=max_score,
                    description=description, remotely_stored=stored)
            for extension in extensions:
                activity.extensions.add(extension)

        return activity, created

    def __unicode__(self):
        return u' '.join([self.user, self.verb, self.activity,
                unicode(self.value)])

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return "Activity(%s)" % (self.verb,)

class IgnoredUser(models.Model):
    user = models.CharField(max_length=255)

    def __unicode__(self):
        return unicode(self.user)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return "IgnoredUser(%s)" % (self,)
