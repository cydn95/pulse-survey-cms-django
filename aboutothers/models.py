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

# Create your models here.
class AOQuestion(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT)
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT)
    subdriver = models.CharField(max_length=50, blank=True)
    questionText = models.CharField(max_length=1000)
    controlType = models.ForeignKey(ControlType)
    questionSequence = models.PositiveIntegerField(default=5)
    sliderTextLeft = models.CharField(max_length=50, blank=True)
    sliderTextRight = models.CharField(max_length=50, blank=True)
    skipOptionYN = models.BooleanField(default=True)
    skipResponses = models.CharField(max_length=1000, blank=True)
    topicPrompt = models.CharField(max_length=255, blank=True)
    commentPrompt = models.CharField(max_length=255, blank=True)
    shGroup = models.ManyToManyField(SHGroup, blank=True)
    option = models.ManyToManyField(Option, blank=True)
    skipOption = models.ManyToManyField(SkipOption, blank=True)

    def __str__(self):
        return self.questionText

class AOQuestionForm(ModelForm):
    shGroup = forms.ModelMultipleChoiceField(queryset=SHGroup.objects.all(), required=False)
    option = forms.ModelMultipleChoiceField(queryset=Option.objects.all(), required=False)
    skipOption = forms.ModelMultipleChoiceField(queryset=SkipOption.objects.all(), required=False)

class AOQuestionSHGroup(models.Model):
    aoQuestion = models.ForeignKey(AOQuestion, on_delete=models.PROTECT)
    shGroup = models.ForeignKey(SHGroup, on_delete=models.PROTECT)

class AOQuestionOption(models.Model):
    option = models.ForeignKey(Option, on_delete=models.PROTECT)
    aoQuestion = models.ForeignKey(AOQuestion, on_delete=models.PROTECT)
    
class AOQuestionSkipOption(models.Model):
    skipOption = models.ForeignKey(SkipOption, on_delete=models.PROTECT)
    aoQuestion = models.ForeignKey(AOQuestion, on_delete=models.PROTECT)

class AOResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="aoUser")
    subjectUser = models.ForeignKey(User, on_delete=models.PROTECT, related_name="aoSubjectUser")
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    aoQuestion = models.ForeignKey(AOQuestion, on_delete=models.PROTECT)
    controlType = models.CharField(max_length=30)
    integerValue = models.PositiveIntegerField(blank=True)
    topicValue = models.TextField(blank=True)
    commentValue = models.TextField(blank=True)
    skipValue = models.TextField(blank=True)
    topicTags = models.TextField(blank=True)
    commentTags = models.TextField(blank=True)

class AOResponseTopic(models.Model):
    aoQuestion = models.ForeignKey(AOQuestion, on_delete=models.PROTECT)
    responseUser = models.ForeignKey(ProjectUser, on_delete=models.PROTECT)
    topicName = models.CharField(max_length=255, blank=True)
    topicComment = models.CharField(max_length=255, blank=True)
    
class AOPage(models.Model):
    aoPageName = models.CharField(max_length=50)
    aoPageSequence = models.PositiveIntegerField()

    def __str__(self):
        return self.aoPageName

class PageAOQuestion(models.Model):
    #pageSetting = models.ForeignKey(PageSetting, on_delete=models.PROTECT)
    pageSetting = models.ForeignKey(PageSetting, related_name="aopagesetting", on_delete=models.SET_NULL, default=None, blank=True, null=True)
    aoQuestion = models.ForeignKey(AOQuestion, on_delete=models.PROTECT)