# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2021-06-22 03:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0022_auto_20200828_0149'),
        ('shgroup', '0039_projectuser_shtype'),
    ]

    operations = [
        migrations.CreateModel(
            name='SHType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shTypeName', models.CharField(blank=True, max_length=50)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Survey')),
            ],
        ),
	migrations.RemoveField(
	    model_name='projectuser',
	    name='shType',
	),
        migrations.AddField(
            model_name='projectuser',
            name='shType',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shgroup.SHType', verbose_name='SHType'),
        ),
    ]