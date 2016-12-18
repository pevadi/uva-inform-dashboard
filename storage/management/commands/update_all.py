from django.core.management.base import BaseCommand, CommandError
from storage.views import update_all

class Command(BaseCommand):
    help = 'Updates all the activities and variables (including all last years data)'

    def handle(self, *args, **options):
        update_all(None, self.stdout)
