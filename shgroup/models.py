import os
from pathlib import Path
from email.mime.image import MIMEImage
from django.contrib.postgres.fields import JSONField
from django.db import models
from survey.models import Project, Survey
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from team.models import Team
from django.forms.models import ModelForm
from django.forms.widgets import CheckboxSelectMultiple
from django import forms
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.conf import settings
from django.contrib import messages
from django.utils.safestring import mark_safe

class InegerPercentageField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)
    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(InegerPercentageField, self).formfield(**defaults)

class SHGroup(models.Model):
    SHGroupName = models.CharField(max_length=255)
    SHGroupAbbrev = models.CharField(max_length=50, blank=True)
    responsePercent = InegerPercentageField(
        default=0, min_value=0, max_value=100, verbose_name='Throttle % Response')        # newly added record
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

    def __str__(self):
        return self.SHGroupName

class MapType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
        
class SHCategory(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    SHCategoryName = models.CharField(max_length=50, blank=True)
    SHCategoryDesc = models.CharField(max_length=200, blank=True)
    mapType = models.ForeignKey(MapType, on_delete=models.PROTECT)
    colour = models.CharField(max_length=50, blank=True)
    icon = models.FileField(upload_to='uploads/shcategory', blank=True)
    
    def __str__(self):
        return self.SHCategoryName

class ProjectUser(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    projectUserTitle = models.CharField(max_length=50, blank=True, verbose_name='Project Title', help_text='Role / Title of the stakeholder on this Project')
    team = models.ForeignKey(Team, null=True, blank=True, verbose_name='Project Team')
    shGroup = models.ForeignKey(SHGroup, null=True, blank=True, verbose_name='SHGroup')

    # added superuser toggle
    isSuperUser = models.BooleanField(
        default=False, verbose_name='Reveal Dashboards')

    isTeamMember = models.BooleanField(default=False)
    isCGroup1 = models.BooleanField(default=False)
    isCGroup2 = models.BooleanField(default=False)
    isCGroup3 = models.BooleanField(default=False)
    sendInvite = models.BooleanField(default=False)

    

    class Meta:
        unique_together = ['survey', 'user']

    def __str__(self):
        return '{0} - {1}'.format(self.survey, self.user.username)

    def save(self, *args, **kwargs):
        self.sendInvite = False

        # blocked sendinvite
        if not self.pk:
            self.sendInvite = True
        
        super(ProjectUser, self).save(*args, **kwargs)

        if self.sendInvite:
            project = Project.objects.get(id=self.survey.project.id)
            survey = Survey.objects.get(id=self.survey.id)
            user = User.objects.get(id=self.user.id)
            token = Token.objects.get(user_id=self.user.id)

            image_path_logo = os.path.join(settings.STATIC_ROOT, 'email', 'img', 'logo-2.png')
            image_name_logo = Path(image_path_logo).name
            image_path_container = os.path.join(settings.STATIC_ROOT, 'email', 'img', 'container.png')
            image_name_container = Path(image_path_container).name
            image_path_connect = os.path.join(settings.STATIC_ROOT, 'email', 'img', 'connect.png')
            image_name_connect = Path(image_path_connect).name

            subject = 'Welcome to Pulse'
            message = get_template('email.html').render(
                {
                    'project_name': project,
                    'survey_name': survey,
                    'image_name_logo': image_name_logo,
                    'image_name_container': image_name_container,
                    'image_name_connect': image_name_connect,
                    'token': token.key,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'site_url': settings.SITE_URL
                }
            )
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email,]

            email = EmailMultiAlternatives(subject=subject, body=message, from_email=email_from, to=recipient_list)
            email.attach_alternative(message, "text/html")
            email.content_subtype = 'html'
            email.mixed_subtype = 'related'

            with open(image_path_logo, mode='rb') as f_logo:
                image_logo = MIMEImage(f_logo.read())
                email.attach(image_logo)
                image_logo.add_header('Content-ID', f"<{image_name_logo}>")

            with open(image_path_connect, mode='rb') as f_connect:
                image_connect = MIMEImage(f_connect.read())
                email.attach(image_connect)
                image_connect.add_header('Content-ID', f"<{image_name_connect}>")

            email.send()

class KeyThemeUpDownVote(models.Model):
    keyTheme = models.TextField(default="", blank=False, null=False)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    tab = models.PositiveIntegerField(default=0)
    projectUser = models.ForeignKey(ProjectUser, on_delete=models.CASCADE)
    voteValue = models.IntegerField(blank=False, null=False)    # 1: upvote, -1: downvote

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SHMapping(models.Model):
    shCategory = models.ForeignKey(SHCategory, on_delete=models.CASCADE)
    projectUser = models.ForeignKey(ProjectUser, on_delete=models.CASCADE, related_name='projectUser')
    subProjectUser = models.ForeignKey(ProjectUser, on_delete=models.CASCADE, related_name='subProjectUser')
    relationshipStatus = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ['shCategory', 'projectUser', 'subProjectUser']
        
    def __str__(self):
        return '{0} - {1} - {2}'.format(self.shCategory, self.projectUser, self.subProjectUser)

class MyMapLayout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False)
    projectUser = models.ManyToManyField(ProjectUser, blank=True)
    layout_json = JSONField(default=dict, blank=True)

class ProjectMapLayout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False)
    projectUser = models.ManyToManyField(ProjectUser, blank=True)
    layout_json = JSONField(default=dict, blank=True)
