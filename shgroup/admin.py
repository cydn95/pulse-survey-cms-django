from django.contrib import admin
from .models import SHGroup, SHCategory, SHMapping, ProjectUser, MapType, ProjectUserForm
from jet.admin import CompactInline
from gremlin import deleteVertex
from django.forms import CheckboxSelectMultiple

class SHGroupAdmin(admin.ModelAdmin):
    fieldset = [
        (None, {'fields': ('SHGroupName', 'SHGroupAbbrev', 'project')})
    ]

    list_display = ('SHGroupName', 'SHGroupAbbrev', 'project')

    model = SHGroup
    action = ['delete_model']

    def delete_model(self, request, obj):
        if obj.id is not None:
            id = 'stakeholder-{0}'.format(obj.id)
            deleteVertex(id)
        obj.delete()

class SHCategoryAdmin(admin.ModelAdmin):
    list_display = ('SHCategoryName', 'survey', 'shGroup', 'mapType', 'colour', 'icon')
    model = SHCategory
    action = ['delete_model']

    def delete_model(self, request, obj):
        if obj.id is not None:
            id = 'category-{0}'.format(obj.id)
            #print(id)
            deleteVertex(id)
        obj.delete()

class ProjectUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'team', 'shGroup')
    model = ProjectUser
    action = ['delete_model']

    def get_changelist_form(self, request, **kwargs):
        return ProjectUserForm

    def delete_model(self, request, obj):
        if obj.id is not None:
            id = 'user-{0}'.format(obj.id)
            #print(id)
            deleteVertex(id)
        obj.delete()

admin.site.register(SHGroup, SHGroupAdmin)
admin.site.register(ProjectUser, ProjectUserAdmin)
admin.site.register(SHCategory, SHCategoryAdmin)
admin.site.register(SHMapping)
admin.site.register(MapType)