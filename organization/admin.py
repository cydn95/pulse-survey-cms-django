from django.contrib import admin
from .models import Organization
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Organization
from gremlin import deleteVertex

class OrganizationInline(admin.StackedInline):
    model = Organization
    can_delete = False
    verbose_name_plural = 'organization'

class UserAdmin(BaseUserAdmin):
    inlines = (OrganizationInline,)

# Register your models here.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)