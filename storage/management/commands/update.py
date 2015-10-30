from django.core.management.base import BaseCommand, CommandError
from storage.views import update

class Command(BaseCommand):
    help = 'Updates the activities and variables'

    def handle(self, *args, **options):
        update(None, self.stdout)
