from django.contrib import admin
from .models import SHGroup, SHCategory, SHMapping, ProjectUser, MapType, SHType
from jet.admin import CompactInline
from django.forms import CheckboxSelectMultiple
from django.contrib import messages
import json
from django.conf.urls import include, url
from django.core.serializers import serialize
from django.http import HttpResponse
from django.http.response import JsonResponse

class SHGroupAdmin(admin.ModelAdmin):
    fieldset = [(None, {'fields': ('SHGroupName', 'SHGroupAbbrev', 'survey')})]

    list_display = ('SHGroupName', 'SHGroupAbbrev', 'survey')
    search_fields = ['SHGroupName', 'SHGroupAbbrev']
    list_filter = ['SHGroupName']
    list_per_page = 10

    model = SHGroup

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        survey = form.base_fields['survey']

        survey.widget.can_add_related = False
        survey.widget.can_change_related = False
        survey.widget.can_delete_related = False

        return form

class SHTypeAdmin(admin.ModelAdmin):
    list_display = ('survey', 'shTypeName')
    model = SHType

    search_fields = ['shTypeName']
    list_filter = ['shTypeName', 'survey']
    list_per_page = 10

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        survey = form.base_fields['survey']

        survey.widget.can_add_related = True
        survey.widget.can_change_related = False
        survey.widget.can_delete_related = False

        return form

class SHCategoryAdmin(admin.ModelAdmin):
    list_display = ('SHCategoryName', 'survey', 'mapType', 'icon')
    model = SHCategory

    search_fields = ['SHCategoryName']
    list_filter = ['SHCategoryName', 'survey']
    list_per_page = 10

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

class ProjectUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'projectUserTitle', 'survey', 'shType', 'team', 'shGroup')
    model = ProjectUser

    search_fields = ['user__email', 'projectUserTitle', 'survey__surveyTitle', 'team__name', 'shGroup__SHGroupName']

    list_filter = ['user', 'survey', 'team', 'shGroup']
    list_per_page = 10

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'shgroups_for_survey', self.shgroups_for_survey),
        ]

        return my_urls + urls
    
    def shgroups_for_survey(self, request):
        print(request)
        if request.GET and 'survey_id' in request.GET:
            
            data = serialize('json', SHGroup.objects.filter(survey=request.GET['survey_id']))
            print(data)
            return HttpResponse(data, content_type="text/plain")
        else:
            print('error')
            return JsonResponse({'error': 'Not Ajax or no GET'})
    
    class Media:
        js = ('//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js', '/static/admin/js/fill_shgroup.js',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        team = form.base_fields['team']
        user = form.base_fields['user']
        survey = form.base_fields['survey']
        shGroup = form.base_fields['shGroup']
        addByProjectUser = form.base_fields['addByProjectUser']

        survey.widget.can_add_related = False
        survey.widget.can_change_related = False
        survey.widget.can_delete_related = False
        
        team.widget.can_add_related = False
        team.widget.can_change_related = False
        team.widget.can_delete_related = False

        user.widget.can_add_related = False
        user.widget.can_change_related = False
        user.widget.can_delete_related = False

        shGroup.widget.can_add_related = False
        shGroup.widget.can_change_related = False
        shGroup.widget.can_delete_related = False

        addByProjectUser.widget.can_add_related = False
        addByProjectUser.widget.can_change_related = False
        addByProjectUser.widget.can_delete_related = False

        return form


    def save_model(self, request, obj, form, change):
        super(ProjectUserAdmin, self).save_model(request, obj, form, change)
        
        messages.info(request, 'Email invitation has been sent.')

class SHMappingAdmin(admin.ModelAdmin):
    list_display = ('shCategory', 'projectUser', 'subProjectUser', 'relationshipStatus')

    search_fields = ['shCategory__SHCategoryName', 'projectUser__projectUserTitle', 'subProjectUser__projectUserTitle']
    list_filter = ['shCategory', 'projectUser', 'subProjectUser']
    list_per_page = 10
    
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
admin.site.register(SHType, SHTypeAdmin)
