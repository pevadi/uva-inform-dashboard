# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0007_assignment_max_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='grade_so_far',
            field=models.FloatField(db_index=True, null=True, blank=True),
        ),
    ]
