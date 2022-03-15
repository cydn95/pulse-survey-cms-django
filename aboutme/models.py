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
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import User

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

    class Meta:
         indexes = [
             models.Index(fields=['created_at']),
         ]

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
        # old = AMResponseAcknowledgement.objects.get(pk=self.id)
        super(AMResponseAcknowledgement, self).save(*args, **kwargs)

        # check if this user receive email today
        start = now().date() - timedelta(days=1)
        end = now().date()

        try:
            commentProjectUserResponse = AMResponse.objects.get(id=self.amResponse.id)
            commentProjectUser = ProjectUser.objects.get(id=commentProjectUserResponse.projectUser.id)
            ackCountToday = AMResponseAcknowledgement.objects.filter(
                acknowledgeStatus__range=[1, 6], updated_at__range=[start, end], amResponse__projectUser__id=commentProjectUser.id).count()
            print('actcount', ackCountToday)
            print('start', start)
            print('end', end)
            print('commentProjectUser.id', commentProjectUser.id)
            flagCountToday = AMResponseAcknowledgement.objects.filter(
                flagStatus__range=[1, 5], updated_at__range=[start, end], amResponse__projectUser__id=commentProjectUser.id).count()

            userInfo = User.objects.get(id=commentProjectUser.user.id)
            ackProjectUser = ProjectUser.objects.get(id=self.projectUser.id)
            ackUserInfo = User.objects.get(id=ackProjectUser.user.id)
            pulseQuestion = AMQuestion.objects.get(
                id=commentProjectUserResponse.amQuestion.id).questionText
            pulseAnswer = commentProjectUserResponse.topicValue
            surveyName = Survey.objects.get(
                id=commentProjectUserResponse.survey.id).surveyTitle
            ackText = ""
            if self.acknowledgeStatus == 1:
                ackText = "Thanks for sharing"
            elif self.acknowledgeStatus == 2:
                ackText = "Great idea"
            elif self.acknowledgeStatus == 3:
                ackText = "Working on it"
            elif self.acknowledgeStatus == 4:
                ackText = "Let's talk about it"
            elif self.acknowledgeStatus == 5:
                ackText = "I agree"
            elif self.acknowledgeStatus == 6:
                ackText = "Tell us more"
            # if yes, form2
            # if no,
            # if you receive 1 more after the last email today,
            # form1
            # if no,
            # form3
            if ackCountToday >= 1:
                image_path_logo = os.path.join(
                    settings.STATIC_ROOT, 'email', 'img', 'logo-2.png')
                image_name_logo = Path(image_path_logo).name
                image_path_star = os.path.join(
                    settings.STATIC_ROOT, 'email', 'img', 'star.png')
                image_name_star = Path(image_path_star).name

                subject = "Pulse"
                message = get_template('ackform2.html').render(
                    {
                        "project_name": "Pulse",
                        "survey_name": surveyName,
                        "image_name_logo": image_name_logo,
                        "image_name_star": image_name_star,
                        "first_name": userInfo.first_name,
                        "last_name": userInfo.last_name,
                        "site_url": settings.SITE_URL,
                        "pulse_question": pulseQuestion,
                        "pulse_answer": pulseAnswer,
                        "ack_first_name": ackUserInfo.first_name,
                        "ack_last_name": ackUserInfo.last_name,
                        "ack_text": ackText
                    }
                )
                email_from = settings.DEFAULT_FROM_EMAIL
                recipient_list = [userInfo.email]

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

            if flagCountToday >= 1:
                image_path_logo = os.path.join(
                    settings.STATIC_ROOT, 'email', 'img', 'logo-2.png')
                image_name_logo = Path(image_path_logo).name
                image_path_star = os.path.join(
                    settings.STATIC_ROOT, 'email', 'img', 'star.png')
                image_name_star = Path(image_path_star).name

                subject = "Pulse"
                message = get_template('ackform2.html').render(
                    {
                        "project_name": "Pulse",
                        "survey_name": surveyName,
                        "image_name_logo": image_name_logo,
                        "image_name_star": image_name_star,
                        "first_name": userInfo.first_name,
                        "last_name": userInfo.last_name,
                        "site_url": settings.SITE_URL,
                        "pulse_question": pulseQuestion,
                        "pulse_answer": pulseAnswer,
                        "ack_first_name": ackUserInfo.first_name,
                        "ack_last_name": ackUserInfo.last_name,
                        "ack_text": ackText
                    }
                )
                email_from = settings.DEFAULT_FROM_EMAIL
                recipient_list = [userInfo.email]

                email = EmailMultiAlternatives(
                    subject=subject, body=message, from_email=email_from, to=recipient_list)
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
                    
        except AMResponse.DoesNotExist:
            print('Incorrect response id')
            return
                
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
