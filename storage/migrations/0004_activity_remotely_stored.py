# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0003_activitytype_activityverb'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='remotely_stored',
            field=models.DateTimeField(null=True),
        ),
    ]
