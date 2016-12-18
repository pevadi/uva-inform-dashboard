# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0013_auto_20161023_1618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='valuehistory',
            name='value',
            field=models.FloatField(db_index=True),
        ),
    ]
