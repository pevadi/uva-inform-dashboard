from django.core.management.base import BaseCommand, CommandError
from storage.views import remove_ignored_user_data

class Command(BaseCommand):
    help = 'Remove all data of the ignored users.'

    def handle(self, *args, **options):
        remove_ignored_user_data(None, self.stdout)
