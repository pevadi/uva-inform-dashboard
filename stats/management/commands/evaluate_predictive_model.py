from django.core.management.base import BaseCommand, CommandError
from stats.helpers import evaluate_predictive_model

class Command(BaseCommand):
    help = 'Evaluates the predictive model for a specific coursegroup. Takes a course group name as an argument.'

    def add_arguments(self, parser):
        parser.add_argument('course_group_name', type=str)

    def handle(self, *args, **options):
        if options['course_group_name']:
            course_group_name = options['course_group_name']
            evaluate_predictive_model(None, self.stdout, course_group_name=course_group_name)
        else:
            evaluate_predictive_model(None, self.stdout, None)
