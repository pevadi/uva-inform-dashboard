# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0012_auto_20151120_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='valuehistory',
            name='student',
            field=models.CharField(max_length=255, db_index=True),
        ),
    ]
