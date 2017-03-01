from django.core.management.base import BaseCommand, CommandError
from stats.helpers import evaluate_msql_res

class Command(BaseCommand):
    help = 'Evaluates the correlation of the msql_res usage.'

    def handle(self, *args, **options):
        evaluate_msql_res(None, self.stdout)
