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
class AMQuestion(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT)
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT)
    subdriver = models.CharField(max_length=50, blank=True)
    questionText = models.CharField(max_length=1000)
    controlType = models.ForeignKey(ControlType, on_delete=models.PROTECT)
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

class AMQuestionForm(ModelForm):

    # here we only need to define the field we want to be editable
    shGroup = forms.ModelMultipleChoiceField(queryset=SHGroup.objects.all(), required=False)
    option = forms.ModelMultipleChoiceField(queryset=Option.objects.all(), required=False)
    skipOption = forms.ModelMultipleChoiceField(queryset=SkipOption.objects.all(), required=False)

class AMQuestionSHGroup(models.Model):
    shGroup = models.ForeignKey(SHGroup, on_delete=models.PROTECT)
    amQuestion = models.ForeignKey(AMQuestion, on_delete=models.PROTECT)

class AMQuestionOption(models.Model):
    option = models.ForeignKey(Option, on_delete=models.PROTECT)
    amQuestion = models.ForeignKey(AMQuestion, on_delete=models.PROTECT)

class AMQuestionSkipOption(models.Model):
    skipOption = models.ForeignKey(SkipOption, on_delete=models.PROTECT)
    amQuestion = models.ForeignKey(AMQuestion, on_delete=models.PROTECT)
    
class AMResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="amUser")
    subjectUser = models.ForeignKey(User, on_delete=models.PROTECT, related_name="amSubjectUser")
    survey = models.ForeignKey(Survey, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    amQuestion = models.ForeignKey(AMQuestion, on_delete=models.PROTECT, verbose_name='Question')
    controlType = models.CharField(max_length=30)
    integerValue = models.PositiveIntegerField(blank=True, verbose_name='Answer(Int)')
    topicValue = models.TextField(blank=True, verbose_name='Answer(Text)')
    commentValue = models.TextField(blank=True, verbose_name='Description')
    skipValue = models.TextField(blank=True, verbose_name='Answer(Skip)')
    topicTags = models.TextField(blank=True)
    commentTags = models.TextField(blank=True)

class AMResponseTopic(models.Model):
    # amResponse = models.ForeignKey(AMResponse, on_delete=models.PROTECT)
    AMQuestion = models.ForeignKey(AMQuestion, on_delete=models.PROTECT)
    responseUser = models.ForeignKey(ProjectUser, on_delete=models.PROTECT)
    topicName = models.CharField(max_length=255, blank=True)

class PageAMQuestion(models.Model):
    pageSetting = models.ForeignKey(PageSetting, related_name="ampagesetting", on_delete=models.SET_NULL, default=None, blank=True, null=True)
    amQuestion = models.ForeignKey(AMQuestion, on_delete=models.PROTECT)
