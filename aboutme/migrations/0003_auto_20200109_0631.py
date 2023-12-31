# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2020-01-09 14:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('aboutme', '0002_auto_20200109_0631'),
        ('option', '0001_initial'),
        ('setting', '0001_initial'),
        ('survey', '0001_initial'),
        ('shgroup', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='amquestionshgroup',
            name='shGroup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shgroup.SHGroup'),
        ),
        migrations.AddField(
            model_name='amquestionoption',
            name='amQuestion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='aboutme.AMQuestion'),
        ),
        migrations.AddField(
            model_name='amquestionoption',
            name='option',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='option.Option'),
        ),
        migrations.AddField(
            model_name='amquestion',
            name='controlType',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='setting.ControlType'),
        ),
        migrations.AddField(
            model_name='amquestion',
            name='driver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='survey.Driver'),
        ),
        migrations.AddField(
            model_name='amquestion',
            name='option',
            field=models.ManyToManyField(blank=True, to='option.Option'),
        ),
        migrations.AddField(
            model_name='amquestion',
            name='shGroup',
            field=models.ManyToManyField(blank=True, to='shgroup.SHGroup'),
        ),
        migrations.AddField(
            model_name='amquestion',
            name='skipOption',
            field=models.ManyToManyField(blank=True, to='option.SkipOption'),
        ),
        migrations.AddField(
            model_name='amquestion',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='survey.Survey'),
        ),
    ]
