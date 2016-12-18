# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0005_assignment_weight'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='weight',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
