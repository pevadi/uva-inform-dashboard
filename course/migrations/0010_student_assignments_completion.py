# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0009_student_predicted_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='assignments_completion',
            field=models.FloatField(db_index=True, null=True, blank=True),
        ),
    ]
