# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-10-30 04:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shgroup', '0002_auto_20191029_2107'),
        ('aboutme', '0003_auto_20191019_0916'),
    ]

    operations = [
        migrations.AddField(
            model_name='amquestion',
            name='shGroup',
            field=models.ManyToManyField(blank=True, null=True, to='shgroup.SHGroup'),
        ),
        migrations.AlterField(
            model_name='amquestion',
            name='controlType',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='setting.ControlType'),
        ),
        migrations.AlterField(
            model_name='amquestion',
            name='driver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='survey.Driver'),
        ),
        migrations.AlterField(
            model_name='amquestion',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='survey.Survey'),
        ),
        migrations.AlterField(
            model_name='amquestionshgroup',
            name='amQuestion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='aboutme.AMQuestion'),
        ),
        migrations.AlterField(
            model_name='amquestionshgroup',
            name='shGroup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shgroup.SHGroup'),
        ),
        migrations.AlterField(
            model_name='amresponse',
            name='amQuestion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='aboutme.AMQuestion'),
        ),
        migrations.AlterField(
            model_name='amresponse',
            name='subjectUser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='amSubjectUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='amresponse',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='survey.Survey'),
        ),
        migrations.AlterField(
            model_name='amresponse',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='amUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='amresponsetopic',
            name='amResponse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='aboutme.AMResponse'),
        ),
    ]
