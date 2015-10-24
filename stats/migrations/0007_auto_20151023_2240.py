# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0003_activitytype_activityverb'),
        ('stats', '0006_auto_20151023_1850'),
    ]

    operations = [
        migrations.CreateModel(
            name='AveragingVariable',
            fields=[
                ('variable_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='stats.Variable')),
                ('types', models.ManyToManyField(to='storage.ActivityType')),
                ('verbs', models.ManyToManyField(to='storage.ActivityVerb')),
            ],
            bases=('stats.variable',),
        ),
        migrations.RemoveField(
            model_name='avggradevariable',
            name='variable_ptr',
        ),
        migrations.DeleteModel(
            name='AvgGradeVariable',
        ),
    ]
