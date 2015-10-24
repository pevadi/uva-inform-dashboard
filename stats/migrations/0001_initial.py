# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('course', '0002_auto_20151024_0149'),
        ('storage', '0003_activitytype_activityverb'),
    ]

    operations = [
        migrations.CreateModel(
            name='ValueHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('student', models.CharField(max_length=255)),
                ('value', models.FloatField()),
                ('course_datetime', models.DurationField()),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(to='course.CourseGroup')),
            ],
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, blank=True)),
                ('label', models.CharField(max_length=255, blank=True)),
                ('num_bins', models.PositiveSmallIntegerField(default=10, blank=True)),
                ('last_consumed_activity_pk', models.PositiveIntegerField(default=0, blank=True)),
                ('type', models.CharField(default=b'IN', max_length=3, choices=[(b'IN', b'Input variable'), (b'OUT', b'Output variable')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AveragingVariable',
            fields=[
                ('variable_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='stats.Variable')),
                ('types', models.ManyToManyField(to='storage.ActivityType')),
                ('verbs', models.ManyToManyField(to='storage.ActivityVerb')),
            ],
            options={
                'abstract': False,
            },
            bases=('stats.variable',),
        ),
        migrations.AddField(
            model_name='variable',
            name='course',
            field=models.ForeignKey(to='course.Course'),
        ),
        migrations.AddField(
            model_name='variable',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_stats.variable_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='valuehistory',
            name='variable',
            field=models.ForeignKey(related_name='+', to='stats.Variable'),
        ),
    ]
