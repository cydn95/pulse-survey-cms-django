# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-05-28 03:26
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0008_auto_20200525_0152'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shgroup', '0019_auto_20200520_2015'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectuser',
            name='survey',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='survey.Survey'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='projectuser',
            unique_together=set([]),
        ),
    ]
