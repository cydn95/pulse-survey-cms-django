from django.db import models
from survey.models import Survey

# Create your models here.
class Option(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    optionName = models.CharField(max_length=255)

    def __str__(self):
        return self.optionName

class SkipOption(models.Model):
    optionName = models.CharField(max_length=255)

    def __str__(self):
        return self.optionName
