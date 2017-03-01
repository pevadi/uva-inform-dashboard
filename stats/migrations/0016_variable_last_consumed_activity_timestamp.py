# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0015_auto_20170103_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='variable',
            name='last_consumed_activity_timestamp',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
