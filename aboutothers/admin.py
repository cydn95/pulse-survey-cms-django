from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import AOQuestion, AOQuestionSHGroup, AOQuestionOption, AOQuestionSkipOption, AOResponse, AOResponseTopic, AOPage, AOQuestionForm
from django.forms import CheckboxSelectMultiple
from django.contrib.admin.views.main import ChangeList
from import_export.admin import ImportExportModelAdmin
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.utils.encoding import smart_text
import json
from django.conf.urls import include, url
from survey.models import Driver
from django.core.serializers import serialize

class AOQuestionList(ChangeList):

    def __init__(self, request, model, list_display,
        list_display_links, list_filter, date_hierarchy,
        search_fields, list_select_related, list_per_page,
        list_max_show_all, list_editable, model_admin):

        super(AOQuestionList, self).__init__(request, model,
            list_display, list_display_links, list_filter,
            date_hierarchy, search_fields, list_select_related,
            list_per_page, list_max_show_all, list_editable,
            model_admin)

        # these need to be defined here, and not in MovieAdmin
        self.list_display = ['action_checkbox', 'aoqOrder', 'questionText', 'survey', 'driver', 'subdriver', 'controlType', 'sliderTextLeft', 'sliderTextRight', 'shGroup']
        self.list_display_links = ['questionText']
        self.list_editable = ['shGroup', 'option', 'skipOption']

class AOQuestionAdmin(SortableAdminMixin, admin.ModelAdmin):

    # Search
    search_fields = ['questionText']
    # Filter
    list_filter = ['driver', 'controlType', 'shGroup']
    model = AOQuestion
    list_display = ['aoqOrder', 'questionText', 'survey', 'driver', 'subdriver', 'controlType', 'sliderTextLeft', 'sliderTextRight', 'longForm', 'shortForm']
    list_display_links = ['questionText']
    exclude = ['isStandard']
    list_per_page = 10

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'drivers_for_survey', self.drivers_for_survey),
        ]
        return my_urls + urls

    def drivers_for_survey(self, request):
        if request.GET and 'survey_id' in request.GET:
            # objs = Driver.objects.filter(survey=request.GET['survey_id'])
            # print(objs)
            # ret = []
            # for o in objs:
            #     ret.append({'id': o.id, 'name': o.driverName})
            data = serialize('json', Driver.objects.filter(survey=request.GET['survey_id']))

            return HttpResponse(data, content_type="text/plain")
        else:
            return JsonResponse({'error': 'Not Ajax or no GET'})

    class Media:
        js = ('//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js', '/static/admin/js/fill_driver.js',)

    def get_changelist_form(self, request, **kwargs):
        return AOQuestionForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        controlType = form.base_fields['controlType']

        controlType.widget.can_add_related = False
        controlType.widget.can_change_related = False
        controlType.widget.can_delete_related = False

        return form

#class AOResponseAdmin(admin.ModelAdmin):
class AOResponseAdmin(ImportExportModelAdmin):
    # old version
    # list_display = ['aoQuestion', 'user', 'subjectUser', 'project', 'survey', 'integerValue', 'topicValue', 'commentValue', 'skipValue']
    # fileds = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']
    # readonly_fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']
    
    # search_fields = ['aoQuestion']
    # list_filter = ['user', 'subjectUser', 'project', 'survey']
    # model = AOResponse

    # def has_add_permission(self, request):
    #     return False
    
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(AOResponseAdmin, self).get_form(request, obj, **kwargs)

    #     controlType = getattr(obj, 'controlType')
    #     skipValue = getattr(obj, 'skipValue')
    #     if controlType == 'TEXT':
    #         if skipValue != '':
    #             self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'skipValue']
    #         else:
    #             self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'topicValue', 'commentValue']
    #     elif controlType == 'SLIDER':
    #         if skipValue != '':
    #             self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'skipValue']
    #         else:
    #             self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'integerValue', 'commentValue']
    #     elif controlType == 'TWO_OPTIONS':
    #         if skipValue != '':
    #             self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'skipValue']
    #         else:
    #             self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'topicValue', 'commentValue']
    #     elif controlType == 'MULTI_OPTIONS':
    #         if skipValue != '':
    #             self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'skipValue']
    #         else:
    #             self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'topicValue', 'commentValue']
    #     elif controlType == 'MULTI_TOPICS':
    #         if skipValue != '':
    #             self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'skipValue']
    #         else:
    #             self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'topicValue', 'commentValue']
    #     elif controlType == 'SMART_TEXT':
    #         if skipValue != '':
    #             self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'skipValue']
    #         else:
    #             self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'topicValue', 'commentValue']
    #     else:
    #         self.fields = ['user', 'subjectUser', 'survey', 'project', 'aoQuestion', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']

    #     return form

    # update user, subjectuser to projectUser, subjectProjectUser     2020-05-20
    list_display = ['aoQuestion', 'projectUser', 'subProjectUser', 'shCategory', 'project', 'survey', 'integerValue', 'topicValue', 'commentValue', 'skipValue']
    fileds = ['projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']
    readonly_fields = ['projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']
    
    search_fields = ['aoQuestion']
    list_filter = ['projectUser', 'subProjectUser', 'shCategory', 'project', 'survey']
    list_per_page = 10
    
    model = AOResponse

    def has_add_permission(self, request):
        return False
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(AOResponseAdmin, self).get_form(request, obj, **kwargs)

        controlType = getattr(obj, 'controlType')
        skipValue = getattr(obj, 'skipValue')
        if controlType == 'TEXT':
            if skipValue != '':
                self.fields = ['projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'skipValue']
            else:
                self.fields = ['projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'topicValue', 'commentValue']
        elif controlType == 'SLIDER':
            if skipValue != '':
                self.fields = ['projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'skipValue']
            else:
                self.fields = ['projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'integerValue', 'commentValue']
        elif controlType == 'TWO_OPTIONS':
            if skipValue != '':
                self.fields = ['projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'skipValue']
            else:
                self.fields = ['projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'topicValue', 'commentValue']
        elif controlType == 'MULTI_OPTIONS':
            if skipValue != '':
                self.fields = ['projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'skipValue']
            else:
                self.fields = ['projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'topicValue', 'commentValue']
        elif controlType == 'MULTI_TOPICS':
            if skipValue != '':
                self.fields = ['projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'skipValue']
            else:
                self.fields = ['projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'topicValue', 'commentValue']
        elif controlType == 'SMART_TEXT':
            if skipValue != '':
                self.fields = ['projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'skipValue']
            else:
                self.fields = ['projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'topicValue', 'commentValue']
        else:
            self.fields = ['projectUser', 'subProjectUser', 'shCategory', 'survey', 'project', 'aoQuestion', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']

        return form

# Register your models here.
admin.site.register(AOQuestion, AOQuestionAdmin)
admin.site.register(AOQuestionSHGroup)
admin.site.register(AOQuestionOption)
admin.site.register(AOQuestionSkipOption)
admin.site.register(AOResponse, AOResponseAdmin)
admin.site.register(AOResponseTopic)
admin.site.register(AOPage)