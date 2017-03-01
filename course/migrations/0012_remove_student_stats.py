# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0011_student_stats'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='stats',
        ),
    ]
