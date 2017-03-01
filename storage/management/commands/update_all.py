from django.core.management.base import BaseCommand, CommandError
from storage.views import update_all

class Command(BaseCommand):
    help = 'Updates all the activities and variables from a specified (calendar) year.'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)

    def handle(self, *args, **options):
        if options['year']:
            year = options['year']
            update_all(None, self.stdout, year=year)
        else:
            update_all(None, self.stdout)
