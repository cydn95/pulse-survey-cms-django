# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-04-13 09:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shgroup', '0013_auto_20200412_1928'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shmapping',
            name='project',
        ),
        migrations.RemoveField(
            model_name='shmapping',
            name='subjectUser',
        ),
        migrations.AlterField(
            model_name='shmapping',
            name='projectUser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shgroup.ProjectUser'),
        ),
        migrations.AlterField(
            model_name='shmapping',
            name='shCategory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shgroup.SHCategory'),
        ),
    ]
