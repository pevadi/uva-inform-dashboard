# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('active', models.BooleanField(default=True)),
                ('last_updated', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CourseGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('name', models.CharField(unique=True, max_length=50)),
                ('label', models.CharField(max_length=255, blank=True)),
                ('course', models.ForeignKey(to='course.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255)),
                ('identification', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='coursegroup',
            name='members',
            field=models.ManyToManyField(related_name='statistic_groups', to='course.Student', blank=True),
        ),
    ]
