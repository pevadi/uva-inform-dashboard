# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0012_remove_student_stats'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='final_grade',
            field=models.FloatField(db_index=True, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='student',
            name='passed_course',
            field=models.NullBooleanField(),
        ),
    ]
