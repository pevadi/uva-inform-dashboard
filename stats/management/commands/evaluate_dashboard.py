from django.core.management.base import BaseCommand, CommandError
from stats.helpers import evaluate_dashboard

class Command(BaseCommand):
    help = 'Evaluates the correlation of the dashboard usage.'

    def handle(self, *args, **options):
        evaluate_dashboard(None, self.stdout)
