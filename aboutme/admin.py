from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import AMQuestion, AMQuestionSHGroup, AMQuestionOption, AMQuestionSkipOption, AMResponse, AMResponseTopic, AMQuestionForm
from django.forms import CheckboxSelectMultiple
from django.contrib.admin.views.main import ChangeList
from import_export.admin import ImportExportModelAdmin


class AMQuestionList(ChangeList):

    def __init__(self, request, model, list_display,
        list_display_links, list_filter, date_hierarchy,
        search_fields, list_select_related, list_per_page,
        list_max_show_all, list_editable, model_admin):

        super(AMQuestionList, self).__init__(request, model,
            list_display, list_display_links, list_filter,
            date_hierarchy, search_fields, list_select_related,
            list_per_page, list_max_show_all, list_editable, 
            model_admin)

        self.list_display = ['action_checkbox', 'amqOrder', 'questionText', 'driver', 'subdriver', 'controlType', 'sliderTextLeft', 'sliderTextRight', 'shGroup']
        self.list_display_links = ['questionText']
        self.list_editable = ['shGroup', 'option', 'skipOption']


class AMQuestionAdmin(SortableAdminMixin, admin.ModelAdmin):

    # Search
    search_fields = ['questionText']
    # Filter
    list_filter = ['driver', 'controlType', 'shGroup']
    model = AMQuestion
    list_display = ['amqOrder', 'questionText', 'driver', 'subdriver', 'controlType', 'sliderTextLeft', 'sliderTextRight']
    list_display_links = ['questionText']

    def get_changelist_form(self, request, **kwargs):
        return AMQuestionForm
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        controlType = form.base_fields['controlType']

        controlType.widget.can_add_related = False
        controlType.widget.can_change_related = False
        controlType.widget.can_delete_related = False

        return form

class AMResponseAdmin(ImportExportModelAdmin):
    # old version
    # list_display = ['amQuestion', 'user', 'project', 'survey', 'integerValue', 'topicValue', 'commentValue', 'skipValue']
    # fields = ['user', 'subjectUser', 'survey', 'project', 'amQuestion', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']
    # readonly_fields = ['user', 'subjectUser', 'survey', 'project', 'amQuestion', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']
    
    # search_fields = ['amQuestion']
    # list_filter = ['user', 'project', 'survey']
    # model = AMResponse

    # def has_add_permission(self, request):
    #     return False
    
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(AMResponseAdmin, self).get_form(request, obj, **kwargs)
        
    #     controlType = getattr(obj, 'controlType')
    #     skipValue = getattr(obj, 'skipValue')
    #     if controlType == 'TEXT':
    #         if skipValue != '':
    #             self.fields = ['user', 'project', 'survey', 'amQuestion', 'skipValue']
    #         else:
    #             self.fields = ['user', 'project', 'survey', 'amQuestion', 'topicValue', 'commentValue']
    #     elif controlType == 'SLIDER':
    #         if skipValue != '':
    #             self.fields = ['user', 'project', 'survey', 'amQuestion', 'skipValue']
    #         else:
    #             self.fields = ['user', 'project', 'survey', 'amQuestion', 'integerValue', 'commentValue']
    #     elif controlType == 'TWO_OPTIONS':
    #         if skipValue != '':
    #             self.fields = ['user', 'project', 'survey', 'amQuestion', 'skipValue']
    #         else:
    #             self.fields = ['user', 'project', 'survey', 'amQuestion', 'topicValue', 'commentValue']
    #     elif controlType == 'MULTI_OPTIONS':
    #         if skipValue != '':
    #             self.fields = ['user', 'project', 'survey', 'amQuestion', 'skipValue']
    #         else:
    #             self.fields = ['user', 'project', 'survey', 'amQuestion', 'topicValue', 'commentValue']
    #     elif controlType == 'MULTI_TOPICS':
    #         if skipValue != '':
    #             self.fields = ['user', 'project', 'survey', 'amQuestion', 'skipValue']
    #         else:
    #             self.fields = ['user', 'project', 'survey', 'amQuestion', 'topicValue', 'commentValue']
    #     elif controlType == 'SMART_TEXT':
    #         if skipValue != '':
    #             self.fields = ['user', 'project', 'survey', 'amQuestion', 'skipValue']
    #         else:
    #             self.fields = ['user', 'project', 'survey', 'amQuestion', 'topicValue', 'commentValue']
    #     else:
    #         self.fields = ['user', 'project', 'survey', 'amQuestion', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']

    #     return form

    # update user, subjectuser to projectUser, subjectProjectUser     2020-05-20
    list_display = ['amQuestion', 'projectUser', 'project', 'survey', 'integerValue', 'topicValue', 'commentValue', 'skipValue']
    fields = ['projectUser', 'subProjectUser', 'survey', 'project', 'amQuestion', 'controlType', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']
    readonly_fields = ['projectUser', 'subProjectUser', 'survey', 'project', 'amQuestion', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']
    
    search_fields = ['amQuestion']
    list_filter = ['projectUser', 'project', 'survey']
    model = AMResponse

    def has_add_permission(self, request):
        return False
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(AMResponseAdmin, self).get_form(request, obj, **kwargs)
        
        controlType = getattr(obj, 'controlType')
        skipValue = getattr(obj, 'skipValue')
        if controlType == 'TEXT':
            if skipValue != '':
                self.fields = ['projectUser', 'project', 'survey', 'amQuestion', 'skipValue']
            else:
                self.fields = ['projectUser', 'project', 'survey', 'amQuestion', 'topicValue', 'commentValue']
        elif controlType == 'SLIDER':
            if skipValue != '':
                self.fields = ['projectUser', 'project', 'survey', 'amQuestion', 'skipValue']
            else:
                self.fields = ['projectUser', 'project', 'survey', 'amQuestion', 'integerValue', 'commentValue']
        elif controlType == 'TWO_OPTIONS':
            if skipValue != '':
                self.fields = ['projectUser', 'project', 'survey', 'amQuestion', 'skipValue']
            else:
                self.fields = ['projectUser', 'project', 'survey', 'amQuestion', 'topicValue', 'commentValue']
        elif controlType == 'MULTI_OPTIONS':
            if skipValue != '':
                self.fields = ['projectUser', 'project', 'survey', 'amQuestion', 'skipValue']
            else:
                self.fields = ['projectUser', 'project', 'survey', 'amQuestion', 'topicValue', 'commentValue']
        elif controlType == 'MULTI_TOPICS':
            if skipValue != '':
                self.fields = ['projectUser', 'project', 'survey', 'amQuestion', 'skipValue']
            else:
                self.fields = ['projectUser', 'project', 'survey', 'amQuestion', 'topicValue', 'commentValue']
        elif controlType == 'SMART_TEXT':
            if skipValue != '':
                self.fields = ['projectUser', 'project', 'survey', 'amQuestion', 'skipValue']
            else:
                self.fields = ['projectUser', 'project', 'survey', 'amQuestion', 'topicValue', 'commentValue']
        else:
            self.fields = ['projectUser', 'project', 'survey', 'amQuestion', 'integerValue', 'topicValue', 'commentValue', 'skipValue', 'topicTags', 'commentTags']

        return form

admin.site.register(AMQuestion, AMQuestionAdmin)
admin.site.register(AMQuestionSHGroup)
admin.site.register(AMQuestionOption)
admin.site.register(AMQuestionSkipOption)
admin.site.register(AMResponse, AMResponseAdmin)
admin.site.register(AMResponseTopic)
