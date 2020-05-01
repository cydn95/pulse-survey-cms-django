from django.contrib import admin
from .models import Survey, Client, Project, Driver
#from gremlin import deleteVertex
from adminsortable2.admin import SortableAdminMixin

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

# Register your models here.
admin.site.register(Survey)
admin.site.register(Client)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Driver, DriverAdmin)