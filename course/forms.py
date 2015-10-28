from django import forms
from .models import CourseGroup

class StudentImportForm(forms.Form):
    course = forms.ChoiceField(label='Course',
            choices=(lambda:
                [ (c['pk'], "%s - %s" % (c['course__title'], c['name']))
                    for c in  CourseGroup.objects.all().values(
                        'pk', 'name', 'course__title')]))
    student_list = forms.CharField(widget=forms.Textarea, label="CSV Student list")
