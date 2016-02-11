from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone

from .models import Activity, ActivityType, ActivityVerb
from .models import IgnoredUser
from storage import XAPIConnector

def local_import(course, epoch=None):
    xapi = XAPIConnector()
    objects = []
    for url in course.url_variations:
        activities = xapi.getAllStatementsByRelatedActitity(url, epoch)
        for activity in activities:
            try:
                activity['context']['contextActivities']\
                        ['grouping'][0]['id'] = course.url
            except:
                pass
            objects.append(Activity.extract_from_statement(activity))
    return objects

def store_event_in_remote_storage(event, user):
    if not settings.STORE_IN_LRS:
        return None
    elif IgnoredUser.objects.filter(user=user).exists():
        return HttpResponse(status=204)

    event["actor"] = {
        "objectType": "Agent",
        "account": {
            "homePage": "https://secure.uva.nl",
            "name": user
        }
    }
    xapi = XAPIConnector()
    resp = xapi.submitStatement(event)
    return event

def import_bb_gradecenter_export(export_file, fields=None, verb=None,
        activity_type=None, course=None, timedelta=None, quoting=None):
    import csv
    from django.utils import timezone
    if quoting is None:
        reader = csv.DictReader(export_file, delimiter=",", quoting=csv.QUOTE_NONE)
    else:
        reader = csv.DictReader(export_file, delimiter=",")
    fields = fields or reader.fieldnames
    verb = verb or "http://adlnet.gov/expapi/verbs/experienced"
    activity_type = (activity_type or
        "http://adlnet.gov/expapi/activities/interaction")
    course = course or "//default"
    username_field = fields.pop(0)
    activities = []
    timestamp = timezone.now()
    if timedelta is not None:
        timestamp = timestamp - timedelta
    for row in reader:
        for field in fields:
            activities.append(Activity(
                user=row[username_field],
                course=course,
                type=activity_type,
                verb=verb,
                activity="%s/%s" % (course, field),
                value=float(row[field]),
                name=field,
                description=field,
                time=timestamp))
    Activity.objects.bulk_create(activities)
    return activities

def import_generic_final_grades_export(export_file, grade_field='grade',
        course_field='course', student_field='student',date_field='date',
        date_format="%d-%m-%Y", verb=None, activity_type=None, quoting=None):
    from csv import DictReader, QUOTE_NONE
    from datetime import datetime
    from course.models import Course
    if quoting is None:
        reader = DictReader(export_file, delimiter=",", quoting=QUOTE_NONE)
    else:
        reader = DictReader(export_file, delimiter=",")
    verb = verb or "http://activitystrea.ms/schema/1.0/complete"
    activity_type = (activity_type or
        "http://adlnet.gov/expapi/activities/course")
    activities = []
    for row in reader:
        try:
            course = Course.objects.get(url=row[course_field])
        except Course.DoesNotExist:
            print "Could not find course `%s`, skipping." % (
                row[course_field],)
            continue
        activities.append(Activity(
            user=row[student_field],
            course=course,
            type=activity_type,
            verb=verb,
            activity=row[course_field],
            value=float(row[grade_field]),
            name=course.title,
            description=course.title,
            time=datetime.strptime(row[date_field], date_format)))
    Activity.objects.bulk_create(activities)
    return activities


class XAPIEvent(object):
    _stmnt = None
    user = None

    def __init__(self, user, course=None, *args, **kwargs):
        self.user = user
        self._stmnt = {}
        # Set the actor
        self.set_actor(user)
        # Set the course if provided.
        if course is not None:
            self.add_context_activity(course)
        # Ensure a default timestamp is already set
        self.set_timestamp()

    def set_actor(self, actor, homepage=None):
        """Set the actor dictionary.

        Parameters:
            user        -   String identifying the actor.
            homepage    -   String identifying the actor's domain.
                            (defaults to settings.XAPI_ACTOR_HOMEPAGE)
        """
        homepage = homepage or settings.XAPI_ACTOR_HOMEPAGE

        self._stmnt["actor"] = {
            "objectType": "Agent",
            "account": {
                "homePage": homepage,
                "name": actor
            }
        }

    def add_context_activity(self, activity_id, ctype=None):
        """Add a context activity to the context dictionary.

        Parameters:
            activity_id -   URI string identifying the activity.
            ctype       -   One of "parent","grouping", "category", "other".
                            (default grouping)
        """
        ctype = ctype or "grouping"
        context = self._stmnt.get("context", {})
        context_activities = context.get("contextActivities", {})
        context_activities_type = context_activities.get(ctype, [])
        context_activities_type.append({"objectType": "Activity",
            "id": activity_id })
        context_activities[ctype] = context_activities_type
        context["contextActivities"] = context_activities
        self._stmnt["context"] = context

    def set_timestamp(self, dtime=None):
        """Set the ISO 8601 timestamp.

        Parameters:
            dtime   -   datetime (default: timezone.now())
        """
        if dtime is None:
            dtime = timezone.now()
        elif not timezone.is_aware(dtime):
            dtime = timezone.make_aware(dtime)

        self._stmnt['timestamp'] = (settings.LRS_TIME_OFFSET(
            dtime.replace(microsecond=0)).isoformat())

    def set_object(self, object_id, def_type, def_name=None,
            def_desc=None, object_type="Activity"):
        """Set the object dictionary.

        Parameters:
            object_id   -   URI string identifying the activity.
            def_type    -   Activity type instance or URI.
            def_name    -   Name of the activity. (optional)
            def_desc    -   Description of the activity. (optional)
            object_type -   Object type. (Default: "Activity")
        """
        definition = {}
        if isinstance(def_type, ActivityType):
            definition['type'] = def_type.uri
        else:
            definition['type'] = def_type

        if def_name is not None:
            if isinstance(def_name, dict):
                definition['name'] = def_name
            else:
                definition['name'] = {"en-US": def_name}

        if def_desc is not None:
            if isinstance(def_desc, dict):
                definition['description'] = def_desc
            else:
                definition['description'] = {"en-US": def_desc}

        self._stmnt['object'] = {
            "definition": definition,
            "id": object_id,
            "objectType": object_type
        }

    def set_verb(self, verb_id, verb_name=None):
        """Set the verb dictionary.

        Parameters:
            verb_id     -   URI string identifying the verb.
            verb_name   -   Displayable name of the verb.
                            (defaults to last part of the URI)
        """
        if verb_name is None:
            verb_name = verb_id.split("/")[-1]

        if not isinstance(verb_name, dict):
            verb_name = {"en-US": verb_name}

        self._stmnt['verb'] = {"id": verb_id, "display": verb_name}

    def set_result(self, result, result_type=None):
        self._stmnt['result'] = self._stmnt.get('result', {})
        if isinstance(result, dict):
            self._stmnt['result']["score"] = result
        else:
            self._stmnt['result']["score"] = {"raw": result}

        if result_type is not None:
            self._stmnt['result']["extensions"] = {
                "http://coach2.innovatievooronderwijs.nl/extensions/gradetype":
                result_type}

    def set_duration(self, duration=None, **kwargs):
        from datetime import timedelta
        from isodate import duration_isoformat
        duration = duration or timedelta(**kwargs)
        
        self._stmnt['result'] = self._stmnt.get('result', {})
        self._stmnt['result']["duration"] = duration_isoformat(duration)

    def statement(self):
        return self._stmnt

    def json(self):
        from json import dumps
        return dumps(self._stmnt)

    def store(self):
        if not settings.STORE_IN_LRS:
            return None
        elif IgnoredUser.objects.filter(user=self.user).exists():
            return None

        xapi = XAPIConnector()
        resp = xapi.submitStatement(self.statement())
        return resp


class DashboardEvent(XAPIEvent):

    def __init__(self, *args, **kwargs):
        super(DashboardEvent, self).__init__(*args, **kwargs)
        self.set_object(
            "https://coach2.innovatievooronderwijs.nl",
            "http://activitystrea.ms/schema/1.0/application",
            def_name= {"en-US": "UvAInform COACH2 Dashboard"},
            def_desc= {"en-US": "UvAInform COACH2 Dashboard"})


class DashboardAccessEvent(DashboardEvent):

    def __init__(self, *args, **kwargs):
        super(DashboardAccessEvent, self).__init__(*args, **kwargs)
        self.set_verb(
            "http://activitystrea.ms/schema/1.0/access",
            verb_name={"en-US": "accessed"})


class DashboardInteractedEvent(DashboardEvent):

    def __init__(self, *args, **kwargs):
        super(DashboardInteractedEvent, self).__init__(*args, **kwargs)
        self.set_verb(
            "http://activitystrea.ms/schema/1.0/interact",
            verb_name={"en-US": "interacted"})


class VideoWatchEvent(XAPIEvent):

    def __init__(self, *args, **kwargs):
        super(VideoWatchEvent, self).__init__(*args, **kwargs)
        self.set_verb(
            "http://activitystrea.ms/schema/1.0/watch",
            verb_name={"en-US": "watched"})

    def set_object(self, object_id, *args, **kwargs):
        super(VideoWatchEvent, self).set_object(object_id,
            "http://adlnet.gov/expapi/activities/media", *args, **kwargs)


class WebsitePingEvent(XAPIEvent):

    def __init__(self, *args, **kwargs):
        super(WebsitePingEvent, self).__init__(*args, **kwargs)
        self.set_verb(
            "http://adlnet.gov/expapi/verbs/experienced",
            verb_name={"en-US": "experiences"})

    def set_object(self, object_id, *args, **kwargs):
        super(WebsitePingEvent, self).set_object(object_id,
            "http://activitystrea.ms/schema/1.0/page", *args, **kwargs)


class CompileEvent(XAPIEvent):

    def __init__(self, *args, **kwargs):
        super(CompileEvent, self).__init__(*args, **kwargs)
        self.set_verb(
            "http://activitystrea.ms/schema/1.0/build",
            verb_name={"en-US": "built"})

    def set_object(self, object_id, *args, **kwargs):
        super(CompileEvent, self).set_object(object_id,
            "http://activitystrea.ms/schema/1.0/application", *args, **kwargs)


class PresenceEvent(XAPIEvent):

    def __init__(self, *args, **kwargs):
        super(PresenceEvent, self).__init__(*args, **kwargs)
        self.set_verb(
                "http://activitystrea.ms/schema/1.0/attend",
            verb_name={"en-US": "attended"})

    def set_object(self, object_id, *args, **kwargs):
        super(PresenceEvent, self).set_object(object_id,
                "http://adlnet.gov/expapi/activities/meeting", *args, **kwargs)

class GradingEvent(XAPIEvent):
    
    def __init__(self, *args, **kwargs):
        super(GradingEvent, self).__init__(*args, **kwargs)
        self.set_verb(
            "http://adlnet.gov/expapi/verbs/scored",
            verb_name={"en-US": "scored"})

    def set_object(self, object_id, *args, **kwargs):
        super(GradingEvent, self).set_object(object_id,
                "http://activitystrea.ms/schema/1.0/application", *args, **kwargs)

