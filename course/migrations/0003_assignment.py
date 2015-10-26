# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0002_auto_20151024_0149'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('url', models.URLField(max_length=255)),
                ('date_available', models.DateTimeField(null=True, blank=True)),
                ('date_due', models.DateTimeField(null=True, blank=True)),
                ('course', models.ForeignKey(to='course.Course')),
            ],
        ),
    ]
