# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-10-10 10:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('setting', '0001_initial'),
        ('shgroup', '0001_initial'),
        ('survey', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AOPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aoPageName', models.CharField(max_length=50)),
                ('aoPageSequence', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='AOQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subdriver', models.CharField(max_length=50)),
                ('questionText', models.CharField(max_length=1000)),
                ('sliderTextLeft', models.CharField(max_length=50)),
                ('sliderTextRight', models.CharField(max_length=50)),
                ('skipOptionYN', models.BooleanField(default=True)),
                ('skipResponses', models.CharField(max_length=1000)),
                ('questionSequence', models.PositiveIntegerField()),
                ('topicPrompt', models.CharField(max_length=255)),
                ('commentPrompt', models.CharField(max_length=255)),
                ('controlType', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='setting.ControlType')),
                ('driver', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='survey.Driver')),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='survey.Survey')),
            ],
        ),
        migrations.CreateModel(
            name='AOQuestionSHGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aoQuestion', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='aboutothers.AOQuestion')),
                ('shGroup', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='shgroup.SHGroup')),
            ],
        ),
        migrations.CreateModel(
            name='AOResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('integerValue', models.PositiveIntegerField()),
                ('topicValue', models.TextField()),
                ('commentValue', models.TextField()),
                ('skipValue', models.TextField()),
                ('topicTags', models.TextField()),
                ('commentTags', models.TextField()),
                ('aoQuestion', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='aboutothers.AOQuestion')),
                ('subjectUser', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='aoSubjectUser', to=settings.AUTH_USER_MODEL)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='survey.Survey')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='aoUser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AOResponseTopic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=100)),
                ('comment', models.CharField(max_length=1000)),
                ('aoResponse', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='aboutothers.AOResponse')),
            ],
        ),
    ]
