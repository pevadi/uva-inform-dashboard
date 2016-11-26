from django.core.management.base import BaseCommand, CommandError
from stats.views import evaluate_activities

class Command(BaseCommand):
    help = 'Evaluates the correlation of the activities.'

    def handle(self, *args, **options):
        evaluate_activities(None, self.stdout)
