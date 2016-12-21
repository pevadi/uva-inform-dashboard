from django.core.management.base import BaseCommand, CommandError
from storage.views import update_grades

class Command(BaseCommand):
    help = 'Updates the actual grades.'

    def handle(self, *args, **options):
        update_grades(None, self.stdout)

