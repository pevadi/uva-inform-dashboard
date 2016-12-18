# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0006_auto_20161117_1742'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='max_grade',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
