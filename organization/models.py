from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save, post_init
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib import messages
from django.core.exceptions import ValidationError

#from gremlin import addVertex

def email_validator(email):
    print('email validation')
    if User.objects.filter(email=email.lower()).exists():
        raise ValidationError("Email already exists ya", code='invalid')

User._meta.get_field('email')._unique = True
User._meta.get_field('email')._validators = [email_validator]

class UserAvatar(models.Model):
    user = models.OneToOneField(User, unique=True, related_name='avatar', on_delete=models.CASCADE)
    name = models.ImageField(upload_to='uploads/user', verbose_name='Avatar', blank=True)

    def save(self, *args, **kwargs):
        super(UserAvatar, self).save(*args, **kwargs)

class UserTitle(models.Model):
    user = models.OneToOneField(User, unique=True, related_name='usertitle', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name='Job Title', blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super(UserTitle, self).save(*args, **kwargs)

class UserTeam(models.Model):
    user = models.OneToOneField(User, unique=True, related_name='userteam', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name='Department', blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super(UserTeam, self).save(*args, **kwargs)

# Create your models here.
class Organization(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, verbose_name='Organization', blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Organization, self).save(*args, **kwargs)

class UserGuideMode(models.Model):
    user = models.OneToOneField(User, unique=True, related_name='guidemode', on_delete=models.CASCADE)
    name = models.BooleanField(default=True, verbose_name='Guide Mode')
    
    def save(self, *args, **kwargs):
        super(UserGuideMode, self).save(*args, **kwargs)

# @receiver(post_init, sender=User)
# def validation_email(sender, instance, **kwargs):
#     print("POST_INIT", instance)
#     instance.email = instance.email.lower()

@receiver(pre_save, sender=User)
def check_email(sender, instance, **kwargs):
    instance.full_clean()
    instance.username = instance.email.lower()
    instance.email = instance.email.lower()

    if User.objects.filter(email=instance.email.lower()).count():
        raise ValidationError('Duplicate email', code='invalid')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)