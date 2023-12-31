# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2021-01-05 16:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0022_auto_20200828_0149'),
        ('aboutme', '0021_amresponsesentiment'),
    ]

    operations = [
        migrations.CreateModel(
            name='AMResponseAcknowledgement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actionText', models.CharField(max_length=10)),
                ('amResponse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aboutme.AMResponse')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Project')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Survey')),
            ],
        ),
    ]
