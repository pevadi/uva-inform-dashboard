from django.core.management.base import BaseCommand, CommandError
from storage.views import repopulate_valuehistorys

class Command(BaseCommand):
    help = 'Repopulates the valuehistory in the database'

    def handle(self, *args, **options):
        repopulate_valuehistorys(None, self.stdout)