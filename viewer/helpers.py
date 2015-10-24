from django.utils import timezone
from datetime import timedelta

def generate_viewer_access_event():
    timestamp = settings.LRS_TIME_OFFSET(timezone.now().replace(microsecond=0))
    return {
        "timestamp": timestamp.isoformat(),
        "object": {
            "definition": {
                "type": "http://activitystrea.ms/schema/1.0/application",
                "name": {"en-US": "UvAInform COACH2 Dashboard"},
                "description": {"en-US": "UvAInform COACH2 Dashboard"}
            }, 
            "id": "https://coach2.innovatievooronderwijs.nl",
            "objectType": "Activity"
        },
        "verb": {
            "id": "http://activitystrea.ms/schema/1.0/access",
            "display": {
                "en-US": "accessed"
            }
        }
    }
