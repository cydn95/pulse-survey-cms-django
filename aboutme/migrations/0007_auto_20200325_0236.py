# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-03-25 09:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shgroup', '0010_auto_20200318_0233'),
        ('aboutme', '0006_auto_20200115_1745'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='amresponsetopic',
            name='amResponse',
        ),
        migrations.RemoveField(
            model_name='amresponsetopic',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='amresponsetopic',
            name='topic',
        ),
        migrations.AddField(
            model_name='amresponsetopic',
            name='AMQuestion',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='aboutme.AMQuestion'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='amresponsetopic',
            name='responseUser',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='shgroup.ProjectUser'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='amresponsetopic',
            name='topicName',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]