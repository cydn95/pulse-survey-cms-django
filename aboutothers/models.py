from django.db import models
from survey.models import Survey, Driver, Project
from setting.models import ControlType
from shgroup.models import SHGroup, ProjectUser, SHCategory
from option.models import Option, SkipOption
from page_setting.models import PageSetting
from django.contrib.auth.models import User
from django.forms.models import ModelForm
from django.forms.widgets import CheckboxSelectMultiple
from django import forms
from django.utils import timezone

class AOQuestion(models.Model):
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
    aoqOrder = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name='Order')
    shortForm = models.BooleanField(default=False)
    longForm = models.BooleanField(default=False)
    isStandard = models.BooleanField(default=False)
    
    class Meta(object):
        ordering = ['aoqOrder']
        
    def __str__(self):
        return self.questionText

class AOQuestionForm(ModelForm):
    shGroup = forms.ModelMultipleChoiceField(queryset=SHGroup.objects.all(), required=False)
    option = forms.ModelMultipleChoiceField(queryset=Option.objects.all(), required=False)
    skipOption = forms.ModelMultipleChoiceField(queryset=SkipOption.objects.all(), required=False)

class AOQuestionSHGroup(models.Model):
    aoQuestion = models.ForeignKey(AOQuestion, on_delete=models.CASCADE)
    shGroup = models.ForeignKey(SHGroup, on_delete=models.CASCADE)

class AOQuestionOption(models.Model):
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    aoQuestion = models.ForeignKey(AOQuestion, on_delete=models.CASCADE)
    
class AOQuestionSkipOption(models.Model):
    skipOption = models.ForeignKey(SkipOption, on_delete=models.CASCADE)
    aoQuestion = models.ForeignKey(AOQuestion, on_delete=models.CASCADE)

class AOResponse(models.Model):
    projectUser = models.ForeignKey(ProjectUser, on_delete=models.CASCADE, related_name="aoProjectUser")
    subProjectUser = models.ForeignKey(ProjectUser, on_delete=models.CASCADE, related_name="aoSubProjectUser")
    shCategory = models.ForeignKey(SHCategory, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    aoQuestion = models.ForeignKey(AOQuestion, on_delete=models.CASCADE)
    controlType = models.CharField(max_length=30)
    integerValue = models.PositiveIntegerField(blank=True)
    topicValue = models.TextField(blank=True)
    commentValue = models.TextField(blank=True)
    skipValue = models.TextField(blank=True)
    topicTags = models.TextField(blank=True)
    commentTags = models.TextField(blank=True)
    latestResponse = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AOResponseAcknowledgement(models.Model):
    aoResponse = models.ForeignKey(AOResponse, on_delete=models.CASCADE)
    projectUser = models.ForeignKey(
        ProjectUser, on_delete=models.CASCADE, related_name="aoCommentProjectUser")
    likeStatus = models.PositiveIntegerField(default=0, blank=False, null=False)    # 0: no answer, 1: like,  2: dislike
    # 0: no answer, 1: thanks for sharing, 2: Great idea, 3: Working on it, 4: Let's talk about it, 5: I agree, 6: Tell us more
    acknowledgeStatus = models.PositiveIntegerField(
        default=0, blank=False, null=False)
    flagStatus = models.PositiveIntegerField(
        default=0, blank=False, null=False)    # 0: no answer, 1: Individual can​ be identified,  2: Commenter can​ be identified, 3: Non-Constructive​ Feedback, 4: Out of Policy, 5: Aggressive or​ Hostile​

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# class AOResponseSentiment(models.Model):
#     aoResponse = models.ForeignKey(AOResponse, on_delete=models.CASCADE)
#     sentiment = models.CharField(max_length=30, blank=True)
#     positiveValue = models.FloatField(blank=True)
#     neutralValue = models.FloatField(blank=True)
#     negativeValue = models.FloatField(blank=True)
#     mixedValue = models.FloatField(blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

class AOResponseTopic(models.Model):
    aoQuestion = models.ForeignKey(AOQuestion, on_delete=models.CASCADE)
    responseUser = models.ForeignKey(ProjectUser, on_delete=models.CASCADE)
    topicName = models.CharField(max_length=255, blank=True)
    topicComment = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class AOPage(models.Model):
    aoPageName = models.CharField(max_length=50)
    aoPageSequence = models.PositiveIntegerField()

    def __str__(self):
        return self.aoPageName

class PageAOQuestion(models.Model):
    pageSetting = models.ForeignKey(PageSetting, related_name="aopagesetting", on_delete=models.SET_NULL, default=None, blank=True, null=True)
    aoQuestion = models.ForeignKey(AOQuestion, on_delete=models.CASCADE)
