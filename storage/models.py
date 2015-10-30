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


class Activity(models.Model):
    user = models.CharField(max_length=255)
    course = models.URLField(max_length=255, blank=True)
    type = models.URLField(max_length=255)
    verb = models.URLField(max_length=255)
    activity = models.URLField(max_length=255)
    value = models.FloatField(null=True)  # Progress/score depending on type *
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
        if 'result' in statement:
            result = statement['result']
            if 'score' in result and 'raw' in result['score']:
                raw_score = result['score']['raw']
                min_score = result['score'].get("min", None)
                max_score = result['score'].get("max", None)
                if min_score is None or max_score is None:
                    value = raw_score
                else:
                    value = 100 * (raw_score - min_score) / max_score
            elif 'extensions' in result and PROGRESS_T in result:
                value = 100 * float(result['extensions'][PROGRESS_T])
            elif 'duration' in result:
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

        activity, created = cls.objects.get_or_create(user=user, verb=verb,
                course=course, activity=activity, time=time,
                type=statement_type, value=value, name=name,
                description=description, defaults={"remotely_stored": stored})
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
