from django.contrib import admin
from .models import Survey, Client, Project, Driver, ConfigPage
#from gremlin import deleteVertex
from adminsortable2.admin import SortableAdminMixin
from django.utils.html import format_html
from django.core.urlresolvers import reverse

class ProjectAdmin(admin.ModelAdmin):

    # Search
    search_fields = ['client', 'projectName']
    # Filter
    list_filter = ['client', 'projectName']
    # list
    list_display = ['client', 'projectName']
    # Edit
    #list_editable = ['projectName']

    model = Project
    # actions = ['delete_model']
        
class DriverAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass

class ClientAdmin(admin.ModelAdmin):
    list_display = ['clientName', 'client_actions']

    model = Client

    def client_actions(self, obj):
        return format_html(
            '<a class="button" href="">Add Project</a>',
        )
        client_actions.short_description = 'Client Actions'
        client_actions.allow_tags = True

# Register your models here.
admin.site.register(Survey)
admin.site.register(Client, ClientAdmin)
admin.site.register(ConfigPage)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Driver, DriverAdmin)