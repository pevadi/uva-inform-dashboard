# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0008_student_grade_so_far'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='predicted_grade',
            field=models.FloatField(db_index=True, null=True, blank=True),
        ),
    ]
