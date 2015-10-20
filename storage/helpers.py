from .models import Activity

def import_bb_gradecenter_export(export_file, fields=None, verb=None,
        activity_type=None, course=None):
    import csv
    from django.utils import timezone
    reader = csv.DictReader(export_file, delimiter=",", quoting=csv.QUOTE_NONE)
    fields = fields or reader.fieldnames
    verb = verb or "http://adlnet.gov/expapi/verbs/experienced"
    activity_type = (activity_type or
        "http://adlnet.gov/expapi/activities/interaction")
    course = course or "//default"
    username_field = fields.pop(0)
    activities = []
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
                time=timezone.now()))
    Activity.objects.bulk_create(activities)
    return activities
