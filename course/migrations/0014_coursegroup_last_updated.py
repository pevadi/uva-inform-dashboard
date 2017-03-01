# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0013_auto_20170122_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursegroup',
            name='last_updated',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
