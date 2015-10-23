# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variable',
            name='last_consumed_activity_pk',
            field=models.PositiveIntegerField(default=0, blank=True),
        ),
    ]
