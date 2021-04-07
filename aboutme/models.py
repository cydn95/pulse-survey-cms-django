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

# Create your models here.
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
    #skipResponses = models.CharField(max_length=1000, blank=True)
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
    # here we only need to define the field we want to be editable
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
    # update user, subjectuser to projectUser, subjectProjectUser     2020-05-20
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="amUser")
    # subjectUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="amSubjectUser")
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
    # new field for history 2021-04-01
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

# # working
# # 1: like
# # 2: dislike
# # 3: Thanks for sharing
# # 4: Great idea
# # 5: Working on it
# # 6: Would love to talk in person
# # 7: I agree
# # 8: 
# class AMResponseAcknowledgement(models.Model):
#     amResponse = models.ForeignKey(AMResponse, on_delete=models.CASCADE)
#     # survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
#     # project = models.ForeignKey(Project, on_delete=models.CASCADE)
#     actionText = models.CharField(max_length=10)
#     actionType = models.PositiveIntegerField(default=0, blank=False, null=False)
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

class AMResponseSentiment(models.Model):
    amResponse = models.ForeignKey(AMResponse, on_delete=models.CASCADE)
    sentiment = models.CharField(max_length=30, blank=True)
    positiveValue = models.FloatField(blank=True)
    neutralValue = models.FloatField(blank=True)
    negativeValue = models.FloatField(blank=True)
    mixedValue = models.FloatField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AMResponseTopic(models.Model):
    # amResponse = models.ForeignKey(AMResponse, on_delete=models.CASCADE)
    amQuestion = models.ForeignKey(AMQuestion, on_delete=models.CASCADE)
    responseUser = models.ForeignKey(ProjectUser, on_delete=models.CASCADE)
    topicName = models.CharField(max_length=255, blank=True)
    topicComment = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class PageAMQuestion(models.Model):
    pageSetting = models.ForeignKey(PageSetting, related_name="ampagesetting", on_delete=models.SET_NULL, default=None, blank=True, null=True)
    amQuestion = models.ForeignKey(AMQuestion, on_delete=models.CASCADE)
