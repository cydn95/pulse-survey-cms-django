from django.contrib import admin
from .models import SHGroup, SHCategory, SHMapping, ProjectUser, MapType#, ProjectUserForm
from jet.admin import CompactInline
#from gremlin import deleteVertex
from django.forms import CheckboxSelectMultiple
from django.contrib import messages

class SHGroupAdmin(admin.ModelAdmin):
    fieldset = [
        (None, {'fields': ('SHGroupName', 'SHGroupAbbrev', 'survey')})
    ]

    list_display = ('SHGroupName', 'SHGroupAbbrev', 'survey')
    # fieldset = [
    #     (None, {'fields': ('SHGroupName', 'SHGroupAbbrev')})
    # ]

    # list_display = ('SHGroupName', 'SHGroupAbbrev')

    # Search
    search_fields = ['SHGroupName', 'SHGroupAbbrev']
    # Filter
    list_filter = ['SHGroupName']

    model = SHGroup

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        survey = form.base_fields['survey']

        survey.widget.can_add_related = False
        survey.widget.can_change_related = False
        survey.widget.can_delete_related = False

        return form
    # action = ['delete_model']

    # def delete_model(self, request, obj):
    #     if obj.id is not None:
    #         id = 'stakeholder-{0}'.format(obj.id)
    #         deleteVertex(id)
    #     obj.delete()

class SHCategoryAdmin(admin.ModelAdmin):
    list_display = ('SHCategoryName', 'survey', 'mapType', 'icon')
    model = SHCategory
    # action = ['delete_model']

    # Search
    search_fields = ['SHCategoryName']
    # Filter
    list_filter = ['SHCategoryName', 'survey']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        survey = form.base_fields['survey']

        survey.widget.can_add_related = False
        survey.widget.can_change_related = False
        survey.widget.can_delete_related = False

        mapType = form.base_fields['mapType']

        mapType.widget.can_add_related = False
        mapType.widget.can_change_related = False
        mapType.widget.can_delete_related = False
        
        return form
    # def delete_model(self, request, obj):
    #     if obj.id is not None:
    #         id = 'category-{0}'.format(obj.id)
    #         #print(id)
    #         deleteVertex(id)
    #     obj.delete()

class ProjectUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'projectUserTitle', 'project', 'team', 'shGroup')
    model = ProjectUser

    # Search
    search_fields = ['user', 'projectUserTitle', 'project', 'team', 'shGroup']
    # Filter
    list_filter = ['user', 'project', 'team', 'shGroup']
    #action = ['delete_model']

    # def get_changelist_form(self, request, **kwargs):
    #     return ProjectUserForm
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        team = form.base_fields['team']
        user = form.base_fields['user']
        project = form.base_fields['project']
        shGroup = form.base_fields['shGroup']

        project.widget.can_add_related = False
        project.widget.can_change_related = False
        project.widget.can_delete_related = False
        
        team.widget.can_add_related = False
        team.widget.can_change_related = False
        team.widget.can_delete_related = False

        user.widget.can_add_related = False
        user.widget.can_change_related = False
        user.widget.can_delete_related = False

        shGroup.widget.can_add_related = False
        shGroup.widget.can_change_related = False
        shGroup.widget.can_delete_related = False

        return form


    def save_model(self, request, obj, form, change):
        super(ProjectUserAdmin, self).save_model(request, obj, form, change)
        messages.info(request, 'Email invitation has been sent.')
    # def delete_model(self, request, obj):
    #     if obj.id is not None:
    #         id = 'user-{0}'.format(obj.id)
    #         #print(id)
    #         deleteVertex(id)
    #     obj.delete()

class SHMappingAdmin(admin.ModelAdmin):
    list_display = ('shCategory', 'projectUser', 'subProjectUser', 'relationshipStatus')

    # Search
    search_fields = ['shCategory', 'projectUser', 'subProjectUser']
    # Filter
    list_filter = ['shCategory', 'projectUser', 'subProjectUser']

    model = SHMapping

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        shCategory = form.base_fields['shCategory']
        projectUser = form.base_fields['projectUser']
        subProjectUser = form.base_fields['subProjectUser']

        shCategory.widget.can_add_related = False
        shCategory.widget.can_change_related = False
        shCategory.widget.can_delete_related = False

        projectUser.widget.can_add_related = False
        projectUser.widget.can_change_related = False
        projectUser.widget.can_delete_related = False

        subProjectUser.widget.can_add_related = False
        subProjectUser.widget.can_change_related = False
        subProjectUser.widget.can_delete_related = False

        return form

admin.site.register(SHGroup, SHGroupAdmin)
admin.site.register(ProjectUser, ProjectUserAdmin)
admin.site.register(SHCategory, SHCategoryAdmin)
admin.site.register(SHMapping, SHMappingAdmin)
admin.site.register(MapType)