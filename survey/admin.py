from django.contrib import admin
from .models import Survey, Client, Project, Driver, ConfigPage, NikelMobilePage
#from gremlin import deleteVertex
from adminsortable2.admin import SortableAdminMixin
from django.utils.html import format_html
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

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

    def get_queryset(self, request):
        self.full_path = request.get_full_path()
        return super(ClientAdmin, self).get_queryset(request)

    def client_actions(self, obj):
        return format_html(
            mark_safe('<a class="button" href="{}project">Add Project</a>'.format(self.full_path)),
        )
        client_actions.short_description = 'Client Actions'
        client_actions.allow_tags = True

class NikelMobilePageAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['pageOrder', 'project', 'pageName', 'pageText']
    list_display_links = ['pageName']
    model = NikelMobilePage

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        project = form.base_fields['project']

        project.widget.can_add_related = False
        project.widget.can_change_related = False
        project.widget.can_delete_related = False

        return form

# Register your models here.
admin.site.register(Survey)
admin.site.register(Client, ClientAdmin)
admin.site.register(ConfigPage)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(NikelMobilePage, NikelMobilePageAdmin)