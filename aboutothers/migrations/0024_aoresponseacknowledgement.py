# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2021-01-14 01:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0022_auto_20200828_0149'),
        ('aboutothers', '0023_aoresponsesentiment'),
    ]

    operations = [
        migrations.CreateModel(
            name='AOResponseAcknowledgement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actionText', models.CharField(max_length=10)),
                ('actionType', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('aoResponse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aboutothers.AOResponse')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Project')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Survey')),
            ],
        ),
    ]
