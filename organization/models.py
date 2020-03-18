from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
#from gremlin import addVertex

class UserAvatar(models.Model):
    user = models.OneToOneField(User, unique=True, related_name='avatar', on_delete=models.CASCADE)
    name = models.ImageField(upload_to='uploads/user', blank=True)

    def save(self, *args, **kwargs):
        super(UserAvatar, self).save(*args, **kwargs)

class UserTitle(models.Model):
    user = models.OneToOneField(User, unique=True, related_name='usertitle', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name
    
# Create your models here.
class Organization(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Organization, self).save(*args, **kwargs)
        #print(self.name)

        # if self.id is not None:
        #     data = [{
        #         'id': 'organization-{0}'.format(self.id),
        #         'label': 'organization_{0}'.format(self.id),
        #         'type': 'organization',
        #         'text': self.name
        #     }]
        #     #print(data)
        #     ret = addVertex(data)
        #     #print(ret)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)