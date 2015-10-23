# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0004_auto_20151023_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistic',
            name='course_datetime',
            field=models.DurationField(default=datetime.timedelta(-1, 86399, 999981)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='valuehistory',
            name='course_datetime',
            field=models.DurationField(default=datetime.timedelta(-1, 86399, 999979)),
            preserve_default=False,
        ),
    ]
