from django.core.management.base import BaseCommand, CommandError
from storage.views import import_final_grades_from_csv

class Command(BaseCommand):
    help = 'Imports final grades from a csv file and stores as student attribute. Takes file name as argument.'

    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str)

    def handle(self, *args, **options):
        if options['file_name']:
            file_name = options['file_name']
            import_final_grades_from_csv(None, self.stdout, file_name=file_name)
        else:
            import_final_grades_from_csv(None, self.stdout, None)
