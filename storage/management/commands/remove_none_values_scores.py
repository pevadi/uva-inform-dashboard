from django.core.management.base import BaseCommand, CommandError
from storage.views import remove_none_values_scores

class Command(BaseCommand):
    help = 'Remove all score-school-assignment value history records with a none value.'

    def handle(self, *args, **options):
        remove_none_values_scores(None, self.stdout)
