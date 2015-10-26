# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0006_variable_post_processing'),
    ]

    operations = [
        migrations.AddField(
            model_name='variable',
            name='order',
            field=models.PositiveSmallIntegerField(default=0, blank=True),
        ),
    ]
