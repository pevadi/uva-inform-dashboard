from django.shortcuts import render
from django.http import HttpResponse

from .models import Student, CourseGroup
from .forms import StudentImportForm

import csv
import StringIO

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def add_students(request):
    if request.method == "GET":
        form = StudentImportForm()
    else:
        form = StudentImportForm(request.POST)
        if form.is_valid():
            group = CourseGroup.objects.get(pk=form.cleaned_data['course'])
            try:
                reader = unicode_csv_reader(StringIO.StringIO(
                    form.cleaned_data['student_list']))
                count = 0
                for row in reader:
                    student, created = Student.objects.get_or_create(
                            identification=row[0],
                            defaults={"first_name": row[1], "last_name":
                                row[2]})
                    group.members.add(student)
                    if created:
                        count += 1
                return HttpResponse("%d new students created" % (count,))
            except Exception as e:
                return HttpResponse("Something went wrong: %s" % (e,))

    return render(request, 'student_import_form.html', {'form': form})
