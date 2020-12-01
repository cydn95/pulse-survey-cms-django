from django.contrib import admin
from .models import Organization, UserAvatar, UserTitle, UserTeam, UserGuideMode
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ValidationError

from django import forms
from django.core.files.images import get_image_dimensions


class UserAvatarInline(admin.StackedInline):
    model = UserAvatar
    can_delete = False
    verbose_name_plural = 'avatar'
    template = 'admin/user/stacked.html'

class OrganizationInline(admin.StackedInline):
    model = Organization
    can_delete = False
    verbose_name_plural = 'organization'
    template = 'admin/user/stacked.html'

class UserTitleInline(admin.StackedInline):
    model = UserTitle
    can_delete = False
    verbose_name_plural = 'Job Title'
    template = 'admin/user/stacked.html'

class UserTeamInline(admin.StackedInline):
    model = UserTeam
    can_delete = False
    verbose_name_plural = 'Department'
    template = 'admin/user/stacked.html'

class UserTeamInline(admin.StackedInline):
    model = UserTeam
    can_delete = False
    verbose_name_plural = 'Department'
    template = 'admin/user/stacked.html'

class UserGuideModeInline(admin.StackedInline):
    model = UserGuideMode
    can_delete = False
    verbose_name_plural = 'Guide Mode'
    template = 'admin/user/stacked.html'

class EmailRequiredMixin(object):
    def __init__(self, *args, **kwargs):
        super(EmailRequiredMixin, self).__init__(*args, **kwargs)
        # make user email field required

        self.fields['email'].required = True

class MyUserCreationForm(EmailRequiredMixin, UserCreationForm):
    def clean_email(self):

        email = self.cleaned_data['email']

        if User.objects.filter(email=email.lower()).exists():
            raise ValidationError("Email already exists ya", code='invalid')
        
        return email

class MyUserChangeForm(EmailRequiredMixin, UserChangeForm):
    pass

class UserAdmin(BaseUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_per_page = 10
    
    BaseUserAdmin.exclude = ('username',)
    BaseUserAdmin.list_display = ('email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff', 'is_superuser')
    BaseUserAdmin.fieldsets = (
        # (None, {'fields': ('username', 'email', 'password')}),
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    BaseUserAdmin.add_fieldsets = (
        (None, {
            'description': (
                "Enter the new user's email address and click save."
            ),
            # 'fields': ('email', 'username', 'password1', 'password2'),
            'fields': ('email', 'password1', 'password2'),
        }),
        # ('Password', {
        #     'description': "Optionally, you may set the user's password here.",
        #     'fields': ('password1', 'password2'),
        #     'classes': ('collapse', 'collapse-closed'),
        # }),
    )
    # inlines = (OrganizationInline, UserAvatarInline, UserTitleInline, UserTeamInline, UserGuideModeInline)
    inlines = (OrganizationInline, UserAvatarInline, UserTitleInline, UserTeamInline)

# Register your models here.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)