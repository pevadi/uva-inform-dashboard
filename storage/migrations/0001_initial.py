# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=255)),
                ('course', models.URLField(max_length=255, blank=True)),
                ('type', models.URLField(max_length=255)),
                ('verb', models.URLField(max_length=255)),
                ('activity', models.URLField(max_length=255)),
                ('value', models.FloatField(null=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('time', models.DateTimeField(null=True)),
                ('stored', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'activities',
            },
        ),
    ]
