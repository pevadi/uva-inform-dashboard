from django.core.management.base import BaseCommand, CommandError
from stats.views import evaluate_predictive_model

class Command(BaseCommand):
    help = 'Evaluates the predictive model.'

    def handle(self, *args, **options):
        evaluate_predictive_model(None, self.stdout)
