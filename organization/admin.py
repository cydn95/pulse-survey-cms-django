from django.contrib import admin
from .models import Organization
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import Organization
from gremlin import deleteVertex

class OrganizationInline(admin.StackedInline):
    model = Organization
    can_delete = False
    verbose_name_plural = 'organization'

class EmailRequiredMixin(object):
    def __init__(self, *args, **kwargs):
        super(EmailRequiredMixin, self).__init__(*args, **kwargs)
        # make user email field required
        self.fields['email'].required = True

class MyUserCreationForm(EmailRequiredMixin, UserCreationForm):
    pass
        
class MyUserChangeForm(EmailRequiredMixin, UserChangeForm):
    pass

class UserAdmin(BaseUserAdmin):
    form = MyUserCreationForm
    add_form = MyUserCreationForm
    BaseUserAdmin.list_display = ('email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff')
    BaseUserAdmin.fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    inlines = (OrganizationInline,)

# Register your models here.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)