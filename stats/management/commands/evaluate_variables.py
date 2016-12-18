from django.core.management.base import BaseCommand, CommandError
from stats.helpers import evaluate_variables

class Command(BaseCommand):
    help = 'Evaluates the correlation of the specified variables.'

    def handle(self, *args, **options):
        evaluate_variables(None, self.stdout)
