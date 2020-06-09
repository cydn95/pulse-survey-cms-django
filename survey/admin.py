from django.contrib import admin
from shgroup.models import ProjectUser, SHGroup, SHCategory
from aboutme.models import AMQuestion
from aboutothers.models import AOQuestion
from .models import Survey, Client, Project, Driver, ConfigPage, NikelMobilePage
#from gremlin import deleteVertex
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
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

class ProjectUserInline(admin.TabularInline):
    model = ProjectUser
    extra = 0

    readonly_fields = ['invite_button']
    fields = ('user', 'projectUserTitle', 'team', 'shGroup', 'invite_button')
 
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(ProjectUserInline, self).formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name in ['user', 'team', 'shGroup']:
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False

        return formfield

class DriverInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Driver
    extra = 0

class AMQuestionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = AMQuestion
    extra = 0

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(AMQuestionInline, self).formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name in ['driver', 'controlType', 'shGroup', 'option', 'skipOption']:
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False

        return formfield

class AOQuestionInline(SortableInlineAdminMixin, admin.TabularInline):
    model = AOQuestion
    extra = 0

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(AOQuestionInline, self).formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name in ['driver', 'controlType', 'shGroup', 'option', 'skipOption']:
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False

        return formfield

class SHGroupInline(admin.TabularInline):
    model = SHGroup
    extra = 0

class SHCategoryInline(admin.TabularInline):
    model = SHCategory
    extra = 0

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super(SHCategoryInline, self).formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name in ['mapType']:
            formfield.widget.can_add_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_delete_related = False

        return formfield

class ConfigPageInline(admin.StackedInline):
    model = ConfigPage
    extra = 0

class SurveyAdmin(admin.ModelAdmin):
    list_display = ['id', 'surveyTitle', 'get_client', 'project']
    search_fields = ['surveyTitle', 'project']
    list_filter = ['project', 'surveyTitle']

    def get_client(self, obj):
        return obj.project.client
    get_client.short_description = 'Client'
    get_client.admin_order_field = 'project__client'

    inlines = [
        ProjectUserInline,
        DriverInline,
        AMQuestionInline,
        AOQuestionInline,
        SHGroupInline,
        SHCategoryInline,
        ConfigPageInline
    ]

class ClientAdmin(admin.ModelAdmin):
    #list_display = ['clientName', 'client_actions']
    list_display = ['clientName']
    model = Client

    # def get_queryset(self, request):
    #     self.full_path = request.get_full_path()
    #     return super(ClientAdmin, self).get_queryset(request)

    # def client_actions(self, obj):
    #     return format_html(
    #         mark_safe('<a class="button" href="{}add">Add Project</a><a class="button" href="{}"></a>'.format(self.full_path)),
    #     )
    #     client_actions.short_description = 'Client Actions'
    #     client_actions.allow_tags = True

class NikelMobilePageAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['pageOrder', 'survey', 'pageName', 'pageText']
    list_display_links = ['pageName']
    model = NikelMobilePage

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        survey = form.base_fields['survey']

        survey.widget.can_add_related = False
        survey.widget.can_change_related = False
        survey.widget.can_delete_related = False

        return form

# Register your models here.
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(ConfigPage)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(NikelMobilePage, NikelMobilePageAdmin)