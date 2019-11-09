from django.db import models

# Create your models here.
class Option(models.Model):
    optionName = models.CharField(max_length=255)

    def __str__(self):
        return self.optionName