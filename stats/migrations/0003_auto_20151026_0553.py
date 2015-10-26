# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0002_assignmentlinkedvariable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='singleeventvariable',
            name='aggregation',
            field=models.CharField(default=b'AVG', max_length=5, choices=[(b'AVG', b'Use the average value'), (b'COUNT', b'Count the number of values'), (b'SUM', b'Use the cumulative value'), (b'MAX', b'Use the highest value'), (b'MIN', b'Use the lowest value')]),
        ),
    ]
