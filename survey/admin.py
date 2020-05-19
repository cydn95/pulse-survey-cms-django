from django.contrib import admin
from .models import Survey, Client, Project, Driver, Page
#from gremlin import deleteVertex
from adminsortable2.admin import SortableAdminMixin
from django.utils.html import format_html
from django.core.urlresolvers import reverse

class ProjectAdmin(admin.ModelAdmin):

    # Search
    search_fields = ['projectName']
    # Filter
    list_filter = ['projectName']
    # list
    list_display = ['projectName']
    # Edit
    #list_editable = ['projectName']

    model = Project
    # actions = ['delete_model']

    # def delete_model(self, request, obj):
        
    #     #print("before delete")
    #     if obj.id is not None:
    #         id = 'project-{0}'.format(obj.id)
    #         deleteVertex(id)
    #     obj.delete()
    #     #print("after delete")
        
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
admin.site.register(Page)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Driver, DriverAdmin)