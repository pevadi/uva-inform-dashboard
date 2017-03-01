# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0015_auto_20170103_1522'),
        ('course', '0010_student_assignments_completion'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='stats',
            field=models.ManyToManyField(related_name='student_stats', to='stats.ValueHistory', blank=True),
        ),
    ]
