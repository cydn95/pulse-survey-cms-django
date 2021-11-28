import os
from pathlib import Path
from email.mime.image import MIMEImage
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.conf import settings
from django.contrib import messages
from django.db import models
from survey.models import Survey, Driver, Project
from setting.models import ControlType
from shgroup.models import SHGroup, ProjectUser
from option.models import Option, SkipOption
from page_setting.models import PageSetting
from django.contrib.auth.models import User
from django.forms.models import ModelForm
from django.forms.widgets import CheckboxSelectMultiple
from django import forms
from django.utils import timezone
from smtplib import SMTPException

class AMQuestion(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    subdriver = models.CharField(max_length=50, blank=True)
    questionText = models.CharField(max_length=1000)
    controlType = models.ForeignKey(ControlType)
    questionSequence = models.PositiveIntegerField(default=5)
    sliderTextLeft = models.CharField(max_length=50, blank=True)
    sliderTextRight = models.CharField(max_length=50, blank=True)
    skipOptionYN = models.BooleanField(default=True)
    topicPrompt = models.CharField(max_length=255, blank=True)
    commentPrompt = models.CharField(max_length=255, blank=True)
    shGroup = models.ManyToManyField(SHGroup, blank=True)
    option = models.ManyToManyField(Option, blank=True)
    skipOption = models.ManyToManyField(SkipOption, blank=True)
    amqOrder = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name='Order')
    shortForm = models.BooleanField(default=False)
    longForm = models.BooleanField(default=False)
    isStandard = models.BooleanField(default=False)

    class Meta(object):
        ordering = ['amqOrder']

    def __str__(self):
        return self.questionText

class AMQuestionForm(ModelForm):
    shGroup = forms.ModelMultipleChoiceField(queryset=SHGroup.objects.all(), required=False)
    option = forms.ModelMultipleChoiceField(queryset=Option.objects.all(), required=False)
    skipOption = forms.ModelMultipleChoiceField(queryset=SkipOption.objects.all(), required=False)

class AMQuestionSHGroup(models.Model):
    shGroup = models.ForeignKey(SHGroup, on_delete=models.CASCADE)
    amQuestion = models.ForeignKey(AMQuestion, on_delete=models.CASCADE)

class AMQuestionOption(models.Model):
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    amQuestion = models.ForeignKey(AMQuestion, on_delete=models.CASCADE)

class AMQuestionSkipOption(models.Model):
    skipOption = models.ForeignKey(SkipOption, on_delete=models.CASCADE)
    amQuestion = models.ForeignKey(AMQuestion, on_delete=models.CASCADE)
    
class AMResponse(models.Model):
    projectUser = models.ForeignKey(ProjectUser, on_delete=models.CASCADE, related_name="amProjectUser")
    subProjectUser = models.ForeignKey(ProjectUser, on_delete=models.CASCADE, related_name="amSubProjectUser")
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    amQuestion = models.ForeignKey(AMQuestion, on_delete=models.CASCADE, verbose_name='Question')
    controlType = models.CharField(max_length=30)
    integerValue = models.PositiveIntegerField(blank=True, verbose_name='Answer(Int)')
    topicValue = models.TextField(blank=True, verbose_name='Answer(Text)')
    commentValue = models.TextField(blank=True, verbose_name='Description')
    skipValue = models.TextField(blank=True, verbose_name='Answer(Skip)')
    topicTags = models.TextField(blank=True)
    commentTags = models.TextField(blank=True)
    latestResponse = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AMResponseAcknowledgement(models.Model):
    amResponse = models.ForeignKey(AMResponse, on_delete=models.CASCADE)
    projectUser = models.ForeignKey(
        ProjectUser, on_delete=models.CASCADE, related_name="amCommentProjectUser")
    likeStatus = models.PositiveIntegerField(default=0, blank=False, null=False)    # 0: no answer, 1: like, 2: dislike

    # 0: no answer, 1: thanks for sharing, 2: Great idea, 3: Working on it, 4: Let's talk about it, 5: I agree, 6: Tell us more
    acknowledgeStatus = models.PositiveIntegerField(
        default=0, blank=False, null=False)
    flagStatus = models.PositiveIntegerField(
        default=0, blank=False, null=False)     # 0: no answer, 1: Individual can be identified, 2: Commenter can be identified, 3: Non-Constructive Feedback, 4: Out of Policy, 5: Aggressive or Hostile
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super(AMResponseAcknowledgement, self).save(*args, **kwargs)

        image_path_logo = os.path.join(
            settings.STATIC_ROOT, 'email', 'img', 'logo-2.png')
        image_name_logo = Path(image_path_logo).name
        image_path_star = os.path.join(
            settings.STATIC_ROOT, 'email', 'img', 'star.png')
        image_name_star = Path(image_path_star).name

        subject = "Test"
        message = get_template('ackform2.html').render(
            {
                "project_name": "test project",
                "survey_name": "test survey",
                "image_name_logo": image_name_logo,
                "image_name_star": image_name_star,
                "token": "test_token",
                "email": "test@test.com",
                "first_name": "first name",
                "last_name": "last name",
                "site_url": settings.SITE_URL
            }
        )
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = ['dt897867@gmail.com', 'mike.smith@projectai.com']

        email = EmailMultiAlternatives(subject=subject, body=message, from_email=email_from, to=recipient_list)
        email.attach_alternative(message, "text/html")
        email.content_subtype = "html"
        email.mixed_subtype = "related"

        with open(image_path_logo, mode='rb') as f_logo:
            image_logo = MIMEImage(f_logo.read())
            email.attach(image_logo)
            image_logo.add_header('Content-ID', f"<{image_name_logo}>")
        with open(image_path_star, mode='rb') as f_star:
            image_star = MIMEImage(f_star.read())
            email.attach(image_star)
            image_star.add_header('Content-ID', f"<{image_name_star}>")

        try:
            email.send()
        except SMTPException as e:
            print('There was an error sending an email: ', e)
                
class AMResponseTopic(models.Model):
    amQuestion = models.ForeignKey(AMQuestion, on_delete=models.CASCADE)
    responseUser = models.ForeignKey(ProjectUser, on_delete=models.CASCADE)
    topicName = models.CharField(max_length=255, blank=True)
    topicComment = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class PageAMQuestion(models.Model):
    pageSetting = models.ForeignKey(PageSetting, related_name="ampagesetting", on_delete=models.SET_NULL, default=None, blank=True, null=True)
    amQuestion = models.ForeignKey(AMQuestion, on_delete=models.CASCADE)
